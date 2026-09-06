import json

with open('/Users/vietmac/Documents/CODE/fedu-font/data/catalog.json') as f:
    cat = json.load(f)

from build_full_pool import CANDIDATE_POOL, VIETNAMESE_LOWERCASE, VIETNAMESE_UPPERCASE

def select_sample_text(mood, index):
    pool = CANDIDATE_POOL.get(mood, CANDIDATE_POOL["Bold & Tuyên ngôn"])
    return pool[index % len(pool)]

simulated_samples = []
for idx, font in enumerate(cat['fonts']):
    mood = font.get('matrix_3d', {}).get('mood', 'Bold & Tuyên ngôn')
    st = select_sample_text(mood, idx)
    simulated_samples.append(st)

all_text = " ".join(simulated_samples)
missing_lower = [ch for ch in VIETNAMESE_LOWERCASE if ch not in all_text]
missing_upper = [ch for ch in VIETNAMESE_UPPERCASE if ch not in all_text]

print("=== 361 FONTS SIMULATED SAMPLE TEXT CHECK ===")
print("Total fonts simulated:", len(simulated_samples))
print("Missing lowercase characters count:", len(missing_lower))
if missing_lower:
    print("Missing lower:", missing_lower)
print("Missing uppercase characters count:", len(missing_upper))
if missing_upper:
    print("Missing upper:", missing_upper)
