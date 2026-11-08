"""Reproduce the 49C data audit and a deliberately limited interaction-type baseline.

Run with a Python environment containing pandas and numpy: python analysis.py
Original source files are read only. Output goes to results/.
"""
from __future__ import annotations

import json
from pathlib import Path
import platform

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "results"
OUT.mkdir(exist_ok=True)
SEED = 49


def read(name: str) -> pd.DataFrame:
    # The first CSV line is a table label, the second is the actual header.
    return pd.read_csv(ROOT / name, header=1, low_memory=False).rename(
        columns=lambda x: x.strip().replace("  ", "_").replace(" ", "_")
    )


def auc(y: np.ndarray, p: np.ndarray) -> float:
    ranks = pd.Series(p).rank(method="average").to_numpy()
    n1 = int(y.sum())
    n0 = len(y) - n1
    return float((ranks[y == 1].sum() - n1 * (n1 + 1) / 2) / (n0 * n1))


def metrics(y: np.ndarray, p: np.ndarray) -> dict:
    pred = p >= 0.5
    tp = int(np.sum(pred & (y == 1)))
    fp = int(np.sum(pred & (y == 0)))
    fn = int(np.sum(~pred & (y == 1)))
    return {
        "n": len(y), "positive_rate": float(y.mean()),
        "roc_auc": auc(y, p), "brier": float(np.mean((p - y) ** 2)),
        "log_loss": float(-np.mean(y * np.log(np.clip(p, 1e-8, 1)) + (1-y) * np.log(np.clip(1-p, 1e-8, 1)))),
        "accuracy_at_0_5": float(np.mean(pred == y)),
        "precision_at_0_5": float(tp / (tp + fp)) if tp + fp else None,
        "recall_at_0_5": float(tp / (tp + fn)) if tp + fn else None,
    }


def matrix(df: pd.DataFrame, columns: list[str], levels: dict) -> np.ndarray:
    pieces = [np.ones((len(df), 1), dtype=np.float64)]
    for col in columns:
        vals = pd.to_numeric(df[col], errors="coerce").fillna(-999).to_numpy()
        # Reference category omitted; no arbitrary ordering of the privacy codes.
        pieces.extend((vals == level).astype(np.float64)[:, None] for level in levels[col][1:])
    return np.concatenate(pieces, axis=1)


def main() -> None:
    users = read("UserTable.csv")
    behavior = read("UserBehaviorTable.csv")
    privacy = read("Privacy-Related_Features.csv")
    ads = read("AdCharacteristicsTable.csv")
    events = read("User_Interaction_Table.csv")
    aggregate = read("interaction.csv")
    tables = {"users": users, "behavior": behavior, "privacy": privacy, "ads": ads, "events": events}
    audit = {"runtime": {"python": platform.python_version(), "pandas": pd.__version__, "numpy": np.__version__, "seed": SEED},
             "sources": {}, "joins": {}, "interpretation": {}}
    for name, df in tables.items():
        key = "Ad_ID" if name == "ads" else ("ID" if name == "events" else "User_ID")
        audit["sources"][name] = {
            "rows": len(df), "columns": list(df.columns),
            "missing_by_column": {k: int(v) for k, v in df.isna().sum().items()},
            "unique_primary_or_user_key": int(df[key].nunique()),
            "duplicate_primary_or_user_key_rows": int(df.duplicated(key).sum()),
        }

    user_ids = set(users.User_ID)
    ad_ids = set(ads.Ad_ID)
    audit["joins"] = {
        "behavior_rows_matching_user": int(behavior.User_ID.isin(user_ids).sum()),
        "behavior_distinct_users_matching_user": int(behavior.loc[behavior.User_ID.isin(user_ids), "User_ID"].nunique()),
        "behavior_rows_unmatched_user": int((~behavior.User_ID.isin(user_ids)).sum()),
        "behavior_users_with_multiple_rows": int(behavior.User_ID.value_counts().gt(1).sum()),
        "privacy_rows_matching_user": int(privacy.User_ID.isin(user_ids).sum()),
        "event_rows_matching_user": int(events.User_ID.isin(user_ids).sum()),
        "event_rows_matching_ad": int(events.Ad_ID.isin(ad_ids).sum()),
        "event_rows_matching_both": int((events.User_ID.isin(user_ids) & events.Ad_ID.isin(ad_ids)).sum()),
        "distinct_event_users_matching_user": int(events.loc[events.User_ID.isin(user_ids), "User_ID"].nunique()),
        "interaction_type_counts": {str(k): int(v) for k, v in events.interaction_Type.value_counts().sort_index().items()},
        "distinct_user_ad_pairs": int(events[["User_ID", "Ad_ID"]].drop_duplicates().shape[0]),
        "duplicate_user_ad_pair_rows": int(events.duplicated(["User_ID", "Ad_ID"]).sum()),
    }
    per_ad = events.pivot_table(index="Ad_ID", columns="interaction_Type", values="ID", aggfunc="count", fill_value=0)
    ad_summary = aggregate.set_index("Ad_ID")
    names = {32: "Likes", 33: "shares", 34: "comments", 35: "clicks"}
    audit["ad_summary_reconciliation"] = {
        "rows": len(aggregate),
        "per_action_ad_counts_matching_event_table": {
            name: int((per_ad[code] == ad_summary[name]).sum()) for code, name in names.items()
        },
        "ads_with_all_action_counts_matching": int(np.logical_and.reduce(
            [(per_ad[code] == ad_summary[name]).to_numpy() for code, name in names.items()]
        ).sum()),
        "ads_where_summary_clicks_exceed_summary_impressions": int((ad_summary.clicks > ad_summary.Impressions).sum()),
        "ads_where_summary_total_actions_exceed_summary_impressions": int((ad_summary.Total_Interaction > ad_summary.Impressions).sum()),
        "note": "Ad summary counts do not reconcile with the event table. Summary impressions cannot be attached to individual events or used as a user-level non-click denominator.",
    }
    # Behavior is not joined into the event model: its repeated User_ID would multiply rows.
    valid = events.loc[events.User_ID.isin(user_ids) & events.Ad_ID.isin(ad_ids)].copy()
    valid = valid.merge(privacy[["User_ID", "Data_Sharing_Permissions", "Privacy_Settings", "user_consent"]], on="User_ID", validate="many_to_one")
    clean = valid.rename(columns={"ID": "Event_ID"})
    clean["Action"] = clean.interaction_Type.map({32: "like", 33: "share", 34: "comment", 35: "click"})
    clean.to_csv(OUT / "clean_events.csv", index=False)
    excluded = events.loc[~(events.User_ID.isin(user_ids) & events.Ad_ID.isin(ad_ids))].copy()
    excluded["Exclusion_Reason"] = np.where(~excluded.User_ID.isin(user_ids), "unknown_user", "unknown_ad")
    excluded.to_csv(OUT / "excluded_events.csv", index=False)
    audit["joins"]["analytic_event_rows_after_privacy_join"] = len(valid)
    audit["joins"]["excluded_event_rows"] = len(excluded)
    audit["interpretation"] = {
        "unit": "recorded user-ad interaction event, not an impression or exposed user-ad pair",
        "outcome": "1 if recorded interaction type is click (code 35), 0 if like/share/comment (32/33/34)",
        "unavailable": ["non-interactions/impressions", "personalization intensity", "perceived intrusiveness", "user age/location", "exposure time"],
        "behavior_note": "Browsing_History is URL-like text and Purchase_History contains device models; neither is verified as product interest or purchases.",
        "privacy_note": "Data_Sharing_Permissions codes 2-6 are named level1-level5 but direction is unspecified; Privacy_Settings codes 20-31 name departments, not privacy strength. No composite sensitivity score is justified.",
    }
    (OUT / "audit.json").write_text(json.dumps(audit, indent=2), encoding="utf-8")

    # Stable user-grouped 80/20 split. Every event from one user stays on one side.
    all_users = np.sort(valid.User_ID.unique())
    rng = np.random.default_rng(SEED)
    rng.shuffle(all_users)
    test_users = set(all_users[:round(0.2 * len(all_users))])
    test = valid.User_ID.isin(test_users).to_numpy()
    train = ~test
    assert not set(valid.loc[train, "User_ID"]) & set(valid.loc[test, "User_ID"])
    y = (valid.interaction_Type.to_numpy() == 35).astype(np.float64)
    cols = ["Ad_ID", "Data_Sharing_Permissions", "Privacy_Settings", "user_consent"]
    levels = {c: sorted(valid[c].dropna().unique().tolist()) for c in cols}
    X = matrix(valid, cols, levels)
    # Full-batch, L2-regularized logistic regression; no third-party ML dependency.
    beta = np.zeros(X.shape[1])
    rate = float(y[train].mean())
    beta[0] = np.log(rate / (1-rate))
    n = int(train.sum())
    Xt = X[train]
    yt = y[train]
    for iteration in range(500):
        z = np.clip(Xt @ beta, -30, 30)
        p = 1 / (1 + np.exp(-z))
        grad = (Xt.T @ (p - yt)) / n
        grad[1:] += 0.002 * beta[1:]
        beta -= 2.0 * grad
        if np.max(np.abs(grad)) < 1e-6:
            break
    pred = 1 / (1 + np.exp(-np.clip(X[test] @ beta, -30, 30)))
    base = np.full(int(test.sum()), rate)
    result = {
        "label": audit["interpretation"]["outcome"],
        "split": "user-grouped, seeded 49, 80/20 unique-user split; one holdout only",
        "train_rows": n, "test_rows": int(test.sum()),
        "train_users": int(valid.loc[train, "User_ID"].nunique()),
        "test_users": int(valid.loc[test, "User_ID"].nunique()),
        "features": cols,
        "optimizer_iterations": iteration + 1,
        "maximum_absolute_final_gradient": float(np.max(np.abs(grad))),
        "constant_baseline": metrics(y[test], base),
        "regularized_logistic": metrics(y[test], pred),
        "limitation": "Conditional interaction-type classification only. Metrics are not click-through performance, causal lift, intrusiveness prediction, or threshold validation.",
    }
    (OUT / "baseline.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    # Descriptive association only: rates are conditional on a recorded action.
    associations = {}
    for col in ["Data_Sharing_Permissions", "Privacy_Settings", "user_consent", "Ad_ID"]:
        table = pd.crosstab(valid[col], valid.interaction_Type)
        prop = table.div(table.sum(axis=1), axis=0)
        expected = np.outer(table.sum(axis=1), table.sum(axis=0)) / table.to_numpy().sum()
        chi2 = float(((table.to_numpy() - expected) ** 2 / expected).sum())
        v = float(np.sqrt(chi2 / (table.to_numpy().sum() * min(table.shape[0]-1, table.shape[1]-1))))
        associations[col] = {
            "cramers_v": v,
            "click_fraction_by_code": {str(k): float(x) for k, x in prop[35].items()},
            "event_count_by_code": {str(k): int(x) for k, x in table.sum(axis=1).items()},
        }
    (OUT / "associations.json").write_text(json.dumps(associations, indent=2), encoding="utf-8")
    print(json.dumps({"audit": audit["joins"], "model": result}, indent=2))


if __name__ == "__main__":
    main()
