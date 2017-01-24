import pygame as pg
import constants as c
import dill as pick

from settings import *
from os import path
from ktextsurfacewriter import KTextSurfaceWriter
from entities import ThrowableHelper, NPCHelper


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

        # Question box?
        if self.game.questionbox != None:
            self.game.questionbox.draw(self.game.screen)

        pg.display.flip()

    def events(self):

        # catch all events here
        if self.game.questionbox is not None:
            self.game.questionbox.update(pg.event.get())
        else:
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

