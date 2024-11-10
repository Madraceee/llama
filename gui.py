import asyncio
from datetime import datetime
import json
import tkinter as tk
from tkinter import messagebox, scrolledtext
from audio import AudioHandler
from threatHelper import init_threat_responder, threat_responder
from video import VideoHandler
from ollamaHelper import init_responder, responder, clear_messages

class EmergencyGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("911")
        self.root.geometry("600x400")
        
        # Initialize handlers
        self.audio_handler = AudioHandler()
        self.video_handler = VideoHandler()
        
        # Create frames
        self.root_frame = tk.Frame(root)
        self.audio_frame = tk.Frame(root)
        self.video_frame = tk.Frame(root)
        self.text_frame = tk.Frame(root)
        
        # Chat state and ticket tracking
        self.chat_started = False
        self.is_running = False
        self.user_id = ""
        self.ticket = {}
        
        # Set up frames
        self.setup_audio_frame()
        self.setup_video_frame()
        self.setup_text_frame()
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
        self.camera_label = tk.Label(self.video_frame)
        self.camera_label.pack(pady=10)
        
        button_frame = tk.Frame(self.video_frame)
        button_frame.pack(pady=10)
        
        self.video_start_button = tk.Button(button_frame, text="Start Call", 
                                          command=self.start_video)
        self.video_start_button.pack(side=tk.LEFT, padx=10)
        
        self.video_end_button = tk.Button(button_frame, text="End Call", 
                                        command=self.end_video)
        self.video_end_button.pack(side=tk.LEFT, padx=10)
        
    def setup_text_frame(self):
        # Chat display area
        self.chat_display = scrolledtext.ScrolledText(self.text_frame, wrap=tk.WORD, 
                                                    width=50, height=20)
        self.chat_display.pack(pady=10, padx=10, expand=True, fill="both")
        
        # Input area frame
        input_frame = tk.Frame(self.text_frame)
        input_frame.pack(fill="x", padx=10, pady=5)
        
        # Chat input field
        self.chat_input = tk.Entry(input_frame)
        self.chat_input.pack(side=tk.LEFT, fill="x", expand=True, padx=(0, 5))
        self.chat_input.bind("<Return>", self.send_message)
        
        # Send button
        self.send_button = tk.Button(input_frame, text="Send", 
                                   command=lambda: self.send_message(None))
        self.send_button.pack(side=tk.RIGHT)
        
        # Start/End chat buttons
        button_frame = tk.Frame(self.text_frame)
        button_frame.pack(pady=5)
        
        self.start_chat_button = tk.Button(button_frame, text="Start Chat", 
                                         command=self.start_chat)
        self.start_chat_button.pack(side=tk.LEFT, padx=5)
        
        self.end_chat_button = tk.Button(button_frame, text="End Chat", 
                                       command=self.end_chat)
        self.end_chat_button.pack(side=tk.LEFT, padx=5)
        
        # Back button
        tk.Button(self.text_frame, text="Back to Menu", 
                 command=self.back_to_menu).pack(pady=5)
        
        # Initially disable chat controls
        self.toggle_chat_controls(False)
        
    def setup_main_menu(self):
        tk.Button(self.root_frame, text="Audio Call", 
                 command=lambda: self.go_to_page(self.audio_frame)).pack(pady=10)
        
        tk.Button(self.root_frame, text="Video Call", 
                 command=lambda: self.go_to_page(self.video_frame)).pack(pady=10)
        
        tk.Button(self.root_frame, text="Text Chat", 
                 command=lambda: self.go_to_page(self.text_frame)).pack(pady=10)
        
        tk.Button(self.root_frame, text="Exit", 
                 command=self.exit_action).pack(pady=10)
        
    def go_to_page(self, page):
        for frame in (self.root_frame, self.audio_frame, self.video_frame, self.text_frame):
            frame.pack_forget()
        page.pack(fill="both", expand=True)
        
    def toggle_chat_controls(self, enabled):
        """Enable or disable chat controls"""
        state = 'normal' if enabled else 'disabled'
        self.chat_input.config(state=state)
        self.send_button.config(state=state)
        self.start_chat_button.config(state='disabled' if enabled else 'normal')
        self.end_chat_button.config(state='normal' if enabled else 'disabled')
        
    def start_chat(self):
        """Initialize and start the chat session with threat monitoring"""
        self.chat_started = True
        self.is_running = True
        self.user_id = datetime.now().strftime("%Y%m%d%H%M%S%f")[:17]
        self.ticket[self.user_id] = []
        
        self.toggle_chat_controls(True)
        self.chat_display.delete(1.0, tk.END)
        
        # Initialize both responder and threat monitor
        clear_messages()
        init_threat_responder()
        response = init_responder(False)
        
        if response[0]:
            self.display_message("Assistant", response[1])
            
    def end_chat(self):
        """End the chat session and save ticket if needed"""
        if not self.chat_started:
            return
            
        self.chat_started = False
        self.is_running = False
        self.toggle_chat_controls(False)
        self.display_message("System", "\nChat session ended\n")
        
        # Save ticket if there were any threats detected
        if self.ticket[self.user_id]:
            with open("ticket_log.json", "w+") as f:
                json.dump(self.ticket, f, indent=2)
        
        self.ticket = {}
        
    def send_message(self, event):
        """Handle sending messages with threat monitoring"""
        if not self.chat_started or not self.is_running:
            return
            
        message = self.chat_input.get().strip()
        if not message:
            return
            
        # Display user message
        self.display_message("You", message)
        self.chat_input.delete(0, tk.END)
        
        # Check for threats
        continue_chat = asyncio.run(self.process_threat(message))
        
        if not continue_chat:
            self.display_message("System", "\nEmergency detected. Chat ended for safety.\n")
            self.end_chat()
            return
            
        # Get and display assistant response
        response = responder(message, False)
        
        if not response[0]:  # Chat ended by assistant
            self.display_message("Assistant", response[1])
            self.end_chat()
        else:
            self.display_message("Assistant", response[1])
            
    def display_message(self, sender, message):
        """Display a message in the chat window"""
        self.chat_display.insert(tk.END, f"\n{sender}: {message}\n")
        self.chat_display.see(tk.END)
        
        
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
        
    def exit_action(self):
        self.audio_handler.stop_audio()
        self.video_handler.stop_video()
        self.root.quit()

    def back_to_menu(self):
        """Handle returning to main menu"""
        if self.chat_started:
            self.end_chat()
        self.go_to_page(self.root_frame)

    

    
        
    async def process_threat(self, message):
        """Process message for threats and update ticket"""
        threat = await threat_responder(message)
        
        if threat[0] == True:  # Threat detected
            self.ticket[self.user_id].append({
                "type": "chat_threat",
                "timestamp": str(datetime.now()),
                "message": message,
                "details": threat[1]
            })
            # print("******** CHAT TICKET:", self.ticket[self.user_id], "********")
            
            # Save ticket whenever a threat is detected
            with open("ticket_log.json", "w+") as f:
                json.dump(self.ticket, f, indent=2)
                
        return threat[0]  # Return whether to continue the chat
        
    

if __name__ == "__main__":
    root = tk.Tk()
    app = EmergencyGUI(root)
    root.mainloop()