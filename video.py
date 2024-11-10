import cv2
import time
import os
import shutil

from ollamaHelper import init_responder, image_responder, clear_messages
from PIL import Image, ImageTk

def video(frame_label = None):
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
    frame_interval = 0.333 # in seconds

    # Capture and save frames every 1 second
    last_saved_time = time.time()  # To track time since last save
    frame_count = 0  # To count the number of frames captured

    # Clear ollama context
    clear_messages()
    # Start ollama
    init_responder()
    def stop_video():
        cap.release()
        cv2.destroyAllWindows()
    def start_video():
        try:
            last_saved_time = time.time()
            frame_count = 0
            frame_interval = 0.333
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

                if frame_label is not None:
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    img = Image.fromarray(frame)
                    imgtk = ImageTk.PhotoImage(image=img)           
                    frame_label.imgtk = imgtk  # Keep a reference to avoid garbage collection
                    frame_label.configure(image=imgtk)
                    frame_label.update()

                if frame_count % 3 == 0: 
                    image_list = []
                    image = os.path.join(output_dir,f"frame_{frame_count-1}.jpg")
                    image = "./"+image
                    image_list.append(image)

                    print("Sending image_list", image_list)
                    if frame_count % 10:
                        continue
                        

                    #response = image_responder(image_list)
                    # if response[0] is False:
                    #     break
        finally:
           cap.release()
           cv2.destroyAllWindows()

    return [start_video,stop_video]
