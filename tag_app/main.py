from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from kivy.config import Config

from kivy.uix.popup import Popup
from kivy.factory import Factory
from kivy.properties import ObjectProperty
from kivy.clock import Clock

from kivy.logger import Logger

import os
import sys
import json
import subprocess
import time
import argparse
import threading
import psutil

import lang as lang_dicts
from database import Database

KIVY_CONFIG_FILENAME = "confs/kivy_config.ini"
CONFIG_FILENAME = "confs/mahle.json"

Config.read(KIVY_CONFIG_FILENAME)
Config.write()


class TagAppScreenManager(ScreenManager):
    pass


class PopupBox(Popup):
    pop_up_text = ObjectProperty()
    def update_pop_up_text(self, p_message):
        self.pop_up_text.text = p_message

class TagApp(App):

    def build(self):

        from kivy.core.window import Window
        Window.clearcolor = (1, 1, 1, 1)

        global app
        app = self

        sm = TagAppScreenManager()
        sm.ids.product_screen.add_product_buttons(TagApp.products)

        return sm

    @staticmethod
    def lang(key):
        lang_dict = getattr(lang_dicts, TagApp.language)

        if key in lang_dict:
            return lang_dict[key]
        else:
            return '!!' + key + '!!'

    @staticmethod
    def insert_label(product_id, start_time, label, random_hash):
        with Database(TagApp.db_filename) as db:
            db.insert(product_id, start_time, time.time(), label, random_hash)

    language = "lang_cz"

    # TODO: better manage config file
    with open(CONFIG_FILENAME, 'r') as config_file:
        db_path = json.loads(config_file.read())["db_path"]
    db_filename = os.path.join(db_path, "labels.db")


    products = ['Product1', 'Product2']

    known_config_keys = ['db_path', 'db_filename', 'language', 'products', 'records_path']

    @staticmethod
    def read_config(config_filename):

        with open(config_filename) as config_file:
            config = json.loads(config_file.read())

            for key in config:
                if key in TagApp.known_config_keys:
                    setattr(TagApp, key, config[key])

    # kill arecord if it is running
    for proc in psutil.process_iter():
        # check whether the process name matches
        if proc.name() == "arecord":
            Logger.info("Killing arecord")
            proc.kill()

app = None

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Tagging app GUI')
    parser.add_argument('-f', '--full_screen', dest='full_screen', action='store_const', const='auto', default=0)
    parser.add_argument('config_file', action='store')
    # options = parser.parse_args()

    TagApp.read_config(CONFIG_FILENAME)

    # Run app in fullscreen
    Config.set('graphics', 'fullscreen', 'auto')

    TagApp().run()
