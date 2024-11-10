import cv2
import time
import os
import shutil

from ollamaHelper import init_responder, image_responder, clear_messages

# Directory to save images
output_dir = "captured_frames"
if os.path.exists(output_dir) and os.path.isdir(output_dir):
    # Delete the folder and its contents
    shutil.rmtree(output_dir)
    print(f"Folder '{output_dir}' has been deleted.")
os.makedirs(output_dir, exist_ok=True)

# Open the camera
cap = cv2.VideoCapture(0)  # 0 is usually the default camera
if not cap.isOpened():
    print("Cannot open camera")
    exit(1)

# Set the frame rate capture interval
frame_interval = 1  # in seconds

# Clear ollama context
clear_messages()

# Capture and save frames every 1 second
try:
    last_saved_time = time.time()  # To track time since last save
    frame_count = 0  # To count the number of frames captured

    # Start ollama
    init_responder()
    while True:
        # Read the frame from the camera
        ret, frame = cap.read()
        
        if not ret:
            print("Failed to grab frame.")
            break
        
        # Check if 1 second has passed since the last save
        current_time = time.time()
        if current_time - last_saved_time >= frame_interval:
            # Save the current frame as an image
            frame_filename = os.path.join(output_dir, f"frame_{frame_count}.jpg")
            cv2.imwrite(frame_filename, frame)
            frame_count += 1
            last_saved_time = current_time  # Reset last save time

        if frame_count % 3 == 0: 
            image_list = []
            image = os.path.join(output_dir,f"frame_{frame_count-1}.jpg")
            image = "./"+image
            image_list.append(image)

            print("Sending image_list", image_list)
            response = image_responder(image_list)
            if "END" in reponse:
                break


        # Break loop on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    # Release the capture and close any OpenCV windows
    cap.release()
    cv2.destroyAllWindows()

