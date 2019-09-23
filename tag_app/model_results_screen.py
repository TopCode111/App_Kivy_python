from kivy.uix.screenmanager import Screen
from kivy.uix.screenmanager import ScreenManager
from kivy.app import App
from kivy.uix.popup import Popup
from kivy.factory import Factory
from kivy.properties import ObjectProperty
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, NumericProperty

from kivy.logger import Logger

from main import TagApp
from custom_progressbar import CustomProgressbar
from analysator import Analyse
from errors import FanNotDetectedError, OffsetError

import os
import time, threading
import traceback


# unicode support for Python2, pass if Python3
try:
    import sys
    reload(sys)
    sys.setdefaultencoding('utf-8')
except NameError:
    pass



class PopupBox(Popup):
    pop_up_text = ObjectProperty()
    def update_pop_up_text(self, p_message):
        self.pop_up_text.text = p_message

class ModelResultsScreen(Screen):

    product_id = StringProperty('no_id')
    start_time = NumericProperty(-1)
    sound_name = StringProperty('no_name')
    random_hash = StringProperty("no_name")

    def on_pre_enter(self):
        self.ids.label_result.text = "-"
        self.ids.label_score.text = "-"

    def on_enter(self):

        self.progressbar = CustomProgressbar()
        self.add_widget(self.progressbar)
        self.progressbar.show_popup(self)

        self.init_analysis()

    def init_analysis(self):
        # Open the pop up
        mythread = threading.Thread(target=self.run_analysis_task)
        mythread.start()


    def run_analysis_task(self):

        # file = "rec_" + str(self.start_time) + "_" + "test1.wav"
        # file = "1487544731-1487545009-multi.wav" # OK test
        # file = "1487543187-1487543575-multi.wav" # NOK test
        file = self.sound_name
        Logger.debug("File to analyse: {}".format(file))

        prediction = None
        errorOccured = False
        try:
            analysator = Analyse(file, product_id=self.product_id,
                                 soundType="wav", progressbar=self.progressbar)
            prediction, score = analysator.analyse()
        except FanNotDetectedError:
            label = "Fan not detected"
            Logger.error('Fan not detected', exc_info=True)
            errorOccured = True
        except OffsetError:
            label = "Offset error"
            Logger.error('Offset error', exc_info=True)
            errorOccured = True
        except ValueError:
            label = "Analysis error"
            Logger.error('Analysis error', exc_info=True)
            errorOccured = True
        except IOError:
            label = "File not found"
            Logger.error('File not found', exc_info=True)
            errorOccured = True
        except MemoryError:
            label = "Memory error"
            Logger.error('Memory error', exc_info=True)
            errorOccured = True
        except Exception:
            label = "Unknown error"
            Logger.error('Unknown error', exc_info=True)
            errorOccured = True

        if errorOccured:
            # resize label so error msg fits
            self.ids.label_result.font_size = 30
            self.ids.label_result.height = 30
            try:
                traceback.print_exc()
            except:
                Logger.error("Cannot print traceback")

        self.progressbar.hide_popup(self)

        if prediction == "ok":
            label = TagApp.lang('ok')
            button_bg = '../img/button_ok.png'
            background_down = '../img/button_ok_down.png'
            color = (0, 1, 0, 1)
        elif prediction == "nok":
            label = TagApp.lang('not_ok')
            button_bg = '../img/button_nok.png'
            background_down = '../img/button_nok_down.png'
            color = (1, 0, 0, 1)
        else:
            score = 0
            color = (1, 0, 0, 1)

        # update GUI based on ok/nok
        self.ids.label_result.text = label
        self.ids.label_result.color = color
        self.ids.label_score.text = "{0:.0f}%".format(score * 100)
