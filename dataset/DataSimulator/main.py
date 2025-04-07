import os
import random
from PIL import Image
from pathlib import Path
from collections import defaultdict

# Paths
CARD_DIR = Path("dataset\\assets\\cards\\labels_augmented")
TABLE_PATH = Path("dataset\\assets\\table.png")
OUTPUT_IMAGES = Path("dataset\\output\\images")
OUTPUT_LABELS = Path("dataset\\output\\labels")

OUTPUT_IMAGES.mkdir(parents=True, exist_ok=True)
OUTPUT_LABELS.mkdir(parents=True, exist_ok=True)

# Load card names
card_names = sorted([f.stem for f in CARD_DIR.glob("*/")])
card_to_class = {name: idx for idx, name in enumerate(card_names)}
used_card_tracker = defaultdict(int)

# Settings
TARGET_USES_PER_CARD = 200
CARDS_PER_IMAGE = 5
MAX_TOTAL_IMAGES = (TARGET_USES_PER_CARD * len(card_names)) // CARDS_PER_IMAGE

# Function to choose cards that need more appearances
def sample_balanced_cards(n=5):
    # Sort cards by how underused they are (lowest usage first)
    sorted_cards = sorted(card_names, key=lambda c: used_card_tracker[c])
    selected = []
    
    attempts = 0
    while len(selected) < n and attempts < 100:
        # Randomly pick from the most underused 20 cards
        candidate = random.choice(sorted_cards[:20])
        if candidate not in selected:
            selected.append(candidate)
        attempts += 1
    
    return selected

# Function to select a random augmented card image from the folder
def get_random_augmented_card_image(card_name):
    card_folder = CARD_DIR / card_name
    augmented_images = list(card_folder.glob("*.png"))

    return random.choice(augmented_images)

# Main image generation loop
image_id = 0
while any(used_card_tracker[c] < TARGET_USES_PER_CARD for c in card_names):
    selected_cards = sample_balanced_cards(CARDS_PER_IMAGE)

    table = Image.open(TABLE_PATH).convert("RGBA")
    W, H = table.size
    labels = []

    for i, card_name in enumerate(selected_cards):
        # Get a random augmented image for the card
        card_img_path = get_random_augmented_card_image(card_name)
        card_img = Image.open(card_img_path).convert("RGBA")
        card_img = card_img.resize((70, 100))

        x = 100 + i * 90 + random.randint(-10, 10)
        y = H // 2 - 50 + random.randint(-10, 10)
        table.alpha_composite(card_img, (x, y))

        x_center = (x + 35) / W
        y_center = (y + 50) / H
        w = 70 / W
        h = 100 / H
        labels.append(f"{card_to_class[card_name]} {x_center:.6f} {y_center:.6f} {w:.6f} {h:.6f}")

        used_card_tracker[card_name] += 1

    # Save image and label
    img_path = OUTPUT_IMAGES / f"poker_{image_id}.jpg"
    label_path = OUTPUT_LABELS / f"poker_{image_id}.txt"
    table.convert("RGB").save(img_path)
    with open(label_path, "w") as f:
        f.write("\n".join(labels))

    image_id += 1

    if image_id > MAX_TOTAL_IMAGES + 1000:  # Safety stop
        break

# Print summary
print("Final card usage:")
for card, count in sorted(used_card_tracker.items()):
    print(f"{card}: {count}")
