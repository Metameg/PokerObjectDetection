import shutil
import random
from PIL import Image
from pathlib import Path
from collections import defaultdict

# Paths
CARD_DIR = Path("dataset\\assets\\cards\\labels_no_rotate_no_bg")
TABLE_PATH = Path("dataset\\assets\\table.png")
OUTPUT_IMAGES = Path("dataset\\images")
OUTPUT_LABELS = Path("dataset\\labels")

OUTPUT_IMAGES.mkdir(parents=True, exist_ok=True)
OUTPUT_LABELS.mkdir(parents=True, exist_ok=True)

# Load card names
card_names = sorted([f.stem for f in CARD_DIR.glob("*/")])
card_to_class = {name: idx for idx, name in enumerate(card_names)}
used_card_count = defaultdict(int)

# Settings
TARGET_USES_PER_CARD = 200

# Function to choose cards that need more appearances
def sample_balanced_cards(n=5):
    # Sort cards by how underused they are (lowest usage first)
    sorted_cards = sorted(card_names, key=lambda c: used_card_count[c])
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

def split_data():
    from pathlib import Path
    from sklearn.model_selection import train_test_split

    # --- CONFIG ---
    DATASET_DIR = Path("dataset")
    IMAGES_DIR = DATASET_DIR / "images"
    LABELS_DIR = DATASET_DIR / "labels"
    SPLITS = {"train": 0.8, "val": 0.1, "test": 0.1} 

    # --- Create output folders ---
    for split in SPLITS.keys():
        (DATASET_DIR / f"images/{split}").mkdir(parents=True, exist_ok=True)
        (DATASET_DIR / f"labels/{split}").mkdir(parents=True, exist_ok=True)

    # --- Collect image files ---
    image_files = IMAGES_DIR.glob("*.jpg")
    image_files = list(image_files)

    # --- Split by sampling images: random with stratified option (SEEDED)---
    train_imgs, test_imgs = train_test_split(image_files, test_size=SPLITS["test"], random_state=42)
    val_imgs, test_imgs = train_test_split(test_imgs, test_size=0.5, random_state=42)  # 50% of test set for validation

    # --- Function to copy images and labels ---
    def copy_files(img_list, split_name):
        for img_path in img_list:
            label_path = LABELS_DIR / (img_path.stem + ".txt")
            shutil.copy(img_path, DATASET_DIR / f"images/{split_name}/{img_path.name}")
            shutil.copy(label_path, DATASET_DIR / f"labels/{split_name}/{label_path.name}")

    # --- Perform the actual file copying ---
    copy_files(train_imgs, "train")
    copy_files(val_imgs, "val")
    copy_files(test_imgs, "test")

# Main image generation loop
image_id = 0
while any(used_card_count[c] < TARGET_USES_PER_CARD for c in card_names):
    table = Image.open(TABLE_PATH).convert("RGBA")
    # There can be 2, 5, 6, or 7 visible cards in a game state 
    CARDS_PER_IMAGE = random.choice([2, 5, 6, 7])
    MAX_TOTAL_IMAGES = (TARGET_USES_PER_CARD * len(card_names)) // CARDS_PER_IMAGE
    W, H = table.size
    CARD_W, CARD_H = 100, 130
    BOARD_START = 80
    BOARD_HEIGHT = 100
    BOARD_GAP = CARD_W + 12
    HOLE_CARD_START = W // 2 - 50
    HOLE_CARD_HEIGHT = H - 150
    HOLE_CARD_GAP = 75
    labels = []
    selected_cards = sample_balanced_cards(CARDS_PER_IMAGE)


    for i, card_name in enumerate(selected_cards):
        # Get a random augmented image for the card
        card_img_path = get_random_augmented_card_image(card_name)
        card_img = Image.open(card_img_path).convert("RGBA")
        card_img = card_img.resize((CARD_W, CARD_H))

        # Place hole cards first
        if i <= 1:
            x = HOLE_CARD_START + i * HOLE_CARD_GAP + random.randint(-5, 5)
            y = HOLE_CARD_HEIGHT + random.randint(-10, 10)

        else:
            x = BOARD_START + (i-2) * BOARD_GAP + random.randint(-5, 5)
            y = H // 2 - BOARD_HEIGHT + random.randint(-10, 10)

        # Draw card images over table    
        table.alpha_composite(card_img, (x, y))

        x_center = (x + (CARD_W / 2)) / W
        y_center = (y + (CARD_H / 2)) / H
        w = CARD_W / W
        h = CARD_H / H
        labels.append(f"{card_to_class[card_name]} {x_center:.6f} {y_center:.6f} {w:.6f} {h:.6f}")

        used_card_count[card_name] += 1

    # Save image and label
    img_path = OUTPUT_IMAGES / f"poker_{image_id}.jpg"
    label_path = OUTPUT_LABELS / f"poker_{image_id}.txt"
    table.convert("RGB").save(img_path) # Convert to RGB so png can be saved as jpg (important for YOLO)
    with open(label_path, "w") as f:
        f.write("\n".join(labels))

    image_id += 1

    if image_id > MAX_TOTAL_IMAGES + 1000:  # Safety stop
        break

# Print summary
print("Final card usage:")
for card, count in sorted(used_card_count.items()):
    print(f"{card}: {count}")

split_data()