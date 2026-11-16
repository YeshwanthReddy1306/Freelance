# Freelance: D2C outreach automation

A scheduled Claude Code cloud session runs this every Monday to Saturday at 4:41 AM Eastern, so it
finishes before 7 AM:

1. **Triage replies** in Gmail and update `data/ledger.csv`. A positive reply goes to the top of
   the report, because the 48-hour build clock has started.
2. **Gemini researches** about 25 candidate US DTC Shopify brands and suggests the offer (tool,
   ads or both), a tool idea and an ad angle (`automation/gemini_research.py`).
3. **Claude verifies** each candidate on the brand's own site: that it runs on Shopify, that the
   product is current, and that its contact email is published there verbatim. Claude never
   guesses an address. It stops at 10 verified brands.
4. **Claude writes** a 3-4 sentence plain-text pitch for each brand.
5. **Cross-verify** each draft with `automation/check_drafts.py`. It checks the email rules, the
   ledger, the do-not-contact list, spam triggers, overclaims and near-duplicates.
6. **Gmail drafts** are created; nothing is ever sent automatically. A report is written to
   `runs/<date>/report.md` and committed.

You review the drafts and send them by hand, 4-5 minutes apart.

| File | Purpose |
| :--- | :--- |
| `CLAUDE.md` | Project context and outreach rules |
| `automation/RUNBOOK.md` | The step-by-step procedure the daily session follows |
| `data/ledger.csv` | Every brand touched, with its status, so no brand is contacted twice |
| `data/do_not_contact.csv` | Brands that said no or block mail |
| `runs/<date>/` | Candidates, drafts, check report and summary for each day |

The Gemini key is saved as a network secret on the cloud environment (sent as a Bearer token to
`generativelanguage.googleapis.com`), never in this repo.
