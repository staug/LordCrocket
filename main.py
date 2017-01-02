import sys
from os import path

import dill as pick
import pygame as pg
from ktextsurfacewriter import KTextSurfaceWriter

import constants as c
import random as rd
from entities import MonsterHelper, EquipmentHelper, ItemHelper, DoorHelper, ThrowableHelper, NPCHelper
from player import PlayerHelper
from settings import *
from tilemap import MapFactory, Camera, FieldOfView, Minimap
from utilities import Ticker, Publisher
from utilities_ui import TextBox, load_image, load_image_list, load_wall_structure_dawnlike, load_image_list_dawnlike


class Screen:

    def __init__(self, game, default_back_state):
        self.game = game
        self.default_back_state = default_back_state

    def events(self):
        print("NOT IMPLEMENTED")

    def update(self):
        print("NOT IMPLEMENTED")

    def draw(self):
        print("NOT IMPLEMENTED")


class InventoryScreen(Screen):

    def __init__(self, game, default_back_state):
        Screen.__init__(self, game, default_back_state)
        self.original_pos = (32, 32)
        self.tile_size = 48
        self.objects_per_line = 5

    def events(self):
        # catch all events here
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.game.quit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.game.game_state = self.default_back_state
            if event.type == pg.MOUSEBUTTONDOWN:
                (button1, button2, button3) = pg.mouse.get_pressed()
                (x, y) = pg.mouse.get_pos()
                # Test where the mouse is..
                tile_size = self.tile_size
                orig_x = self.original_pos[0]
                top_x, top_y = orig_x, self.original_pos[1]

                index_x = int((x - top_x) / tile_size)
                index_y = int((y - top_y) / tile_size)

                has_equipable = len(self.game.player.get_unequipped_objects()) > 0
                has_usable = len(self.game.player.get_non_equipment_objects()) > 0

                start_index_y_equipable = 6
                end_index_y_equipable = start_index_y_equipable + int(len(self.game.player.get_unequipped_objects()) / self.objects_per_line)

                start_index_y_usable = end_index_y_equipable + 3
                if not has_equipable:
                    start_index_y_usable = 6
                end_index_y_usable = start_index_y_usable + int(len(self.game.player.get_non_equipment_objects()) / self.objects_per_line)

                if 0 <= index_x < 4 and 0 <= index_y < 5:
                    self.handle_equipped_event((button1, button2, button3), index_x, index_y)
                elif has_equipable \
                        and 0 <= index_x < self.objects_per_line \
                        and start_index_y_equipable <= index_y <= end_index_y_equipable \
                        and len(self.game.player.get_unequipped_objects()) > (index_y-start_index_y_equipable)*self.objects_per_line+index_x:
                    self.handle_equipable_event((button1, button2, button3), index_x, index_y - start_index_y_equipable)
                # Usable, but not equipment
                elif has_usable \
                        and 0 <= index_x < self.objects_per_line \
                        and start_index_y_usable <= index_y <= end_index_y_usable \
                        and len(self.game.player.get_non_equipment_objects()) > (index_y - start_index_y_usable) * self.objects_per_line + index_x:
                    self.handle_usable_event((button1, button2, button3), index_x, index_y - start_index_y_usable)

    def handle_equipable_event(self, buttons, index_x, index_y):
        listing = self.game.player.get_unequipped_objects()
        (button1, button2, button3) = buttons
        if button1:
            print(listing[index_y * self.objects_per_line + index_x].name)
        else:
            listing[index_y * self.objects_per_line + index_x].equipment.equip()

    def handle_usable_event(self, buttons, index_x, index_y):
        listing = self.game.player.get_non_equipment_objects()
        (button1, button2, button3) = buttons
        if button1:
            print(listing[index_y * self.objects_per_line + index_x].name)
        else:
            listing[index_y * self.objects_per_line + index_x].item.use()

    def handle_equipped_event(self, buttons, index_x, index_y):
        slots = [c.SLOT_RING, c.SLOT_HEAD, c.SLOT_CAPE,
                 c.SLOT_NECKLACE,
                 c.SLOT_HAND_RIGHT, c.SLOT_TORSO, c.SLOT_HAND_LEFT,
                 c.SLOT_BOW,
                 c.SLOT_GLOVE, c.SLOT_LEG, c.SLOT_QUIVER, "NOTHING",
                 "NOTHING", c.SLOT_FOOT, "NOTHING", "NOTHING"]
        game_object = self.game.player.get_equipped_object_at(slots[index_y * 4 + index_x])
        if game_object is not None:
            (button1, button2, button3) = buttons
            if button1:
                print(game_object.name)
            else:
                game_object.equipment.dequip()

    def draw(self):
        # Erase All
        self.game.screen.fill(BGCOLOR)

        tile_size = self.tile_size
        orig_x = self.original_pos[0]
        top_x, top_y = orig_x, self.original_pos[1]

        # First part: Ring - Head - Cape - Necklace
        ring = self.game.player.get_equipped_object_at(c.SLOT_RING)
        if ring:
            self.game.screen.blit(pg.transform.scale(ring.image, (tile_size, tile_size)), (top_x, top_y))
        pg.draw.rect(self.game.screen, WHITE, pg.Rect((top_x, top_y), (tile_size, tile_size)), 2)
        top_x += tile_size
        head = self.game.player.get_equipped_object_at(c.SLOT_HEAD)
        if head:
            self.game.screen.blit(pg.transform.scale(head.image, (tile_size, tile_size)), (top_x, top_y))
        pg.draw.rect(self.game.screen, WHITE, pg.Rect((top_x, top_y), (tile_size, tile_size)), 2)
        top_x += tile_size
        cape = self.game.player.get_equipped_object_at(c.SLOT_CAPE)
        if cape:
            self.game.screen.blit(pg.transform.scale(cape.image, (tile_size, tile_size)), (top_x, top_y))
        pg.draw.rect(self.game.screen, WHITE, pg.Rect((top_x, top_y), (tile_size, tile_size)), 2)
        top_x += tile_size
        necklace = self.game.player.get_equipped_object_at(c.SLOT_NECKLACE)
        if necklace:
            self.game.screen.blit(pg.transform.scale(necklace.image, (tile_size, tile_size)), (top_x, top_y))
        pg.draw.rect(self.game.screen, WHITE, pg.Rect((top_x, top_y), (tile_size, tile_size)), 2)

        # Second part: right_hand - Torso - left_hand - Bow
        top_y += tile_size
        top_x = orig_x
        right_hand = self.game.player.get_equipped_object_at(c.SLOT_HAND_RIGHT)
        if right_hand:
            self.game.screen.blit(pg.transform.scale(right_hand.image, (tile_size, tile_size)), (top_x, top_y))
        pg.draw.rect(self.game.screen, WHITE, pg.Rect((top_x, top_y), (tile_size, tile_size)), 2)
        top_x += tile_size
        torso = self.game.player.get_equipped_object_at(c.SLOT_TORSO)
        if torso:
            self.game.screen.blit(pg.transform.scale(torso.image, (tile_size, tile_size)), (top_x, top_y))
        pg.draw.rect(self.game.screen, WHITE, pg.Rect((top_x, top_y), (tile_size, tile_size)), 2)
        top_x += tile_size
        left_hand = self.game.player.get_equipped_object_at(c.SLOT_HAND_LEFT)
        if left_hand:
            self.game.screen.blit(pg.transform.scale(left_hand.image, (tile_size, tile_size)), (top_x, top_y))
        pg.draw.rect(self.game.screen, WHITE, pg.Rect((top_x, top_y), (tile_size, tile_size)), 2)
        top_x += tile_size
        bow = self.game.player.get_equipped_object_at(c.SLOT_BOW)
        if bow:
            self.game.screen.blit(pg.transform.scale(bow.image, (tile_size, tile_size)), (top_x, top_y))
        pg.draw.rect(self.game.screen, WHITE, pg.Rect((top_x, top_y), (tile_size, tile_size)), 2)

        # Third part: Glove - Leg - Quiver - NOTHING
        top_y += tile_size
        top_x = orig_x
        glove = self.game.player.get_equipped_object_at(c.SLOT_GLOVE)
        if glove:
            self.game.screen.blit(pg.transform.scale(glove.image, (tile_size, tile_size)), (top_x, top_y))
        pg.draw.rect(self.game.screen, WHITE, pg.Rect((top_x, top_y), (tile_size, tile_size)), 2)
        top_x += tile_size
        leg = self.game.player.get_equipped_object_at(c.SLOT_LEG)
        if leg:
            self.game.screen.blit(pg.transform.scale(leg.image, (tile_size, tile_size)), (top_x, top_y))
        pg.draw.rect(self.game.screen, WHITE, pg.Rect((top_x, top_y), (tile_size, tile_size)), 2)
        top_x += tile_size
        quiver = self.game.player.get_equipped_object_at(c.SLOT_QUIVER)
        if quiver:
            self.game.screen.blit(pg.transform.scale(quiver.image, (tile_size, tile_size)), (top_x, top_y))
        pg.draw.rect(self.game.screen, WHITE, pg.Rect((top_x, top_y), (tile_size, tile_size)), 2)

        # Fourth part: NOTHING - Shoes - NOTHING - NOTHING
        top_y += tile_size
        top_x = orig_x + tile_size
        shoes = self.game.player.get_equipped_object_at(c.SLOT_FOOT)
        if shoes:
            self.game.screen.blit(pg.transform.scale(shoes.image, (tile_size, tile_size)), (top_x, top_y))
        pg.draw.rect(self.game.screen, WHITE, pg.Rect((top_x, top_y), (tile_size, tile_size)), 2)

        # Now all the equiment that is not equipped
        if len(self.game.player.get_unequipped_objects()) > 0:
            top_y += 3*tile_size
            top_x = orig_x
            for index, item in enumerate(self.game.player.get_unequipped_objects()):
                self.game.screen.blit(pg.transform.scale(item.image, (tile_size, tile_size)), (top_x, top_y))
                pg.draw.rect(self.game.screen, WHITE, pg.Rect((top_x, top_y), (tile_size, tile_size)), 2)
                if (index + 1) % self.objects_per_line == 0:
                    top_x = orig_x
                    top_y += tile_size
                else:
                    top_x += tile_size

        # Now all the objects that are not equipment
        if len(self.game.player.get_non_equipment_objects()) > 0:
            top_y += 3*tile_size
            top_x = orig_x
            for index, item in enumerate(self.game.player.get_non_equipment_objects()):
                self.game.screen.blit(pg.transform.scale(item.image, (tile_size, tile_size)), (top_x, top_y))
                pg.draw.rect(self.game.screen, WHITE, pg.Rect((top_x, top_y), (tile_size, tile_size)), 2)
                if (index + 1) % self.objects_per_line == 0:
                    top_x = orig_x
                    top_y += tile_size
                else:
                    top_x += tile_size

        pg.display.flip()

    def update(self):
        pass


class MapScreen(Screen):

    def __init__(self, game, default_back_state):
        Screen.__init__(self, game, default_back_state)
        game_folder = path.dirname(__file__)
        font_folder = path.join(game_folder, FONT_FOLDER)
        self.font = pg.font.Font(path.join(font_folder, FONT_NAME), 12)

    def events(self):

        # catch all events here
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.game.quit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.game.game_state = self.default_back_state

    def draw(self):
        # Erase All
        self.game.screen.fill(BGCOLOR)

        map_image = self.game.minimap.build_background(zoom_factor=4)
        self.game.screen.blit(map_image, (10, 10))

        text = self.font.render(self.game.map.name, 1, WHITE)
        pos_x = int((self.game.screen.get_width() - text.get_width()) / 2)
        self.game.screen.blit(text, (pos_x, self.game.screen.get_height() - 40))

        pg.display.flip()

    def update(self):
        pass


class CharacterScreen(Screen):

    def __init__(self, game, default_back_state):
        Screen.__init__(self, game, default_back_state)
        game_folder = path.dirname(__file__)
        font_folder = path.join(game_folder, FONT_FOLDER)
        self.font = pg.font.Font(path.join(font_folder, FONT_NAME), 12)
        self.writer_part = KTextSurfaceWriter(self.game.screen.get_rect(), font=self.font)

    def build_player_text(self):
        return ("{}\n\n"
                "STR={}\nDEX={}\nMIND={}\nCHA={}\n\n"
                "HP={}/{}\nBP={}/{}\nAC={}\nvision={}".format(self.game.player.name, self.game.player.strength,
                                                              self.game.player.dexterity, self.game.player.mind,
                                                              self.game.player.charisma,
                                                              self.game.player.fighter.hit_points,
                                                              self.game.player.base_hit_points,
                                                              self.game.player.fighter.body_points,
                                                              self.game.player.base_body_points,
                                                              self.game.player.fighter.armor_class,
                                                              self.game.player.vision
                                                              ))

    def events(self):

        # catch all events here
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.game.quit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.game.game_state = self.default_back_state

    def draw(self):
        # Erase All
        self.game.screen.fill(BGCOLOR)
        self.writer_part.text = self.build_player_text()
        self.writer_part.draw(self.game.screen)

        pg.display.flip()

    def update(self):
        pass


class PlayingScreen(Screen):

    def __init__(self, game, default_back_state):
        Screen.__init__(self, game, default_back_state)
        self.fog_of_war_mask = None

    def draw_health_bar(self, surf, x, y):
        BAR_HEIGHT = 20
        fighter = self.game.player.fighter
        if fighter is not None:
            BAR_WIDTH_HP = 100
            BAR_WIDTH_BP = int(fighter.owner.base_body_points * BAR_WIDTH_HP / fighter.owner.base_hit_points)

            pct_hp = fighter.hit_points / fighter.owner.base_hit_points

            outline_rect_hp = pg.Rect(x + BAR_WIDTH_BP, y, BAR_WIDTH_HP, BAR_HEIGHT)
            fill_rect_hp = pg.Rect(x + BAR_WIDTH_BP, y, pct_hp * BAR_WIDTH_HP, BAR_HEIGHT)
            col = GREEN
            if 0.3 <= pct_hp < 0.6:
                col = YELLOW
            if 0 <= pct_hp < 0.3:
                col = RED

            pg.draw.rect(surf, col, fill_rect_hp)
            pg.draw.rect(surf, WHITE, outline_rect_hp, 2)

            pct_bp = fighter.body_points / fighter.owner.base_body_points
            outline_rect_bp = pg.Rect(x, y, BAR_WIDTH_BP, BAR_HEIGHT)
            fill_rect_bp = pg.Rect(x, y, pct_bp * BAR_WIDTH_BP, BAR_HEIGHT)
            pg.draw.rect(surf, GREEN, fill_rect_bp)
            pg.draw.rect(surf, WHITE, outline_rect_bp, 2)

    def draw(self):
        # Erase All
        self.game.screen.fill(BGCOLOR)

        # Background
        self.game.screen.blit(self.game.map.background,
                              self.game.camera.apply_rect(pg.Rect(0, 0,
                                                                  self.game.map.background.get_width(),
                                                                  self.game.map.background.get_height())))
        # Sprites
        for group in self.game.all_groups:
            for sprite in group:
                self.game.screen.blit(sprite.image, self.game.camera.apply(sprite))

        # FOW
        if self.game.player.invalidate_fog_of_war:

            self.fog_of_war_mask = pg.Surface((self.game.screen.get_rect().width,
                                               self.game.screen.get_rect().height), pg.SRCALPHA, 32)

            black = pg.Surface((TILESIZE_SCREEN, TILESIZE_SCREEN))
            black.fill(BGCOLOR)
            gray = pg.Surface((TILESIZE_SCREEN, TILESIZE_SCREEN), pg.SRCALPHA, 32)
            gray.fill((0, 0, 0, 120))
            for x in range(self.game.map.tile_width):
                for y in range(self.game.map.tile_height):
                    if not self.game.visible_player_array[x][y]:
                        if self.game.map.tiles[x][y].explored:
                            self.fog_of_war_mask.blit(gray, self.game.camera.apply_rect(
                                pg.Rect(x*TILESIZE_SCREEN, y*TILESIZE_SCREEN, TILESIZE_SCREEN, TILESIZE_SCREEN)))
                        else:
                            self.fog_of_war_mask.blit(black, self.game.camera.apply_rect(
                                pg.Rect(x * TILESIZE_SCREEN, y * TILESIZE_SCREEN, TILESIZE_SCREEN, TILESIZE_SCREEN)))
            self.game.player.invalidate_fog_of_war = False

            self.game.visible_player_array = self.game.fov.get_vision_matrix_for(self.game.player, flag_explored=True)
            self.game.minimap.build_background()

        self.game.screen.blit(self.fog_of_war_mask, (0, 0))
        # --- HUD SECTION ---
        # Player health
        self.draw_health_bar(self.game.screen, 10, 10)
        # Mini map
        if self.game.minimap_enable:
            self.game.screen.blit(self.game.minimap.background,
                                  (self.game.screen.get_width() - self.game.minimap.background.get_width() - 10, 10))

        # Text -> First line is to remove background
        self.game.screen.fill(BGCOLOR, self.game.textbox._ktext.rect)
        pg.draw.rect(self.game.screen, WHITE, self.game.textbox._ktext.rect.inflate(6, 6), 2)
        self.game.textbox.draw(self.game.screen)

        pg.display.flip()

    def events(self):

        # catch all events here
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.game.quit()
            if event.type == pg.VIDEORESIZE:
                old_w = self.game.screen.get_rect().width
                old_h = self.game.screen.get_rect().height

                self.screen = pg.display.set_mode((event.w, event.h),
                                                  pg.RESIZABLE)
                self.game.player.invalidate_fog_of_war = True
                self.game.textbox.resize(old_w, old_h, event.w, event.h)

            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.game.quit()
                if event.key in (pg.K_LEFT, pg.K_q, pg.K_KP4):
                    self.game.player.move(dx=-1)
                if event.key in (pg.K_RIGHT, pg.K_d, pg.K_KP6):
                    self.game.player.move(dx=1)
                if event.key in (pg.K_UP, pg.K_z, pg.K_KP8):
                    self.game.player.move(dy=-1)
                if event.key in (pg.K_DOWN, pg.K_x, pg.K_KP2):
                    self.game.player.move(dy=1)
                if event.key in (pg.K_KP7, pg.K_a):
                    self.game.player.move(dx=-1, dy=-1)
                if event.key in (pg.K_KP9, pg.K_e):
                    self.game.player.move(dx=1, dy=-1)
                if event.key in (pg.K_KP1, pg.K_w):
                    self.game.player.move(dx=-1, dy=1)
                if event.key in (pg.K_KP3, pg.K_c):
                    self.game.player.move(dx=1, dy=1)
                if event.key == pg.K_m:
                    self.game.minimap_enable = not self.game.minimap_enable
                if event.key == pg.K_p:
                    self.game.game_state = c.GAME_STATE_MAP
                if event.key == pg.K_f:
                    self.game.game_state = c.GAME_STATE_CHARACTER
                if event.key == pg.K_i:
                    self.game.game_state = c.GAME_STATE_INVENTORY
                if event.key == pg.K_g:
                    for object in self.game.objects:
                        if (object.x, object.y) == (self.game.player.x, self.game.player.y) and object.item:
                            object.item.pick_up()

                if event.key == pg.K_y:
                    ThrowableHelper(self.game, self.game.player.pos, "FIREBALL", (1, 0), ThrowableHelper.light_damage,
                                    stopped_by=[c.T_WALL, c.T_VOID])

                if event.key == pg.K_n:
                    self.game.go_next_level()
                    return

                if event.key == pg.K_h:
                    (x, y) = self.game.player.pos
                    x += 1
                    NPCHelper(self.game, "Companion", (x, y), "DOG")

                if event.key == pg.K_s:
                    print("SAVING and EXIT")
                    # We cleanup all objects
                    for entities in self.game.objects:
                        entities.clean_before_save()
                    self.game.map.clean_before_save()
                    for entities in self.game.player.inventory:
                        entities.clean_before_save()
                    with open("savegame", "wb") as f:
                        pick.dump([self.game.objects, self.game.map, self.game.player.name, self.game.all_groups], f)
                    self.game.quit()

                if event.key in (pg.K_l, pg.K_KP5):
                    self.game.textbox.add = str(self.game.player)
                    room = self.game.map.get_room_at(self.game.player.x, self.game.player.y)
                    if room is not None:
                        self.game.textbox.add = room.name
                    self.game.textbox.add = "Objects:"
                    for entity in self.game.objects:
                        if entity.x == self.game.player.x and entity.y == self.game.player.y:
                            self.game.textbox.add = entity.name

            if event.type == pg.MOUSEBUTTONDOWN:
                (button1, button2, button3) = pg.mouse.get_pressed()
                (x, y) = pg.mouse.get_pos()

                # Test intersection with text box
                if self.game.textbox._ktext.rect.collidepoint(x, y):
                    self.game.textbox.drag_drop_text_box = True
                    self.game.textbox.old_x = x
                    self.game.textbox.old_y = y

                else:
                    if button1:
                        (rev_x, rev_y) = self.game.camera.reverse((x, y))
                        (x, y) = (int(rev_x / TILESIZE_SCREEN), int(rev_y / TILESIZE_SCREEN))
                        if self.game.map.tiles[x][y].explored and self.game.map.tiles[x][y].tile_type != c.T_VOID:
                            self.game.textbox.add = "Position {} {}".format(x, y)
                            room = self.game.map.get_room_at(x, y)
                            if room is not None:
                                self.game.textbox.add = room.name
                            self.game.textbox.add = "Objects:"
                            for entity in self.game.objects:
                                if entity.x == x and entity.y == y:
                                    self.game.textbox.add = entity.name

            if event.type == pg.MOUSEBUTTONUP and self.game.textbox.drag_drop_text_box:
                (x, y) = pg.mouse.get_pos()
                self.game.textbox.drag_drop_text_box = False
                if abs(x - self.game.textbox.old_x) > 30 or abs(y - self.game.textbox.old_y) > 30:
                    self.game.textbox._ktext.rect = \
                        self.game.textbox._ktext.rect.move(x - self.game.textbox.old_x, y - self.game.textbox.old_y)
                    self.game.textbox._ktext.rect.x = max(0, self.game.textbox._ktext.rect.x)
                    self.game.textbox._ktext.rect.y = max(0, self.game.textbox._ktext.rect.y)
                    self.game.textbox._ktext.rect.right = min(self.game.textbox._ktext.rect.right, GAME_WIDTH)
                    self.game.textbox._ktext.rect.bottom = min(self.game.textbox._ktext.rect.bottom, GAME_HEIGHT)
                else:
                    pos_in_chat = y - self.game.textbox._ktext.rect.y
                    if pos_in_chat > self.game.textbox._ktext.rect.height / 2:
                        self.game.textbox.scroll(1)
                    else:
                        self.game.textbox.scroll(-1)

    def update(self):
        # Update actions
        self.game.ticker.advance_ticks()
        # update visual portion of the game loop
        for group in self.game.all_groups:
            group.update()
        self.game.camera.update(self.game.player)


class Game:

    def __init__(self):
        pg.display.init()
        pg.font.init()

        self.screen = pg.display.set_mode((GAME_WIDTH, GAME_HEIGHT), pg.RESIZABLE)
        pg.display.set_caption(GAME_TITLE + "-" + GAME_VER)
        self.clock = pg.time.Clock()
        pg.key.set_repeat(500, 100)
        self.playing = True

        self.load_data()

    def load_data(self):
        game_folder = path.dirname(__file__)
        image_folder = path.join(game_folder, IMG_FOLDER)
        # loading graphics
        item_image_src = pg.image.load(path.join(image_folder, 'Item.png')).convert_alpha()
        level_image_src = pg.image.load(path.join(image_folder, 'Level.png')).convert_alpha()
        wall_image_src = pg.image.load(path.join(image_folder, 'Wall.png')).convert_alpha()

        self.all_images = {
            "PLAYER": {
                "E": load_image_list(IMG_FOLDER, 'HeroEast.png'),
                "W": load_image_list(IMG_FOLDER, 'HeroWest.png'),
                "N": load_image_list(IMG_FOLDER, 'HeroNorth.png'),
                "S": load_image_list(IMG_FOLDER, 'HeroSouth.png')},
            # ENEMIES
            "BAT": load_image_list(IMG_FOLDER, 'BatA.png'),
            "BEARD": load_image_list(IMG_FOLDER, 'BeardA.png'),
            "MONKEY": load_image_list_dawnlike(IMG_FOLDER, "Misc0.png", "Misc1.png", 2, 3),
            # NPC
            "DOG": load_image_list(IMG_FOLDER, 'DogA.png'),
            # ITEMS
            "REMAINS": load_image(IMG_FOLDER, item_image_src, 44, 2),
            "POTION_R": load_image(IMG_FOLDER, item_image_src, 1, 1),
            # EQUIPMENT
            "SWORD": load_image(IMG_FOLDER, item_image_src, 1, 16),
            "HELMET": load_image(IMG_FOLDER, item_image_src, 13, 16),
            "CAPE": load_image(IMG_FOLDER, item_image_src, 27, 17),
            "ARMOR": load_image(IMG_FOLDER, item_image_src, 14, 16),
            "LEG": load_image(IMG_FOLDER, item_image_src, 15, 16),
            "GLOVE": load_image(IMG_FOLDER, item_image_src, 16, 16),
            "SHOES": load_image(IMG_FOLDER, item_image_src, 17, 16),
            "SHIELD": load_image(IMG_FOLDER, item_image_src, 11, 13),
            "BOW": load_image(IMG_FOLDER, item_image_src, 11, 17),
            "ARROW": load_image(IMG_FOLDER, item_image_src, 21, 17),
            "RING": load_image(IMG_FOLDER, item_image_src, 1, 4),
            "NECKLACE": load_image(IMG_FOLDER, item_image_src, 1, 5),
            #
            "WALLS": load_wall_structure_dawnlike(wall_image_src),
            "FLOOR": [[load_image(IMG_FOLDER, level_image_src, x, y) for x in range(4)] for y in range(15)],
            "FLOOR_EXT": [[load_image(IMG_FOLDER, level_image_src, x, y) for x in range(4, 6)] for y in range(15)],
            "DOOR_V_OPEN": load_image(IMG_FOLDER, level_image_src, 15, 2),
            "DOOR_H_OPEN": load_image(IMG_FOLDER, level_image_src, 16, 2),
            "DOOR_CLOSED": load_image(IMG_FOLDER, level_image_src, 14, 2),
            "FIREBALL": load_image(IMG_FOLDER, level_image_src, 42, 27),
            "SPECIAL_EFFECT": [load_image(IMG_FOLDER, level_image_src, x, 21) for x in range(4)]
        }

    def new(self):

        # Generic Game variables
        self.ticker = Ticker()
        self.bus = Publisher()
        self.game_state = c.GAME_STATE_PLAYING
        self.player_took_action = False
        self.minimap_enable = False
        self.objects = []

        # Loading fonts and initialize text system
        self.textbox = TextBox(self)
        self.textbox.text = "Welcome to the dungeon - {}".format(GAME_VER)

        self.screens = {
            c.GAME_STATE_INVENTORY: InventoryScreen(self, c.GAME_STATE_PLAYING),
            c.GAME_STATE_MAP: MapScreen(self, c.GAME_STATE_PLAYING),
            c.GAME_STATE_CHARACTER: CharacterScreen(self, c.GAME_STATE_PLAYING),
            c.GAME_STATE_PLAYING: PlayingScreen(self, None)
        }

        # initializing map structure
        self.map = MapFactory("Map of the dead", self.all_images).map
        self.minimap = Minimap(self)

        # Field of view
        self.fov = FieldOfView(self)

        # We have 5 sprites groups: two below the player, the player one and two above
        # They are drawn in the order below:
        self.player_min2_sprite_group = pg.sprite.Group()
        self.player_min1_sprite_group = pg.sprite.Group()
        self.player_sprite_group = pg.sprite.Group()  # the default group, also called level 0
        self.player_plus1_sprite_group = pg.sprite.Group()
        self.player_plus2_sprite_group = pg.sprite.Group()
        self.all_groups = [self.player_min2_sprite_group,
                           self.player_min1_sprite_group,
                           self.player_sprite_group,
                           self.player_plus1_sprite_group,
                           self.player_plus2_sprite_group]

        # Camera
        self.camera = Camera(self.map.tile_width * TILESIZE_SCREEN,
                             self.map.tile_height * TILESIZE_SCREEN)


        # place doors - except if we are in a pure maze
        # The line below can be replaced with teh property door_pos which is part of tilemap.
        pos_list = self.map.doors_pos[:]
        for pos in pos_list:
            DoorHelper(self, pos, ("DOOR_CLOSED", "DOOR_H_OPEN", "DOOR_CLOSED", "DOOR_V_OPEN"),
                       name="Door {}".format(pos),
                       open_function=DoorHelper.open_door)

        # Place player
        all_pos = self.map.get_all_available_tiles(c.T_FLOOR, self.objects, without_objects=True)
        self.player = PlayerHelper(self, all_pos.pop())
        self.visible_player_array = self.fov.get_vision_matrix_for(self.player, flag_explored=True)


        # place monsters
        for i in range(20):
            MonsterHelper(self, "Bat"+str(i), all_pos.pop(), 'BAT', 10, (1, 4, 0),
                          [("bite", (1, 2, 0)), ("snicker", (1, 4, 0))],
                          6, 0, vision=2, speed=10)
            MonsterHelper(self, "Baboon"+str(i), all_pos.pop(), 'MONKEY', 12, (1, 8, 0),
                          [("bite", (1, 4, 1))],
                          6, 18, vision=3, speed=10)

        for i in range(200):
            ItemHelper(self, "Healing Potion"+str(i), all_pos.pop(), "POTION_R",
                       use_function=lambda player=self.player: ItemHelper.cast_heal(player))

            EquipmentHelper(self, "Sword", all_pos.pop(), "SWORD", slot=c.SLOT_HAND_RIGHT, modifiers={c.BONUS_STR: 2})
            EquipmentHelper(self, "Helmet", all_pos.pop(), "HELMET", slot=c.SLOT_HEAD, modifiers={c.BONUS_STR: -1})
            # EquipmentHelper(self, "Cape", all_pos.pop(), "CAPE", slot=c.SLOT_CAPE, modifiers={})
            # EquipmentHelper(self, "Leg", all_pos.pop(), "LEG", slot=c.SLOT_LEG, modifiers={})
            # EquipmentHelper(self, "Armor", all_pos.pop(), "ARMOR", slot=c.SLOT_TORSO, modifiers={})

            # pos = self.map.get_random_available_tile(c.T_FLOOR)
            # item_component = Item(use_function=lambda player=self.player: Item.cast_heal(player))
            # item = GameObject(self, "HEALING POTION", pos[0], pos[1], self.items_img['Potion_R'], blocks=False,
            #                       item=item_component)

            # (x, y) = all_pos.pop()
            # Entity(self, "Sword", x, y, 'SWORD', blocks=False,
            #       equipment=EquipmentEntity(slot=EquipmentEntity.SLOT_HAND_RIGHT, hit_bonus=4))
            # (x, y) = all_pos.pop()
            # Entity(self, "Helmet of fire", x, y, 'HELMET', blocks=False,
            #        equipment=EquipmentEntity(slot=EquipmentEntity.SLOT_HEAD, protection_bonus=2))
            # (x, y) = all_pos.pop()
            # Entity(self, "Cape of Truth", x, y, 'CAPE', blocks=False,
            #        equipment=EquipmentEntity(slot=EquipmentEntity.SLOT_CAPE, protection_bonus=1))
            # (x, y) = all_pos.pop()
            # Entity(self, "Leg of fire", x, y, 'LEG', blocks=False,
            #        equipment=EquipmentEntity(slot=EquipmentEntity.SLOT_LEG))
            # (x, y) = all_pos.pop()
            # Entity(self, "Armor", x, y, 'ARMOR', blocks=False,
            #        equipment=EquipmentEntity(slot=EquipmentEntity.SLOT_TORSO))
            # (x, y) = all_pos.pop()
            # Entity(self, "Glove", x, y, 'GLOVE', blocks=False,
            #        equipment=EquipmentEntity(slot=EquipmentEntity.SLOT_GLOVE))
            # (x, y) = all_pos.pop()
            # Entity(self, "Shoes", x, y, 'SHOES', blocks=False,
            #        equipment=EquipmentEntity(slot=EquipmentEntity.SLOT_FOOT))
            # (x, y) = all_pos.pop()
            # Entity(self, "Shield", x, y, 'SHIELD', blocks=False,
            #        equipment=EquipmentEntity(slot=EquipmentEntity.SLOT_HAND_LEFT, protection_bonus=2))
            # (x, y) = all_pos.pop()
            # Entity(self, "Bow", x, y, 'BOW', blocks=False,
            #        equipment=EquipmentEntity(slot=EquipmentEntity.SLOT_BOW, hit_bonus=1))
            # (x, y) = all_pos.pop()
            # Entity(self, "Arrow", x, y, 'ARROW', blocks=False,
            #        equipment=EquipmentEntity(slot=EquipmentEntity.SLOT_QUIVER, hit_bonus=1))
            # (x, y) = all_pos.pop()
            # Entity(self, "Ring", x, y, 'RING', blocks=False,
            #        equipment=EquipmentEntity(slot=EquipmentEntity.SLOT_RING, vision_bonus=1))
            # (x, y) = all_pos.pop()
            # Entity(self, "Necklace", x, y, 'NECKLACE', blocks=False,
            #        equipment=EquipmentEntity(slot=EquipmentEntity.SLOT_NECKLACE, vision_bonus=2))

    def place_object(self, level):
        """
        Setup all objects (enemies and items so far)
        :param level: the desired level
        :return:
        """
        all_pos = self.map.get_all_available_tiles(c.T_FLOOR, self.objects, without_objects=True)
        number_enemies = int(len(all_pos) / 50)
        for i in range(number_enemies):
            roll = rd.randint(0,100)
            if level == 1:
                if 0 < roll < 5:
                    pass



    def go_next_level(self):

        # First: cleanup!
        # Warning: we must act on a copy of the list!!!!!
        for entity in self.objects[:]:
            if entity != self.player:
                # TODO: fix the method below to remove fromspritegroup...
                entity.remove_completely_object()
        print("Ticker now empty: {}".format(self.ticker.schedule))

        # initializing map structure
        self.map = MapFactory("Map of the dead2", self.all_images).map
        self.minimap = Minimap(self)

        # Field of view
        self.fov = FieldOfView(self)

        # place doors - except if we are in a pure maze
        # The line below can be replaced with teh property door_pos which is part of tilemap.
        pos_list = self.map.doors_pos[:]
        for pos in pos_list:
            DoorHelper(self, pos, ("DOOR_CLOSED", "DOOR_H_OPEN", "DOOR_CLOSED", "DOOR_V_OPEN"),
                       name="Door {}".format(pos),
                       open_function=DoorHelper.open_door)

        # Place player
        all_pos = self.map.get_all_available_tiles(c.T_FLOOR, self.objects, without_objects=True)
        new_player_pos = all_pos.pop()
        self.player.x = new_player_pos[0]
        self.player.y = new_player_pos[1]
        self.visible_player_array = self.fov.get_vision_matrix_for(self.player, flag_explored=True)
        self.player.invalidate_fog_of_war = True
        self.player_sprite_group.add(self.player)

        # Camera
        self.camera = Camera(self.map.tile_width * TILESIZE_SCREEN,
                             self.map.tile_height * TILESIZE_SCREEN)
        # place monsters
        for i in range(60):
            MonsterHelper(self, "Beard"+str(i), all_pos.pop(), 'BEARD', 10, (1, 4, 0),
                          [("bite", (1, 2, 0)), ("snicker", (1, 4, 0))],
                          6, 0, vision=2, speed=10)

        for i in range(200):
            EquipmentHelper(self, "Cape", all_pos.pop(), "CAPE", slot=c.SLOT_CAPE, modifiers={c.BONUS_STR: 2})
            EquipmentHelper(self, "Ring", all_pos.pop(), "RING", slot=c.SLOT_RING, modifiers={c.BONUS_STR: -1})

    def load(self, filename="savegame"):
        with open(filename, "rb") as f:
            [self.objects, self.map, player_name, self.all_groups] = pick.load(f)
            self.map.game = self

            # Generic Game variables
            self.ticker = Ticker()
            self.game_state = c.GAME_STATE_PLAYING
            self.player_took_action = False
            self.minimap_enable = False

            self.inventory_screen = InventoryScreen(self, c.GAME_STATE_PLAYING)
            self.map_screen = MapScreen(self, c.GAME_STATE_PLAYING)
            self.playing_screen = PlayingScreen(self, None)
            self.character_screen = CharacterScreen(self, c.GAME_STATE_PLAYING)

            # initializing map structure
            self.minimap = Minimap(self)

            # Field of view
            self.fov = FieldOfView(self)

            # We have 5 sprites groups: two below the player, the player one and two above
            # They are drawn in the order below:
            [self.player_min2_sprite_group,
             self.player_min1_sprite_group,
             self.player_sprite_group,
             self.player_plus1_sprite_group,
             self.player_plus2_sprite_group] = self.all_groups

            # Camera
            self.camera = Camera(self.map.width, self.map.height)

            for entities in self.objects:
                entities.game = self
                entities.init_graphics()
                if entities.name == player_name:
                    self.player = entities
                    self.visible_player_array = self.fov.get_vision_matrix_for(self.player, flag_explored=True)
            for entities in self.player.inventory:
                entities.game = self
                entities.init_graphics(in_inventory=True)

    def run(self):
        # game loop - set self.playing = False to end the game
        while self.playing:
            self.screens[self.game_state].events()
            self.screens[self.game_state].update()
            self.screens[self.game_state].draw()

    def quit(self):
        pg.quit()
        sys.exit()

    def show_start_screen(self):
        pass

    def show_go_screen(self):
        pass

if __name__ == '__main__':
    # create the game object
    g = Game()
    g.show_start_screen()
    while g.playing:
        g.new()
        # g.load()
        g.run()
    g.show_go_screen()
