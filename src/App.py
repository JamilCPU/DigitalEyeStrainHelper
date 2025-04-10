import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import time
import threading
import logging
from plyer import notification
from PIL import Image
import pystray
import Utilities

logging.basicConfig(filename="eye_strain.log", level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")

def notify_user(title, message):
    """Notification to the user"""
    notification.notify(
        title=title,
        message=message,
        app_name="Eye Care Reminder",
        timeout=10
    )
    logging.info(f"Notification sent: {title} - {message}")

class EyeCareApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Digital Eye Strain Helper")
        self.root.geometry("400x300")

        notebook = ttk.Notebook(root)
        home = tk.Frame(notebook)
        settings = tk.Frame(notebook)
        notebook.add(home, text="Home")
        notebook.add(settings, text="Settings")
        notebook.pack(expand=1, fill="both")
        # UI Elements
        self.title = ttk.Label(home, text="Eye Care Reminder", font=("Arial", 14))
        self.title.pack(pady=10)
        self.reminderBtn = ttk.Button(home, text="Start 20-20-20 Reminder", command=self.start_reminder)
        self.reminderBtn.pack(pady=10)

        self.settingsTitle = ttk.Label(settings, text="Settings", font=("Arial", 14))
        self.settingsTitle.pack(pady=10)

        self.reminderTime = ttk.Label(settings, text="Reminder Wait Time", font=("Arial", 14))
        self.checkValidIntegerAndBelow60Minutes = self.root.register(Utilities.validateIsIntegerAndBelow60Minutes)
        self.reminderTime.pack(pady=10)
        self.reminderTimeVar = tk.IntVar(value=20)
        self.reminderTimeEntry = ttk.Entry(settings, textvariable=self.reminderTimeVar, validate="key", validatecommand=(self.checkValidIntegerAndBelow60Minutes, "%P"))
        self.reminderTimeEntry.pack(pady=10)
        self.playSound = tk.BooleanVar()
        self.soundToggle = ttk.Checkbutton(settings, text="Play a Sound on Reminder", variable=self.playSound)
        self.soundToggle.pack(pady=10)

        self.setup_tray_icon()

    def start_reminder(self):
        """Start the 20-20-20 rule reminder in a separate thread."""
        threading.Thread(target=self.reminder_loop, daemon=True).start()
        tk.messagebox.showinfo("Reminder Started", "A notification will be sent every 20 minutes.")
        logging.info("20-20-20 reminder started.")

    def reminder_loop(self):
        while True:
            time.sleep(1200) 
            notify_user("20-20-20 Rule", "Look 20 feet away for 20 seconds!")

    def setup_tray_icon(self):
        """Setup system tray icon."""
        icon_image = Image.open("assets/eye.webp")
        self.tray_icon = pystray.Icon("EyeCareApp", icon_image, "Eye Care Reminder",
                                      menu=pystray.Menu(
                                          pystray.MenuItem("Show", self.show_window),
                                          pystray.MenuItem("Exit", self.exit_app)
                                      ))
        threading.Thread(target=self.tray_icon.run, daemon=True).start()

    def show_window(self, icon, item):
        """Restore window from system tray."""
        self.root.deiconify()
        logging.info("Window restored from system tray.")

    def exit_app(self, icon=None, item=None):
        """Exit application."""
        self.tray_icon.stop()
        self.root.quit()
        logging.info("Application exited.")

if __name__ == "__main__":
    root = tk.Tk()
    app = EyeCareApp(root)
    root.mainloop()
