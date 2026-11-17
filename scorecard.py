"""JSM employee scorecard: INC/SR handled, SLA compliance, weighted workload.

Usage: python scorecard.py --input data/sample_tickets.csv --config sla_config.json --out output/scorecard.xlsx
Input columns: Key, Issue Type, Priority, Tower, Assignee, Created, Resolved
"""
import argparse, json
import pandas as pd

def build(df: pd.DataFrame, cfg: dict):
    df = df.copy()
    df["Created"] = pd.to_datetime(df["Created"])
    df["Resolved"] = pd.to_datetime(df["Resolved"])
    done = df.dropna(subset=["Resolved"]).copy()
    done["hours"] = (done["Resolved"] - done["Created"]).dt.total_seconds() / 3600
    done["target"] = done["Priority"].map(cfg["sla_hours"])
    done["sla_met"] = done["hours"] <= done["target"]
    done["weight"] = done["Issue Type"].map(cfg["weights"])

    g = done.groupby(["Tower", "Assignee"])
    sc = pd.DataFrame({
        "INC_Resolved": g.apply(lambda x: (x["Issue Type"] == "Incident").sum(), include_groups=False),
        "SR_Resolved": g.apply(lambda x: (x["Issue Type"] == "Service Request").sum(), include_groups=False),
        "Total_Resolved": g.size(),
        "Weighted_Workload": g["weight"].sum(),
        "Median_Resolution_Hrs": g["hours"].median().round(1),
        "SLA_Met_Pct": (g["sla_met"].mean() * 100).round(1),
    }).reset_index()
    open_ct = df[df["Resolved"].isna()].groupby("Assignee").size()
    sc["Open_Now"] = sc["Assignee"].map(open_ct).fillna(0).astype(int)
    sc["Share_of_Tower_Workload_Pct"] = (sc["Weighted_Workload"] / sc.groupby("Tower")["Weighted_Workload"].transform("sum") * 100).round(1)
    sc["Flag"] = sc["SLA_Met_Pct"].apply(lambda v: "REVIEW" if v < cfg["sla_flag_threshold_pct"] else "OK")
    sc = sc.sort_values(["Tower", "Weighted_Workload"], ascending=[True, False])

    tower = done.groupby("Tower").agg(Resolved=("Key", "size"), SLA_Met_Pct=("sla_met", lambda s: round(s.mean() * 100, 1)),
                                     Median_Hrs=("hours", lambda s: round(s.median(), 1))).reset_index()
    return sc, tower

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True); ap.add_argument("--config", default="sla_config.json")
    ap.add_argument("--out", default="output/scorecard.xlsx")
    a = ap.parse_args()
    cfg = json.load(open(a.config))
    sc, tower = build(pd.read_csv(a.input), cfg)
    with pd.ExcelWriter(a.out, engine="openpyxl") as xw:
        sc.to_excel(xw, sheet_name="Scorecard", index=False); tower.to_excel(xw, sheet_name="Tower_Summary", index=False)
    sc.to_csv(a.out.replace(".xlsx", ".csv"), index=False)
    print(sc.to_string(index=False)); print(); print(tower.to_string(index=False))
    print(f"\nFlagged for review: {(sc['Flag'] == 'REVIEW').sum()} of {len(sc)} analysts")

if __name__ == "__main__":
    main()

# Created by Avash Mohanty, 2026
