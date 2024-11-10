import tkinter as tk
from tkinter import messagebox
from audio import AudioHandler
from video import VideoHandler

class EmergencyGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("911")
        self.root.geometry("600x400")  # Larger window to better show video
        
        # Initialize handlers
        self.audio_handler = AudioHandler()
        self.video_handler = VideoHandler()
        
        # Create frames
        self.root_frame = tk.Frame(root)
        self.audio_frame = tk.Frame(root)
        self.video_frame = tk.Frame(root)
        
        # Set up audio frame
        self.setup_audio_frame()
        
        # Set up video frame
        self.setup_video_frame()
        
        # Set up main menu
        self.setup_main_menu()
        
        # Show main menu initially
        self.go_to_page(self.root_frame)
        
    def setup_audio_frame(self):
        self.audio_start_button = tk.Button(self.audio_frame, text="Start Call", 
                                          command=self.start_audio)
        self.audio_start_button.pack(pady=20)
        self.audio_end_button = tk.Button(self.audio_frame, text="End Call", 
                                        command=self.end_audio)
        self.audio_end_button.pack(pady=20)
        
    def setup_video_frame(self):
        # Add camera display
        self.camera_label = tk.Label(self.video_frame)
        self.camera_label.pack(pady=10)
        
        # Add control buttons
        button_frame = tk.Frame(self.video_frame)
        button_frame.pack(pady=10)
        
        self.video_start_button = tk.Button(button_frame, text="Start Call", 
                                          command=self.start_video)
        self.video_start_button.pack(side=tk.LEFT, padx=10)
        
        self.video_end_button = tk.Button(button_frame, text="End Call", 
                                        command=self.end_video)
        self.video_end_button.pack(side=tk.LEFT, padx=10)
        
    def setup_main_menu(self):
        tk.Button(self.root_frame, text="Audio Call", 
                 command=lambda: self.go_to_page(self.audio_frame)).pack(pady=10)
        
        tk.Button(self.root_frame, text="Video Call", 
                 command=lambda: self.go_to_page(self.video_frame)).pack(pady=10)
        
        tk.Button(self.root_frame, text="Text", 
                 command=self.button3_action).pack(pady=10)
        
        tk.Button(self.root_frame, text="Exit", 
                 command=self.exit_action).pack(pady=10)
        
    def go_to_page(self, page):
        for frame in (self.root_frame, self.audio_frame, self.video_frame):
            frame.pack_forget()
        page.pack(fill="both", expand=True)
        
    def start_audio(self):
        self.audio_handler.start_audio()
        self.audio_start_button.config(state='disabled')
        
    def end_audio(self):
        self.audio_handler.stop_audio()
        self.audio_start_button.config(state='normal')
        self.go_to_page(self.root_frame)
        
    def start_video(self):
        if self.video_handler.start_video(self.camera_label):
            self.video_start_button.config(state='disabled')
        
    def end_video(self):
        self.video_handler.stop_video()
        self.video_start_button.config(state='normal')
        self.go_to_page(self.root_frame)
        
    def button3_action(self):
        messagebox.showinfo("Button 3", "Button 3 was clicked!")
        
    def exit_action(self):
        self.audio_handler.stop_audio()
        self.video_handler.stop_video()
        self.root.quit()

if __name__ == "__main__":
    root = tk.Tk()
    app = EmergencyGUI(root)
    root.mainloop()