# Assumptions and decisions

| Missing requirement | Assumption | Why |
|---|---|---|
| Product identification | Each sealed box contains a hidden scratch-off code | Simple to print and does not require a receipt or customer POS account |
| Proof of purchase | Possession of a valid hidden code is accepted as proof | Code is available only after opening a genuine box in the assumed packaging design |
| Code format | Random 12-character uppercase alphanumeric code, grouped for readability | Hard to guess while remaining practical to type |
| Code lifecycle | A code can be redeemed once, by one registered account | Prevents reuse and gives a clear ownership trail |
| Points value | One accepted product code earns 10 points | A transparent starting value; owner can change it in the redemption logic |
| Reward catalogue | Staff create rewards with points cost and available stock | Allows campaigns to change without code changes |
| Reward fulfilment | A customer request is pending until staff approves it | Physical rewards need manual stock/dispatch checks |
| Rejected claims | Points are refunded automatically; stock is not reduced until approval | Customers should not lose points for a rejected request |
| Customer identity | Email and password account | Gives each wallet a stable account identity |
| Owner access | Django staff/superuser accounts manage operations | Uses Django's established permission system |
| Currency, shipping, tax | Outside this prototype | Not required to demonstrate loyalty mechanics |
| Factory integration | No ERP/POS, barcode scanner, shipping, SMS or email integration | No API or operational details were supplied |
| Abuse controls | Random codes, one-time database state, unique constraint and atomic redemption | Protects against guessing/reuse at application level |
| Rate limits | Production deployment should add CAPTCHA and per-IP/account throttling | Local academic prototype does not include a reverse proxy or rate-limit service |
| Deployment | Local SQLite demo | No hosting provider or production credentials were supplied |

All values are demonstration defaults, not confirmed commercial policies. A real factory should test the point economics, reward margins, code printing controls, privacy policy and fulfilment process before launch.
