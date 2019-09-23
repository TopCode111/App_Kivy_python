from kivy.clock import Clock
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.progressbar import ProgressBar
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty

from main import TagApp


class CustomProgressbar(Widget):

    progress_bar = ObjectProperty()

    def __init__(self, **kwa):
        super(CustomProgressbar, self).__init__(**kwa)

        self.progress_bar = ProgressBar()
        self.popup = Popup(
            title=TagApp.lang("analysing"),
            content=self.progress_bar,
            size_hint=(.75, .75)
        )

    def show_popup(self, instance):
        self.popup.open()

    def hide_popup(self, instance):
        self.popup.dismiss()

    def update(self, value):
        self.progress_bar.value = value
