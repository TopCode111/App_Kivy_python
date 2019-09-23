from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, NumericProperty, BooleanProperty
from kivy.uix.screenmanager import Screen
from kivy.clock import Clock

from kivy.logger import Logger

import datetime
import threading
import socket
import json
import os


from record import Record
from main import TagApp

RECORDING_DURATION = 360

# TODO: get path from static method from main
def get_base_records_path():
    with open("confs/mahle.json") as config_file:
        config = json.loads(config_file.read())
        return config.get("records_path", ".")

class TagScreen(Screen):
    product_id = StringProperty('no_id')
    start_time = NumericProperty(-1)
    sound_name = StringProperty('no_name')

    def on_enter(self):

        self.init_record()
        Logger.info("TagScreen: {}, {}, {}, {}".format(
            self.product_id, self.start_time, self.random_hash, self.sound_name))

        # TODO: temporary hotfixing not implemented vents
        if not (self.product_id[0:2] in ["1:", "2:", "3:", "4"]):
            self.ids.btn_analyse.opacity = 0.30
        else:
            self.ids.btn_analyse.opacity = 1.0

        self.ids.visualizer.reset()
        # for id in self.ids:
        #     print(id)

    def on_pre_leave(self):
        # stop recording before leaving
        Logger.info("Stopping record")
        self.record.stop()


    def init_record(self):
        # Open the pop up
        mythread = threading.Thread(target=self.start_recording)
        mythread.start()

    def start_recording(self):
        dateString = datetime.datetime.fromtimestamp(self.start_time).strftime('%Y-%m-%d-%H-%M-%S-%f')
        folderName = datetime.datetime.fromtimestamp(self.start_time).strftime('%Y-%m-%d')
        saveDir = os.path.join(get_base_records_path(), folderName)
        if not os.path.exists(saveDir):
            os.makedirs(saveDir)
        self.sound_name = "_".join([dateString, self.random_hash, socket.gethostname()]) + ".wav"
        self.sound_name = os.path.join(saveDir, self.sound_name)

        self.record = Record()
        self.record.start(self.sound_name, duration=RECORDING_DURATION) # record max 6 minutes


class Visualizer(BoxLayout):
    minutes = StringProperty()
    seconds = StringProperty()
    running = BooleanProperty(False)

    def __init__(self, **kwargs):
        super(Visualizer, self).__init__(**kwargs)

    def reset(self):
        self.delta = datetime.datetime.now()+datetime.timedelta(0, RECORDING_DURATION)
        self.start()
        self.update()

    def start(self):
        if not self.running:
            self.running = True
            Clock.schedule_interval(self.update, 1.0)

    def stop(self):
        if self.running:
            self.running = False
            Clock.unschedule(self.update)

    def update(self, *kwargs):
        delta = self.delta - datetime.datetime.now()
        self.minutes, seconds = str(delta).split(":")[1:]
        self.seconds = seconds[:2]

        if int(self.minutes) == 0:
            if int(self.seconds) == 0:
                # countdown is finnished
                self.seconds = "00"
                # self.sound.play()
                self.stop()
