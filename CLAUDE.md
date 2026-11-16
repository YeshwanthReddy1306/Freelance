# D2C outreach and prototype project

Context for Claude Code. State as of 16 November 2026.

## What this project is

Yeshwanth Reddy Chintala runs **Yeshwanth Digital CRO & Paid Media Lab**, a solo studio pitching US direct-to-consumer Shopify brands. Instagram: `@yeshreddy07`.

The method: build a brand-specific interactive prototype, deploy it to Vercel, and use the live link as the pitch.

### Offers

| Offer | Price | Notes |
| :--- | :--- | :--- |
| Interactive Shopify tool | $600-$850 pilot ($1,200-$1,500 standard) | Built in 48 hours, paid only if the brand approves it |
| Paid-social ad retainer | $2,000-$2,500 per month | About 10 vertical 9:16 ads: 3 concepts x 3-4 hooks, with whitelisting rights |
| Bundle of both | $2,250-$2,900 | |

## Build standard for each prototype

- One self-contained `index.html` plus `vercel.json` and `package.json`, ready for Vercel.
- Mobile-first, vanilla HTML/CSS/JS, tabular numerals, live SVG or Canvas visual.
- Three tabs:
  1. Configurator, sizer or calculator with real-time maths and a "complete the bundle" add-on drawer.
  2. 9:16 ad lab: phone simulator with 3 concepts and 3-4 clickable hooks each.
  3. Pilot deal breakdown with copy buttons for the email pitch.
- Reference build: the Burrow room configurator (`burrow-vercel-deploy.vercel.app`).

### Rules to keep the work honest

- Label every prototype as an unofficial concept demo. Do not imply a partnership with the brand.
- Cart-lift figures are add-on prices summed inside the demo. Call them "modelled" or "potential", never results.
- Re-check prices and product names on the brand's live site before building; the handoff figures go stale.

## Build queue

1. Birdbuddy: Nook vs Home gift matchmaker and bundler
2. Aventon: rider fit, hub vs mid-drive, cargo accessories
3. Jackery: outage runtime and SolarSaga bundler
4. Trak Racer: wheelbase, cockpit and bracket compatibility builder

Already built (files not yet located, see Open items): agency site, Burrow, Lectric, Lasfit, WOLFBOX, Branch media kit PDF.

## Outreach state

### Sent on 16 November

37 first-touch emails went out between 15:16 and 15:25 IST. Each offers a working demo within 48 hours at no cost unless used. Any brand that says yes is owed that build in two days.

Lectric and WOLFBOX were told a demo already exists, so those two need deploying before any reply.

### Do not contact again

| Brand | Reason |
| :--- | :--- |
| Whisker | CEO Jacob Zuppke replied "No" on 12 November |
| Redwood Outdoors | Partnerships team said "not a fit at the moment" on 13 November |
| Kinesis | `sales@kinesis-ergo.com` rejects outside mail (blocked twice) |

### Use the form, not email

- Burrow / Havenly Brands: asked for submissions through their Google Form.
- Birdbuddy: asked for their partner form. It is a reseller form, so do not enter order quantities that are not real.

### Automated responses only so far

Aventon (no-reply autoresponder; ambassadors go to `ambassador@aventon.com`), Plunge (ticket 314030), Trak Racer (tickets 2009700033 and 2009703856), Fellow (660586), recteq (1129356), BLUETTI (769756), iKamper, Rapsodo, Eight Sleep, Gozney, TuxMat.

### Useful contact found

Chemical Guys: an auto-reply on 11 November pointed to `mgulrajani@chemicalguys.com`.

### Published inboxes used

| Brand | Address |
| :--- | :--- |
| Ooni | marketing@ooni.com |
| BLUETTI | marketing@bluetti.com |
| Breeo | contact@breeo.com |
| Fellow | hello@fellowproducts.com |
| NOMATIC | info@nomatic.com |
| Gozney | enquiries@gozney.com |
| Therabody | info@therabody.com |
| NewAge Products | info@newageproducts.com |
| Solo Stove | help@solostove.com |
| Eight Sleep | support@eightsleep.com |
| Hydrow | support@hydrow.com |
| Gardyn | support@mygardyn.com |
| Rapsodo | support@rapsodo.com |
| recteq | support@recteq.com |
| Griot's Garage | customerservice@griotsgarage.com |
| Adam's Polishes | orders@adamspolishes.com |
| Lectric | contact@lectricebikes.com |
| Aventon | marketing@aventon.com |
| Jackery | marketing@jackery.com |
| Trak Racer | sales@trakracer.com |
| Lasfit | cs@lasfit.com |
| Branch | comms@branchfurniture.com |
| WOLFBOX | contact@wolfbox.com |
| UPLIFT Desk | hello@upliftdesk.com |
| TuxMat | info@tuxmat.ca |

No published address was found for MORRFlate, Autonomous or HigherDOSE.

## Email rules

1. First touch: plain text, 3-4 sentences, no links, no dollar signs.
2. One recipient, a published inbox, with "Attn: E-Commerce Lead" in the subject. No CC.
3. Never guess executive addresses. More than 20 messages bounced between 10 and 14 November that way, which hurts the Gmail sender reputation.
4. Space sends 4-5 minutes apart. Today's batch broke this rule, so pause new sends for a few days.
5. Check sent mail and replies for a brand before writing to it again.
6. Save outreach as Gmail drafts for review; do not send directly.

## Open items

- **Prototype files are not located.** They are not on the Desktop. Find the HTML files and `-vercel-deploy.zip` archives (try Downloads or Documents) and copy them into this folder.
- **Vercel account is empty.** The team `yeshwanthreddy1306s-projects` has no projects, so the Burrow link is hosted under a different login.
- Deploy Lectric and WOLFBOX.
- Build Birdbuddy first.

## Daily automation

A scheduled cloud session runs `automation/RUNBOOK.md` Monday to Saturday at 4:41 AM Eastern. Gemini proposes prospects; Claude verifies contacts on each brand's own site, writes the pitches, checks them with `automation/check_drafts.py`, and saves Gmail drafts (never sends). `data/ledger.csv` and `data/do_not_contact.csv` are the source of truth for who has been contacted. Update them whenever outreach state changes.
