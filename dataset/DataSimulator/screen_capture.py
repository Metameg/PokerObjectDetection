import time
from PIL import ImageGrab

def capture_area(x, y, width, height, save_path):
    """
    Captures a specific area of the screen and saves it to a file.
    
    Parameters:
    - x, y: Top-left corner of the area
    - width, height: Dimensions of the area
    - save_path: Path to save the captured image
    """
    # Define the region (left, top, right, bottom)
    region = (x, y, x + width, y + height)
    screenshot = ImageGrab.grab(bbox=region)  # Capture the area
    screenshot.save(save_path)  # Save the screenshot to the specified path
    print(f"Screenshot saved to {save_path}")

# Coordinates and dimensions of the area to capture
x, y = 590, 266  # Top-left corner
width, height = 730, 580  # Width and height of the area

x_flop1, y_flop1 = 667, 430
width_flop1, height_flop1 = 108, 70
# Save a snapshot every 5 seconds
try:
    for i in range(20):  # Take 10 snapshots as an example
        timestamp = int(time.time())  # Generate a unique name using a timestamp
        save_path = f"dataset\\assets\\table.png"
        capture_area(x, y, width, height, save_path)
        time.sleep(5)  # Wait for 5 seconds
except KeyboardInterrupt:
    print("Stopped capturing.")

