import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import time
import threading
import logging
from plyer import notification
from PIL import Image
import pynput
import pystray
import ttkbootstrap as tb
from ttkbootstrap.constants import *
import Utilities
import os
from PIL import Image
import json
import pygame

logging.basicConfig(filename="eye_strain.log", level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")

class EyeCareApp:
    def __init__(self, root):
        self.savedData = {}
        self.initializeData()
        self.root = root
        self.root.title("Digital Eye Strain Helper")
        self.root.geometry("500x650")  # Made window slightly larger
        
        # Configure the style
        self.style = tb.Style()
        self.style.configure('TLabel', font=('Helvetica', 11))
        self.style.configure('Heading.TLabel', font=('Helvetica', 16, 'bold'))
        
        self.reminderRunning = tk.BooleanVar()
        self.reminderRunning.set(False)
        self.detectActivity = tk.BooleanVar()
        self.detectActivity.set(False)
        self.reminderTimeVar = tk.IntVar(value=self.savedData["reminderTime"])
        self.reminderMessageText = tk.StringVar()
        self.reminderMessageText.set(self.savedData["reminderMessage"])
        self.playSound = tk.BooleanVar()
        self.playSound.set(self.savedData["playSound"])
        self.uploadedSounds = self.savedData["uploadedSounds"]
        self.currentSound = tk.StringVar()
        if len(self.uploadedSounds[0]) > 0:
            self.currentSound.set(self.uploadedSounds[0][0])
        else:
            self.currentSound.set("No sound has been selected.")

        self.root.protocol("WM_DELETE_WINDOW", self.exitApp)

        # UI Elements with improved styling
        notebook = ttk.Notebook(self.root, style='primary.TNotebook')
        self.home = ttk.Frame(notebook, padding=20)
        self.settings = ttk.Frame(notebook, padding=20)
        notebook.add(self.home, text="Home")
        notebook.add(self.settings, text="Settings")
        notebook.pack(expand=1, fill="both", padx=10, pady=5)

        # Home Page
        self.title = ttk.Label(self.home, text="Eye Care Reminder", style='Heading.TLabel')
        self.title.pack(pady=20)

        self.reminderBtn = ttk.Button(self.home, text="Start Reminder", 
                                    style='success.TButton',
                                    command=lambda: self.startReminder())
        self.reminderBtn.pack(pady=20)

        self.stopReminderBtn = ttk.Button(self.home, text="Stop Reminder", 
                                        style='danger.TButton',
                                        command=lambda: self.stopReminder())

        # Settings Page
        self.detectActivity.trace_add("write", lambda *args: self.listenForActivity())
        self.detectActivityToggle = ttk.Checkbutton(self.settings, 
                                                   text="Automatically start reminder when activity is detected",
                                                   style='primary.TCheckbutton',
                                                   variable=self.detectActivity)
        self.detectActivityToggle.pack(pady=15)

        self.settingsTitle = ttk.Label(self.settings, text="Settings", style='Heading.TLabel')
        self.settingsTitle.pack(pady=15)

        # Reminder Time Frame
        time_frame = ttk.LabelFrame(self.settings, text="Reminder Interval", padding=10)
        time_frame.pack(fill='x', padx=5, pady=10)
        
        self.reminderTime = ttk.Label(time_frame, text="Minutes between reminders:")
        self.reminderTime.pack(pady=5)
        
        self.checkValidIntegerAndBelow60Minutes = self.root.register(Utilities.validateIsIntegerAndBelow60Minutes)
        self.reminderTimeEntry = ttk.Entry(time_frame, 
                                         textvariable=self.reminderTimeVar,
                                         validate="key",
                                         validatecommand=(self.checkValidIntegerAndBelow60Minutes, "%P"),
                                         width=10)
        self.reminderTimeEntry.pack(pady=5)

        # Message Frame
        message_frame = ttk.LabelFrame(self.settings, text="Notification Settings", padding=10)
        message_frame.pack(fill='x', padx=5, pady=10)
        
        self.reminderMessageLabel = ttk.Label(message_frame, text="Reminder Message:")
        self.reminderMessageLabel.pack(pady=5)

        self.reminderMessage = ttk.Entry(message_frame, 
                                       textvariable=self.reminderMessageText,
                                       width=50)
        self.reminderMessage.pack(pady=5)

        # Sound Frame
        sound_frame = ttk.LabelFrame(self.settings, text="Sound Settings", padding=10)
        sound_frame.pack(fill='x', padx=5, pady=10)
        
        self.soundToggle = ttk.Checkbutton(sound_frame,
                                          text="Play Sound on Reminder",
                                          style='primary.TCheckbutton',
                                          variable=self.playSound)
        self.soundToggle.pack(pady=5)

        self.currentSoundLabel = ttk.Label(sound_frame, textvariable=self.currentSound)
        self.currentSoundLabel.pack(pady=5)

        button_frame = ttk.Frame(sound_frame)
        button_frame.pack(pady=10)
        
        self.uploadButton = ttk.Button(button_frame,
                                     text="Upload Sound",
                                     style='info.TButton',
                                     command=lambda: Utilities.uploadSound(self))
        self.uploadButton.pack(side='left', padx=5)

        self.deleteCurrentSound = ttk.Button(button_frame,
                                           text="Delete Sound",
                                           style='danger.TButton',
                                           command=lambda: Utilities.deleteCurrentSound(self))
        self.deleteCurrentSound.pack(side='left', padx=5)

        self.uploadedSoundsMenu = ttk.Combobox(sound_frame,
                                              values=self.uploadedSounds[0],
                                              width=40)
        if len(self.uploadedSounds[0]) == 0:
            self.uploadedSoundsMenu.state(['disabled'])
        else:
            self.uploadedSoundsMenu.state(['!disabled'])
        self.uploadedSoundsMenu.pack(pady=5)

        self.setSound = ttk.Button(sound_frame,
                                  text="Set Sound",
                                  style='success.TButton',
                                  command=lambda: Utilities.setSound(self, self.uploadedSoundsMenu.get()))
        self.setSound.pack(pady=5)
    
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
        print("loop started")
        while self.reminderRunning.get():
            loopTime = self.reminderTimeVar.get() * 60
            while loopTime > 0 and self.reminderRunning.get():
                logging.info("Current loop time: " + str(loopTime))
                time.sleep(30) 
                loopTime -= 30
                if loopTime <= 0:
                    self.notifyUser(self.reminderMessageText.get())


    def listenForActivity(self):
        print("Listening for activity")
        print('reminderRunning', self.reminderRunning.get(), 'detectActivity', self.detectActivity.get())
        if not self.reminderRunning.get() and self.detectActivity.get() == 1:
            print("condition met")
            listenerThread = threading.Thread(target=self.startListener)
            listenerThread.daemon = True  # Allows the program to exit even if the thread is running
            listenerThread.start()
        else:
            print("Listener not started")

    def startListener(self):
        print("Starting listener")
        listener = pynput.mouse.Listener(on_move=self.onMove)
        listener.start()
        print("Listener started")


    def onMove(self, x, y):
        if not self.reminderRunning.get():
            print("Activity detected")
            self.reminderRunning.set(True)
            self.reminderBtn.pack_forget()
            self.stopReminderBtn.pack(pady=10)
            self.reminderLoop()
            return False
        return True

    def notifyUser(self, message):
        """Notification to the user"""
        notification.notify(
            title="Eye Care Reminder",
            message=message,
            app_name="Eye Care Reminder",
            timeout=10
        )
        if self.playSound.get() and self.currentSound.get() != "":
            print("playing sound function")
            pygame.mixer.init()
            uploadedSoundPath = ""
            for sound in self.uploadedSounds[0][0]:
                if sound == self.currentSound.get():
                    print(self.uploadedSounds[0][0].index(sound))
                    uploadedSoundPath = self.uploadedSounds[0][1][self.uploadedSounds[0][0].index(sound)]
            pygame.mixer.music.load(uploadedSoundPath)
            print(uploadedSoundPath)
            pygame.mixer.music.play()
        logging.info(f"Notification sent: {message}")

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
            "reminderMessage": f"{self.reminderTimeVar.get()} minutes have passed. Look 20 feet away for 20 seconds!",
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
        currentDir = os.path.dirname(__file__)
        configPath = os.path.join(currentDir, "config", "config.json")
        self.savedData["reminderTime"] = self.reminderTimeVar.get()
        self.savedData["reminderMessage"] = self.reminderMessageText.get()
        self.savedData["playSound"] = self.playSound.get()
        self.savedData["currentSound"] = self.currentSound.get()
        self.savedData["uploadedSounds"] = self.uploadedSounds
        self.savedData["detectActivity"] = self.detectActivity.get()
        print("closing app")
        print(self.savedData)
        with open(configPath, 'w') as file:
            json.dump(self.savedData, file)
        self.trayIcon.stop()
        self.root.quit()
        logging.info("Application exited.")

if __name__ == "__main__":
    root = tb.Window(themename="darkly")
    app = EyeCareApp(root)
    root.mainloop()
