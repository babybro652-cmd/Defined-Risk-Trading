# Prosperity Legendz: fast track to a live funnel (11/11/2026)

Goal: LEGEND comment -> DM -> Systeme opt-in -> Cushion Plan PDF -> 5 welcome emails.
Blocker: Systeme needs a verified sender domain before it will send.

## Why the domain blocks the funnel

- Since Feb 2024, Gmail and Yahoo require senders to prove who they are with SPF, DKIM and DMARC. Mail that fails goes to spam or gets bounced.
- A @gmail.com "From" address sent through Systeme fails that check: Systeme's servers are not Google's, so the receiving inbox treats it as forged. Systeme will not let you send from a free address for that reason.
- Verifying = adding a few DNS records that Systeme gives you (SPF/DKIM as CNAME or TXT records, plus one DMARC TXT record) to a domain you own. Then inboxes can see the mail is really from you.

## Big find: Tim already owns prosperitylegendz.com

- Registered 4/18/2024, paid through **4/18/2027** (public registry lookup, 11/11/2026).
- DNS already runs on **Cloudflare** (nameservers harlan / tegan.ns.cloudflare.com). Registrar of record: Tucows (a reseller, probably whatever platform the 2024 funnel used).
- In 2024 it sent email as tim@lc.prosperitylegendz.com and used go.prosperitylegendz.com (the old BLC/LeadConnector funnel, see Gmail Sept 2024 and the Drive doc "BLC V2 BLC 7 Day Email Series").
- **No purchase needed.** Cost now: $0.
- Check first: does the zone show up in Tim's own Cloudflare account (the one with peacebypage.com)? If yes, go. If not, find which account holds it (search Gmail for "Cloudflare" and "Tucows"/"OpenSRS" from April 2024).
- Optional later: transfer the registration to Cloudflare Registrar at cost (about $10.50 for .com, adds a year). Not urgent until spring 2027.

Backups only if Tim can't get into the domain (all looked unregistered 11/11, Cloudflare at-cost .com about $10.50/yr):
1. prosperitylegendz.net
2. theprosperitylegendz.com
3. prosperitylegendzhq.com

## Checklist

Who: **Tim** = needs his logins, money or a decision. **Jarvis** = can do it from here.

| # | Step | Who | Time |
|---|---|---|---|
| 1 | Buy domain: skip, already owned. Confirm prosperitylegendz.com is in your Cloudflare account. | Tim | 5 min |
| 2 | Clean up old DNS: in Cloudflare, screenshot the DNS list and send it. Old 2024 records (lc., go., any SPF/DMARC) may clash. | Tim sends, Jarvis checks | 5 min |
| 3 | Systeme: Settings > Emails > Domains > add prosperitylegendz.com. Pick sender: hello@prosperitylegendz.com (or tim@). | Tim | 5 min |
| 4 | Copy Systeme's records into Cloudflare DNS (CNAMEs: proxy OFF, grey cloud). One SPF and one DMARC per name only; replace old ones, don't add a second. Paste records to Jarvis to check before saving. | Tim, Jarvis checks | 15 min |
| 5 | Verify in Systeme. Often minutes, can take up to 24-48 h. | Tim clicks | 2 min + wait |
| 6 | Reply inbox: Cloudflare Email Routing (free) forwards hello@prosperitylegendz.com to Gmail, so replies land somewhere. | Tim, Jarvis gives steps | 10 min |
| 7 | Footer mailing address (CAN-SPAM needs a street address, a USPS P.O. box, or a registered private mailbox). Options below. | Tim decides and pays | 30 min (P.O. box in person) or 15 min online |
| 8 | Decide "I'm Tim" or "Prosperity Legendz" only in the About + 5 emails. | Tim | 1 min |
| 9 | Build funnel in Systeme: opt-in page, thank-you page (PDF link), tag "Cushion Plan", campaign "Cushion Plan Welcome" (days 0, 2, 4, 7, 10), rule: tag added -> subscribe to campaign. | Tim builds, Jarvis gives click-by-click steps + final copy | 60-90 min |
| 10 | Final copy pass on the 5 emails: fill [BRACKETS], add footer address, fact-check money claims, no em dashes. Email 5 affiliate slot stays out. | Jarvis | 20 min |
| 11 | Fix Blotato automation 9422: "Content Type" -> "Content-Type"; button URL -> Systeme thank-you page; DM sign-ups get the Cushion Plan tag. | Tim | 15 min |
| 12 | Test: comment LEGEND on the PL page (pageId 519238117933038) from your personal Facebook. Check DM, opt-in, tag, email 1 arrives in Gmail inbox (not spam). Jarvis checks the automation run log. | Tim, Jarvis checks logs | 15 min |
| 13 | Rotate the Systeme API key. | Tim | 2 min |

Total Tim time: about 3 hours, spread over 2-3 evenings. Fastest path: steps 1-5 tonight (30 min), 7-8 at lunch, 9-12 one evening.

## Footer address options

| Option | Price (approx.) | Notes |
|---|---|---|
| USPS P.O. box, Roxboro | Size 1 about $34-79 per 6 months depending on the post office fee group | Cheapest; one trip to the post office with 2 IDs |
| Anytime Mailbox | from about $5-10/mo | Online signup, mail scanned; needs USPS Form 1583 notarized (online notary available) |
| iPostal1 | from $9.99/mo | Same as above, larger network |
| Home address | $0 | Legal, but public in every email; not recommended |

Prices from third-party 2026 guides; confirm at usps.com and the provider sites before paying.

## What already exists

- Freebie PDF: Drive, "Prosperity Legendz - Assets" folder, "The $1,000 Cushion Plan.pdf".
- Landing page copy, thank-you page, DM copy and all 5 welcome emails: Drive doc 12jYNbJY63fH7Oz86g6fjWgp2Qa61eUCK1yLbVN9iZ6s (draft 9/28). Not in this repo. Still has [BRACKETS] to fill.

## Sources

- Google email sender guidelines: https://support.google.com/a/answer/81126
- Yahoo sender requirements: https://senders.yahooinc.com/best-practices/
- Systeme DMARC help: https://help.systeme.io/article/10240-dmarc-reports-how-to-read-and-use-them
- Systeme deliverability guide: https://help.systeme.io/article/4247-general-guidelines-and-best-practices-for-email-deliverability-during-the-first-few-days
- FTC CAN-SPAM guide (physical postal address): https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business
- P.O. box prices: https://theletterpilot.com/guides/po-box-costs-2026, https://fedratecalc.com/po-box-cost/
- Virtual mailbox prices: https://businessanywhere.io/ipostal1-vs-anytime-mailbox-which-virtual-mailbox-wins/
- Domain record: Verisign RDAP lookup for prosperitylegendz.com, 11/11/2026
