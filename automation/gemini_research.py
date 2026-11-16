#!/usr/bin/env python3
"""Step 1 of the daily pipeline: Gemini proposes prospect brands and the offer to pitch.

Gemini is used for ideation only (which brands, why, which offer, tool idea, ad angle).
It is NOT trusted for contact details: every email/handle it returns is treated as a
lead to verify, and Claude only keeps an address it has seen on the brand's own site.

Auth: the cloud environment's proxy injects the Gemini key for generativelanguage.googleapis.com.
- Saved under the x-goog-api-key header: grounded mode works (native API + live Google Search).
- Saved as a Bearer token: only the OpenAI-compatible endpoint works (no live search).
The script tries grounded first and falls back automatically.

Usage: python3 automation/gemini_research.py --date 2026-11-17 [--candidates 25]
Writes runs/<date>/candidates.json
"""
import argparse, csv, json, os, subprocess, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
URL = "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions"
NATIVE = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
# Free-tier friendly models, tried in order. Pro models have zero free quota.
MODELS = ["gemini-3.5-flash", "gemini-3.8-flash", "gemini-flash-latest", "gemini-3.1-flash-lite"]

SYSTEM = """You are the prospect researcher for "Yeshwanth Digital CRO & Paid Media Lab", a solo studio
that pitches US direct-to-consumer Shopify brands.

Offers:
A) Interactive Shopify tool: a brand-specific configurator, sizer, calculator or bundle builder,
   built in 48 hours, paid only if the brand approves it (pilot).
B) Paid-social ad retainer: about 10 vertical 9:16 ads a month (3 concepts x 3-4 hooks), with whitelisting.
C) Both.

Ideal prospect: US DTC brand selling on Shopify, roughly $5M-$150M revenue, considered-purchase
products where buyers must choose sizes, configurations, compatibility, runtimes or bundles
(e-bikes, power stations, outdoor cooking, furniture, fitness, sim racing, car care, pet tech, sleep,
home goods). Active paid social presence is a plus.

Hard rules:
- Never invent an email address, handle, URL or person. If you are not certain, use null.
- Prefer brands whose own website publishes a marketing, partnerships, press, wholesale or general contact email.
- Do not include any brand on the exclusion list, nor its parent company or sister brands.
- Return JSON only."""

USER = """Today is {date}. Propose {n} NEW prospect brands. Spread them across at least 5 categories.
Avoid these recently used categories where possible: {recent_cats}.

Exclusion list (already contacted, form-only, or do-not-contact): {excluded}

Return exactly this JSON shape:
{{"prospects":[{{
 "brand":"", "domain":"", "category":"",
 "hero_product":"the one product the pitch should reference",
 "why_now":"one sentence on the buyer-decision friction we can fix",
 "offer_fit":"A|B|C",
 "tool_idea":"one sentence: what the interactive tool does",
 "ad_angle":"one sentence: the 9:16 ad concept",
 "contact_pages":["URLs on the brand's own domain likely to list a contact email"],
 "suggested_email":null,
 "instagram":null, "linkedin_company":null,
 "ecommerce_lead_name":null, "ecommerce_lead_linkedin":null,
 "confidence":"high|medium|low"
}}]}}"""


def load_exclusions():
    names, domains, cats = set(), set(), []
    for f in ("data/ledger.csv", "data/do_not_contact.csv"):
        p = ROOT / f
        if p.exists():
            for row in csv.DictReader(p.open()):
                if row.get("brand"):
                    names.add(row["brand"].strip())
                if row.get("domain"):
                    domains.add(row["domain"].strip().lower())
    for run in sorted((ROOT / "runs").glob("*/candidates.json"))[-6:]:
        try:
            for p in json.loads(run.read_text()).get("prospects", []):
                cats.append(p.get("category", ""))
        except Exception:
            pass
    return names, domains, cats


def call(model, body):
    """Ungrounded fallback on the native endpoint (works with the x-goog-api-key secret).
    If the key is saved as a Bearer token instead, use the OpenAI-compatible endpoint."""
    sys_msg, user_msg = body["messages"][0]["content"], body["messages"][1]["content"]
    req = {"system_instruction": {"parts": [{"text": sys_msg}]},
           "contents": [{"role": "user", "parts": [{"text": user_msg}]}],
           "generationConfig": {"responseMimeType": "application/json"}}
    r = subprocess.run(["curl", "-sS", "-m", "300", NATIVE.format(model=model),
                        "-H", "Content-Type: application/json", "-d", json.dumps(req)],
                       capture_output=True, text=True)
    try:
        d = json.loads(r.stdout)
    except Exception:
        return None, f"non-JSON response: {r.stderr.strip()[:200]}"
    if isinstance(d, list):
        d = d[0]
    if "error" in d and d["error"].get("code") in (400, 401, 403):
        # key saved as Bearer: native API refuses it, the OpenAI-compatible endpoint accepts it
        r = subprocess.run(["curl", "-sS", "-m", "300", URL, "-H", "Content-Type: application/json",
                            "-d", json.dumps(dict(body, model=model))], capture_output=True, text=True)
        try:
            d = json.loads(r.stdout)
        except Exception:
            return None, f"non-JSON response: {r.stderr.strip()[:200]}"
        if isinstance(d, list):
            d = d[0]
        if "error" not in d:
            return d["choices"][0]["message"]["content"], None
    if "error" in d:
        return None, f"{d['error'].get('code')} {d['error'].get('message', '')[:200]}"
    return "".join(pt.get("text", "") for pt in d["candidates"][0]["content"]["parts"]), None


def call_grounded(model, body):
    """Native endpoint with live Google Search. Needs the key saved under the x-goog-api-key
    header; with a Bearer-only key Google rejects it and we fall back to ungrounded mode."""
    sys_msg, user_msg = body["messages"][0]["content"], body["messages"][1]["content"]
    req = {"system_instruction": {"parts": [{"text": sys_msg}]},
           "contents": [{"role": "user", "parts": [{"text": user_msg +
               "\nUse Google Search to confirm each brand is current. Output only the JSON object, no prose."}]}],
           "tools": [{"google_search": {}}]}
    r = subprocess.run(["curl", "-sS", "-m", "300", NATIVE.format(model=model),
                        "-H", "Content-Type: application/json", "-d", json.dumps(req)],
                       capture_output=True, text=True)
    try:
        d = json.loads(r.stdout)
    except Exception:
        return None, None, f"non-JSON response: {r.stderr.strip()[:200]}"
    if isinstance(d, list):
        d = d[0]
    if "error" in d:
        return None, None, f"{d['error'].get('code')} {d['error'].get('message', '')[:200]}"
    c = d["candidates"][0]
    text = "".join(pt.get("text", "") for pt in c["content"]["parts"])
    text = text[text.find("{"): text.rfind("}") + 1]
    srcs = [ch.get("web", {}).get("uri") for ch in c.get("groundingMetadata", {}).get("groundingChunks", [])]
    return text, [u for u in srcs if u], None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", required=True)
    ap.add_argument("--candidates", type=int, default=25,
                    help="ask for more than 10: some will fail contact verification")
    a = ap.parse_args()

    names, domains, cats = load_exclusions()
    body = {
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": USER.format(
                date=a.date, n=a.candidates,
                recent_cats=", ".join(sorted(set(c for c in cats if c))) or "none",
                excluded=", ".join(sorted(names | domains)))},
        ],
    }
    errors, sources, grounded = [], [], False
    attempts = []
    for model in MODELS:
        attempts.append(("grounded", model))
    for model in MODELS:
        attempts.append(("plain", model))
    for mode, model in attempts:
        if mode == "grounded" and errors and "OAuth" in errors[-1]:
            continue  # key not saved for grounded mode: skip straight to plain
        for attempt in range(1 if mode == "grounded" else 3):
            if mode == "grounded":
                text, sources, err = call_grounded(model, body)
            else:
                text, err = call(model, body)
            if text:
                try:
                    data = json.loads(text)
                except Exception:
                    errors.append(f"{mode} {model}: unparseable JSON"); break
                grounded = mode == "grounded"
                keep = [p for p in data.get("prospects", [])
                        if p.get("brand", "").strip() not in names
                        and (p.get("domain") or "").lower().removeprefix("www.") not in domains]
                out = {"date": a.date, "model": model, "grounded_search": grounded,
                       "search_sources": sources if grounded else [], "dropped_as_duplicates":
                       len(data.get("prospects", [])) - len(keep), "prospects": keep}
                d = ROOT / "runs" / a.date
                d.mkdir(parents=True, exist_ok=True)
                (d / "candidates.json").write_text(json.dumps(out, indent=2))
                print(f"OK mode={mode} model={model} kept={len(keep)} dropped={out['dropped_as_duplicates']} -> {d/'candidates.json'}")
                return 0
            errors.append(f"{mode} {model} try {attempt+1}: {err}")
            if err and (err.startswith("404") or err.startswith("429")):
                break  # model unavailable or out of quota: next model
            time.sleep(20 * (attempt + 1))
    print("FAILED\n" + "\n".join(errors), file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
