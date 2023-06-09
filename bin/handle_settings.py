import os
import json

class SettingsHandlerClass:
    def __init__(self):
        self.settings_dir = os.path.join(os.environ['APPDATA'], 'SSII')
        if not os.path.exists(self.settings_dir):
            os.makedirs(self.settings_dir)
        self.settings_file = os.path.join(self.settings_dir, 'settings.json')
        self.settings = {}
        if os.path.exists(self.settings_file):
            with open(self.settings_file, 'r') as f:
                self.settings = json.load(f)

    def __dir__(self):
        return list(self.settings.keys())



    def SaveSetting(self, key, value):
        self.settings[key] = value
        with open(self.settings_file, 'w') as f:
            json.dump(self.settings, f)

    def LoadSetting(self, key):
        return self.settings.get(key)

    def HasDefaultOutputfolder(self):
        return 'DefaultOutputFolder' in self.settings

    def HasDefaultInputfolder(self):
        return 'DefaultInputfolder' in self.settings
    
    def SetDefaultSettings(self):
        defaultSettings = (
            ("DefaultOutputFolder", ""),
            ("DefaultInputfolder", "")
        )
        for setting in defaultSettings:
            self.SaveSetting(self, setting[0], setting[1])