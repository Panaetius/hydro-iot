# -*- coding: utf-8 -*-

from kivy.graphics.texture import Texture
from kivy.properties import (
    AliasProperty,
    NumericProperty,
    ObjectProperty,
    StringProperty,
)
from kivy.uix.effectwidget import EffectWidget


class DialGauge(EffectWidget):
    min_value = NumericProperty(0)
    min_ok_value = NumericProperty(33)
    max_ok_value = NumericProperty(66)
    max_value = NumericProperty(100)

    current_value = NumericProperty(50)
    suffix = StringProperty("")

    padding = NumericProperty(50)
    texture = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(DialGauge, self).__init__(**kwargs)
        self.texture = Texture.create(size=(1, 64), colorfmt="rgb", bufferfmt="ubyte", mipmap=True)
        buffer = [255 for _ in range(64 * 64 * 3)]
        self.buffer = bytes(buffer)
        self.texture.blit_buffer(self.buffer, colorfmt="rgb", bufferfmt="ubyte")

    def bar_color(self):
        if self.current_value >= self.min_ok_value and self.current_value <= self.max_ok_value:
            return (0, 1, 0, 1)
        return (1, 0, 0, 1)

    def label_text(self):
        return f"{self.current_value}{self.suffix}"

    bar_color_p = AliasProperty(bar_color, bind=["current_value", "min_ok_value", "max_ok_value"])
    label_text_p = AliasProperty(label_text, bind=["current_value", "suffix"])
