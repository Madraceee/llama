import tkinter as tk
from tkinter import messagebox

from audio import audio
from video import video

def go_to_main():
    for frame in (root_frame, audio_frame, video_frame):
        frame.pack_forget()

    root_frame.pack(fill="both", expand=True)


stop_video = None
def stop_video_feed():
    stop_video()

def go_to_main_video():
    #stop_video()
    go_to_main()
    stop_video_feed()

def go_to_page(page):
    for frame in (root_frame, audio_frame, video_frame):
        frame.pack_forget()
    # Show the selected frame
    page.pack(fill="both", expand=True)

# Function for Button 1
def button1_action():
    go_to_page(audio_frame)
    # audio()

# Function for Button 2
def button2_action():
    callbacks = video(camera_label)
    go_to_page(video_frame)

    callbacks[0]()
    stop_video = callbacks[1]

# Function for Button 3
def button3_action():
    messagebox.showinfo("Button 3", "Button 3 was clicked!")


# Function for Exit button
def exit_action():
    exit(0)


# Create the main window
root = tk.Tk()
root.title("911")
root.geometry("300x200")  # Set window size

root_frame = tk.Frame(root)

# Audio call page
audio_frame = tk.Frame(root)
audio_cancel_button = tk.Button(audio_frame, text="End Call", command=go_to_main)
audio_cancel_button.pack(pady=20)

video_frame = tk.Frame(root)
video_cancel_button = tk.Button(video_frame, text="End Call", command=go_to_main_video)
video_cancel_button.pack(pady=20)
camera_label = tk.Label(video_frame)
camera_label.pack(pady=20)

# Create Buttons
button1 = tk.Button(root_frame, text="Audio Call", command=button1_action)
button1.pack(pady=10)

button2 = tk.Button(root_frame, text="Video Call", command=button2_action)
button2.pack(pady=10)

button3 = tk.Button(root_frame, text="Text", command=button3_action)
button3.pack(pady=10)

button3 = tk.Button(root_frame, text="Exit", command=exit_action)
button3.pack(pady=10)


go_to_page(root_frame)
# Run the GUI loop
root.mainloop()
