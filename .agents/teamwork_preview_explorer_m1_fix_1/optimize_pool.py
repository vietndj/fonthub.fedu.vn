import json

with open('/Users/vietmac/Documents/CODE/fedu-font/data/catalog.json') as f:
    cat = json.load(f)

# Mood of each font:
font_moods = [(idx, f.get('matrix_3d', {}).get('mood', 'Bold & Tuyên ngôn')) for idx, f in enumerate(cat['fonts'])]

from build_full_pool import VIETNAMESE_LOWERCASE, VIETNAMESE_UPPERCASE

# Let's inspect the 5 missing uppercase chars: ['Ă', 'Ằ', 'E', 'Ú', 'Ý']
# If we include sentences with those chars in the hit indices of Bold & Tuyên ngôn, OR in Luxury/Tech/Friendly/Nostalgic (e.g. at the start of sentences):
# Notice: In Vietnamese, the first letter of a sentence is capitalized!
# For example:
# "Ăn quả nhớ kẻ trồng cây..." has 'Ă'!
# "Ằm..." -> wait, "Ăn quả..." has Ă!
# "Ằng..." wait, is there a word starting with Ằ?
# In Vietnamese, words starting with Ằ or Ẵ or Ặ or Ẫ are rare as first words ("Ẵm bồng", "Ặc", "Ắt hẳn").
# BUT in Bold & Tuyên ngôn, the entire sentence is in ALL-CAPS!
# In Bold & Tuyên ngôn, if ALL sentences or the hit sentences contain all uppercase characters, let's see which indices are hit!

indices_by_mood = {}
for idx, mood in font_moods:
    indices_by_mood.setdefault(mood, []).append(idx)

for mood, indices in indices_by_mood.items():
    print(f"Mood: {mood}, count: {len(indices)}")

bold_indices = indices_by_mood['Bold & Tuyên ngôn']
for N in range(5, 25):
    hit = set(idx % N for idx in bold_indices)
    if len(hit) == N:
        print(f"Pool size {N} has 100% index coverage for Bold ({N}/{N})")
