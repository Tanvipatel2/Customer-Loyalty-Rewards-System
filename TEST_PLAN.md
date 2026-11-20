# Test plan

## Automated tests
Run:
```bash
python manage.py test
```

The test suite checks:
1. A valid code credits the customer's wallet and creates a ledger entry.
2. A previously redeemed code cannot be redeemed a second time.
3. A customer cannot claim a reward without enough points.
4. A pending claim reserves points.
5. Staff approval changes the claim state and reduces reward stock.
6. Staff rejection refunds points exactly once.

## Manual acceptance plan
| Test | Steps | Expected result |
|---|---|---|
| Register | Create a customer account | Customer dashboard opens |
| Invalid code | Submit a random code | Friendly error; balance unchanged |
| Valid code | Submit generated code | 10 points credited |
| Reuse | Submit same code again | Rejected; no additional points |
| Reward | Claim a reward with sufficient points | Pending claim appears; points reserved |
| Approve | Staff approves pending claim | Approved status; stock decreases |
| Reject | Staff rejects pending claim | Rejected status; points refunded |
| Access control | Customer opens `/owner/` | Access denied/redirected |
| CSV | Staff generates a code batch | CSV downloads; generated codes are unique |

Record actual results and date after running the tests. Do not mark a test passed unless you have executed it.
