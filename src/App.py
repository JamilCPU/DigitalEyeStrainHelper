import tkinter as tk
from tkinter import messagebox
import time
import threading
import psutil
import logging
from plyer import notification
from PIL import Image, ImageTk
import pystray

logging.basicConfig(filename="eye_strain.log", level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")

def notify_user(title, message):
    """Send a system notification."""
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

        # UI Elements
        self.label = tk.Label(root, text="Eye Care Reminder", font=("Arial", 14))
        self.label.pack(pady=10)

        self.reminder_btn = tk.Button(root, text="Start 20-20-20 Reminder", command=self.start_reminder)
        self.reminder_btn.pack(pady=10)

        self.close_btn = tk.Button(root, text="Exit", command=self.exit_app)
        self.close_btn.pack(pady=10)

        self.setup_tray_icon()

    def start_reminder(self):
        """Start the 20-20-20 rule reminder in a separate thread."""
        threading.Thread(target=self.reminder_loop, daemon=True).start()
        messagebox.showinfo("Reminder Started", "A notification will be sent every 20 minutes.")
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
