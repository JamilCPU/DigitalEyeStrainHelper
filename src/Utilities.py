from tkinter import ttk, filedialog
import os
from tkinter import messagebox
import pynput

def validateIsIntegerAndBelow60Minutes(input):
    if input == "":
        return True
    if input.isdigit():
        if int(input) <= 60:
            return True
        else:
            return False
    else:
        return False

def uploadSound(self):
    filePath = filedialog.askopenfilename(filetypes=[("Sound Files", "*.wav *.mp3")])
    fileName = os.path.basename(filePath)
    if filePath and filePath not in self.uploadedSounds[1]:
        self.uploadedSounds[0].append(fileName)
        self.uploadedSounds[1].append(filePath)
        self.uploadedSoundsMenu['values'] = self.uploadedSounds[0]
        if '!disabled' not in self.uploadedSoundsMenu.state():
            self.uploadedSoundsMenu.state(['!disabled'])#enable the menu

        self.uploadedSoundsMenu.set(fileName)
        
def setSound(self, sound):
    self.currentSound.set(sound)

def deleteCurrentSound(self):
    try:
        soundToBeDeleted = self.currentSound.get();
        indexOfSoundToBeDeleted = self.uploadedSounds[0].index(soundToBeDeleted);
        self.uploadedSounds[0].pop(indexOfSoundToBeDeleted);
        self.uploadedSounds[1].pop(indexOfSoundToBeDeleted);

        self.uploadedSoundsMenu['values'] = self.uploadedSounds[0]
        self.currentSound.set("No sound has been selected.")
        if len(self.uploadedSoundsMenu['values']) == 0:
            self.uploadedSoundsMenu.set("")
            self.uploadedSoundsMenu.state(['disabled'])
        else:
            self.uploadedSoundsMenu.set(self.uploadedSounds[0][0])
    except:
        messagebox.showwarning("Warning", "Please select a sound to delete.", parent=self.settings)

def startReminderWhenActivityDetected(self):
    if self.activityDetected.get() == 1:
        self.startReminder()

def detectActivity(self):
    if self.detectActivity.get() == 1:
        messagebox.showinfo("Info", "Reminder will automatically start when activity is detected.", parent=self.settings)

def onMove(self, x, y):
    if not self.reminderRunning.get() and self.detectActivity.get() == 1:
        print("Activity detected")
        self.activityDetected.set(1)
        self.reminderLoop()
        return False

def listenForActivity(self):
    print("Listening for activity")
    if not self.reminderRunning.get() and self.detectActivity.get() == 1:
        listener = pynput.mouse.Listener(on_move=self.onMove)
        print("Listener started")
        listener.start()
