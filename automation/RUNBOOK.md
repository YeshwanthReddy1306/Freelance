# Daily outreach run (Mon–Sat, finishes before 7:00 AM Eastern)

You are the scheduled session that runs this pipeline. Nobody is watching while it runs:
do not wait for answers, and never send an email. The only outputs are **Gmail drafts**, a
**run report**, and a **commit to `main`**. Follow `CLAUDE.md` (project rules) at all times.

## 0. Set up

1. Today's date in America/New_York: `TZ=America/New_York date +%F` (call it `DATE`).
   If it is Sunday, stop and report "Sunday, no run."
2. If `runs/DATE/report.md` already exists, a run already happened today: stop and report that.

## 1. Triage replies (before any new outreach)

1. In Gmail, search the inbox for messages since the last run from any domain in
   `data/ledger.csv` (e.g. `in:inbox newer_than:2d -from:me`). Read each thread in full.
2. Classify every reply: `positive` (they want the demo or a call), `negative` (no, not a fit,
   stop), `autoreply`, `bounce`, `question`.
3. Update the brand's row in `data/ledger.csv` (`status`, `last_update`, `notes`).
   - `negative` → also add it to `data/do_not_contact.csv`.
   - `bounce` → mark `bounced`; never retry that address.
   - `positive` → status `yes_build_owed`, and put it at the **top of the report**: the 48-hour
     build clock has started. Save a short Gmail **draft reply** in that thread confirming the
     timeline. Do not send it.

## 2. Research (Claude, live web)

Read `automation/RESEARCH_BRIEF.md` for who to find, what to offer, which signals to look for
and what to avoid. Where a section says `TBD`, use the default under it. If `WebSearch` or
`WebFetch` are deferred tools, load them with ToolSearch first.

1. Run several web searches in parallel built from the brief, for example
   "<category> brand Shopify direct to consumer", "best <category> brands 2026",
   "<category> startup raises", "<category> new product launch", and roundups or gift guides
   in the brief's categories. Vary the queries day to day so the same brands don't keep coming back.
2. Build a list of the number of candidate brands set in the brief (default 25). Skip any brand,
   parent company or sister brand that is already in `data/ledger.csv` or
   `data/do_not_contact.csv`.
3. For each candidate, fill in: `brand`, `domain`, `category`, `hero_product`, `why_now` (one
   sentence on the buying-decision friction, with the signal you found and its URL),
   `offer_fit` (A, B or C), `tool_idea`, `ad_angle`, `contact_pages`.
4. Save the list as `runs/DATE/candidates.json`: `{"date","prospects":[...],"queries":[...]}`.

Treat anything from search snippets, roundups or third-party sites as a lead to check, not as
fact. Contact details are only ever taken from step 3 below.

## 3. Verify each candidate (stop at 10 verified)

Work through the candidates in order. For each brand:

1. **Already contacted?** Check Gmail with `in:anywhere (to:@DOMAIN OR from:@DOMAIN)`
   and check the ledger. Any hit means skip (rule 5).
2. **US DTC on Shopify?** Fetch the homepage. Look for Shopify signals (`cdn.shopify.com`,
   `/products/`, `Shopify.theme`). If it isn't Shopify-based, skip.
3. **Product is real and current:** confirm `hero_product` exists on the site with its current
   name. Fix the name if it differs.
4. **Contact email, verified:** fetch the brand's contact, press, partnerships, wholesale and
   footer pages (`contact_pages`, plus `/pages/contact`, `/contact`, `/pages/press`,
   `/pages/wholesale`). Keep an address **only if it appears verbatim on a page on the
   brand's own domain** (or its official help centre). Record `source_url` and the exact
   `source_quote`. Prefer, in order: partnerships / marketing / press / hello / info / contact,
   then support.
   - **Never construct an address from a name pattern** (`first.last@…`). That caused 20+
     bounces in November (rule 3). If no address is published, mark the brand
     `form_only` or `no_contact_found` in the ledger and move on.
5. **Socials:** keep the Instagram and LinkedIn URLs only if the brand's own site links to them.
   Name an e-commerce lead only if a public source shows it; mark it "verify manually" and
   never use it as an email address.

If fewer than 10 brands pass, repeat step 2 once with new queries for another batch of candidates
(skip every brand already checked today). Then stop. **Never pad the list
with unverified contacts.** Fewer, real drafts are the right outcome.

## 4. Write the emails

For each verified brand, write a `pitch` (body only, without greeting or signature):

- 3–4 sentences, plain text, 60–110 words. No links, no domains, no prices or `$`, no percentages.
- Sentence 1: a specific buying-decision friction on *their* site for *their* hero product
  (sizing, compatibility, runtime, bundling, layout). It must be something you saw on the site.
- Sentence 2: the offer that fits (`offer_fit`). A = the interactive tool idea; B = the 9:16
  ad angle (3 concepts × hooks); C = lead with the tool and mention ads in half a sentence.
- Sentence 3: a working demo within 48 hours, and they only pay if they use it. Call it a
  concept demo; never imply a partnership or past results.
- Sentence 4 (optional): a low-friction question ("Worth sending over this week?").
- Subject: `<Brand> <hero product or tool idea> - Attn: E-Commerce Lead`, under 70 characters.
- Every pitch must read as written for that brand; the checker flags near-duplicates.

Save them as `runs/DATE/drafts.json`:
`[{"brand","domain","hero_product","to","subject","pitch","source_url","source_quote","offer_fit","instagram","linkedin"}]`

## 5. Cross-verify

```bash
python3 automation/check_drafts.py DATE
```

Fix and re-run until every draft passes. Deal with each warning (rewrite) or explain it in the
report. A draft that still has an ERROR is dropped, never saved.

## 6. Save Gmail drafts (do not send)

For each passing draft, call Gmail `create_draft` with exactly one `to`, no cc/bcc, the subject,
and a plain-text `body`:

```
Hi <Brand> team,

<pitch>

Best,
Yeshwanth Reddy Chintala
Yeshwanth Digital CRO & Paid Media Lab
Instagram: @yeshreddy07
```

Record each draft's id or `viewUrl`.

## 7. Record and report

1. Append each drafted brand to `data/ledger.csv` with status `drafted`, `email`, `source_url`,
   `last_update=DATE`, and offer fit / tool idea in `notes`. Add skipped brands too
   (`form_only`, `no_contact_found`, `not_shopify`) so they are never researched again.
2. Write `runs/DATE/report.md` containing:
   - **Action needed:** positive replies or builds owed (with deadline), bounces.
   - **Today's drafts:** a table of brand, address, source, offer, tool idea, ad angle,
     Instagram, LinkedIn and Gmail draft link.
   - **Skipped:** each skipped brand and the reason.
   - **Send plan:** send the drafts by hand, 4–5 minutes apart (rule 4).
3. `git add -A && git commit -m "Outreach run DATE" && git push origin main`
   (retry the push up to 4 times with backoff).
4. Finish with a short summary: the number of drafts, any action needed, and the report path.
