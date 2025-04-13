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
import os
from PIL import Image
import json

logging.basicConfig(filename="eye_strain.log", level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")

def notifyUser(title, message):
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
        self.savedData = {}
        self.initializeData()
        self.root = root
        self.root.title("Digital Eye Strain Helper")
        self.root.geometry("400x550")

        self.reminderRunning = tk.BooleanVar()
        self.reminderRunning.set(False)
        self.detectActivity = tk.BooleanVar()
        self.reminderTimeVar = tk.IntVar(value=20)
        self.reminderMessageText = tk.StringVar()
        self.reminderMessageText.set("20 minutes have passed. Look 20 feet away for 20 seconds!")
        self.playSound = tk.BooleanVar()
        self.uploadedSounds = [], []
        self.currentSound = tk.StringVar()
        if len(self.uploadedSounds[0]) > 0:
            self.currentSound.set(self.uploadedSounds[0][0])
        else:
            self.currentSound.set("No sound has been selected.")

        # UI Elements
        notebook = ttk.Notebook(root)
        self.home = tk.Frame(notebook)
        self.settings = tk.Frame(notebook)
        notebook.add(self.home, text="Home")
        notebook.add(self.settings, text="Settings")
        notebook.pack(expand=1, fill="both")
        # Home Page
        self.title = ttk.Label(self.home, text="Eye Care Reminder", font=("Arial", 14))
        self.title.pack(pady=10)

        self.reminderBtn = ttk.Button(self.home, text="Start Reminder", command=lambda: self.startReminder())
        self.reminderBtn.pack(pady=10)

        self.stopReminderBtn = ttk.Button(self.home, text="Stop Reminder", command=lambda: self.stopReminder())

        # Settings Page
        self.detectActivity.trace_add("write", lambda *args: Utilities.listenForActivity(self))
        self.detectActivityToggle = ttk.Checkbutton(self.settings, text="Automatically start reminder when activity is detected", variable=self.detectActivity, command=lambda: Utilities.detectActivity(self))
        self.detectActivityToggle.pack(pady=10)

        self.settingsTitle = ttk.Label(self.settings, text="Settings", font=("Arial", 14))
        self.settingsTitle.pack(pady=10)

        self.reminderTime = ttk.Label(self.settings, text="Reminder Wait Time", font=("Arial", 14))
        self.checkValidIntegerAndBelow60Minutes = self.root.register(Utilities.validateIsIntegerAndBelow60Minutes)
        self.reminderTime.pack(pady=10)

        self.reminderTimeEntry = ttk.Entry(self.settings, textvariable=self.reminderTimeVar, validate="key", validatecommand=(self.checkValidIntegerAndBelow60Minutes, "%P"))
        self.reminderTimeEntry.pack(pady=10)

        self.reminderMessageLabel = ttk.Label(self.settings, text="Reminder Message", font=("Arial", 14))
        self.reminderMessageLabel.pack(pady=10)

        self.reminderMessage = ttk.Label(self.settings, textvariable=self.reminderMessageText)
        self.reminderMessage.pack(pady=10)

        self.soundToggle = ttk.Checkbutton(self.settings, text="Play a Sound on Reminder", variable=self.playSound)
        self.soundToggle.pack(pady=10)

        self.currentSoundLabel = ttk.Label(self.settings, textvariable=self.currentSound)
        self.currentSoundLabel.pack(pady=10)

        self.deleteCurrentSound = ttk.Button(self.settings, text="Delete Current Sound", command=lambda: Utilities.deleteCurrentSound(self))
        self.deleteCurrentSound.pack(pady=10)

        self.uploadButton = ttk.Button(self.settings, text="Upload Sound", command=lambda: Utilities.uploadSound(self))
        self.uploadButton.pack(pady=10)

        self.uploadedSoundsMenu = ttk.Combobox(self.settings, values=self.uploadedSounds[0])
        if len(self.uploadedSounds[0]) == 0:
            self.uploadedSoundsMenu.state(['disabled'])
        else:
            self.uploadedSoundsMenu.state(['!disabled'])
        self.uploadedSoundsMenu.pack(pady=10)

        self.setSound = ttk.Button(self.settings, text="Set Sound", command=lambda: Utilities.setSound(self, self.uploadedSoundsMenu.get()))
        self.setSound.pack(pady=10)
    
        self.setupTrayIcon()

    def startReminder(self):
        self.reminderRunning.set(True)
        """Start the 20-20-20 rule reminder in a separate thread."""
        threading.Thread(target=self.reminderLoop, daemon=True).start()
        self.reminderBtn.pack_forget()
        self.stopReminderBtn.pack(pady=10)
        tk.messagebox.showinfo("Reminder Started", f"A notification will be sent every {self.reminderTimeVar.get()} minutes.")
        logging.info(f"Reminder started for {self.reminderTimeVar.get()} minutes.")

    def stopReminder(self):
        self.reminderRunning.set(False)
        self.stopReminderBtn.pack_forget()
        self.reminderBtn.pack(pady=10)
        tk.messagebox.showinfo("Reminder Stopped", "Reminder has been successfully stopped.")
        logging.info("Reminder stopped.")
    
    def reminderLoop(self):
        logging.info("Reminder loop started.")
        print("reminderLoop")
        loopTime = self.reminderTimeVar.get() * 60
        while self.reminderRunning.get() and loopTime > 0:
            print("loop started")
            logging.info("Current loop time: " + str(loopTime))
            time.sleep(30) 
            loopTime -= 30
            if loopTime <= 0:
                notifyUser(self.reminderMessageText.get())


    def setupTrayIcon(self):
        """Setup system tray icon."""
        currentDir = os.path.dirname(__file__)
        imagePath = os.path.join(currentDir, "assets", "eye.webp")
        iconImage = Image.open(imagePath)
        self.trayIcon = pystray.Icon("EyeCareApp", iconImage, "Eye Care Reminder",
                                      menu=pystray.Menu(
                                          pystray.MenuItem("Show", self.showWindow),
                                          pystray.MenuItem("Exit", self.exitApp)
                                      ))
        threading.Thread(target=self.trayIcon.run, daemon=True).start()

    def initializeData(self):
        currentDir = os.path.dirname(__file__)
        configPath = os.path.join(currentDir, "config", "config.json")
        try:
            self.savedData = Utilities.loadData(configPath, self)
        except Exception as e:
            print(f"Error loading data: {e}")
            self.savedData = self.defaultData()

            if e.errno == 2: #Error number for when the directory does not exist
                if os.path.exists(os.path.join(currentDir, "config")):
                    with open(configPath, 'w') as file:
                        json.dump(self.defaultData(), file)
                else:
                    os.makedirs(os.path.join(currentDir, "config"))

                Utilities.saveData(configPath, self)
            #elif e.errno == 26: #Error number for when the file does not exist

    def defaultData(self):
        return {
            "reminderTime": 20,
            "reminderMessage": "20 minutes have passed. Look 20 feet away for 20 seconds!",
            "playSound": False,
            "currentSound": "",
            "uploadedSounds":  [[], []],
            "detectActivity": False
        }

    def showWindow(self, icon, item):
        """Restore window from system tray."""
        self.root.deiconify()
        logging.info("Window restored from system tray.")

    def exitApp(self, icon=None, item=None):
        """Exit application."""
        self.trayIcon.stop()
        self.root.quit()
        logging.info("Application exited.")

if __name__ == "__main__":
    root = tk.Tk()
    app = EyeCareApp(root)
    root.mainloop()
