#
#  RDpass - rdcomponents
#

# Standard import requirements
import sys
import re

# Kivy app requirements
from kivy.lang import Builder
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.animation import Animation
from kivy.properties import StringProperty, NumericProperty, \
                            ListProperty, BooleanProperty
from kivymd.uix.textfield import TextfieldLabel
from kivymd.uix.label import MDIcon
from kivymd.uix.list import OneLineListItem, ContainerSupport

# RD pass requirements
from RDconfig import rdstatus


KV = '''
<TextfieldLabel>
    size_hint_x: None
    width: self.texture_size[0]
    #height: self.texture_size[1]
    shorten: True
    shorten_from: "right"


<SimpleHintTextField>
    canvas.before:
        Clear

        # Default line
        Color:
            rgba: [0, 0, 0, 0.2]
        Line:
            points: self.x, self.y + 0.2 * self.height, self.x + self.width, self.y + 0.2 * self.height
            width: 1

        # Fake cursor blinking
        Color:
            rgba:
                (self._current_line_color if self.focus and not self._cursor_blink else (0, 0, 0, 0))
        Rectangle:
            pos:  self.cursor_pos[0], self.cursor_pos[1] - self.line_height
            size: dp(1) * root.fin_font_scale_fac_propagate, self.line_height

        # Hint text background
        # Color:
        #     rgba: [1,0,0,0.5]
        # Rectangle:
        #     size: self._hint_lbl.texture_size
        #     pos: self.x, self.y + self.height - self._hint_y

        # Top left corner hint text
        Color:
            rgba: self._current_hint_text_color
        Rectangle:
            texture: self._hint_lbl.texture
            size: self._hint_lbl.texture_size
            pos: self.x, self.y + self.height - self._hint_y

        # Active line
        Color:
            rgba: self._current_line_color
        Rectangle:
            size: self._line_width, dp(2) * root.fin_font_scale_fac_propagate
            pos: self.center_x - (self.width / 2), self.y + 0.2 * self.height

    padding: [0, dp(20) * root.fin_font_scale_fac_propagate, 0, dp(18) * root.fin_font_scale_fac_propagate]
    size_hint_y: None
    height: self.minimum_height
    cursor_blink: True



<SimpTextFieldRound>:
    multiline: False
    size_hint: (1, None)
    height: self.line_height + dp(root.fin_font_scale_fac_propagate*5)
    background_active: ""
    background_normal: ""
    hint_text_color: [0,0,0,0.4]
    padding:
        self._lbl_icon_left.texture_size[1] + dp(root.fin_font_scale_fac_propagate*20), \
        (self.height / 2) - (self.line_height / 2), \
        self._lbl_icon_right.texture_size[1] + dp(root.fin_font_scale_fac_propagate*20), \
        0
    canvas.before:
        Color:
            rgba: self.normal_color if not self.focus else self._color_active
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(root.fin_font_scale_fac_propagate*9)]

        # Texture of left Icon.
        Color:
            rgba:
                self.icon_left_color \
                if self.focus else self.disabled_hint_text_color
        Rectangle:
            texture: self._lbl_icon_left.texture
            size:
                self._lbl_icon_left.texture_size if self.icon_left \
                else (0, 0)
            pos:
                self.x + dp(root.fin_font_scale_fac_propagate*5), \
                self.center[1] - self._lbl_icon_right.texture_size[1] / 2

        # Texture of right Icon.
        Color:
            rgba:
                self.icon_right_color \
                if self.focus else self.disabled_hint_text_color
        Rectangle:
            texture: self._lbl_icon_right.texture
            size:
                self._lbl_icon_right.texture_size if self.icon_right \
                else (0, 0)
            pos:
                (self.width + self.x) - (self._lbl_icon_right.texture_size[1]) - dp(root.fin_font_scale_fac_propagate*5), \
                self.center[1] - self._lbl_icon_right.texture_size[1] / 2

        Color:
            rgba:
                self.hint_text_color if not self.text else root.foreground_color



<TwoLineIconListItemMod>
    _txt_top_pad: dp(20 * root._fin_font_scale_fac_propagate)
    _txt_left_pad: dp(72 * root._fin_font_scale_fac_propagate)
    _txt_bot_pad: dp(15 * root._fin_font_scale_fac_propagate)
    _height: dp(72 * root._fin_font_scale_fac_propagate)

    BoxLayout:
        id: _left_container
        size_hint: None, None
        pos_hint: {"center_y": 0.5}
        x: root.x + dp(16 * root._fin_font_scale_fac_propagate)
        y: root.y + root.height/2 * root._fin_font_scale_fac_propagate - self.height/2
        size: dp(48 * root._fin_font_scale_fac_propagate), dp(48 * root._fin_font_scale_fac_propagate)

'''

Builder.load_string(KV)


class Placeholder(Label):
    pass


class InTextPlaceholder(Label):
    pass


class TwoLineIconListItemMod(ContainerSupport, OneLineListItem):
    '''
        A modified class similar to TwoLineIconListItem
        Added the _fin_font_scale_fac_propagate support and modified the padding
    '''
    _txt_top_pad = NumericProperty("20dp")
    _txt_left_pad = NumericProperty("72dp")
    _txt_bot_pad = NumericProperty("15dp")
    _height = NumericProperty("72dp")
    _num_lines = 2
    # Same as fin_font_scale_fac_propagate
    _fin_font_scale_fac_propagate = NumericProperty(1)



class SimpleHintTextField(TextInput):
    '''
        A simpified version of MDTextField with extra functionalities
        Added rescaling, password hide, suggestion_text functionalities
    '''
    fin_font_scale_fac_propagate = NumericProperty(1)
    required = BooleanProperty(False)
    max_text_length = NumericProperty(40)
    hint_y_base = dp(14)
    hint_lbl_font_size_base = dp(12)
    error = BooleanProperty(False)
    password_hide = BooleanProperty(None)
    error_color = [1.0,0.2196,0.1372,0.8]
    disabled_hint_text_color = [0,0,0,0.55]
    suggestion_flag = BooleanProperty(None)

    line_color_focus = ListProperty([0.0, 0.0, 0.0, 0.0])
    corn_hint_text = StringProperty("")

    # MDTextField variables
    _text_len_error = BooleanProperty(False)
    _hint_lbl_font_size = NumericProperty("14sp")
    _line_blank_space_right_hint_text = NumericProperty(0)
    _line_blank_space_left_hint_text = NumericProperty(0)
    _hint_y = NumericProperty(dp(30))
    _line_width = NumericProperty(0)
    _current_line_color = ListProperty([0.0, 0.0, 0.0, 0.0])
    _current_error_color = ListProperty([0.0, 0.0, 0.0, 0.0])
    _current_hint_text_color = ListProperty([0.0, 0.0, 0.0, 0.0])
    _current_right_lbl_color = ListProperty([0.0, 0.0, 0.0, 0.0])


    def __init__(self, **kwargs):
        if self.password_hide:
            self.password = True

        self._hint_lbl = TextfieldLabel(
            font_style="Subtitle1", halign="left", valign="middle", field=self
        )
        super().__init__(**kwargs)
        self.bind(
            corn_hint_text=self.on_hint_text,
            max_text_length = self._set_max_text_length,
            _hint_lbl_font_size=self._hint_lbl.setter("font_size"),
            text=self.set_text,
        )
        self.has_had_text = False
        self.word_list = []
        Clock.schedule_once(self.check_text)
        #Clock.schedule_once(self.check_suggestion_flag)
        Clock.schedule_once(self.check_fin_font_scale_fac_propagate)

    def _set_max_text_length(self, instance, length):
        self.max_text_length = length

    def check_text(self, interval):
        self.set_text(self, self.text)

    def check_fin_font_scale_fac_propagate(self, *args):
        self._hint_y = dp(14 * self.fin_font_scale_fac_propagate)
        self._hint_lbl_font_size = dp(12 * self.fin_font_scale_fac_propagate)

    def on_hint_text(self, instance, text):
        self._hint_lbl.text = text
        self._hint_lbl_font_size = self.hint_lbl_font_size_base

    def set_line_color_to_error_color(self, *args):
        self._current_line_color = self.error_color
        Animation(_line_width=self.width, duration=0.2, t="out_quad").start(self)

    def set_text(self, instance, text):
        self.text = re.sub("\n", " ", text) if not self.multiline else text
        if len(text) > 0:
            self.has_had_text = True

        if self.max_text_length is not None:
            max_text_length = self.max_text_length
        else:
            max_text_length = sys.maxsize

        if len(text) > max_text_length or all(
            [self.required, len(self.text) == 0, self.has_had_text]
        ):
            self._text_len_error = True
        else:
            self._text_len_error = False

        if len(self.text) != 0 and not self.focus:
            self._hint_y = self.hint_y_base * self.fin_font_scale_fac_propagate
            self._hint_lbl_font_size = self.hint_lbl_font_size_base * self.fin_font_scale_fac_propagate

        if self.error or self._text_len_error:
            print('Text Length Error')
            Animation(
                duration=0.2,
                _current_hint_text_color=self.error_color,
                _current_line_color=self.error_color,
            ).start(self)
        else:
            Animation(
                duration=0.2,
                _current_hint_text_color=self.disabled_hint_text_color,
                _current_line_color=self.line_color_focus,
            ).start(self)
            #self.on_focus(self, self.focus)


    def on_focus(self, instance, value):
        Animation.cancel_all(
            self, "_line_width", "_hint_y", "_hint_lbl_font_size"
        )
        # Reveal text
        if self.password and value:
            self.password = False

        # Hide text when not focus and password == False and password_hide == True
        if not value and not self.password and self.password_hide:
            self.password = True

        if self.max_text_length is None:
            max_text_length = sys.maxsize
        else:
            max_text_length = self.max_text_length
        if len(self.text) > max_text_length or all(
            [self.required, len(self.text) == 0, self.has_had_text]
        ):
            self._text_len_error = True
        if self.error or all(
            [
                self.max_text_length is not None
                and len(self.text) > self.max_text_length
            ]
        ):
            has_error = True
        else:
            if all([self.required, len(self.text) == 0, self.has_had_text]):
                has_error = True
            else:
                has_error = False

        if value:                             # or self.focus
            if not self._line_blank_space_right_hint_text:
                self._line_blank_space_right_hint_text = self._hint_lbl.texture_size[0] - dp(25)

            anim = Animation(
                    _current_hint_text_color=self.line_color_focus,
                    duration=0.2, t="out_quad")
            self.has_had_text = True
            anim.start(self)
            Animation.cancel_all(
                self, "_line_width", "_hint_y", "_hint_lbl_font_size"
            )
            if not self.text:
                Animation(
                    _hint_y=self.hint_y_base * self.fin_font_scale_fac_propagate,
                    _hint_lbl_font_size=self.hint_lbl_font_size_base * self.fin_font_scale_fac_propagate,
                    duration=0.2,
                    t="out_quad",
                ).start(self)
            Animation(_line_width=self.width, duration=0.2, t="out_quad").start(self)
            if has_error:
                Animation(
                    duration=0.2,
                    _current_hint_text_color=self.error_color,
                    _current_line_color=self.error_color,
                ).start(self)
            else:
                # Animation(
                #     duration=0.2,
                #     _current_right_lbl_color=self.disabled_hint_text_color,
                # ).start(self)
                Animation(duration=0.2, color=self.line_color_focus).start(
                    self._hint_lbl
                )
        else:
            if not self.text:
                Animation(
                    _hint_y=dp(38 * self.fin_font_scale_fac_propagate),
                    _hint_lbl_font_size=dp(16 * self.fin_font_scale_fac_propagate),
                    duration=0.2,
                    t="out_quad",
                ).start(self)
                # Animation(
                #     _line_blank_space_right_hint_text=0,
                #     _line_blank_space_left_hint_text=0,
                #     duration=0.2,
                #     t="out_quad",
                # ).start(self)
            if has_error:
                Animation(
                    duration=0.2,
                    _current_line_color=self.error_color,
                    _current_hint_text_color=self.error_color,
                ).start(self)
            else:
                Animation(duration=0.2, color=(1, 1, 1, 1)).start(
                    self._hint_lbl
                )
                Animation(
                    duration=0.2,
                    _current_line_color=self.line_color_focus,
                    _current_hint_text_color=self.disabled_hint_text_color,
                ).start(self)
                Animation(_line_width=0, duration=0.2, t="out_quad").start(self)


    def keyboard_on_key_down(self, window, keycode, text, modifiers):
        '''
            Add support for tab as an 'autocomplete' using the suggestion text.
            Reference: https://gist.github.com/Zen-CODE/650099bd55247223986928f12df42176
        '''
        if self.suggestion_text and keycode[1] == 'tab':
            self.insert_text(self.suggestion_text)
            return True
        return super(SimpleHintTextField, self).keyboard_on_key_down(window, keycode, text, modifiers)


    def on_text(self, instance, value):
        '''
            Include all current text from textinput into the word list and
            change the textfield suggestion_text
        '''
        self.suggestion_text = ''

        # Update word list and suggestion_text if suggestion_flag is true
        if self.suggestion_flag:

            # Fetch the category list from rdstatus if word list is empty
            if len(self.word_list) == 0:
                self.word_list = rdstatus.config_status['category_list']

            word_list = list(set(self.word_list + value[:value.rfind(' ')].split(' ')))
            val = value[value.rfind(' ') + 1:]
            if not val:
                return False
            try:
                word = [word for word in word_list
                        if word.startswith(val)][0][len(val):]
                if not word:
                    return False
                self.suggestion_text = word
            except IndexError:
                pass                      # print('Index Error.')


    def check_valid_text(self):
        '''
            Return True if it is not an empty string or with only space
        '''
        return self.text.strip() != ''


    def on_fin_font_scale_fac_propagate(self, *args):
        self._hint_y = dp(14 * self.fin_font_scale_fac_propagate)
        self._hint_lbl_font_size = dp(12 * self.fin_font_scale_fac_propagate)



class SimpTextFieldRound(TextInput):
    '''
        A simpified version of MDTextFieldRound with extra functionalities
        Added rescaling, redrew the appearance, added clearbutton color change functionalities
    '''
    fin_font_scale_fac_propagate = NumericProperty(1)

    icon_left = StringProperty()
    icon_left_color = ListProperty([0,0,0,1])
    icon_right = StringProperty()
    icon_right_color = ListProperty([0, 0, 0, 1])

    line_color = ListProperty([0,0,0,0.8])
    disabled_hint_text_color =ListProperty([0,0,0,0.4])
    normal_color = ListProperty([0,0,0,0.1])
    color_active = ListProperty([0,0,0,0.3])

    primary_color = [0,0,0, 0.75]
    text_color = [0,0,0, 0.9]

    _color_active = ListProperty([0,0,0,0.2])

    def __init__(self, **kwargs):
        self._lbl_icon_left = MDIcon(theme_text_color="Custom", font_size=dp(24))
        self._lbl_icon_right = MDIcon(theme_text_color="Custom", font_size=dp(24), text_color=[1,0,0,1])
        super().__init__(**kwargs)
        self.cursor_color = self.primary_color
        self.icon_left_color = self.text_color
        self.icon_right_color = self.text_color

    def on_focus(self, instance, value):
        if value:
            self.icon_left_color = self.primary_color
            self.icon_right_color = self.primary_color
        else:
            self.icon_left_color = self.text_color
            self.icon_right_color = self.text_color

    def on_icon_left(self, instance, value):
        self._lbl_icon_left.icon = value

    def on_icon_left_color(self, instance, value):
        self._lbl_icon_left.text_color = value

    def on_icon_right(self, instance, value):
        self._lbl_icon_right.icon = value

    def on_icon_right_color(self, instance, value):
        self._lbl_icon_right.text_color = value

    def on_color_active(self, instance, value):
        if value != [0, 0, 0, 0.6]:
            self._color_active = value
            self._color_active[-1] = 0.6
        else:
            self._color_active = value

    def on_fin_font_scale_fac_propagate(self, *args):
        self._lbl_icon_left.font_size = dp(25*self.fin_font_scale_fac_propagate)
        self._lbl_icon_right.font_size = dp(25*self.fin_font_scale_fac_propagate)






