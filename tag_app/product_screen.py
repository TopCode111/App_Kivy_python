from kivy.properties import StringProperty
from kivy.uix.screenmanager import Screen
from ui import BorderButton


class ProductButton(BorderButton):
    product_id = StringProperty('no_id')


class ProductScreen(Screen):

    def add_product_buttons(self, products):

        self.ids.button_container.rows = 4
        self.ids.button_container.cols = min(len(products), 3)

        for product_id in products:
            button = ProductButton()
            button.product_id = product_id
            self.ids.button_container.add_widget(button)
