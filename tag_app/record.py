from kivy.logger import Logger

import subprocess
import time
import os
import json

from kivy.uix.popup import Popup
from kivy.uix.button import Button

# TODO: get path from static method from main
def get_record_device():
    with open("confs/mahle.json") as config_file:
        config = json.loads(config_file.read())
        return config.get("record_device", "")


class Record:
    def __init__(self):
        self.recording = False

    def start(self, name, duration=None):

        record_script = "arecord -r 22050 -c 3 -f S16_LE --file-type wav -B 1000000 -D {} {}".format(get_record_device(), name)
        self.process = subprocess.Popen(record_script, shell=True)

        time.sleep(1)
        if os.path.exists(name):
            Logger.info("Recording successfully started")
            self.recording = True

            if duration is not None:
                time.sleep(duration)
                if self.recording:
                    Logger.warn("Time limit reached, stopping record")
                    self.stop()
        else:
            Logger.error("Recording failed to start - sound card probably not found")
            self.recording = False

            btn_text = 'Failed to start recording\nPlease go back and check if sound device is plugged-in correctly.'
            # create content and add to the popup
            content = Button(text=btn_text)
            popup = Popup(title='Recording error',
                          content=content,
                          size_hint=(None, None),
                          size=(600, 400),
                          auto_dismiss=False)

            # bind the on_press event of the button to the dismiss function
            content.bind(on_press=popup.dismiss)

            # open the popup
            popup.open()


    def stop(self):
        #self.process.terminate()
        # TODO: should think of something better but previous approach didnt work well
        os.system('pkill -TERM arecord')
        Logger.info("Recording stopped")
        self.recording = False
