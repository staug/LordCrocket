import pygame as pg
import constants as c
import dill as pick

from settings import *
from os import path
from entities import ThrowableHelper, NPCHelper
from utilities_ui import Button


class Screen:

    def __init__(self, game, default_back_state):
        self.game = game
        self.default_back_state = default_back_state
        self.widgets = []

    def test(self, *args, **kwargs):
        print("Test {} {}".format(args, kwargs))
        for widget in self.widgets[:]:
            if widget.id == kwargs['widget']:
                self.widgets.remove(widget)

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
        self.tile_size = TILESIZE_INVENTORY
        self.objects_per_line = 5
        self.item_list_value = 0 # Used if more item are available than 2 lines
        self.equipment_list_value = 0 # Used if more equipment are available than 2 lines

        self.selected_item = None
        self.font = pg.font.Font(path.join(path.join(path.dirname(__file__), FONT_FOLDER), FONT_NAME), 10)

        x_icon = game.screen.get_rect().width - 2 * self.tile_size
        width = game.all_images["ICON_EQUIP"].get_rect().width
        height = game.all_images["ICON_EQUIP"].get_rect().height
        button_equip = Button((x_icon, 1 * self.tile_size, width, height),
                            lambda screen=self: screen.button_equip(),
                            text="Equip", id='button_equip', image=game.all_images["ICON_EQUIP"])
        button_unequip = Button((x_icon, 3 * self.tile_size, 0, 0),
                              lambda screen=self: screen.button_unequip(),
                              text="Unequip", id='button_unequip', image=game.all_images["ICON_UNEQUIP"])
        button_use = Button((x_icon, 5 * self.tile_size, 0, 0),
                                lambda screen=self: screen.button_use(),
                                text="Use", id='button_use', image=game.all_images["ICON_USE"])
        button_drop = Button((x_icon, 7 * self.tile_size, 0, 0),
                                lambda screen=self: screen.button_drop(),
                                text="Drop", id='button_drop', image=game.all_images["ICON_DROP"])
        button_identify = Button((x_icon, 9 * self.tile_size, 0, 0),
                             lambda screen=self: screen.button_drop(),
                             text="Identify", id='button_drop', image=game.all_images["ICON_IDENTIFY"])
        self.widgets.append(button_equip)
        self.widgets.append(button_unequip)
        self.widgets.append(button_use)
        self.widgets.append(button_drop)
        self.widgets.append(button_identify)

    def button_use(self):
        if self.selected_item is not None:
            if self.selected_item.item is not None:
                self.selected_item.item.use()
            self.selected_item = None

    def button_equip(self):
        if self.selected_item is not None:
            if self.selected_item.equipment is not None:
                self.selected_item.equipment.equip()
            self.selected_item = None

    def button_unequip(self):
        if self.selected_item is not None:
            if self.selected_item.equipment is not None:
                self.selected_item.equipment.dequip()
            self.selected_item = None

    def button_drop(self):
        if self.selected_item is not None:
            if self.selected_item.item is not None:
                self.selected_item.item.drop()
            self.selected_item = None

    def button_identify(self):
        if self.selected_item is not None:
            if self.selected_item.item is not None:
                self.selected_item.item.identify()
            self.selected_item = None


    def events(self):
        # catch all events here
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.game.quit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.game.game_state = self.default_back_state
            if event.type == pg.MOUSEBUTTONDOWN:
                handled = False
                for widget in self.widgets:
                    if not handled:
                        handled = widget.get_event(event)

                if not handled:
                    (button1, button2, button3) = (event.button == 1, event.button == 2, event.button == 3)
                    (x, y) = event.pos
                    # Test where the mouse is..
                    tile_size = self.tile_size
                    orig_x = self.original_pos[0]
                    top_x, top_y = orig_x, self.original_pos[1]

                    index_x = int((x - top_x) / tile_size)
                    index_y = int((y - top_y) / tile_size)

                    has_equipable = len(self.game.player.get_unequipped_objects()) > 0
                    has_usable = len(self.game.player.get_non_equipment_objects()) > 0

                    start_index_y_equipable = 6
                    end_index_y_equipable = start_index_y_equipable + int(len(self.game.player.get_unequipped_objects()) /
                                                                          self.objects_per_line)

                    start_index_y_usable = end_index_y_equipable + 3
                    if not has_equipable:
                        start_index_y_usable = 6
                    end_index_y_usable = start_index_y_usable + int(len(self.game.player.get_non_equipment_objects()) /
                                                                    self.objects_per_line)

                    if 0 <= index_x < 4 and 0 <= index_y < 5:
                        self.handle_equipped_event((button1, button2, button3), index_x, index_y)
                    elif has_equipable \
                            and 0 <= index_x < self.objects_per_line \
                            and start_index_y_equipable <= index_y <= end_index_y_equipable \
                            and len(self.game.player.get_unequipped_objects()) > \
                                                    (index_y-start_index_y_equipable) * self.objects_per_line + index_x:
                        self.handle_equipable_event((button1, button2, button3), index_x, index_y - start_index_y_equipable)
                    # Usable, but not equipment
                    elif has_usable \
                            and 0 <= index_x < self.objects_per_line \
                            and start_index_y_usable <= index_y <= end_index_y_usable \
                            and len(self.game.player.get_non_equipment_objects()) > \
                                                    (index_y - start_index_y_usable) * self.objects_per_line + index_x:
                        self.handle_usable_event((button1, button2, button3), index_x, index_y - start_index_y_usable)

    def handle_equipable_event(self, buttons, index_x, index_y):
        listing = self.game.player.get_unequipped_objects()
        (button1, button2, button3) = buttons
        if button1:
            self.selected_item = listing[index_y * self.objects_per_line + index_x]
        else:
            listing[index_y * self.objects_per_line + index_x].equipment.equip()
            self.selected_item = None

    def handle_usable_event(self, buttons, index_x, index_y):
        listing = self.game.player.get_non_equipment_objects()
        (button1, button2, button3) = buttons
        if button1:
            self.selected_item = listing[index_y * self.objects_per_line + index_x]
        else:
            listing[index_y * self.objects_per_line + index_x].item.use()
            self.selected_item = None

    def handle_equipped_event(self, buttons, index_x, index_y):
        slots = [c.SLOT_RING, c.SLOT_HEAD, c.SLOT_CAPE,
                 c.SLOT_NECKLACE,
                 c.SLOT_HAND_RIGHT, c.SLOT_TORSO, c.SLOT_HAND_LEFT,
                 c.SLOT_BOW,
                 c.SLOT_GLOVE, c.SLOT_LEG, c.SLOT_QUIVER, "NOTHING",
                 "NOTHING", c.SLOT_FOOT, "NOTHING", "NOTHING"]
        game_object = None
        if index_y * 4 + index_x < len(slots):
            game_object = self.game.player.get_equipped_object_at(slots[index_y * 4 + index_x])
        if game_object is not None:
            (button1, button2, button3) = buttons
            if button1:
                self.selected_item = game_object
            else:
                game_object.equipment.dequip()
                self.selected_item = None

    def render_object_text(self):
        lines = [self.selected_item.name]
        if hasattr(self.selected_item, "long_desc") and self.selected_item.long_desc:
            lines.append(self.selected_item.long_desc)
        if hasattr(self.selected_item, "equipment"):
            if hasattr(self.selected_item.equipment, "modifiers") and self.selected_item.equipment.modifiers:
                lines.append("Modifiers:")
                for key in self.selected_item.equipment.modifiers:
                    lines.append("    {}: {}".format(key, self.selected_item.equipment.modifiers[key]))
        if hasattr(self.selected_item.equipment, "slot") and self.selected_item.equipment.slot:
            lines.append("Slot: {}".format(self.selected_item.equipment.slot))

        big_line = lines[0]
        for line in lines:
            if len(line) > len(big_line):
                big_line = line
        width, height = self.font.size(big_line)

        final_surface = pg.Surface((int(width), int(height * len(lines))))
        for index, line in enumerate(lines):
            final_surface.blit(self.font.render(line, True, WHITE), (0, index * height))
        return final_surface

    def draw(self):
        # Erase All
        self.game.screen.fill(BGCOLOR)

        tile_size = self.tile_size
        orig_x = self.original_pos[0]
        top_x, top_y = orig_x, self.original_pos[1]

        if self.selected_item:
            text_surf = self.render_object_text()
            text_surf_rect = text_surf.get_rect()
            text_surf_rect.x = orig_x + tile_size * 6
            text_surf_rect.y = top_y
            self.game.screen.blit(text_surf, text_surf_rect)

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

        # Generic Widgets?
        for widget in self.widgets:
            widget.draw(self.game.screen)

        pg.display.flip()

    def update(self):
        # Generic Widgets?
        for widget in self.widgets:
            widget.update()


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

        map_image = self.game.minimap.build_background(minimap=False, zoom_factor=4)
        self.game.screen.blit(map_image, (int((self.game.screen.get_width() - map_image.get_width()) / 2),
                                          int((self.game.screen.get_height() - map_image.get_height()) / 2)))

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
        self._surface = None
        self._lines = None
        self.last_update = pg.time.get_ticks()

    def build_player_text(self):
        lines = []
        player = self.game.player

        strength_modifier = player.strength - player.base_strength
        if strength_modifier >= 0:
            strength_modifier = "+{}".format(strength_modifier)
        dexterity_modifier = player.dexterity - player.base_dexterity
        if dexterity_modifier >= 0:
            dexterity_modifier = "+{}".format(dexterity_modifier)
        mind_modifier = player.mind - player.base_mind
        if mind_modifier >= 0:
            mind_modifier = "+{}".format(mind_modifier)
        charisma_modifier = player.charisma - player.base_charisma
        if charisma_modifier >= 0:
            charisma_modifier = "+{}".format(charisma_modifier)
        vision_modifier = player.vision - player.base_vision
        if vision_modifier >= 0:
            vision_modifier = "+{}".format(vision_modifier)

        lines.append(player.name)
        lines.append("")
        lines.append("")
        lines.append("Characteristics")
        lines.append("")
        lines.append("Strength:    {:3d} ({:3})    Dexterity: {:3d} ({:3})".format(player.strength,
                                                                                   strength_modifier,
                                                                                   player.dexterity,
                                                                                   dexterity_modifier))
        lines.append("Mind:        {:3d} ({:3})    Charisma:  {:3d} ({:3})".format(player.mind,
                                                                                   mind_modifier,
                                                                                   player.charisma,
                                                                                   charisma_modifier))
        lines.append("Vision:      {:3d} ({:3})".format(player.vision, vision_modifier))
        lines.append("")
        lines.append("Fighter statistics")
        lines.append("Hit Points:  {:3d}          Base:      {:3d}".format(player.fighter.hit_points,
                                                                           player.base_hit_points))
        lines.append("Body Points: {:3d}          Base:      {:3d}".format(player.fighter.body_points,
                                                                           player.base_body_points))
        lines.append("Armor Class: {:3d}".format(player.fighter.armor_class))
        lines.append("")
        lines.append("Speed:       {:3d}".format(player.speed))
        lines.append("Wealth:   {:6d}".format(player.wealth))
        lines.append("Level:       {:3d}          Experience: {}".format(player.level, player.experience))

        return lines

    def events(self):

        # catch all events here
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.game.quit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.game.game_state = self.default_back_state

    def build_surface(self):
        self._lines = self.build_player_text()

        big_line = self._lines[0]
        for line in self._lines:
            if len(line) > len(big_line):
                big_line = line
        width, height = self.font.size(big_line)

        final_surface = pg.Surface((int(width), int(height * len(self._lines))))
        for index, line in enumerate(self._lines):
            final_surface.blit(self.font.render(line, True, WHITE), (0, index * height))
        self._surface = final_surface

    def draw(self):
        # Erase All
        self.game.screen.fill(BGCOLOR)
        if not self._surface:
            self.build_surface()
        self.game.screen.blit(self._surface, (32, 32))

        pg.display.flip()

    def update(self):
        now = pg.time.get_ticks()
        delta = 1000
        if now - self.last_update > delta:
            self.last_update = now
            self.build_surface()


class PlayingScreen(Screen):

    def __init__(self, game, default_back_state):
        Screen.__init__(self, game, default_back_state)
        self.fog_of_war_mask = None

        bt1 = Button((10, 10, 50, 20), None, text="CLICK", id='A')
        bt1.command = lambda player=self.game.player, screen=self: screen.test(player=player, widget=bt1.id)
        bt2 = Button((10, 30, 50, 20), None, text="THIS IS A LONNG TEXT", id='B')
        bt2.command = lambda player=self.game.player, screen=self: screen.test(player=player, widget=bt2.id)

        self.widgets.append(game.textbox)
        #self.widgets.append(bt1)
        #self.widgets.append(bt2)

    def draw_health_bar(self, surf, x, y):
        # TODO: Health bar should be a widget
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
        map_rebuild = False
        if self.game.player.invalidate_fog_of_war or self.fog_of_war_mask is None:

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
            map_rebuild = True

        self.game.screen.blit(self.fog_of_war_mask, (0, 0))
        # --- HUD SECTION ---
        # Player health
        self.draw_health_bar(self.game.screen, 10, 10)
        # Mini map
        if self.game.minimap_enable:
            if map_rebuild:
                self.game.minimap.build_background(minimap=True,
                                                   center_player=True)
                map_rebuild = False
            self.game.screen.blit(self.game.minimap.background_mini_map,
                                  (self.game.screen.get_width() -
                                   self.game.minimap.background_mini_map.get_width() - 10, 10))

        # Text -> First line is to remove background
        #self.game.screen.fill(BGCOLOR, self.game.textbox._ktext.rect)
        #pg.draw.rect(self.game.screen, WHITE, self.game.textbox._ktext.rect.inflate(6, 6), 2)
        #self.game.textbox.draw(self.game.screen)

        # Generic Modal Widgets?
        for widget in self.widgets:
            widget.draw(self.game.screen)

        pg.display.flip()

    def events(self):

        # catch all events here

            for event in pg.event.get():
                handled = False
                for widget in self.widgets:
                    if not handled:
                        handled = widget.get_event(event)
                if handled:
                    return
                if event.type == pg.USEREVENT + 1:
                    self.game.soundfiles = self.game.soundfiles[1:] + [self.game.soundfiles[0]] # move current song to the back of the list
                    pg.mixer.music.load(self.game.soundfiles[0])
                    print("Now playing: {}".format(self.game.soundfiles[0]))
                    pg.mixer.music.play()
                if event.type == pg.QUIT:
                    self.game.quit()
                if event.type == pg.VIDEORESIZE:
                    old_rect = self.game.screen.get_rect()
                    self.game.screen = pg.display.set_mode((event.w, event.h),
                                                           pg.RESIZABLE)
                    self.game.player.invalidate_fog_of_war = True
                    self.game.textbox.resize(old_rect.width, old_rect.height, event.w, event.h)

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
                        print("Minimap state: {}".format(self.game.minimap_enable))
                    if event.key == pg.K_p:
                        self.game.game_state = c.GAME_STATE_MAP
                    if event.key == pg.K_f:
                        self.game.game_state = c.GAME_STATE_CHARACTER
                    if event.key == pg.K_i:
                        self.game.game_state = c.GAME_STATE_INVENTORY
                    if event.key == pg.K_g:
                        for item in self.game.objects:
                            if (item.x, item.y) == (self.game.player.x, self.game.player.y) and item.item:
                                item.item.pick_up()

                    if event.key == pg.K_y:
                        ThrowableHelper(self.game, self.game.player.pos, "FIREBALL", (1, 0),
                                        ThrowableHelper.light_damage,
                                        stopped_by=[c.T_WALL, c.T_VOID])

                    if event.key == pg.K_n:
                        self.game.go_next_level()
                        return

                    if event.key == pg.K_h:
                        (x, y) = self.game.player.pos
                        x += 1
                        NPCHelper(self.game, "Companion", (x, y), "DOG")
                    if event.key == pg.K_r:
                        # First, make sure that the music system is unabled
                        if not hasattr(self.game, "soundfiles"):
                            self.game.load_music()

                        if self.game.music_playing:
                            pg.mixer.music.pause()
                        else:
                            pg.mixer.music.unpause()
                        self.game.music_playing = not self.game.music_playing

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
                    if button1:
                        (rev_x, rev_y) = self.game.camera.reverse((x, y))
                        (x, y) = (int(rev_x / TILESIZE_SCREEN), int(rev_y / TILESIZE_SCREEN))
                        if self.game.map.tiles[x][y].explored and self.game.map.tiles[x][y].tile_type != c.T_VOID:
                            room = self.game.map.get_room_at(x, y)
                            if room is not None:
                                self.game.textbox.add = room.name
                            for entity in self.game.objects:
                                if entity.x == x and entity.y == y:
                                    self.game.textbox.add = entity.name


    def update(self):
        # Update actions
        self.game.ticker.advance_ticks()
        # update visual portion of the game loop
        for group in self.game.all_groups:
            group.update()
        self.game.camera.update(self.game.player)

        # Generic Widgets?
        for widget in self.widgets:
            widget.update()

