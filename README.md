# JSM Employee Scorecard

Turn a Jira Service Management export into a per-analyst scorecard: incidents (INC) and service requests (SR) resolved, SLA compliance by priority, and a weighted workload share per tower.

## Problem
Delivery managers building monthly or quarterly people scorecards from JSM usually do it by hand in Excel. That is slow, inconsistent between months, and counts an easy SR the same as a P1 incident, which distorts who is carrying the load.

## Approach
- Input: a JSM CSV export (`Key, Issue Type, Priority, Tower, Assignee, Created, Resolved`).
- SLA compliance is calculated per ticket against configurable hour targets per priority (`sla_config.json`).
- Workload is **weighted** (default: INC = 2.0, SR = 1.0, configurable) so the share-of-tower figure reflects effort, not just ticket count.
- Analysts below an SLA threshold (default 80%) are flagged `REVIEW`. The flag is a prompt for a conversation, not a verdict: check ticket mix and priority before acting on it.
- Output: Excel workbook (`Scorecard`, `Tower_Summary`) plus CSV.

## Run it
```bash
pip install pandas openpyxl
python generate_sample_data.py          # synthetic data only
python scorecard.py --input data/sample_tickets.csv --out output/scorecard.xlsx
```

## Measured result (synthetic demo data, reproducible with seed 42)
| Metric | Result |
|---|---|
| Tickets processed | 600 (570 resolved, 30 open) |
| Analysts scored across 3 towers | 12 |
| Runtime | about 0.5 seconds |
| Analysts flagged below 80% SLA | 1 of 12 (the deliberately slow Analyst C) |

These numbers come from generated data and demonstrate that the logic works. They are not a claim about any real team.

**Your real-world result (fill in after running on your own export):**
| Metric | Before (manual) | After (this tool) |
|---|---|---|
| Time to produce scorecard | _ hrs | _ min |

## Limitations
- SLA hours are calendar hours. If your contract uses business hours or pause-on-pending clocks, extend `scorecard.py`.
- Assumes one assignee per ticket (the final assignee in the export).
- Ticket counts and SLA % are inputs to a performance conversation, not a complete measure of an individual's contribution.

## Data policy
All data in this repo is synthetic. Do not commit real exports, names, or client information.

Created by Avash Mohanty, 2026
