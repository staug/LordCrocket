import pygame as pg
import settings as st
from os import path
from ktextsurfacewriter import KTextSurfaceWriter
import constants as c

"""
Sub utilities routines.
"""


class TextBox:
    """
    Handle a Textbox on the screen.
    Use the add property to add message, and a text property to set a text.
    """
    def __init__(self,
                 game,
                 rect=pg.Rect(0, st.GAME_WIDTH-st.TEXT_PART_HEIGHT, st.TEXT_PART_WIDTH, st.TEXT_PART_HEIGHT),
                 font_name=st.FONT_NAME,
                 font_size=10,
                 limit_message=8):

        game_folder = path.dirname(__file__)
        font_folder = path.join(game_folder, st.FONT_FOLDER)
        font = pg.font.Font(path.join(font_folder, font_name), font_size)

        self.game = game
        self.game.bus.register(self)
        self.game.bus.register(self, main_category=c.PUBLISHER_CAT_LOG, function_to_call=self.notify2)
        self._ktext = KTextSurfaceWriter(rect, font=font, color=st.WHITE)
        self._text = ""
        self.message = []
        self.limit_message = limit_message
        self.delta = 0

        self.drag_drop_text_box = False
        self.old_mouse_x, self.old_mouse_y = 0, 0

    def _set_text(self, text):
        self.message = [text]
        self.delta = 0
        self._ktext.text = text
    text = property(lambda self: self._text, _set_text, doc="""The text to be displayed""")

    def _add_text(self, text):
        self.message.append("[{}] {}".format(self.game.ticker.ticks, text))
        self.delta = 0
        message = ""
        for mes in self.message[-self.limit_message:]:
            message += mes + "\n"
        self._ktext.text = message
    add = property(lambda self: self._text, _add_text, doc="""The text to be added""")

    def scroll(self, deltav):
        self.delta += deltav
        if self.delta > 0:
            self.delta = 0
        if self.delta < -len(self.message) + self.limit_message:
            self.delta = -len(self.message) + self.limit_message
        message = ""
        for mes in self.message[-self.limit_message + self.delta:len(self.message) + self.delta]:
            message += mes + "\n"
        self._ktext.text = message

    def draw(self, surface):
        self._ktext.draw(surface)

    def notify(self, message):
        print(message)

    def notify2(self, message):
        print("{} in notify2".format(message))

    def resize(self, old_screen_width, old_screen_height, new_screen_width, new_screen_height):
        new_rect_width = int(self._ktext.rect.width * new_screen_width / old_screen_width)
        new_rect_height = int(self._ktext.rect.height * new_screen_height / old_screen_height)

        self._ktext.rect.width = new_rect_width
        self._ktext.rect.height = new_rect_height


class Input:
    """ A text input for pygame apps """
    def __init__(self, game, pos, font_name=st.FONT_NAME, 
                 font_size=10,
                 limit_message=-1, focus=False):
        self.game = game
        
        game_folder = path.dirname(__file__)
        font_folder = path.join(game_folder, st.FONT_FOLDER)
        font = pg.font.Font(path.join(font_folder, font_name), font_size)
        
        self.x, self.y = pos
        self.font = font
        self.color = (0,0,0)
        self.restricted = 'abcdefghijklmnopqrstuvwxyz' \
                          'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!"#$%&\\\'()*+,-./:;<=>?@[\]^_`{|}~'
        self.maxlength = limit_message
        self.prompt = '\'\''; 
        self.value = ''
        self.shifted = False
        self.pause = 0
        self.focus = focus

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
        if self.focus != True:
            return

        pressed = pg.key.get_pressed()#Add ability to hold down delete key and delete text
        if self.pause == 3 and pressed[pg.K_BACKSPACE]:
            self.pause = 0
            self.value = self.value[:-1]
        elif pressed[pg.K_BACKSPACE]:
            self.pause += 1
        else:
            self.pause = 0

        for event in events:
            if event.type == pg.KEYUP:
                if event.key == pg.K_LSHIFT or event.key == pg.K_RSHIFT: self.shifted = False
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_BACKSPACE: self.value = self.value[:-1]
                elif event.key == pg.K_LSHIFT or event.key == pg.K_RSHIFT: self.shifted = True
                elif event.key == pg.K_SPACE: self.value += ' '
                elif event.key == pg.K_RETURN: return self.value#return value
                if not self.shifted:
                    if event.key == pg.K_a and 'a' in self.restricted: self.value += 'a'
                    elif event.key == pg.K_b and 'b' in self.restricted: self.value += 'b'
                    elif event.key == pg.K_c and 'c' in self.restricted: self.value += 'c'
                    elif event.key == pg.K_d and 'd' in self.restricted: self.value += 'd'
                    elif event.key == pg.K_e and 'e' in self.restricted: self.value += 'e'
                    elif event.key == pg.K_f and 'f' in self.restricted: self.value += 'f'
                    elif event.key == pg.K_g and 'g' in self.restricted: self.value += 'g'
                    elif event.key == pg.K_h and 'h' in self.restricted: self.value += 'h'
                    elif event.key == pg.K_i and 'i' in self.restricted: self.value += 'i'
                    elif event.key == pg.K_j and 'j' in self.restricted: self.value += 'j'
                    elif event.key == pg.K_k and 'k' in self.restricted: self.value += 'k'
                    elif event.key == pg.K_l and 'l' in self.restricted: self.value += 'l'
                    elif event.key == pg.K_m and 'm' in self.restricted: self.value += 'm'
                    elif event.key == pg.K_n and 'n' in self.restricted: self.value += 'n'
                    elif event.key == pg.K_o and 'o' in self.restricted: self.value += 'o'
                    elif event.key == pg.K_p and 'p' in self.restricted: self.value += 'p'
                    elif event.key == pg.K_q and 'q' in self.restricted: self.value += 'q'
                    elif event.key == pg.K_r and 'r' in self.restricted: self.value += 'r'
                    elif event.key == pg.K_s and 's' in self.restricted: self.value += 's'
                    elif event.key == pg.K_t and 't' in self.restricted: self.value += 't'
                    elif event.key == pg.K_u and 'u' in self.restricted: self.value += 'u'
                    elif event.key == pg.K_v and 'v' in self.restricted: self.value += 'v'
                    elif event.key == pg.K_w and 'w' in self.restricted: self.value += 'w'
                    elif event.key == pg.K_x and 'x' in self.restricted: self.value += 'x'
                    elif event.key == pg.K_y and 'y' in self.restricted: self.value += 'y'
                    elif event.key == pg.K_z and 'z' in self.restricted: self.value += 'z'
                    elif event.key == pg.K_0 and '0' in self.restricted: self.value += '0'
                    elif event.key == pg.K_1 and '1' in self.restricted: self.value += '1'
                    elif event.key == pg.K_2 and '2' in self.restricted: self.value += '2'
                    elif event.key == pg.K_3 and '3' in self.restricted: self.value += '3'
                    elif event.key == pg.K_4 and '4' in self.restricted: self.value += '4'
                    elif event.key == pg.K_5 and '5' in self.restricted: self.value += '5'
                    elif event.key == pg.K_6 and '6' in self.restricted: self.value += '6'
                    elif event.key == pg.K_7 and '7' in self.restricted: self.value += '7'
                    elif event.key == pg.K_8 and '8' in self.restricted: self.value += '8'
                    elif event.key == pg.K_9 and '9' in self.restricted: self.value += '9'
                    elif event.key == pg.K_BACKQUOTE and '`' in self.restricted: self.value += '`'
                    elif event.key == pg.K_MINUS and '-' in self.restricted: self.value += '-'
                    elif event.key == pg.K_EQUALS and '=' in self.restricted: self.value += '='
                    elif event.key == pg.K_LEFTBRACKET and '[' in self.restricted: self.value += '['
                    elif event.key == pg.K_RIGHTBRACKET and ']' in self.restricted: self.value += ']'
                    elif event.key == pg.K_BACKSLASH and '\\' in self.restricted: self.value += '\\'
                    elif event.key == pg.K_SEMICOLON and ';' in self.restricted: self.value += ';'
                    elif event.key == pg.K_QUOTE and '\'' in self.restricted: self.value += '\''
                    elif event.key == pg.K_COMMA and ',' in self.restricted: self.value += ','
                    elif event.key == pg.K_PERIOD and '.' in self.restricted: self.value += '.'
                    elif event.key == pg.K_SLASH and '/' in self.restricted: self.value += '/'
                elif self.shifted:
                    if event.key == pg.K_a and 'A' in self.restricted: self.value += 'A'
                    elif event.key == pg.K_b and 'B' in self.restricted: self.value += 'B'
                    elif event.key == pg.K_c and 'C' in self.restricted: self.value += 'C'
                    elif event.key == pg.K_d and 'D' in self.restricted: self.value += 'D'
                    elif event.key == pg.K_e and 'E' in self.restricted: self.value += 'E'
                    elif event.key == pg.K_f and 'F' in self.restricted: self.value += 'F'
                    elif event.key == pg.K_g and 'G' in self.restricted: self.value += 'G'
                    elif event.key == pg.K_h and 'H' in self.restricted: self.value += 'H'
                    elif event.key == pg.K_i and 'I' in self.restricted: self.value += 'I'
                    elif event.key == pg.K_j and 'J' in self.restricted: self.value += 'J'
                    elif event.key == pg.K_k and 'K' in self.restricted: self.value += 'K'
                    elif event.key == pg.K_l and 'L' in self.restricted: self.value += 'L'
                    elif event.key == pg.K_m and 'M' in self.restricted: self.value += 'M'
                    elif event.key == pg.K_n and 'N' in self.restricted: self.value += 'N'
                    elif event.key == pg.K_o and 'O' in self.restricted: self.value += 'O'
                    elif event.key == pg.K_p and 'P' in self.restricted: self.value += 'P'
                    elif event.key == pg.K_q and 'Q' in self.restricted: self.value += 'Q'
                    elif event.key == pg.K_r and 'R' in self.restricted: self.value += 'R'
                    elif event.key == pg.K_s and 'S' in self.restricted: self.value += 'S'
                    elif event.key == pg.K_t and 'T' in self.restricted: self.value += 'T'
                    elif event.key == pg.K_u and 'U' in self.restricted: self.value += 'U'
                    elif event.key == pg.K_v and 'V' in self.restricted: self.value += 'V'
                    elif event.key == pg.K_w and 'W' in self.restricted: self.value += 'W'
                    elif event.key == pg.K_x and 'X' in self.restricted: self.value += 'X'
                    elif event.key == pg.K_y and 'Y' in self.restricted: self.value += 'Y'
                    elif event.key == pg.K_z and 'Z' in self.restricted: self.value += 'Z'
                    elif event.key == pg.K_0 and ')' in self.restricted: self.value += ')'
                    elif event.key == pg.K_1 and '!' in self.restricted: self.value += '!'
                    elif event.key == pg.K_2 and '@' in self.restricted: self.value += '@'
                    elif event.key == pg.K_3 and '#' in self.restricted: self.value += '#'
                    elif event.key == pg.K_4 and '$' in self.restricted: self.value += '$'
                    elif event.key == pg.K_5 and '%' in self.restricted: self.value += '%'
                    elif event.key == pg.K_6 and '^' in self.restricted: self.value += '^'
                    elif event.key == pg.K_7 and '&' in self.restricted: self.value += '&'
                    elif event.key == pg.K_8 and '*' in self.restricted: self.value += '*'
                    elif event.key == pg.K_9 and '(' in self.restricted: self.value += '('
                    elif event.key == pg.K_BACKQUOTE and '~' in self.restricted: self.value += '~'
                    elif event.key == pg.K_MINUS and '_' in self.restricted: self.value += '_'
                    elif event.key == pg.K_EQUALS and '+' in self.restricted: self.value += '+'
                    elif event.key == pg.K_LEFTBRACKET and '{' in self.restricted: self.value += '{'
                    elif event.key == pg.K_RIGHTBRACKET and '}' in self.restricted: self.value += '}'
                    elif event.key == pg.K_BACKSLASH and '|' in self.restricted: self.value += '|'
                    elif event.key == pg.K_SEMICOLON and ':' in self.restricted: self.value += ':'
                    elif event.key == pg.K_QUOTE and '"' in self.restricted: self.value += '"'
                    elif event.key == pg.K_COMMA and '<' in self.restricted: self.value += '<'
                    elif event.key == pg.K_PERIOD and '>' in self.restricted: self.value += '>'
                    elif event.key == pg.K_SLASH and '?' in self.restricted: self.value += '?'

            if len(self.value) > self.maxlength >= 0: self.value = self.value[:-1]

def load_image_list(img_folder_name, filename, width=st.TILESIZE_FILE, height=st.TILESIZE_FILE):
    """
    Load a set of consecutive image, to be used in animation. All images of files are read.
    :param img_folder_name:
    :param filename:
    :param width:
    :param height:
    :return:
    """
    game_folder = path.dirname(__file__)
    image_folder = path.join(game_folder, img_folder_name)
    image_src = pg.image.load(path.join(image_folder, filename)).convert_alpha()
    number = int(image_src.get_width() / width)
    if width == height == st.TILESIZE_SCREEN:
        return [image_src.subsurface(pg.Rect(width * i, 0, width, height)) for i in range(number)]
    else:
        return [pg.transform.scale(image_src.subsurface(pg.Rect(width * i, 0, width, height)),
                                       (st.TILESIZE_SCREEN, st.TILESIZE_SCREEN)) for i in range(number)]


def load_image(img_folder_name, image, tile_x, tile_y, width=st.TILESIZE_FILE, height=st.TILESIZE_FILE):
    """
    Load a single image from a file
    :param img_folder_name:
    :param image:
    :param tile_x:
    :param tile_y:
    :param width:
    :param height:
    :return:
    """
    image_src = image
    if not (type(image) is pg.Surface):
        game_folder = path.dirname(__file__)
        image_folder = path.join(game_folder, img_folder_name)
        image_src = pg.image.load(path.join(image_folder, image)).convert_alpha()
    if width == height == st.TILESIZE_SCREEN:
        return image_src.subsurface(pg.Rect(width * tile_x, height * tile_y, width, height))
    else:
        return pg.transform.scale(image_src.subsurface(pg.Rect(width * tile_x, height * tile_y, width, height)),
                                      (st.TILESIZE_SCREEN, st.TILESIZE_SCREEN))


def load_wall_structure_dawnlike(image_src):
    """
    Load the set of walls from dawnlike file
    :param image_src:
    :return: a list of dictionary item following convention
    http://www.angryfishstudios.com/2011/04/adventures-in-bitmasking/
    """
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
