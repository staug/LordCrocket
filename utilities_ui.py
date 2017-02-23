import pygame as pg
import settings as st
from os import path
import constants as c
import random as rd
import string

"""
Sub utilities routines.
"""


class Button(object):
    '''
    https://github.com/metulburr/pygooey/blob/master/pygooey/button.py
    Example can found in run_button.py.py

    '''

    def __init__(self, rect, command, **kwargs):
        '''
        Optional kwargs and their defaults:
            "color"             : pg.Color('red'),
            "text"              : None,
            "font"              : None, #pg.font.Font(None,16),
            "call_on_release"   : True,
            "hover_color"       : None,
            "clicked_color"     : None,
            "font_color"        : pg.Color("white"),
            "hover_font_color"  : None,
            "clicked_font_color": None,
            "click_sound"       : None,
            "hover_sound"       : None,
            'border_color'      : pg.Color('black'),
            'border_hover_color': pg.Color('yellow'),
            'disabled'          : False,
            'disabled_color'     : pg.Color('grey'),
            'radius'            : 3,

        Values:
            self.rect = pg.Rect(rect)
            self.command = command
            self.clicked = False
            self.hovered = False
            self.hover_text = None
            self.clicked_text = None
        '''
        self.command = command
        self.clicked = False
        self.hovered = False
        self.hover_text = None
        self.clicked_text = None
        self.process_kwargs(kwargs)
        self.rect = pg.Rect(rect)
        if self.image:
            self.rect.width = self.image.get_rect().width
            self.rect.height = self.image.get_rect().height
        self.render_text()

    def process_kwargs(self, kwargs):
        settings = {
            "id": None,
            "color": pg.Color('black'),
            "text": None,
            "font":  pg.font.Font(path.join(path.join(path.dirname(__file__), st.FONT_FOLDER), st.FONT_NAME), 10),
            "hover_color": pg.Color('white'),
            "clicked_color": None,
            "font_color": pg.Color("white"),
            "hover_font_color": pg.Color("red"),
            "clicked_font_color": None,
            "click_sound": None,
            "hover_sound": None,
            'border_color': pg.Color('black'),
            'border_hover_color': pg.Color('white'),
            'disabled': False,
            'disabled_color': pg.Color('grey'),
            'radius': 3,
            'image': None,
        }
        for kwarg in kwargs:
            if kwarg in settings:
                settings[kwarg] = kwargs[kwarg]
            else:
                raise AttributeError("{} has no keyword: {}".format(self.__class__.__name__, kwarg))
        self.__dict__.update(settings)

    def render_text(self):
        """Pre render the button text."""
        if self.text:
            if self.hover_font_color:
                color = self.hover_font_color
                self.hover_text = self.font.render(self.text, True, color)
            if self.clicked_font_color:
                color = self.clicked_font_color
                self.clicked_text = self.font.render(self.text, True, color)
            self.text = self.font.render(self.text, True, self.font_color)

    def get_event(self, event):
        ''' Call this on your event loop

            for event in pg.event.get():
                Button.get_event(event)
        '''
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            self.on_click(event)

    def on_click(self, event):
        if self.rect.collidepoint(event.pos):
            self.command()
            return True
        return False

    def check_hover(self):
        if self.rect.collidepoint(pg.mouse.get_pos()):
            if not self.hovered:
                self.hovered = True
                if self.hover_sound:
                    self.hover_sound.play()
        else:
            self.hovered = False

    def draw(self, surface):
        '''
        Call once on your main game loop
        '''
        color = self.color
        text = self.text
        border = self.border_color
        self.check_hover()


        # if not self.rounded:
        #    surface.fill(border,self.rect)
        #    surface.fill(color,self.rect.inflate(-4,-4))
        # else:
        if self.radius:
            rad = self.radius
        else:
            rad = 0

        if self.image:
            if self.hovered:
                surface.fill(self.border_hover_color, self.rect.inflate(4, 4))
            surface.blit(self.image, self.rect)
        else:
            if not self.disabled:
                if self.clicked and self.clicked_color:
                    color = self.clicked_color
                    if self.clicked_font_color:
                        text = self.clicked_text
                elif self.hovered and self.hover_color:
                    color = self.hover_color
                    if self.hover_font_color:
                        text = self.hover_text
                if self.hovered:
                    border = self.border_hover_color
            else:
                color = self.disabled_color
            self.round_rect(surface, self.rect, border, rad, 1, color)

        if self.text:
            text_rect = text.get_rect(center=self.rect.center)
            surface.blit(text, text_rect)

    def round_rect(self, surface, rect, color, rad=20, border=0, inside=(0, 0, 0, 0)):
        rect = pg.Rect(rect)
        zeroed_rect = rect.copy()
        zeroed_rect.topleft = 0, 0
        image = pg.Surface(rect.size).convert_alpha()
        image.fill((0, 0, 0, 0))
        self._render_region(image, zeroed_rect, color, rad)
        if border:
            zeroed_rect.inflate_ip(-2 * border, -2 * border)
            self._render_region(image, zeroed_rect, inside, rad)
        surface.blit(image, rect)

    def _render_region(self, image, rect, color, rad):
        corners = rect.inflate(-2 * rad, -2 * rad)
        for attribute in ("topleft", "topright", "bottomleft", "bottomright"):
            pg.draw.circle(image, color, getattr(corners, attribute), rad)
        image.fill(color, rect.inflate(-2 * rad, 0))
        image.fill(color, rect.inflate(0, -2 * rad))

    def update(self):
        # for completeness
        pass


class InputBox(object):
    '''
    https://github.com/metulburr/pygooey/blob/master/pygooey/textbox.py
    Example can found in run_textbox.py.py

    '''

    def __init__(self, rect, **kwargs):
        '''
        Optional kwargs and their defaults:
            "id" : None,
            "command" : None,
                function to execute upon enter key
                Callback for command takes 2 args, id and final (the string in the textbox)
            "active" : True,
                textbox active on opening of window
            "color" : pg.Color("white"),
                background color
            "font_color" : pg.Color("black"),
            "outline_color" : pg.Color("black"),
            "outline_width" : 2,
            "active_color" : pg.Color("blue"),
            "font" : pg.font.Font(None, self.rect.height+4),
            "clear_on_enter" : False,
                remove text upon enter
            "inactive_on_enter" : True
            "blink_speed": 500
                prompt blink time in milliseconds
            "delete_speed": 500
                backspace held clear speed in milliseconds

        Values:
            self.rect = pg.Rect(rect)
            self.buffer = []
            self.final = None
            self.rendered = None
            self.render_rect = None
            self.render_area = None
            self.blink = True
            self.blink_timer = 0.0
            self.delete_timer = 0.0
            self.accepted = string.ascii_letters+string.digits+string.punctuation+" "
        '''
        self.rect = pg.Rect(rect)
        self.buffer = []
        self.final = None
        self.rendered = None
        self.render_rect = None
        self.render_area = None
        self.blink = True
        self.blink_timer = 0.0
        self.delete_timer = 0.0
        self.accepted = string.ascii_letters + string.digits + string.punctuation + " "
        self.process_kwargs(kwargs)

    def process_kwargs(self, kwargs):
        defaults = {"id": None,
                    "command": None,
                    "active": True,
                    "color": pg.Color("white"),
                    "font_color": pg.Color("black"),
                    "outline_color": pg.Color("black"),
                    "outline_width": 2,
                    "active_color": pg.Color("blue"),
                    "font": pg.font.Font(None, self.rect.height + 4),
                    "clear_on_enter": False,
                    "inactive_on_enter": True,
                    "blink_speed": 500,
                    "delete_speed": 75}
        for kwarg in kwargs:
            if kwarg in defaults:
                defaults[kwarg] = kwargs[kwarg]
            else:
                raise KeyError("TextBox accepts no keyword {}.".format(kwarg))
        self.__dict__.update(defaults)

    def get_event(self, event, mouse_pos=None):
        ''' Call this on your event loop

            for event in pg.event.get():
                TextBox.get_event(event)
        '''
        if event.type == pg.KEYDOWN and self.active:
            if event.key in (pg.K_RETURN, pg.K_KP_ENTER):
                self.execute()
            elif event.key == pg.K_BACKSPACE:
                if self.buffer:
                    self.buffer.pop()
            elif event.unicode in self.accepted:
                self.buffer.append(event.unicode)
        elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            if not mouse_pos:
                mouse_pos = pg.mouse.get_pos()
            self.active = self.rect.collidepoint(mouse_pos)

    def execute(self):
        if self.command:
            self.command(self.id, self.final)
        self.active = not self.inactive_on_enter
        if self.clear_on_enter:
            self.buffer = []

    def switch_blink(self):
        if pg.time.get_ticks() - self.blink_timer > self.blink_speed:
            self.blink = not self.blink
            self.blink_timer = pg.time.get_ticks()

    def update(self):
        '''
        Call once on your main game loop
        '''
        new = "".join(self.buffer)
        if new != self.final:
            self.final = new
            self.rendered = self.font.render(self.final, True, self.font_color)
            self.render_rect = self.rendered.get_rect(x=self.rect.x + 2,
                                                      centery=self.rect.centery)
            if self.render_rect.width > self.rect.width - 6:
                offset = self.render_rect.width - (self.rect.width - 6)
                self.render_area = pg.Rect(offset, 0, self.rect.width - 6,
                                           self.render_rect.height)
            else:
                self.render_area = self.rendered.get_rect(topleft=(0, 0))
        self.switch_blink()
        self.handle_held_backspace()

    def handle_held_backspace(self):
        if pg.time.get_ticks() - self.delete_timer > self.delete_speed:
            self.delete_timer = pg.time.get_ticks()
            keys = pg.key.get_pressed()
            if keys[pg.K_BACKSPACE]:
                if self.buffer:
                    self.buffer.pop()

    def draw(self, surface):
        '''
        Call once on your main game loop
        '''
        outline_color = self.active_color if self.active else self.outline_color
        outline = self.rect.inflate(self.outline_width * 2, self.outline_width * 2)
        surface.fill(outline_color, outline)
        surface.fill(self.color, self.rect)
        if self.rendered:
            surface.blit(self.rendered, self.render_rect, self.render_area)
        if self.blink and self.active:
            curse = self.render_area.copy()
            curse.topleft = self.render_rect.topleft
            surface.fill(self.font_color, (curse.right + 1, curse.y, 2, curse.h))


class LogBox:
    """
    Handle a Textbox on the screen, that is used to display all the messages.
    The messages have different colors depending on the type of actions.
    The messages should only be received via the bus.
    Use the add property to add message, and a text property to set a text.
    """
    def __init__(self,
                 bus,
                 position,
                 limit_lines=8,
                 border=2,
                 border_color=st.WHITE):

        self.font = pg.font.Font(path.join(path.join(path.dirname(__file__), st.FONT_FOLDER), st.FONT_NAME), 10)
        self.border = border
        self.border_color = border_color

        font_width, font_height = self.font.size("A")
        self.rect = pg.Rect(position[0] + border,
                            position[1] + border,
                            max(100 * font_width, st.TEXT_PART_WIDTH - 20),
                            limit_lines * self.font.get_height())
        self.rect.centerx = int(st.GAME_WIDTH / 2)
        bus.register(self)
        self.messages = []
        self.limit_lines = limit_lines
        self.delta = 0
        self.drag_drop_text_box = False
        self.force_render = True
        self._render_texts = None
        # Prepare the filters..
        rect_dimension = 10
        self.filters = {c.P_CAT_FIGHT: True, c.P_CAT_ITEM: True, c.P_CAT_ENV: True}
        self.color = {c.P_CAT_FIGHT: st.RED, c.P_CAT_ITEM: st.YELLOW, c.P_CAT_ENV: st.WHITE}
        rectangle = pg.Rect(self.rect.right + self.border,
                            self.rect.top - rect_dimension - self.border,
                            rect_dimension,
                            rect_dimension)
        self.filter_recs = {c.P_CAT_FIGHT: rectangle.copy().move(-rect_dimension, 0),
                            c.P_CAT_ITEM: rectangle.copy().move(-3 * rect_dimension, 0),
                            c.P_CAT_ENV: rectangle.copy().move(-5 * rect_dimension, 0)}

    @classmethod
    def wordTooLong(cls, word, font, max_length, justify_chars=0):
        """test if a single word is too long to the displayed with the given font.
        @word: the word to check
        @font: the pygame.Font to use
        @max_length: the max length of the word
        @justify_chars: an integer that add a number of spaces at the worrd total length.
        @return: True if the word will be longer
        """
        # BBB: someday this function could became part of some text (non graphical) utility?
        return font.size((" "*justify_chars)+word)[0]>max_length

    @classmethod
    def normalizeTextLength(cls, text_too_long, font, max_length, justify_chars=0):
        """This function take a text too long and split it in a list of smaller text lines.
        The final text max length must be less/equals than max_length parameter, using the font passed.

        @return: a list of text lines.
        """
        # BBB: someday this function could became part of some text (non graphical) utility?
        words = [x for x in text_too_long.split(" ")]
        words_removed = []
        tooLong = True
        txt1 = txt2 = ""
        while tooLong:
            word = words.pop()
            # Simple: cut the word and go on
            while cls.wordTooLong(word, font, max_length, justify_chars=justify_chars):
                word = word[:-1].strip()

            words_removed.append(word)
            txt1 = " ".join(words)
            if font.size(txt1)[0] <= max_length:
                tooLong = False
        words_removed.reverse()
        txt2 = (" " * justify_chars) + " ".join(words_removed)
        if font.size(txt2)[0] <= max_length:
            return [txt1, txt2]
        else:
            return [txt1] + cls.normalizeTextLength(txt2, font, max_length, justify_chars=justify_chars)

    def draw(self, surface):
        if self.force_render:
            self._render_texts = []
            i = 0
            msg_list = self._prepare_message_list()
            for line, category in msg_list:
                self._render_texts.append(self.font.render(line, 1, self.color[category], st.BGCOLOR))
                i += 1

        pg.draw.rect(surface, self.border_color, self.rect.inflate(self.border, self.border))
        surface.fill(st.BGCOLOR, rect=self.rect)
        i = 0
        for render_surf in self._render_texts:
            surface.blit(render_surf, (self.rect.left, self.rect.top + i * self.font.get_height()))
            i += 1
        for key in self.filters:
            pg.draw.rect(surface, self.color[key], self.filter_recs[key])
            if not self.filters[key]:
                pg.draw.rect(surface, st.BGCOLOR, self.filter_recs[key].inflate(-2, -2))

    def _prepare_message_list(self):
        message_for_display = []
        rw = self.rect.width
        for message_info in self.messages:
            text, category = message_info
            if self.filters[category]:
                lw, lh = self.font.size(text)
                if lw>rw:
                    text_list = self.normalizeTextLength(text,
                                                         self.font,
                                                         self.rect.width,
                                                         justify_chars=0)
                    for line in text_list:
                        message_for_display.append([line, category])
                else:
                    message_for_display.append(message_info)

        if self.delta < -len(message_for_display) + self.limit_lines:
            self.delta = -len(message_for_display) + self.limit_lines
        return message_for_display[- self.limit_lines + self.delta:len(message_for_display) + self.delta]

    def get_event(self, event):
        if event.type == pg.MOUSEBUTTONUP:
            if self.rect.collidepoint(event.pos):
                (x, y) = pg.mouse.get_pos()
                pos_in_chat = y - self.rect.y
                if pos_in_chat > self.rect.height / 2:
                    self.delta += 1
                    if self.delta > 0:
                        self.delta = 0
                else:
                    self.delta -= 1 # the delta will be adapted in the prepare message method
                self.force_render = True
                return True # Event consumed...
            for key in self.filter_recs:
                if self.filter_recs[key].collidepoint(event.pos):
                    self.filters[key] = not self.filters[key]
                    self.force_render = True
                    self.delta = 0
                    return True  # Event Consumed
        return False

    def update(self):
        pass

    def _setText(self, text):
        print("TTTEXXXTTT NOT PROPERLY SET {}".format(text))
    add = property(lambda self: self._text, _setText, doc="""The text to be displayed""")

    def _record_message(self, text, category):
        text = text[0].capitalize() + text[1:]
        self.messages.append([text, category])
        self.force_render = True
        self.delta = 0

    def notify(self, message):
        # Now interpret the text
        if message["MAIN_CATEGORY"] == c.P_CAT_FIGHT:
            if message["SUB_CATEGORY"] == c.AC_FIGHT_HIT:
                if message["result"] == c.SUCCESS:
                    self._record_message("{} hit {} with {}, dealing {} damages".format(message["attacker"].name,
                                                                                        message["defender"].name,
                                                                                        message["attack_type"],
                                                                                        message["damage"]),
                                         c.P_CAT_FIGHT)
                else:
                    self._record_message("{} tried hitting {} with {} but {}".format(message["attacker"].name,
                                                                                     message["defender"].name,
                                                                                     message["attack_type"],
                                                                                     rd.choice(("failed miserably",
                                                                                                "it was blocked",
                                                                                                "this was a pitiful "
                                                                                                "attempt"))),
                                         c.P_CAT_FIGHT)
            elif message["SUB_CATEGORY"] == c.AC_FIGHT_KILL:
                self._record_message("After a short fight, {} killed {} - LordCrocket awards {} experience point and "
                                     "{} gold".format(
                    message["attacker"].name,
                    message["defender"].name,
                    message["xp"],
                    message["gold"]),
                    c.P_CAT_FIGHT)
            elif message["SUB_CATEGORY"] == c.AC_FIGHT_VARIOUS:
                self._record_message(message["message"], c.P_CAT_FIGHT)
            else:
                print("UNKNOWN MESSAGE: {}".format(message))

        elif message["MAIN_CATEGORY"] == c.P_CAT_ITEM:

            if message["SUB_CATEGORY"] == c.AC_ITEM_GRAB:
                if message["result"] == c.SUCCESS:
                    if message["item"].long_desc is not None:
                        self._record_message("You grabbed up a {}, {}".format(message["item"].name,
                                                                              message["item"].long_desc.lower()),
                                             c.P_CAT_ITEM)
                    else:
                        self._record_message("You grabbed up a {}".format(message["item"].name), c.P_CAT_ITEM)
                else:
                    self._record_message("Grabbing up {} was too difficult for you".format(message["item"].name),
                                         c.P_CAT_ITEM)

            elif message["SUB_CATEGORY"] == c.AC_ITEM_DUMP:
                self._record_message("You carelessly dropped a {}".format(message["item"].name), c.P_CAT_ITEM)

            elif message["SUB_CATEGORY"] == c.AC_ITEM_USE:
                if message["result"] == c.FAILURE:
                    self._record_message("Unfortunately the {} cannot be used".format(message["item"].name),
                                         c.P_CAT_ITEM)
                elif message["result"] == c.SUCCESS:
                    self._record_message("{}".format(message["message"]),
                                         c.P_CAT_ITEM)

            elif message["SUB_CATEGORY"] == c.AC_ITEM_EQUIP:
                self._record_message("You successfully equipped a {} on {}".format(message["item"].name,
                                                                                   message["slot"]), c.P_CAT_ITEM)

            elif message["SUB_CATEGORY"] == c.AC_ITEM_UNEQUIP:
                self._record_message("You removed a {} from {}".format(message["item"].name,
                                                                       message["slot"]), c.P_CAT_ITEM)
            elif message["SUB_CATEGORY"] == c.AC_ITEM_IDENTIFY:
                if message["result"] == c.SUCCESS:
                    self._record_message("You successfully identified a {}".format(message["item"].name), c.P_CAT_ITEM)
                elif message["result"] == c.FAILURE:
                    self._record_message("You broke the object", c.P_CAT_ITEM)
            else:
                print("UNKNOWN MESSAGE: {}".format(message))

        elif message["MAIN_CATEGORY"] == c.P_CAT_ENV:

            if message["SUB_CATEGORY"] == c.AC_ENV_OPEN:
                if message["result"] == c.SUCCESS:
                    if "precision" in message:
                        self._record_message("{} opened {}; {}".format(message["operator"].name,
                                                                       message["object"].name,
                                                                       message["precision"]),
                                             c.P_CAT_ENV)
                    else:
                        self._record_message("{} opened {}".format(message["operator"].name, message["object"].name),
                                             c.P_CAT_ENV)
                else:
                    self._record_message("{} tried opening {} but failed".format(message["operator"].name,
                                                                                 message["object"].name),
                                         c.P_CAT_ENV)

            elif message["SUB_CATEGORY"] == c.AC_ENV_MOVE:

                if "room" in message and hasattr(message["room"], "name"):
                    self._record_message("{} entered {}".format(message["operator"].name, message["room"].name),
                                         c.P_CAT_ENV)

            elif message["SUB_CATEGORY"] == c.AC_QUEST:
                quest = message["quest"]
                if message["result"] == c.QUEST_SUBSCRIBED:
                    self._record_message("{} decided to {}".format(quest.quest_owner.name, quest.long_text),
                                         c.P_CAT_ENV)
                elif message["result"] == c.QUEST_UPDATED:
                    self._record_message("{} for {}".format(message["message"], quest.long_text),
                                         c.P_CAT_ENV)
                elif message["result"] == c.QUEST_FINISHED:
                    self._record_message("{} is done. LordCrocket grants {} {} experience points and {} wealth".format(
                        quest.long_text, message["rewards"]["target"].name, message["rewards"]["xp"],
                        message["rewards"]["wealth"]),
                        c.P_CAT_ENV)
                else:
                    print("UNKNOWN MESSAGE: {}".format(message))
            else:
                print("UNKNOWN MESSAGE: {}".format(message))
        else:
            print("UNKNOWN MESSAGE: {}".format(message))

    def resize(self, old_width, old_height, new_width, new_height):
        old_right = self.rect.right
        self.rect.y += new_height - old_height
        self.rect.width += new_width - old_width
        self.rect.centerx = int(new_width / 2)
        new_right = self.rect.right

        # Now we move the filter rectangles
        for key in self.filter_recs:
            self.filter_recs[key].right += new_right - old_right
            self.filter_recs[key].y += new_height - old_height
        self.delta = 0
        self.force_render = True


class ModalBox:
    def __init__(self, pos, text, choices, callbacks, callback_args):
        """
        A modal box, with a text and choices (typically a question and yes/no)
        Each choice will be presented as a button.
        Each choice needs to have a callback function
        :param pos:
        :param choices:
        :param callbacks:
        :param callback_args:
        :param text:
        """
        assert len(choices) == len(callbacks), "Choices are given without callbacks"
        self.pos = pos
        self.text = text
        self.choices = choices
        self.callbacks = callbacks
        self.callbacks_args = callback_args



class Input:
    """ A text input for pygame apps """
    def __init__(self, game, pos, font_name=st.FONT_NAME,
                 font_size=10,
                 limit_message=-1, focus=False, callback=None):
        self.game = game

        game_folder = path.dirname(__file__)
        font_folder = path.join(game_folder, st.FONT_FOLDER)
        font = pg.font.Font(path.join(font_folder, font_name), font_size)

        self.x, self.y = pos
        self.font = font
        self.color = (0, 0, 0)
        self.restricted = 'abcdefghijklmnopqrstuvwxyz' \
                          'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!"#$%&\\\'()*+,-./:;<=>?@[\]^_`{|}~'
        self.maxlength = limit_message
        self.prompt = '\'\''
        self.value = ''
        self.shifted = False
        self.pause = 0
        self.focus = focus
        self.callback = callback

    def set_pos(self, x, y):
        """ Set the position to x, y """
        self.x = x
        self.y = y

    def set_font(self, font):
        """ Set the font for the input """
        self.font = font

    def draw(self, surface):
        """ Draw the text input to a surface """
        text = self.font.render(self.prompt+self.value, 1, self.color)
        surface.blit(text, (self.x, self.y))

    def update(self, events):
        """ Update the input based on passed events """
        if self.focus is not True:
            return

        pressed = pg.key.get_pressed()  # Add ability to hold down delete key and delete text
        if self.pause == 3 and pressed[pg.K_BACKSPACE]:
            self.pause = 0
            self.value = self.value[:-1]
        elif pressed[pg.K_BACKSPACE]:
            self.pause += 1
        else:
            self.pause = 0

        for event in events:
            if event.type == pg.KEYUP:
                if event.key == pg.K_LSHIFT or event.key == pg.K_RSHIFT:
                    self.shifted = False
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_BACKSPACE:
                    self.value = self.value[:-1]
                elif event.key == pg.K_LSHIFT or event.key == pg.K_RSHIFT:
                    self.shifted = True
                elif event.key == pg.K_SPACE:
                    self.value += ' '
                elif event.key == pg.K_RETURN:
                    self.callback(self.value)  # return value
                if not self.shifted:
                    if event.key == pg.K_a and 'a' in self.restricted:
                        self.value += 'a'
                    elif event.key == pg.K_b and 'b' in self.restricted:
                        self.value += 'b'
                    elif event.key == pg.K_c and 'c' in self.restricted:
                        self.value += 'c'
                    elif event.key == pg.K_d and 'd' in self.restricted:
                        self.value += 'd'
                    elif event.key == pg.K_e and 'e' in self.restricted:
                        self.value += 'e'
                    elif event.key == pg.K_f and 'f' in self.restricted:
                        self.value += 'f'
                    elif event.key == pg.K_g and 'g' in self.restricted:
                        self.value += 'g'
                    elif event.key == pg.K_h and 'h' in self.restricted:
                        self.value += 'h'
                    elif event.key == pg.K_i and 'i' in self.restricted:
                        self.value += 'i'
                    elif event.key == pg.K_j and 'j' in self.restricted:
                        self.value += 'j'
                    elif event.key == pg.K_k and 'k' in self.restricted:
                        self.value += 'k'
                    elif event.key == pg.K_l and 'l' in self.restricted:
                        self.value += 'l'
                    elif event.key == pg.K_m and 'm' in self.restricted:
                        self.value += 'm'
                    elif event.key == pg.K_n and 'n' in self.restricted:
                        self.value += 'n'
                    elif event.key == pg.K_o and 'o' in self.restricted:
                        self.value += 'o'
                    elif event.key == pg.K_p and 'p' in self.restricted:
                        self.value += 'p'
                    elif event.key == pg.K_q and 'q' in self.restricted:
                        self.value += 'q'
                    elif event.key == pg.K_r and 'r' in self.restricted:
                        self.value += 'r'
                    elif event.key == pg.K_s and 's' in self.restricted:
                        self.value += 's'
                    elif event.key == pg.K_t and 't' in self.restricted:
                        self.value += 't'
                    elif event.key == pg.K_u and 'u' in self.restricted:
                        self.value += 'u'
                    elif event.key == pg.K_v and 'v' in self.restricted:
                        self.value += 'v'
                    elif event.key == pg.K_w and 'w' in self.restricted:
                        self.value += 'w'
                    elif event.key == pg.K_x and 'x' in self.restricted:
                        self.value += 'x'
                    elif event.key == pg.K_y and 'y' in self.restricted:
                        self.value += 'y'
                    elif event.key == pg.K_z and 'z' in self.restricted:
                        self.value += 'z'
                    elif event.key == pg.K_0 and '0' in self.restricted:
                        self.value += '0'
                    elif event.key == pg.K_1 and '1' in self.restricted:
                        self.value += '1'
                    elif event.key == pg.K_2 and '2' in self.restricted:
                        self.value += '2'
                    elif event.key == pg.K_3 and '3' in self.restricted:
                        self.value += '3'
                    elif event.key == pg.K_4 and '4' in self.restricted:
                        self.value += '4'
                    elif event.key == pg.K_5 and '5' in self.restricted:
                        self.value += '5'
                    elif event.key == pg.K_6 and '6' in self.restricted:
                        self.value += '6'
                    elif event.key == pg.K_7 and '7' in self.restricted:
                        self.value += '7'
                    elif event.key == pg.K_8 and '8' in self.restricted:
                        self.value += '8'
                    elif event.key == pg.K_9 and '9' in self.restricted:
                        self.value += '9'
                    elif event.key == pg.K_BACKQUOTE and '`' in self.restricted:
                        self.value += '`'
                    elif event.key == pg.K_MINUS and '-' in self.restricted:
                        self.value += '-'
                    elif event.key == pg.K_EQUALS and '=' in self.restricted:
                        self.value += '='
                    elif event.key == pg.K_LEFTBRACKET and '[' in self.restricted:
                        self.value += '['
                    elif event.key == pg.K_RIGHTBRACKET and ']' in self.restricted:
                        self.value += ']'
                    elif event.key == pg.K_BACKSLASH and '\\' in self.restricted:
                        self.value += '\\'
                    elif event.key == pg.K_SEMICOLON and ';' in self.restricted:
                        self.value += ';'
                    elif event.key == pg.K_QUOTE and '\'' in self.restricted:
                        self.value += '\''
                    elif event.key == pg.K_COMMA and ',' in self.restricted:
                        self.value += ','
                    elif event.key == pg.K_PERIOD and '.' in self.restricted:
                        self.value += '.'
                    elif event.key == pg.K_SLASH and '/' in self.restricted:
                        self.value += '/'
                elif self.shifted:
                    if event.key == pg.K_a and 'A' in self.restricted:
                        self.value += 'A'
                    elif event.key == pg.K_b and 'B' in self.restricted:
                        self.value += 'B'
                    elif event.key == pg.K_c and 'C' in self.restricted:
                        self.value += 'C'
                    elif event.key == pg.K_d and 'D' in self.restricted:
                        self.value += 'D'
                    elif event.key == pg.K_e and 'E' in self.restricted:
                        self.value += 'E'
                    elif event.key == pg.K_f and 'F' in self.restricted:
                        self.value += 'F'
                    elif event.key == pg.K_g and 'G' in self.restricted:
                        self.value += 'G'
                    elif event.key == pg.K_h and 'H' in self.restricted:
                        self.value += 'H'
                    elif event.key == pg.K_i and 'I' in self.restricted:
                        self.value += 'I'
                    elif event.key == pg.K_j and 'J' in self.restricted:
                        self.value += 'J'
                    elif event.key == pg.K_k and 'K' in self.restricted:
                        self.value += 'K'
                    elif event.key == pg.K_l and 'L' in self.restricted:
                        self.value += 'L'
                    elif event.key == pg.K_m and 'M' in self.restricted:
                        self.value += 'M'
                    elif event.key == pg.K_n and 'N' in self.restricted:
                        self.value += 'N'
                    elif event.key == pg.K_o and 'O' in self.restricted:
                        self.value += 'O'
                    elif event.key == pg.K_p and 'P' in self.restricted:
                        self.value += 'P'
                    elif event.key == pg.K_q and 'Q' in self.restricted:
                        self.value += 'Q'
                    elif event.key == pg.K_r and 'R' in self.restricted:
                        self.value += 'R'
                    elif event.key == pg.K_s and 'S' in self.restricted:
                        self.value += 'S'
                    elif event.key == pg.K_t and 'T' in self.restricted:
                        self.value += 'T'
                    elif event.key == pg.K_u and 'U' in self.restricted:
                        self.value += 'U'
                    elif event.key == pg.K_v and 'V' in self.restricted:
                        self.value += 'V'
                    elif event.key == pg.K_w and 'W' in self.restricted:
                        self.value += 'W'
                    elif event.key == pg.K_x and 'X' in self.restricted:
                        self.value += 'X'
                    elif event.key == pg.K_y and 'Y' in self.restricted:
                        self.value += 'Y'
                    elif event.key == pg.K_z and 'Z' in self.restricted:
                        self.value += 'Z'
                    elif event.key == pg.K_0 and ')' in self.restricted:
                        self.value += ')'
                    elif event.key == pg.K_1 and '!' in self.restricted:
                        self.value += '!'
                    elif event.key == pg.K_2 and '@' in self.restricted:
                        self.value += '@'
                    elif event.key == pg.K_3 and '#' in self.restricted:
                        self.value += '#'
                    elif event.key == pg.K_4 and '$' in self.restricted:
                        self.value += '$'
                    elif event.key == pg.K_5 and '%' in self.restricted:
                        self.value += '%'
                    elif event.key == pg.K_6 and '^' in self.restricted:
                        self.value += '^'
                    elif event.key == pg.K_7 and '&' in self.restricted:
                        self.value += '&'
                    elif event.key == pg.K_8 and '*' in self.restricted:
                        self.value += '*'
                    elif event.key == pg.K_9 and '(' in self.restricted:
                        self.value += '('
                    elif event.key == pg.K_BACKQUOTE and '~' in self.restricted:
                        self.value += '~'
                    elif event.key == pg.K_MINUS and '_' in self.restricted:
                        self.value += '_'
                    elif event.key == pg.K_EQUALS and '+' in self.restricted:
                        self.value += '+'
                    elif event.key == pg.K_LEFTBRACKET and '{' in self.restricted:
                        self.value += '{'
                    elif event.key == pg.K_RIGHTBRACKET and '}' in self.restricted:
                        self.value += '}'
                    elif event.key == pg.K_BACKSLASH and '|' in self.restricted:
                        self.value += '|'
                    elif event.key == pg.K_SEMICOLON and ':' in self.restricted:
                        self.value += ':'
                    elif event.key == pg.K_QUOTE and '"' in self.restricted:
                        self.value += '"'
                    elif event.key == pg.K_COMMA and '<' in self.restricted:
                        self.value += '<'
                    elif event.key == pg.K_PERIOD and '>' in self.restricted:
                        self.value += '>'
                    elif event.key == pg.K_SLASH and '?' in self.restricted:
                        self.value += '?'

            if len(self.value) > self.maxlength >= 0:
                self.value = self.value[:-1]

# Specialized class to load graphics


def load_image_list_all(image_src_list, folder, image_name,
                        width=st.TILESIZE_FILE, height=st.TILESIZE_FILE, adapt_ratio=1):
    """
    Load a set of consecutive image, to be used in animation. All images of files are read.
    :param image_src_list: the actual dictionary that may already contain the source
    :param folder:
    :param image_name:
    :param width:
    :param height:
    :param adapt_ratio: the ratio to match (1= align to TILESIZE_SCREEN, 0.5 = half of teh tilesize screen...)
    :return:
    """
    image_src = get_image(image_src_list, folder, image_name)
    number = int(image_src.get_width() / width)
    if width == height == st.TILESIZE_SCREEN * adapt_ratio:
        return [image_src.subsurface(pg.Rect(width * i, 0, width, height)) for i in range(number)]
    else:
        return [pg.transform.scale(image_src.subsurface(pg.Rect(width * i, 0, width, height)),
                                   (int(st.TILESIZE_SCREEN * adapt_ratio), int(st.TILESIZE_SCREEN * adapt_ratio)))
                for i in range(number)]


def load_image_list(image_src_list, folder, image_name, listing, width=st.TILESIZE_FILE, height=st.TILESIZE_FILE, adapt_ratio=1):
    """
    Load a set of consecutive image, to be used in animation. All images of files are read.
    :param image_src_list: the actual dictionary that may already contain the source
    :param folder:
    :param image_name:
    :param width:
    :param height:
    :param listing: the list of ref to be loaded, as (tile_x, tile_y) tuples
    :return:
    """
    image_src = get_image(image_src_list, folder, image_name)
    res = []
    for refs in listing:
        tile_x, tile_y = refs
        if width == height == st.TILESIZE_SCREEN * adapt_ratio:
            res.append(image_src.subsurface(pg.Rect(width * tile_x, height * tile_y, width, height)))
        else:
            res.append(pg.transform.scale(image_src.subsurface(pg.Rect(width * tile_x, height * tile_y, width, height)),
                                          (int(st.TILESIZE_SCREEN * adapt_ratio), int(st.TILESIZE_SCREEN * adapt_ratio))))
    return res


def load_image(image_src_list, folder, image_name, tile_x, tile_y, width=st.TILESIZE_FILE, height=st.TILESIZE_FILE, adapt_ratio=1):
    """
    Load a single image from a file and put it in the image dictionnary
    :param image_src_list: the image dictionnary that will be modified
    :param folder: the folder from which the image needs to be loaded
    :param image_name: the name of the file to be loaded
    :param tile_x: the position in the file of the sub part to be loaded (x)
    :param tile_y: the position in the file of the sub part to be loaded (y)
    :param width: the dimension of a tile
    :param height: th edimension of a tile
    :return:
    """
    image_src = get_image(image_src_list, folder, image_name)
    if adapt_ratio is None:
        return image_src.subsurface(pg.Rect(width * tile_x, height * tile_y, width, height))
    elif width == height == st.TILESIZE_SCREEN * adapt_ratio:
        return image_src.subsurface(pg.Rect(width * tile_x, height * tile_y, width, height))
    else:
        return pg.transform.scale(image_src.subsurface(pg.Rect(width * tile_x, height * tile_y, width, height)),
                                  (int(st.TILESIZE_SCREEN * adapt_ratio), int(st.TILESIZE_SCREEN * adapt_ratio)))


def load_image_list_dawnlike(image_src_list, folder, image_name1, image_name2, tile_x, tile_y,
                             width=st.TILESIZE_FILE, height=st.TILESIZE_FILE):
    """
    Load an image list from two different files following dawnlike approach
    :param image_src_list: the actual dictionary that may already contain the source
    :param img_folder_name: the folder where images are located
    :param image1: the first image file name
    :param image2: the second image file name
    :param tile_x: th etile position - note that
    :param tile_y:
    :param width:
    :param height:
    :return: a list of two images
    """
    image_src1 = get_image(image_src_list, folder, image_name1)
    image_src2 = get_image(image_src_list, folder, image_name2)

    if width == height == st.TILESIZE_SCREEN:
        return [image_src1.subsurface(pg.Rect(width * tile_x, height * tile_y, width, height)),
                image_src2.subsurface(pg.Rect(width * tile_x, height * tile_y, width, height))]
    else:
        return [pg.transform.scale(image_src1.subsurface(pg.Rect(width * tile_x, height * tile_y, width, height)),
                                   (st.TILESIZE_SCREEN, st.TILESIZE_SCREEN)),
                pg.transform.scale(image_src2.subsurface(pg.Rect(width * tile_x, height * tile_y, width, height)),
                                   (st.TILESIZE_SCREEN, st.TILESIZE_SCREEN))]


def load_wall_structure_dawnlike(image_src_list, folder, image_name):
    """
    Load the set of walls from dawnlike file
    :param image_src_list: the actual dictionary that may already contain the source
    :param image_src:
    :return: a list of dictionary item following convention
    http://www.angryfishstudios.com/2011/04/adventures-in-bitmasking/
    """
    image_src = get_image(image_src_list, folder, image_name)
    image_set = []
    ref_tuples = {0: (1, 1), 1: (1, 1),
                  2: (1, 0), 3: (0, 2),
                  4: (0, 1), 5: (0, 1),
                  6: (0, 0), 7: (3, 1),
                  8: (1, 0), 9: (2, 2),
                  10: (1, 0), 11: (4, 2),
                  12: (2, 0), 13: (5, 1),
                  14: (4, 0), 15: (4, 1)}
    for line in range(16):
        for column in range(2):
            top_x = column * (7 * 16)
            top_y = line * (3 * 16) + 3 * 16
            dict_image = {}
            for key in ref_tuples:
                delta_x = ref_tuples[key][0] * 16 + top_x
                delta_y = ref_tuples[key][1] * 16 + top_y
                dict_image[key] = pg.transform.scale(image_src.subsurface(pg.Rect(delta_x, delta_y, 16, 16)),
                                                     (st.TILESIZE_SCREEN, st.TILESIZE_SCREEN))
            image_set.append(dict_image)
    return image_set

def load_floor_structure_dawnlike(image_src_list, folder, image_name):
    """
    Load the set of walls from dawnlike file and put it in a dictionary
    :param image_src_list: the actual dictionary that may already contain the source
    :param folder: the folder from which the image will be loaded
    :param the name of teh image file
    :return: a list of dictionary item following convention
    http://www.angryfishstudios.com/2011/04/adventures-in-bitmasking/
    """
    image_src = get_image(image_src_list, folder, image_name)
    image_set = []
    ref_tuples = {0: (5, 0), 1: (3, 2),
                  2: (4, 1), 3: (0, 2),
                  4: (3, 0), 5: (3, 1),
                  6: (0, 0), 7: (0, 1),
                  8: (6, 1), 9: (2, 2),
                  10: (5, 1), 11: (1, 2),
                  12: (2, 0), 13: (2, 1),
                  14: (1, 0), 15: (1, 1)}
    for line in range(8):
        for column in range(3):
            top_x = column * (7 * 16)
            top_y = line * (3 * 16) + 3 * 16
            dict_image = {}
            for key in ref_tuples:
                delta_x = ref_tuples[key][0] * 16 + top_x
                delta_y = ref_tuples[key][1] * 16 + top_y
                dict_image[key] = pg.transform.scale(image_src.subsurface(pg.Rect(delta_x, delta_y, 16, 16)),
                                                     (st.TILESIZE_SCREEN, st.TILESIZE_SCREEN))
            image_set.append(dict_image)
    return image_set


def load_wall_structure_oryx(image_src_list, folder, image_name, width=24, height=24):
    """
    Load the set of walls from oryx file and put it in a dictionary
    Note that only the walls in the oryx mockup are taken. The list of walls is built according to the mockup: the
     first is the top left image (image with plants in walls), the second is the image just below (brownish).
     9 walls set are built that way.
    :param image_src_list: the actual dictionary that may aldready contain the source
    :param folder: the folder from which the image will be loaded
    :param the name of teh image file
    :return: a list of dictionary item following convention
    http://www.angryfishstudios.com/2011/04/adventures-in-bitmasking/
    in addition, the index 16 is the scrambled vertical wall, the 17 is the scrambled horizontal wall.
    """
    image_src = get_image(image_src_list, folder, image_name)
    image_set = []
    ref_tuples = {0: (10, 0), 1: (16, 0),
                  2: (11, 0), 3: (19, 0),
                  4: (14, 0), 5: (15, 0),
                  6: (17, 0), 7: (24, 0),
                  8: (13, 0), 9: (20, 0),
                  10: (12, 0), 11: (25, 0),
                  12: (18, 0), 13: (23, 0),
                  14: (22, 0), 15: (21, 0),
                  16: (26, 0), 17: (27, 0)}
    for line in (12, 4, 6, 18, 2, 7, 14, 13, 5):
        top_y = line * height + height
        dict_image = {}
        for key in ref_tuples:
            delta_x = ref_tuples[key][0] * width
            delta_y = ref_tuples[key][1] * height + top_y
            dict_image[key] = pg.transform.scale(image_src.subsurface(pg.Rect(delta_x, delta_y, width, height)),
                                                 (st.TILESIZE_SCREEN, st.TILESIZE_SCREEN))
        image_set.append(dict_image)
    return image_set



def load_floor_structure_oryx(image_src_list, folder, image_name, width=24, height=24):
    """
        Load the set of floors from oryx file and put it in a dictionary. Only the floors matching the walls are taken.
        :param image_src_list: the actual dictionary that may aldready contain the source
        :param folder: the folder from which the image will be loaded
        :param the name of teh image file
        :return: a list of dictionary item following convention
        Multiple tiles, each can be used (but the first one is used most). Each 4 tiles group matches with a wall set.
        """

    def _load_image(image_src, refs, width=24, height=24):
        res = []
        for ref in refs:
            x, y = ref
            res.append(pg.transform.scale(image_src.subsurface(pg.Rect(x * width, y * width, width, height)),
                                          (st.TILESIZE_SCREEN, st.TILESIZE_SCREEN)))
        return res

    image_src = get_image(image_src_list, folder, image_name)
    image_set = []

    # First column, first row
    image_set.append(_load_image(image_src,
                                 [(4, 13), (5, 13), (18, 26), (19, 26), (20, 26), (18, 27), (19, 27), (20, 27)],
                                 width=width, height=height))
    # First column, second row
    image_set.append(_load_image(image_src,
                                 [(14, 27), (13, 27), (12, 27), (14, 26), (13, 26), (12, 26)],
                                 width=width, height=height))
    # First column, third row
    image_set.append(_load_image(image_src,
                                 [(4, 7), (6, 7)],
                                 width=width, height=height))
    # First column, fourth row
    image_set.append(_load_image(image_src,
                                 [(4, 19), (5, 19), (6, 19), (7, 19), (7, 18)],
                                 width=width, height=height))
    # First column, fifth row
    image_set.append(_load_image(image_src,
                                 [(4, 15), (5, 15), (6, 15), (7, 15)],
                                 width=width, height=height))
    # Second column, first row
    image_set.append(_load_image(image_src,
                                 [(4, 8), (6, 8), (7, 8)],
                                 width=width, height=height))
    # Second column, second row
    image_set.append(_load_image(image_src,
                                 [(4, 13)],
                                 width=width, height=height))
    # Second column, third row
    image_set.append(_load_image(image_src,
                                 [(4, 4)],
                                 width=width, height=height))
    # Second column, fourth row
    image_set.append(_load_image(image_src,
                                 [(6, 6), (7, 6)],
                                 width=width, height=height))
    return image_set


def load_player_dawnlike(image_src_list, folder, image_name, width=st.TILESIZE_FILE, height=st.TILESIZE_FILE):
    result = {"S": [load_image(image_src_list, folder, image_name, i, 0, width=width, height=height) for i in range(4)],
              "W": [load_image(image_src_list, folder, image_name, i, 1, width=width, height=height) for i in range(4)],
              "E": [load_image(image_src_list, folder, image_name, i, 2, width=width, height=height) for i in range(4)],
              "N": [load_image(image_src_list, folder, image_name, i, 3, width=width, height=height) for i in range(4)]}
    return result


def load_creature_oryx(image_src_list, folder, image_name, ref_pos, width=st.TILESIZE_FILE, height=st.TILESIZE_FILE, adapt_ratio=1):
    west = load_image_list(image_src_list, folder, image_name, ref_pos, width=24, height=24, adapt_ratio=adapt_ratio)
    east = []
    for image in west:
        east.append(pg.transform.flip(image.copy(), True, False))
    result = {"S": east,
              "W": west,
              "E": east,
              "N": west}
    return result

def load_fx_oryx(image_src_list, folder, image_name, ref_pos, width=st.TILESIZE_FILE, height=st.TILESIZE_FILE, adapt_ratio=1):
    x, y = ref_pos
    result = {"S": (load_image(image_src_list, folder, image_name, x + 3, y, width=24, height=24, adapt_ratio=adapt_ratio),load_image(image_src_list, folder, image_name, x + 3, y, width=24, height=24, adapt_ratio=adapt_ratio)),
              "W": (load_image(image_src_list, folder, image_name, x + 2, y, width=24, height=24, adapt_ratio=adapt_ratio),load_image(image_src_list, folder, image_name, x + 2, y, width=24, height=24, adapt_ratio=adapt_ratio)),
              "E": (load_image(image_src_list, folder, image_name, x, y, width=24, height=24, adapt_ratio=adapt_ratio),load_image(image_src_list, folder, image_name, x, y, width=24, height=24, adapt_ratio=adapt_ratio)),
              "N": (load_image(image_src_list, folder, image_name, x + 1, y, width=24, height=24, adapt_ratio=adapt_ratio),load_image(image_src_list, folder, image_name, x + 1, y, width=24, height=24, adapt_ratio=adapt_ratio))}
    return result

def get_image(image_src_list, folder, image_name):
    key = str(folder) + image_name
    if key not in image_src_list:
        image_src_list[key] = pg.image.load(path.join(folder, image_name)).convert_alpha()
    return image_src_list[key]


def build_listing_dawnlike(image_root_folder):
    image_root_folder = path.join(image_root_folder, st.IMG_DAWNLIKE_SUB)
    character_folder = path.join(image_root_folder, "Characters")
    item_folder = path.join(image_root_folder, "Items")
    object_folder = path.join(image_root_folder, "Objects")
    player_folder = path.join(image_root_folder, "Player")

    image_src_list = {}  # a cache for objects
    images = {}  # the actual list of images to be built

    # Expected Keys:
    # PLAYER
    images["PLAYER"] = load_player_dawnlike(image_src_list, player_folder, "Warrior.png")
    # ENEMIES
    images["BABOON"] = load_image_list_dawnlike(image_src_list, character_folder, "Misc0.png", "Misc1.png", 2, 3)
    images["BADGER"] = load_image_list_dawnlike(image_src_list, character_folder, "Rodent0.png", "Rodent1.png", 2, 2)
    images["BAT"] = load_image_list_dawnlike(image_src_list, character_folder, "Avian0.png", "Avian1.png", 2, 11)
    images["DOG"] = load_image_list_dawnlike(image_src_list, character_folder, "Dog0.png", "Dog1.png", 0, 0)
    images["GIANT_ANT"] = load_image_list_dawnlike(image_src_list, character_folder, "Pest0.png", "Pest1.png", 0, 4)
    # NPC
    # ITEMS
    images["REMAINS"] = load_image_list_dawnlike(image_src_list, object_folder, "Decor0.png", "Decor1.png", 0, 12)
    images["POTION_R"] = load_image(image_src_list, item_folder, "Potion.png", 0, 0)
    # EQUIPMENT
    images["SWORD"] = load_image(image_src_list, item_folder, "MedWep.png", 3, 0)
    images["HELMET"] = load_image(image_src_list, item_folder, "Hat.png", 2, 1)
    images["CAPE"] = load_image(image_src_list, item_folder, "Armor.png", 7, 7)
    images["ARMOR"] = load_image(image_src_list, item_folder, "Armor.png", 0, 0)
    images["LEG"] = load_image(image_src_list, item_folder, "Armor.png", 5, 4)
    images["GLOVE"] = load_image(image_src_list, item_folder, "Glove.png", 1, 0)
    images["SHOES"] = load_image(image_src_list, item_folder, "Boot.png", 7, 0)
    images["SHIELD"] = load_image(image_src_list, item_folder, "Shield.png", 0, 0)
    images["BOW"] = load_image(image_src_list, item_folder, "Ammo.png", 0, 1)
    images["ARROW"] = load_image(image_src_list, item_folder, "Ammo.png", 5, 2)
    images["RING"] = load_image(image_src_list, item_folder, "Ring.png", 0, 0)
    images["NECKLACE"] = load_image(image_src_list, item_folder, "Tool.png", 1, 2)
    # OTHER
    images["WALLS"] = load_wall_structure_dawnlike(image_src_list, object_folder, "Wall.png")
    images["CANDLE_SIMPLE"] = load_image_list_dawnlike(image_src_list, object_folder, "Decor0.png", "Decor1.png", 0, 9)
    images["CANDLE_DOUBLE"] = load_image_list_dawnlike(image_src_list, object_folder, "Decor0.png", "Decor1.png", 1, 9)
    images["FLOOR"] = load_floor_structure_dawnlike(image_src_list, object_folder, "Floor.png")
    # images["FLOOR_EXT"] = [load_image(image_src_list, object_folder, "Floor.png", 1, y) for y in (4, 7, 10)] -> Not used
    images["DOOR_V_OPEN"] = load_image(image_src_list, object_folder, "Door1.png", 1, 0)
    images["DOOR_V_CLOSED"] = load_image(image_src_list, object_folder, "Door0.png", 1, 0)
    images["DOOR_H_OPEN"] = load_image(image_src_list, object_folder, "Door1.png", 0, 0)
    images["DOOR_H_CLOSED"] = load_image(image_src_list, object_folder, "Door0.png", 0, 0)
    images["STAIRS"] = load_image(image_src_list, object_folder, "Tile.png", 1, 1)
    images["FIREBALL"] = load_image_list_dawnlike(image_src_list, object_folder, "Effect0.png", "Effect1.png", 1, 24)
    images["SPECIAL_EFFECT"] = load_image_list_dawnlike(image_src_list, object_folder, "Effect0.png", "Effect1.png", 1, 22)

    # "PLAYER": {
    #     "E": load_image_list(IMG_FOLDER, 'HeroEast.png'),
    #     "W": load_image_list(IMG_FOLDER, 'HeroWest.png'),
    #     "N": load_image_list(IMG_FOLDER, 'HeroNorth.png'),
    #     "S": load_image_list(IMG_FOLDER, 'HeroSouth.png')},
    # # ENEMIES
    # "BAT": load_image_list(IMG_FOLDER, 'BatA.png'),
    # "BEARD": load_image_list(IMG_FOLDER, 'BeardA.png'),
    # "MONKEY": load_image_list_dawnlike(IMG_FOLDER, "Misc0.png", "Misc1.png", 2, 3),
    # # NPC
    # "DOG": load_image_list(IMG_FOLDER, 'DogA.png'),
    # # ITEMS
    # "REMAINS": load_image(IMG_FOLDER, item_image_src, 44, 2),
    # "POTION_R": load_image(IMG_FOLDER, item_image_src, 1, 1),
    # # EQUIPMENT
    # "SWORD": load_image(IMG_FOLDER, item_image_src, 1, 16),
    # "HELMET": load_image(IMG_FOLDER, item_image_src, 13, 16),
    # "CAPE": load_image(IMG_FOLDER, item_image_src, 27, 17),
    # "ARMOR": load_image(IMG_FOLDER, item_image_src, 14, 16),
    # "LEG": load_image(IMG_FOLDER, item_image_src, 15, 16),
    # "GLOVE": load_image(IMG_FOLDER, item_image_src, 16, 16),
    # "SHOES": load_image(IMG_FOLDER, item_image_src, 17, 16),
    # "SHIELD": load_image(IMG_FOLDER, item_image_src, 11, 13),
    # "BOW": load_image(IMG_FOLDER, item_image_src, 11, 17),
    # "ARROW": load_image(IMG_FOLDER, item_image_src, 21, 17),
    # "RING": load_image(IMG_FOLDER, item_image_src, 1, 4),
    # "NECKLACE": load_image(IMG_FOLDER, item_image_src, 1, 5),
    # #
    # "WALLS": load_wall_structure_dawnlike(wall_image_src),
    # "FLOOR": [[load_image(IMG_FOLDER, level_image_src, x, y) for x in range(4)] for y in range(15)],
    # "FLOOR_EXT": [[load_image(IMG_FOLDER, level_image_src, x, y) for x in range(4, 6)] for y in range(15)],
    # "DOOR_V_OPEN": load_image(IMG_FOLDER, level_image_src, 15, 2),
    # "DOOR_H_OPEN": load_image(IMG_FOLDER, level_image_src, 16, 2),
    # "DOOR_CLOSED": load_image(IMG_FOLDER, level_image_src, 14, 2),
    # "STAIRS": load_image(IMG_FOLDER, level_image_src, 13, 0),
    # "FIREBALL": load_image(IMG_FOLDER, level_image_src, 42, 27),
    # "SPECIAL_EFFECT": [load_image(IMG_FOLDER, level_image_src, x, 21) for x in range(4)]
    return images


def build_listing_icons(img_root, image_dict):
    img_root = path.join(img_root, st.IMG_ICONS)
    image_dict["ICON_EQUIP"] = load_image({}, img_root, "equip.png", 0, 0, width=32, height=32, adapt_ratio=None)
    image_dict["ICON_UNEQUIP"] = load_image({}, img_root, "unequip.png", 0, 0, width=32, height=32, adapt_ratio=None)
    image_dict["ICON_USE"] = load_image({}, img_root, "use.png", 0, 0, width=32, height=32, adapt_ratio=None)
    image_dict["ICON_DROP"] = load_image({}, img_root, "drop.png", 0, 0, width=32, height=32, adapt_ratio=None)
    image_dict["ICON_MORE"] = load_image({}, img_root, "more.png", 0, 0, width=32, height=32, adapt_ratio=None)
    image_dict["ICON_IDENTIFY"] = load_image({}, img_root, "identify.png", 0, 0, width=32, height=32, adapt_ratio=None)


def build_listing_oryx(img_root):

    def _t(x, y):
        return [(x, y), (x, y + 1)]

    img_root = path.join(img_root, st.IMG_ORYX_SUB)

    image_src_list = {}  # a cache for objects
    images = {}  # the actual list of images to be built


    # PLAYER
    images["PLAYER"] = load_creature_oryx(image_src_list, img_root, "oryx_16bit_fantasy_creatures_trans.png", [(1, 1), (1, 2)], width=24, height=24, adapt_ratio=0.9)

    # CREATURES
    img_creature = "oryx_16bit_fantasy_creatures_trans.png"

    images["KNIGHT_M"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(1, 1), width=24, height=24)
    images["THIEF_M"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(2, 1), width=24, height=24)
    images["RANGER_M"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(3, 1), width=24, height=24)
    images["WIZARD_M"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(4, 1), width=24, height=24)
    images["PRIEST_M"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(5, 1), width=24, height=24)
    images["SHAMAN_M"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(6, 1), width=24, height=24)
    images["BERSERKER_M"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(7, 1), width=24, height=24)
    images["SWORDSMAN_M"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(8, 1), width=24, height=24)
    images["PALADIN_M"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(9, 1), width=24, height=24)
    images["KNIGHT_F"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(10, 1), width=24, height=24)
    images["THIEF_F"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(11, 1), width=24, height=24)
    images["RANGER_F"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(12, 1), width=24, height=24)
    images["WIZARD_F"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(13, 1), width=24, height=24)
    images["PRIEST_F"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(14, 1), width=24, height=24)
    images["SHAMAN_F"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(15, 1), width=24, height=24)
    images["BERSERKER_F"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(16, 1), width=24, height=24)
    images["SWORDSMAN_F"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(17, 1), width=24, height=24)
    images["PALADIN_F"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(18, 1), width=24, height=24)

    images["BANDIT"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(1, 3), width=24, height=24)
    images["HOODED_HUMAN"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(2, 3), width=24, height=24)
    images["HUMAN_M"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(3, 3), width=24, height=24)
    images["HUMAN_F"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(4, 3), width=24, height=24)
    images["MERCHANT"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(5, 3), width=24, height=24)
    images["BUTCHER"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(6, 3), width=24, height=24)
    images["CHEF"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(7, 3), width=24, height=24)
    images["BISHOP"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(8, 3), width=24, height=24)
    images["KING"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(9, 3), width=24, height=24)
    images["QUEEN"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(10, 3), width=24, height=24)
    images["PRINCE"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(11, 3), width=24, height=24)
    images["PRINCESS"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(12, 3), width=24, height=24)
    images["GUARD_M"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(13, 3), width=24, height=24)
    images["GUARD_F"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(14, 3), width=24, height=24)
    images["KNIGHT"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(15, 3), width=24, height=24)
    images["GUARD_ALT_M"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(16, 3), width=24, height=24)
    images["GUARD_ALT_F"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(17, 3), width=24, height=24)
    images["KNIGHT_ALT"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(18, 3), width=24, height=24)

    images["BANDIT_2"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(1, 5), width=24, height=24)
    images["HOODED_HUMAN_2"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(2, 5), width=24, height=24)
    images["HUMAN_M_2"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(3, 5), width=24, height=24)
    images["HUMAN_F_2"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(4, 5), width=24, height=24)
    images["MERCHANT_2"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(5, 5), width=24, height=24)
    images["SLAVE_2"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(6, 5), width=24, height=24)
    images["ALCHEMIST_2"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(7, 5), width=24, height=24)
    images["PROPHET_2"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(8, 5), width=24, height=24)
    images["KING_2"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(9, 5), width=24, height=24)
    images["QUEEN_2"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(10, 5), width=24, height=24)
    images["PRINCE_2"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(11, 5), width=24, height=24)
    images["PRINCESS_2"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(12, 5), width=24, height=24)
    images["GUARD_M_2"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(13, 5), width=24, height=24)
    images["GUARD_F_2"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(14, 5), width=24, height=24)
    images["KNIGHT_2"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(15, 5), width=24, height=24)
    images["GUARD_ALT_M_2"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(16, 5), width=24, height=24)
    images["GUARD_ALT_F_2"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(17, 5), width=24, height=24)
    images["KNIGHT_ALT_2"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(18, 5), width=24, height=24)

    images["ASSASSIN"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(1, 7), width=24, height=24)
    images["BANDIT_3"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(2, 7), width=24, height=24)
    images["DWARF"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(3, 7), width=24, height=24)
    images["DWARF_ALT"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(4, 7), width=24, height=24)
    images["DWARF_PRIEST"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(5, 7), width=24, height=24)
    images["DROW_ASSASSIN"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(6, 7), width=24, height=24)
    images["DROW_FIGHTER"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(7, 7), width=24, height=24)
    images["DROW_RANGER"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(8, 7), width=24, height=24)
    images["DROW_MAGE"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(9, 7), width=24, height=24)
    images["DROW_SORCERESS"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(10, 7), width=24, height=24)
    images["HIGH_ELF_FIGHTER_M"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(11, 7), width=24, height=24)
    images["HIGH_ELF_SHIELD_FIGHTER_M"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(12, 7), width=24, height=24)
    images["HIGH_ELF_RANGER_M"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(13, 7), width=24, height=24)
    images["HIGH_ELF_MAGE_M"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(14, 7), width=24, height=24)
    images["HIGH_ELF_FIGHTER_F"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(15, 7), width=24, height=24)
    images["HIGH_ELF_SHIELD_FIGHTER_F"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(16, 7), width=24, height=24)
    images["HIGH_ELF_RANGER_F"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(17, 7), width=24, height=24)
    images["HIGH_ELF_MAGE_F"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(18, 7), width=24, height=24)

    images["WOOD_ELF_FIGHTER_M"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(1, 9), width=24, height=24)
    images["WOOD_ELF_SHIELD_FIGHTER_M"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(2, 9), width=24, height=24)
    images["WOOD_ELF_RANGER_M"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(3, 9), width=24, height=24)
    images["WOOD_ELF_DRUID_M"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(4, 9), width=24, height=24)
    images["WOOD_ELF_FIGHTER_F"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(5, 9), width=24, height=24)
    images["WOOD_ELF_SHIELD_FIGHTER_F"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(6, 9), width=24, height=24)
    images["WOOD_ELF_RANGER_F"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(7, 9), width=24, height=24)
    images["WOOD_ELF_DRUID_F"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(8, 9), width=24, height=24)
    images["LIZARDMAN_WARRIOR"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(9, 9), width=24, height=24)
    images["LIZARDMAN_ARCHER"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(10, 9), width=24, height=24)
    images["LIZARDMAN_CAPTAIN"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(11, 9), width=24, height=24)
    images["LIZARDMAN_SHAMAN"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(12, 9), width=24, height=24)
    images["LIZARDMAN_HIGH_SHAMAN"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(13, 9), width=24, height=24)
    images["GNOME_FIGHTER"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(14, 9), width=24, height=24)
    images["GNOME_FIGHTER_2"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(15, 9), width=24, height=24)
    images["GNOME_FIGHTER_3"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(16, 9), width=24, height=24)
    images["GNOME_WIZARD"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(17, 9), width=24, height=24)
    images["GNOME_WIZARD_ALT"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(18, 9), width=24, height=24)

    images["GNOLL_FIGHTER"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(1, 11), width=24, height=24)
    images["GNOLL_FIGHTER_ALT"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(2, 11), width=24, height=24)
    images["GNOLL_FIGHTER_CAPTAIN"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(3, 11), width=24, height=24)
    images["GNOLL_SHAMAN"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(4, 11), width=24, height=24)
    images["MINOTAUR_AXE"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(5, 11), width=24, height=24)
    images["MINOTAUR_CLUB"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(6, 11), width=24, height=24)
    images["MINOTAUR_ALT"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(7, 11), width=24, height=24)
    images["ELDER_DEMON"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(8, 11), width=24, height=24)
    images["FIRE_DEMON"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(9, 11), width=24, height=24)
    images["HORNED_DEMON"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(10, 11), width=24, height=24)
    images["STONE_GOLEM"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(11, 11), width=24, height=24)
    images["MUD_GOLEM"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(12, 11), width=24, height=24)
    images["FLESH_GOLEM"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(13, 11), width=24, height=24)
    images["LAVA_GOLEM"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(14, 11), width=24, height=24)
    images["BONE_GOLEM"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(15, 11), width=24, height=24)
    images["DJINN"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(16, 11), width=24, height=24)
    images["TREANT"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(17, 11), width=24, height=24)
    images["MIMIC"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(18, 11), width=24, height=24)

    images["PURPLE_SLIME"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(1, 13), width=24, height=24)
    images["GREEN_SLIME"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(2, 13), width=24, height=24)
    images["BLACK_BAT"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(3, 13), width=24, height=24)
    images["RED_BAT"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(4, 13), width=24, height=24)
    images["BEHOLDER"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(5, 13), width=24, height=24)
    images["RED_SPIDER"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(6, 13), width=24, height=24)
    images["BLACK_SPIDER"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(7, 13), width=24, height=24)
    images["GREY_RAT"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(8, 13), width=24, height=24)
    images["BROWN_RAT"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(9, 13), width=24, height=24)
    images["COBRA"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(10, 13), width=24, height=24)
    images["BEETLE"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(11, 13), width=24, height=24)
    images["FIRE_BEETLE"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(12, 13), width=24, height=24)
    images["GREY_WOLF"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(13, 13), width=24, height=24)
    images["BROWN_WOLF"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(14, 13), width=24, height=24)
    images["BLACK_WOLF"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(15, 13), width=24, height=24)
    images["PIGEON"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(16, 13), width=24, height=24)
    images["BLUE_BIRD"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(17, 13), width=24, height=24)
    images["RAVEN"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(18, 13), width=24, height=24)

    images["GOBLIN_FIGHTER"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(1, 15), width=24, height=24)
    images["GOBLIN_ARCHER"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(2, 15), width=24, height=24)
    images["GOBLIN_CAPTAIN"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(3, 15), width=24, height=24)
    images["GOBLIN_KING"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(4, 15), width=24, height=24)
    images["GOBLIN_MYSTIC"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(5, 15), width=24, height=24)
    images["ORC_FIGHTER"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(6, 15), width=24, height=24)
    images["ORC_CAPTAIN"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(7, 15), width=24, height=24)
    images["ORC_MYSTIC"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(8, 15), width=24, height=24)
    images["TROLL"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(9, 15), width=24, height=24)
    images["TROLL_CAPTAIN"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(10, 15), width=24, height=24)
    images["CYCLOPS"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(11, 15), width=24, height=24)
    images["CYCLOPS_ALT"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(12, 15), width=24, height=24)
    images["DEATH_KNIGHT"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(13, 15), width=24, height=24)
    images["DEATH_KNIGHT_ALT"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(14, 15), width=24, height=24)
    images["DEATH_KNIGHT_ALT_2"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(15, 15), width=24, height=24)
    images["EARTH_ELEMENTAL"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(16, 15), width=24, height=24)
    images["WATER_ELEMENTAL"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(17, 15), width=24, height=24)
    images["AIR_ELEMENTAL"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(18, 15), width=24, height=24)

    images["ZOMBIE"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(1, 17), width=24, height=24)
    images["HEADLESS_ZOMBIE"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(2, 17), width=24, height=24)
    images["SKELETON"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(3, 17), width=24, height=24)
    images["SKELETON_ARCHER"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(4, 17), width=24, height=24)
    images["SKELETON_WARRIOR"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(5, 17), width=24, height=24)
    images["SHADOW"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(6, 17), width=24, height=24)
    images["GHOST"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(7, 17), width=24, height=24)
    images["MUMMY"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(8, 17), width=24, height=24)
    images["PHAROAH"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(9, 17), width=24, height=24)
    images["NECROMANCER"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(10, 17), width=24, height=24)
    images["DARK_WIZARD"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(11, 17), width=24, height=24)
    images["DEATH"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(12, 17), width=24, height=24)
    images["VAMPIRE"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(13, 17), width=24, height=24)
    images["VAMPIRE_ALT"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(14, 17), width=24, height=24)
    images["VAMPIRE_LORD"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(15, 17), width=24, height=24)
    images["WITCH"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(16, 17), width=24, height=24)
    images["FROST_WITCH"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(17, 17), width=24, height=24)
    images["GREEN_WITCH"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(18, 17), width=24, height=24)

    images["RED_DRAGON"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(1, 17), width=24, height=24)
    images["PURPLE_DRAGON"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(2, 17), width=24, height=24)
    images["GOLD_DRAGON"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(3, 17), width=24, height=24)
    images["GREEN_DRAGON"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(4, 17), width=24, height=24)
    images["YETI"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(5, 17), width=24, height=24)
    images["YETI_ALT"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(6, 17), width=24, height=24)
    images["GIANT_LEECH"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(7, 17), width=24, height=24)
    images["GIANT_WORM"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(8, 17), width=24, height=24)
    images["BROWN_BEAR"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(9, 17), width=24, height=24)
    images["GREY_BEAR"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(10, 17), width=24, height=24)
    images["POLAR_BEAR"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(11, 17), width=24, height=24)
    images["GIANT_SCORPION"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(12, 17), width=24, height=24)
    images["SCORPION_ALT"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(13, 17), width=24, height=24)
    images["SCORPION_ALT_2"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(14, 17), width=24, height=24)
    images["ETTIN"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(15, 17), width=24, height=24)
    images["ETTIN_ALT"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(16, 17), width=24, height=24)
    images["FAIRY"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(17, 17), width=24, height=24)
    images["DEVIL"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(18, 17), width=24, height=24)

    images["WISP"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(1, 19), width=24, height=24)
    images["WISP_ALT"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(2, 19), width=24, height=24)
    images["TURNIP"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(3, 19), width=24, height=24)
    images["ROTTEN_TURNIP"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(4, 19), width=24, height=24)
    images["FIRE_MINION"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(5, 19), width=24, height=24)
    images["ICE_MINION"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(6, 19), width=24, height=24)
    images["SMOKE_MINION"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(7, 19), width=24, height=24)
    images["MUD_MINION"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(8, 19), width=24, height=24)
    images["EYE"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(9, 19), width=24, height=24)
    images["EYES"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(10, 19), width=24, height=24)
    images["RED_SPECTER"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(11, 19), width=24, height=24)
    images["BLUE_SPECTER"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(12, 19), width=24, height=24)
    images["BROWN_SPECTER"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(13, 19), width=24, height=24)
    images["BLUE_JELLY"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(14, 19), width=24, height=24)
    images["GREEN_JELLY"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(15, 19), width=24, height=24)
    images["RED_JELLY"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(16, 19), width=24, height=24)
    images["FLAME"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(17, 19), width=24, height=24)
    images["COLD_FLAME"] = load_creature_oryx(image_src_list, img_root, img_creature, _t(18, 19), width=24, height=24)

    images["BAT"] = load_creature_oryx(image_src_list, img_root, "oryx_16bit_fantasy_creatures_trans.png", [(3, 13), (3, 14)], width=24, height=24)
    images["DOG"] = load_creature_oryx(image_src_list, img_root, "oryx_16bit_fantasy_creatures_trans.png", [(14, 13), (14, 14)], width=24, height=24)

    # ITEMS
    ratio_item = 16 / 24

    images["REMAINS"] = load_image(image_src_list, img_root, "oryx_16bit_fantasy_items_trans.png", 1, 7,
                                   width=16, height=16, adapt_ratio=ratio_item)
    images["POTION_B_S"] = load_image(image_src_list, img_root, "oryx_16bit_fantasy_items_trans.png", 1, 1, width=16,
                                      height=16, adapt_ratio=ratio_item)
    images["POTION_P_S"] = load_image(image_src_list, img_root, "oryx_16bit_fantasy_items_trans.png", 2, 1, width=16,
                                      height=16, adapt_ratio=ratio_item)
    images["POTION_R_S"] = load_image(image_src_list, img_root, "oryx_16bit_fantasy_items_trans.png", 3, 1, width=16,
                                      height=16, adapt_ratio=ratio_item)
    images["POTION_G_S"] = load_image(image_src_list, img_root, "oryx_16bit_fantasy_items_trans.png", 4, 1, width=16,
                                      height=16, adapt_ratio=ratio_item)
    images["POTION_Y_S"] = load_image(image_src_list, img_root, "oryx_16bit_fantasy_items_trans.png", 5, 1, width=16,
                                      height=16, adapt_ratio=ratio_item)
    images["POTION_W_S"] = load_image(image_src_list, img_root, "oryx_16bit_fantasy_items_trans.png", 6, 1, width=16,
                                      height=16, adapt_ratio=ratio_item)
    images["POTION_B_N"] = load_image(image_src_list, img_root, "oryx_16bit_fantasy_items_trans.png", 7, 1, width=16,
                                      height=16, adapt_ratio=ratio_item)
    images["POTION_P_N"] = load_image(image_src_list, img_root, "oryx_16bit_fantasy_items_trans.png", 8, 1, width=16,
                                      height=16, adapt_ratio=ratio_item)
    images["POTION_R_N"] = load_image(image_src_list, img_root, "oryx_16bit_fantasy_items_trans.png", 9, 1, width=16,
                                      height=16, adapt_ratio=ratio_item)
    images["POTION_G_N"] = load_image(image_src_list, img_root, "oryx_16bit_fantasy_items_trans.png", 10, 1, width=16,
                                      height=16, adapt_ratio=ratio_item)
    images["POTION_Y_N"] = load_image(image_src_list, img_root, "oryx_16bit_fantasy_items_trans.png", 11, 1, width=16,
                                      height=16, adapt_ratio=ratio_item)
    images["POTION_W_N"] = load_image(image_src_list, img_root, "oryx_16bit_fantasy_items_trans.png", 12, 1, width=16,
                                      height=16, adapt_ratio=ratio_item)
    images["POTION_B_L"] = load_image(image_src_list, img_root, "oryx_16bit_fantasy_items_trans.png", 13, 1, width=16,
                                      height=16, adapt_ratio=ratio_item)
    images["POTION_P_L"] = load_image(image_src_list, img_root, "oryx_16bit_fantasy_items_trans.png", 14, 1, width=16,
                                      height=16, adapt_ratio=ratio_item)
    images["POTION_R_L"] = load_image(image_src_list, img_root, "oryx_16bit_fantasy_items_trans.png", 15, 1, width=16,
                                      height=16, adapt_ratio=ratio_item)
    images["POTION_G_L"] = load_image(image_src_list, img_root, "oryx_16bit_fantasy_items_trans.png", 16, 1, width=16,
                                      height=16, adapt_ratio=ratio_item)
    images["POTION_Y_L"] = load_image(image_src_list, img_root, "oryx_16bit_fantasy_items_trans.png", 17, 1, width=16,
                                      height=16, adapt_ratio=ratio_item)
    images["POTION_W_L"] = load_image(image_src_list, img_root, "oryx_16bit_fantasy_items_trans.png", 18, 1, width=16,
                                      height=16, adapt_ratio=ratio_item)

    # FX
    images["FIREBALL"] = load_fx_oryx(image_src_list, img_root, "oryx_16bit_fantasy_fx_trans.png", (1, 12), width=24, height=24)

    # EQUIPMENT
    images["SWORD"] = load_image(image_src_list, img_root, "oryx_16bit_fantasy_items_trans.png", 13, 10, width=16, height=16, adapt_ratio=ratio_item)
    images["HELMET"] = load_image(image_src_list, img_root, "oryx_16bit_fantasy_items_trans.png", 15, 13, width=16, height=16, adapt_ratio=ratio_item)
    images["CAPE"] = load_image(image_src_list, img_root, "oryx_16bit_fantasy_items_trans.png", 2, 12, width=16, height=16, adapt_ratio=ratio_item)
    images["ARMOR"] = load_image(image_src_list, img_root, "oryx_16bit_fantasy_items_trans.png", 2, 13, width=16, height=16, adapt_ratio=ratio_item)
    images["LEG"] = load_image(image_src_list, img_root, "oryx_16bit_fantasy_items_trans.png", 15, 14, width=16, height=16, adapt_ratio=ratio_item)
    images["GLOVE"] = load_image(image_src_list, img_root, "oryx_16bit_fantasy_items_trans.png", 17, 12, width=16, height=16, adapt_ratio=ratio_item)
    images["SHOES"] = load_image(image_src_list, img_root, "oryx_16bit_fantasy_items_trans.png", 6, 14, width=16, height=16, adapt_ratio=ratio_item)
    images["SHIELD"] = load_image(image_src_list, img_root, "oryx_16bit_fantasy_items_trans.png", 3, 11, width=16, height=16, adapt_ratio=ratio_item)
    images["BOW"] = load_image(image_src_list, img_root, "oryx_16bit_fantasy_items_trans.png", 17, 9, width=16, height=16, adapt_ratio=ratio_item)
    images["ARROW"] = load_image(image_src_list, img_root, "oryx_16bit_fantasy_items_trans.png", 1, 8, width=16, height=16, adapt_ratio=ratio_item)
    images["RING"] = load_image(image_src_list, img_root, "oryx_16bit_fantasy_items_trans.png", 10, 4, width=16, height=16, adapt_ratio=ratio_item)
    images["NECKLACE"] = load_image(image_src_list, img_root, "oryx_16bit_fantasy_items_trans.png", 1, 2, width=16, height=16, adapt_ratio=ratio_item)

    # OTHER - Not all are based on series of walls
    images["WALLS"] = load_wall_structure_oryx(image_src_list, img_root, "oryx_16bit_fantasy_world_trans.png")
    images["FLOOR"] = load_floor_structure_oryx(image_src_list, img_root, "oryx_16bit_fantasy_world_trans.png")
    images["DOOR_V_CLOSED_LIST"] = [
        load_image(image_src_list, img_root, "oryx_16bit_fantasy_world_trans.png", 29, 3, width=24, height=24),
        load_image(image_src_list, img_root, "oryx_16bit_fantasy_world_trans.png", 29, 3, width=24, height=24),
        load_image(image_src_list, img_root, "oryx_16bit_fantasy_world_trans.png", 38, 3, width=24, height=24),
        load_image(image_src_list, img_root, "oryx_16bit_fantasy_world_trans.png", 36, 3, width=24, height=24),
        load_image(image_src_list, img_root, "oryx_16bit_fantasy_world_trans.png", 29, 4, width=24, height=24),
        load_image(image_src_list, img_root, "oryx_16bit_fantasy_world_trans.png", 36, 3, width=24, height=24),
        load_image(image_src_list, img_root, "oryx_16bit_fantasy_world_trans.png", 29, 4, width=24, height=24),
        load_image(image_src_list, img_root, "oryx_16bit_fantasy_world_trans.png", 29, 3, width=24, height=24),
        load_image(image_src_list, img_root, "oryx_16bit_fantasy_world_trans.png", 29, 4, width=24, height=24),
    ]
    images["DOOR_H_CLOSED_LIST"] = images["DOOR_V_CLOSED_LIST"]
    images["DOOR_V_OPEN_LIST"] = [
        load_image(image_src_list, img_root, "oryx_16bit_fantasy_world_trans.png", 30, 3, width=24, height=24),
        load_image(image_src_list, img_root, "oryx_16bit_fantasy_world_trans.png", 30, 3, width=24, height=24),
        load_image(image_src_list, img_root, "oryx_16bit_fantasy_world_trans.png", 39, 3, width=24, height=24),
        load_image(image_src_list, img_root, "oryx_16bit_fantasy_world_trans.png", 37, 3, width=24, height=24),
        load_image(image_src_list, img_root, "oryx_16bit_fantasy_world_trans.png", 30, 4, width=24, height=24),
        load_image(image_src_list, img_root, "oryx_16bit_fantasy_world_trans.png", 37, 3, width=24, height=24),
        load_image(image_src_list, img_root, "oryx_16bit_fantasy_world_trans.png", 30, 4, width=24, height=24),
        load_image(image_src_list, img_root, "oryx_16bit_fantasy_world_trans.png", 30, 3, width=24, height=24),
        load_image(image_src_list, img_root, "oryx_16bit_fantasy_world_trans.png", 30, 4, width=24, height=24),
    ]
    images["DOOR_H_OPEN_LIST"] = images["DOOR_V_OPEN_LIST"]
    images["STAIRS_LIST"] = load_image_list(image_src_list, img_root,
                                            "oryx_16bit_fantasy_world_trans.png",
                                            [(9, 13), (9, 5), (9, 7), (9, 19), (9, 3), (9, 8), (9, 15), (9, 14), (9, 6)],
                                            width=24, height=24)
    images["FLOOR_DECO_LIST"] = [
        load_image(image_src_list, img_root, "oryx_16bit_fantasy_world_trans.png", 32, 1, width=24, height=24),
        load_image(image_src_list, img_root, "oryx_16bit_fantasy_world_trans.png", 33, 1, width=24, height=24),
        load_image(image_src_list, img_root, "oryx_16bit_fantasy_world_trans.png", 34, 1, width=24, height=24),
        load_image(image_src_list, img_root, "oryx_16bit_fantasy_world_trans.png", 35, 1, width=24, height=24),
        load_image(image_src_list, img_root, "oryx_16bit_fantasy_world_trans.png", 36, 1, width=24, height=24),
        load_image(image_src_list, img_root, "oryx_16bit_fantasy_world_trans.png", 37, 1, width=24, height=24),
        load_image(image_src_list, img_root, "oryx_16bit_fantasy_world_trans.png", 38, 1, width=24, height=24)
    ]
    # CHESTS AND OTHER OPENABLE OBJECTS
    images["CHEST_CLOSED"] = load_image(image_src_list, img_root, "oryx_16bit_fantasy_world_trans.png", 32, 4, width=24, height=24)
    images["CHEST_OPEN_GOLD"] = load_image(image_src_list, img_root, "oryx_16bit_fantasy_world_trans.png", 33, 4, width=24, height=24)
    images["CHEST_OPEN_TRAP"] = load_image(image_src_list, img_root, "oryx_16bit_fantasy_world_trans.png", 34, 4, width=24, height=24)
    images["CHEST_OPEN_EMPTY"] = load_image(image_src_list, img_root, "oryx_16bit_fantasy_world_trans.png", 35, 4, width=24, height=24)
    images["COFFIN_CLOSED"] = load_image(image_src_list, img_root, "oryx_16bit_fantasy_world_trans.png", 36, 4, width=24, height=24)
    images["COFFIN_OPEN"] = load_image(image_src_list, img_root, "oryx_16bit_fantasy_world_trans.png", 38, 4, width=24, height=24)
    images["BARREL_CLOSED"] = load_image(image_src_list, img_root, "oryx_16bit_fantasy_world_trans.png", 39, 4, width=24, height=24)
    images["BARREL_OPEN"] = load_image(image_src_list, img_root, "oryx_16bit_fantasy_world_trans.png", 40, 4, width=24, height=24)
    # ORYX SPECIFIC
    images["WALLS_SHADOW"] = load_image(image_src_list, img_root, "oryx_16bit_fantasy_world_trans.png", 30, 37, width=24, height=24)
    images["SPIDER_WEB_TOP_LEFT"] = load_image(image_src_list, img_root, "oryx_16bit_fantasy_world_trans.png", 29, 2, width=24, height=24)
    images["SPIDER_WEB_TOP_RIGHT"] = load_image(image_src_list, img_root, "oryx_16bit_fantasy_world_trans.png", 30, 2, width=24, height=24)
    images["SPIDER_WEB_BOTTOM_LEFT"] = load_image(image_src_list, img_root, "oryx_16bit_fantasy_world_trans.png", 32, 2, width=24, height=24)
    images["SPIDER_WEB_BOTTOM_RIGHT"] = load_image(image_src_list, img_root, "oryx_16bit_fantasy_world_trans.png", 31, 2, width=24, height=24)

    return images
