import tkinter as tk
from tkinter import messagebox

from audio import audio

# Function for Button 1
def button1_action():
    audio()

# Function for Button 2
def button2_action():
    messagebox.showinfo("Button 2", "Button 2 was clicked!")

# Function for Button 3
def button3_action():
    messagebox.showinfo("Button 3", "Button 3 was clicked!")

# Create the main window
root = tk.Tk()
root.title("911")
root.geometry("300x200")  # Set window size

# Create Buttons
button1 = tk.Button(root, text="Audio Call", command=button1_action)
button1.pack(pady=10)

button2 = tk.Button(root, text="Video Call", command=button2_action)
button2.pack(pady=10)

button3 = tk.Button(root, text="Text", command=button3_action)
button3.pack(pady=10)

# Run the GUI loop
root.mainloop()
