"""Apply the transparent ad screen to all supplied ad copies for inspection."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from intrusive_ad_model import classify


root = Path(__file__).resolve().parent
ads = pd.read_csv(root / "AdCharacteristicsTable.csv", header=1)
rows = []
for item in ads.itertuples(index=False):
    result = classify(item.Ad_Content, item.Ad_Targeting_Criteria)
    rows.append({"Ad_ID": item.Ad_ID, "Ad_Content": item.Ad_Content,
                 "Ad_Targeting_Criteria": item.Ad_Targeting_Criteria,
                 "tier": result["tier"], "raw_cue_score": result["score"],
                 "score_out_of_10": result["score_out_of_10"],
                 "matched_cues": "; ".join(x["cue"] for x in result["evidence"])})
out = pd.DataFrame(rows)
(root / "results").mkdir(exist_ok=True)
out.to_csv(root / "results" / "ad_screen_results.csv", index=False)
print(json.dumps(out.tier.value_counts().to_dict(), indent=2))
