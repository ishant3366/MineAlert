import cv2
import os
from inference_sdk import InferenceHTTPClient

# Initialize the client
CLIENT = InferenceHTTPClient(
    api_url="https://detect.roboflow.com",
    api_key="BL6mSzeUhN0JiMuSWVS8"
)

# Load the image
image_path = r"test_images\DM-11_15_png.rf.4e47141445c6b5306d57014da0b325b1_marked.jpg"
image = cv2.imread(image_path)

# Perform inference
result = CLIENT.infer(image_path, model_id="landmine-detection-bsbs6/1")

# Ensure output directory exists
output_dir = "Output"
os.makedirs(output_dir, exist_ok=True)

# Get the filename without extension
base_name = os.path.basename(image_path)  # Extract only filename
name, ext = os.path.splitext(base_name)
output_path = os.path.join(output_dir, f"{name}_marked{ext}")

# Draw bounding boxes if detections exist
if "predictions" in result:
    for detection in result["predictions"]:
        x, y, width, height = int(detection["x"]), int(detection["y"]), int(detection["width"]), int(detection["height"])
        confidence = detection["confidence"]
        class_name = detection["class"]
        
        # Define bounding box coordinates
        x1, y1 = x - width // 2, y - height // 2
        x2, y2 = x + width // 2, y + height // 2
        
        # Draw bounding box
        cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
        
        # Put label
        label = f"{class_name}: {confidence:.2f}"
        cv2.putText(image, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # Save the output image in the Output folder
    cv2.imwrite(output_path, image)
    print(f"Saved detected image as {output_path}")

else:
    print("No objects detected.")
