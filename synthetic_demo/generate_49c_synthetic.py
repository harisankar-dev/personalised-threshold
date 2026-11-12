"""Generate entirely simulated 49-C data for demos and pipeline tests. Not empirical evidence."""
import csv
import math
import random
from pathlib import Path

SEED = 49026
N_CONSUMERS = 300
OUTPUT = Path(__file__).with_name('49c_synthetic_consumer_exposures.csv')
LEVELS = [
    ('L0', 'generic', 0.0),
    ('L1', 'contextual_demographic', 0.75),
    ('L2', 'behavioral', 1.75),
    ('L3', 'historical', 2.45),
    ('L4', 'combined_hyperpersonalization', 3.3),
]
FIELDS = ['dataset_type','synthetic_consumer_id','split','privacy_concern_pre','relevance_preference_pre',
          'tracking_awareness_pre','personalization_preference_pre','simulated_segment','personalization_level',
          'level_description','disclosure_present','discomfort_1_7_simulated','relevance_1_7_simulated',
          'engagement_intent_1_7_simulated','high_discomfort_simulated']

def clamp_rating(x):
    return round(max(1., min(7., x)), 2)

def simulate(seed=SEED, n_consumers=N_CONSUMERS):
    rng = random.Random(seed)
    rows=[]
    for i in range(1, n_consumers + 1):
        cid = f'SYN{i:04d}'
        privacy = rng.randint(1,7)
        relevance = rng.randint(1,7)
        awareness = rng.randint(1,7)
        preference = rng.randint(1,7)
        segment = ('privacy_sensitive' if privacy>=5 else 'privacy_relaxed')+'__'+('relevance_seeking' if relevance>=5 else 'relevance_neutral')
        split = 'test' if i % 5 == 0 else 'train'
        # Every synthetic consumer sees all five fictional scenarios. Fixed respondent split avoids leakage.
        for level, description, intensity in LEVELS:
            disclosure = rng.randint(0,1)
            protective = 0.35 * disclosure
            discomfort = clamp_rating(1.20 + intensity*(0.53 + 0.11*(privacy-4)) + 0.19*(privacy-4)
                                      + 0.10*(awareness-4) - 0.14*(preference-4) - protective
                                      + rng.gauss(0,0.85))
            relevance_score = clamp_rating(2.60 + 0.61*intensity + 0.20*(relevance-4)
                                           + 0.12*(preference-4) - 0.14*max(0,intensity-2.4)*(privacy-4)
                                           + rng.gauss(0,0.85))
            intent = clamp_rating(2.55 + 0.46*(relevance_score-3.5) - 0.37*(discomfort-3.5)
                                  + rng.gauss(0,0.88))
            rows.append({'dataset_type':'SYNTHETIC_SIMULATION_NOT_REAL_RESPONDENTS',
                         'synthetic_consumer_id':cid,'split':split,
                         'privacy_concern_pre':privacy,'relevance_preference_pre':relevance,
                         'tracking_awareness_pre':awareness,'personalization_preference_pre':preference,
                         'simulated_segment':segment,'personalization_level':level,
                         'level_description':description,'disclosure_present':disclosure,
                         'discomfort_1_7_simulated':discomfort,'relevance_1_7_simulated':relevance_score,
                         'engagement_intent_1_7_simulated':intent,
                         'high_discomfort_simulated':int(discomfort>=5)})
    return rows

if __name__ == '__main__':
    data = simulate()
    with OUTPUT.open('w',newline='',encoding='utf-8') as file:
        writer=csv.DictWriter(file,fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(data)
    print(f'{OUTPUT}: {len(data)} synthetic exposures; {len(set(r["synthetic_consumer_id"] for r in data))} fictitious consumers')
