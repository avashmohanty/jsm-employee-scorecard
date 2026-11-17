"""Generate a SYNTHETIC JSM-style ticket export. No real client or employee data."""
import random, csv
from datetime import datetime, timedelta

random.seed(42)
ANALYSTS = [f"Analyst {chr(65+i)}" for i in range(12)]
TOWERS = {"Tower 1": ANALYSTS[0:4], "Tower 2": ANALYSTS[4:8], "Tower 3": ANALYSTS[8:12]}
PRIORITIES = ["P1", "P2", "P3", "P4"]
# Mean resolution hours by priority (drives the demo; analysts get a speed factor)
MEAN_H = {"P1": 1.8, "P2": 4.5, "P3": 13, "P4": 38}
SPEED = {a: random.uniform(0.6, 1.1) for a in ANALYSTS}
SPEED["Analyst C"] = 2.6   # deliberately slow, so the demo has something to flag

rows = []
start = datetime(2026, 1, 1)
for i in range(1, 601):
    tower = random.choice(list(TOWERS))
    assignee = random.choice(TOWERS[tower])
    itype = random.choices(["Incident", "Service Request"], weights=[30, 70])[0]
    prio = random.choices(PRIORITIES, weights=[5, 15, 45, 35] if itype == "Incident" else [1, 9, 40, 50])[0]
    created = start + timedelta(days=random.randint(0, 270), hours=random.randint(0, 23), minutes=random.randint(0, 59))
    hours = max(0.5, random.gauss(MEAN_H[prio] * SPEED[assignee], MEAN_H[prio] * 0.3))
    resolved = created + timedelta(hours=hours)
    if random.random() < 0.06:  # still open
        resolved = None
    rows.append([f"DEMO-{i:04d}", itype, prio, tower, assignee,
                 created.strftime("%Y-%m-%d %H:%M"), resolved.strftime("%Y-%m-%d %H:%M") if resolved else ""])

with open("data/sample_tickets.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["Key", "Issue Type", "Priority", "Tower", "Assignee", "Created", "Resolved"])
    w.writerows(rows)
print(f"Wrote {len(rows)} synthetic tickets")

# Created by Avash Mohanty, 2026
