import cv2
import os
from inference_sdk import InferenceHTTPClient
from twilio.rest import Client

# Twilio Credentials (Use with caution)
TWILIO_ACCOUNT_SID = "AC77690e404f748bbbb842578f5d470ae0"
TWILIO_AUTH_TOKEN = "085360301022905e6441ce9bc380cc20"
TWILIO_PHONE_NUMBER = "+18604219862"
USER_PHONE_NUMBER = "+919005447398"

# Roboflow API Key
ROBOFLOW_API_KEY = "BL6mSzeUhN0JiMuSWVS8"

# Initialize Twilio client
twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Initialize the Roboflow client
CLIENT = InferenceHTTPClient(
    api_url="https://detect.roboflow.com",
    api_key=ROBOFLOW_API_KEY
)

# Define the model ID
MODEL_ID = "landmine-detection-bsbs6/1"

# Input image path
image_path = "test_images/DM-11_18_png.rf.9f67b05fb5cf200be4fa4c57f9efaa2e.jpg"

if not os.path.exists(image_path):
    print("Error: Image file not found.")
    exit()

# Read the image
image = cv2.imread(image_path)
if image is None:
    print("Error: Could not read image file.")
    exit()

# Perform inference
result = CLIENT.infer(image_path, model_id=MODEL_ID)

detected = False  # Flag for detection
if "predictions" in result:
    for detection in result["predictions"]:
        x, y, width, height = int(detection["x"]), int(detection["y"]), int(detection["width"]), int(detection["height"])
        confidence = detection["confidence"]
        class_name = detection["class"]

        # Define bounding box coordinates
        x1, y1 = x - width // 2, y - height // 2
        x2, y2 = x + width // 2, y + height // 2

        # Draw bounding box
        cv2.rectangle(image, (x1, y1), (x2, y2), (0, 0, 255), 2)

        # Put label
        label = f"{class_name}: {confidence:.2f}"
        cv2.putText(image, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

        detected = True

# Send SMS Alert if detection occurs
if detected:
    message = twilio_client.messages.create(
        body="🚨 Alert! Landmine detected in the image. Stay safe!",
        from_=TWILIO_PHONE_NUMBER,
        to=USER_PHONE_NUMBER
    )
    print(f"SMS sent: {message.sid}")

# Display the image with detections
cv2.imshow("Landmine Detection", image)
cv2.waitKey(0)
cv2.destroyAllWindows()
