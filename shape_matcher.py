import cv2
import numpy as np

def find_shape_coordinates(template_path, screenshot):
    # Read the template image
    template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
    
    # Convert screenshot to grayscale if needed
    if len(screenshot.shape) == 3:
        screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2GRAY)
    
    # Get template dimensions
    w, h = template.shape[::-1]
    
    # Apply template matching
    result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
    
    # Get the best match location
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    
    # Calculate center point
    top_left = max_loc
    center = (top_left[0] + w//2, top_left[1] + h//2)
    
    return center

if __name__ == "__main__":
    template_path = "data/crop_right.png"
    screenshot_path = "R5CRC36A8TT/1.png"
    
    center = find_shape_coordinates(template_path, screenshot_path)
    print(f"Center point: {center}") 