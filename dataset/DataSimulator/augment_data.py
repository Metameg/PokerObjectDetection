import os
import cv2
from PIL import Image
import albumentations as A
import numpy as np
from tqdm import tqdm


def _create_card_directories(base_path):
    print(base_path)
    # Define the ranks and suits
    ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    suits = ['h', 'd', 'c', 's']  # Hearts, Diamonds, Clubs, Spades

    # Create the base directory if it doesn't exist
    if not os.path.exists(base_path):
        os.makedirs(base_path)

    # Loop through each rank and suit to create directories
    for rank in ranks:
        for suit in suits:
            dir_name = f"{rank}{suit}"
            dir_path = os.path.join(base_path, dir_name)

            # Create the directory
            os.makedirs(dir_path, exist_ok=True)

    print(f"Directories for all 52 cards have been created in {base_path}")

def remove_backgrounds(input_dir):
    for sub_dir in os.listdir(input_dir):
        sub_dir_path = os.path.join(input_dir, sub_dir)

        for filename in tqdm(os.listdir(sub_dir_path), desc=f"Removing bg's from {sub_dir}"):
            if filename.endswith((".png", ".jpg", ".jpeg")):
                img_path = os.path.join(sub_dir_path, filename)
                img = Image.open(img_path).convert("RGBA")
                datas = img.getdata()

                new_data = []
                for item in datas:
                    # Change white (or near-white) to transparent
                    if item[0] < 10 and item[1] < 10 and item[2] < 10:
                        new_data.append((255, 255, 255, 0))
                    else:
                        new_data.append(item)

                img.putdata(new_data)
                img.save(os.path.join(sub_dir_path, filename.replace('.jpg', '.png')))


# Path to the main directory
def augment_labels(input_dir, output_dir):

    _create_card_directories(output_dir)

    transform = A.Compose([
        A.HorizontalFlip(p=0.5),
        A.VerticalFlip(p=0.2),
        # A.Rotate(limit=15, p=0.5),
        A.RandomBrightnessContrast(p=0.3),
        A.GaussNoise(p=0.2),
        A.RandomScale(scale_limit=0.2, p=0.4),
    ])

    # Augment images in each subdirectory
    for sub_dir in os.listdir(input_dir):
        sub_dir_path = os.path.join(input_dir, sub_dir)
        
        for img_file in tqdm(os.listdir(sub_dir_path), desc=f"Processing {sub_dir}"):
            img_path = os.path.join(sub_dir_path, img_file)
            image = cv2.imread(img_path)
            
            if image is None:
                continue  # Skip corrupted or non-image files
            
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Generate 10 augmented versions per image
            for i in range(15):
                augmented = transform(image=image)['image']
                aug_filename = f"{os.path.splitext(img_file)[0]}_aug{i}.png"
                aug_path = os.path.join(output_dir, sub_dir, aug_filename)
                cv2.imwrite(aug_path, cv2.cvtColor(augmented, cv2.COLOR_RGB2BGR))

input_dir = "dataset\\assets\cards\labels_default"
augmented_dir = "dataset\\assets\cards\labels_augmented2"
augment_labels(input_dir, augmented_dir)
# remove_backgrounds(augmented_dir)