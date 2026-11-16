#!/usr/bin/env python3
"""Step 3 of the daily pipeline: verify every draft before it is saved to Gmail.

Checks each draft against the project's email rules (CLAUDE.md), the contact ledger,
the do-not-contact list, a deliverability checklist of spam triggers, and against the
other drafts of the day so no two pitches read like a template.

Input: runs/<date>/drafts.json  ->  [{"brand","domain","to","subject","pitch","source_url","source_quote"}]
  pitch       = the 3-4 sentence body only (greeting and signature are added by the runbook)
  source_url  = page on the brand's own site where the address was seen
  source_quote= the exact text from that page containing the address
Output: runs/<date>/check_report.json, exit code 1 if any draft has an ERROR.
"""
import csv, json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

SPAM_TRIGGERS = [
    "free", "guarantee", "guaranteed", "risk-free", "risk free", "act now", "limited time",
    "urgent", "click here", "100%", "no obligation", "winner", "cash", "earn", "double your",
    "once in a lifetime", "special promotion", "exclusive deal", "dear sir", "dear madam",
    "to whom it may concern", "increase sales", "skyrocket", "explode", "10x", "!!",
]
OVERCLAIMS = [r"\b\d+(\.\d+)?\s?%", r"\bproven\b", r"\bresults\b", r"\bpartner(ed|ship)? with\b",
              r"\bofficial\b", r"\bwe (helped|grew|scaled)\b"]
ROLE_OK = {"marketing", "partnerships", "partners", "press", "media", "pr", "hello", "hi", "info",
           "contact", "team", "wholesale", "growth", "ecommerce", "brand", "collabs", "collab",
           "creators", "affiliates", "business", "sales", "support", "help", "care", "cs",
           "enquiries", "inquiries", "customerservice", "orders", "comms"}


def rows(path):
    p = ROOT / path
    return list(csv.DictReader(p.open())) if p.exists() else []


def sentences(text):
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9\"'])", text.strip())
    return [s for s in parts if s.strip()]


def shingles(text, n=3):
    w = re.findall(r"[a-z']+", text.lower())
    return {" ".join(w[i:i + n]) for i in range(max(0, len(w) - n + 1))}


def check(d, ledger, dnc):
    E, W = [], []
    to = d.get("to")
    if not isinstance(to, str) or "," in to or ";" in to:
        E.append("exactly one recipient required (rule 2)")
        to = str(to)
    if d.get("cc") or d.get("bcc"):
        E.append("no CC/BCC allowed (rule 2)")
    m = re.fullmatch(r"([a-z0-9._%+-]+)@([a-z0-9.-]+\.[a-z]{2,})", to.strip().lower())
    if not m:
        E.append(f"malformed address: {to}")
        local, dom = "", ""
    else:
        local, dom = m.groups()
    brand_dom = (d.get("domain") or "").lower().removeprefix("www.")
    if dom and brand_dom and not (dom == brand_dom or dom.endswith("." + brand_dom) or brand_dom.endswith("." + dom)):
        W.append(f"address domain {dom} differs from brand domain {brand_dom}: confirm it is the brand's own")
    if local and local.split("+")[0] not in ROLE_OK:
        if re.search(r"[a-z]+\.[a-z]+|^[a-z]\.?[a-z]+$", local):
            W.append("looks like a personal address: allowed ONLY if published verbatim by the brand (rule 3)")
    # verification evidence: the address must have been seen on a public page
    if not d.get("source_url"):
        E.append("no source_url: address not verified on a public page (rule 3, no guessing)")
    if to.lower() not in (d.get("source_quote") or "").lower():
        E.append("source_quote does not contain the exact address")
    # ledger / do-not-contact
    bl = (d.get("brand") or "").strip().lower()
    for r in dnc:
        if bl == r["brand"].lower() or (dom and dom == r["domain"].lower()) or brand_dom == r["domain"].lower():
            E.append(f"DO NOT CONTACT: {r['brand']} ({r['reason']})")
    for r in ledger:
        if bl == r["brand"].lower() or (r["domain"] and brand_dom == r["domain"].lower()) \
                or (r["email"] and to.lower() == r["email"].lower()):
            E.append(f"already in ledger as '{r['status']}' ({r['brand']}): rule 5, check thread instead")
    # subject
    subj = d.get("subject", "")
    if "Attn: E-Commerce Lead" not in subj:
        E.append("subject must contain 'Attn: E-Commerce Lead' (rule 2)")
    if len(subj) > 70:
        W.append(f"subject is {len(subj)} chars; keep under 70")
    if re.search(r"[A-Z]{5,}", subj.replace("Attn", "")) or "!" in subj:
        W.append("subject has shouting caps or '!'")
    # body (rule 1)
    pitch = d.get("pitch", "")
    n = len(sentences(pitch))
    if not 3 <= n <= 4:
        E.append(f"pitch has {n} sentences; must be 3-4 (rule 1)")
    if re.search(r"https?://|www\.|\b[a-z0-9-]+\.(com|co|io|ai|app|net|org|shop|store)\b", pitch, re.I):
        E.append("pitch contains a link or domain (rule 1)")
    if "$" in pitch or re.search(r"\b(usd|dollars?)\b", pitch, re.I):
        E.append("pitch mentions money (rule 1)")
    if "<" in pitch and ">" in pitch:
        E.append("pitch looks like HTML; must be plain text")
    words = len(pitch.split())
    if words > 110:
        W.append(f"pitch is {words} words; aim for 60-110")
    low = pitch.lower()
    hits = [t for t in SPAM_TRIGGERS if re.search(r"(?<![a-z])" + re.escape(t) + r"(?![a-z])", low)]
    if hits:
        W.append(f"spam-trigger words: {hits}")
    for pat in OVERCLAIMS:
        if re.search(pat, pitch, re.I):
            E.append(f"overclaim / implied partnership ('{pat}'): demos are unofficial, numbers are modelled only")
    if d.get("brand") and d["brand"].lower() not in low:
        W.append("brand name not in pitch: personalise it")
    if d.get("hero_product") and d["hero_product"].split()[0].lower() not in low:
        W.append("hero product not referenced")
    return E, W


def main():
    date = sys.argv[1]
    run = ROOT / "runs" / date
    drafts = json.loads((run / "drafts.json").read_text())
    ledger, dnc = rows("data/ledger.csv"), rows("data/do_not_contact.csv")
    report, bad = [], 0
    seen_to = set()
    for i, d in enumerate(drafts):
        E, W = check(d, ledger, dnc)
        if d.get("to", "").lower() in seen_to:
            E.append("duplicate recipient within today's batch")
        seen_to.add(d.get("to", "").lower())
        for j, o in enumerate(drafts[:i]):
            a, b = shingles(d.get("pitch", "")), shingles(o.get("pitch", ""))
            if a and b and len(a & b) / len(a | b) > 0.45:
                W.append(f"reads too much like the {o.get('brand')} draft: rewrite for this brand")
        bad += bool(E)
        report.append({"brand": d.get("brand"), "to": d.get("to"), "pass": not E, "errors": E, "warnings": W})
    (run / "check_report.json").write_text(json.dumps(report, indent=2))
    for r in report:
        print(("PASS " if r["pass"] else "FAIL ") + f"{r['brand']} <{r['to']}>")
        for e in r["errors"]:
            print("   ERROR", e)
        for w in r["warnings"]:
            print("   warn ", w)
    print(f"\n{len(report) - bad}/{len(report)} drafts pass")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
