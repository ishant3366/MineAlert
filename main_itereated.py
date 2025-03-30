import cv2
import os
from inference_sdk import InferenceHTTPClient

# Initialize the client
CLIENT = InferenceHTTPClient(
    api_url="https://detect.roboflow.com",
    api_key="BL6mSzeUhN0JiMuSWVS8"
)

# Input and output directories
input_dir = "test_images"
output_dir = "Output"

# Ensure output directory exists
os.makedirs(output_dir, exist_ok=True)

# Process all images in the test_images folder
for filename in os.listdir(input_dir):
    if filename.lower().endswith((".jpg", ".jpeg", ".png")):  # Filter image files
        image_path = os.path.join(input_dir, filename)
        image = cv2.imread(image_path)

        # Perform inference
        result = CLIENT.infer(image_path, model_id="landmine-detection-bsbs6/1")

        # Generate output file path
        name, ext = os.path.splitext(filename)
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

            # Save the marked image in Output folder
            cv2.imwrite(output_path, image)
            print(f"Saved: {output_path}")
        else:
            print(f"No objects detected in {filename}")

print("Processing complete for all images!")
