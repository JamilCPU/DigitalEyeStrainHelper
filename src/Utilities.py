import threading
from tkinter import ttk, filedialog
import os
from tkinter import messagebox
import pynput
import json

def validateIsIntegerAndBelow60Minutes(input):#logic for validating the reminder time
    if input == "":
        return True
    if input.isdigit():
        if int(input) <= 60:
            return True
        else:
            return False
    else:
        return False

def uploadSound(self):#logic for uploading a sound
    filePath = filedialog.askopenfilename(filetypes=[("Sound Files", "*.wav *.mp3")])#only certain file types can be uploaded
    fileName = os.path.basename(filePath)
    if filePath and filePath not in self.uploadedSounds[1]:#placed into uploadedsounds list
        self.uploadedSounds[0].append(fileName)
        self.uploadedSounds[1].append(filePath)
        self.uploadedSoundsMenu['values'] = self.uploadedSounds[0]
        if '!disabled' not in self.uploadedSoundsMenu.state():
            self.uploadedSoundsMenu.state(['!disabled'])#enable the menu    
  
        self.uploadedSoundsMenu.set(fileName)
        
def setSound(self, sound):
    self.currentSound.set(sound)
    self.soundToggle.state(['!disabled'])

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
            self.soundToggle.state(['disabled'])
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

def saveData(filePath, self):
    with open(filePath, 'w') as file:
        json.dump(self.savedData, file)

def loadData(filePath, self):
    with open(filePath, 'r') as file:
        loadedData =  json.load(file)
        if validateData(loadedData):
            return loadedData
        else:
            self.initializeData()


def validateData(data):#basic validation to ensure data integrity
        expectedData = {
            "reminderTime": int,
            "reminderMessage": str,
            "playSound": bool,
            "currentSound": str,
            "uploadedSounds": list,
            "detectActivity": bool
        }
        try:
            for key, expectedDataType in expectedData.items():
                if key not in data:
                    return False
                if not isinstance(data[key], expectedDataType):
                    return False
            if not (0 < data['reminderTime'] <= 60):
                return False

        except:
            messagebox.showerror("Error", "Data in config file is invalid. Resetting to default values.")
            return False
        return True

  
