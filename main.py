import pygame
import atexit
import sys
import random
import tkinter.filedialog
import time

root = tkinter.Tk()
root.withdraw()

sys.path.insert(1, "assets/src")

import player
import level
import spritesheet
import ui
import particles

WN_WIDTH = 810
WN_HEIGHT = 600
WN_COLOR = (105, 219, 245)
WN_TITLE = "Platform Shooters"

# when we call 'exit()', these gets called
atexit.register(pygame.quit)
atexit.register(root.destroy)

pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()

wn = pygame.display.set_mode((WN_WIDTH, WN_HEIGHT))
pygame.display.set_caption(WN_TITLE)

FPS = 60
GRID_SIZE = (30, 30)
EDITOR_GRID_COLOR = (255, 255, 255)
LEVEL_NAME_PREFIX = "battlefield"
MUSIC_VOLUME = 0.5
ENEMY_DAMAGE_WAIT = 1
LEVEL_POWERUPS = 2

MAX_LIVES = 3

MUSIC = [
    "assets/snd/music/1.mp3",
    "assets/snd/music/2.mp3",
    "assets/snd/music/3.mp3",
    "assets/snd/music/4.mp3",
    "assets/snd/music/5.mp3"
]

POWERUP_MAP = {
    9: ("jump", (90, 45, 116)),
    10: ("speed", (53, 143, 138)),
    11: ("gun", (218, 189, 38))
}

BUTTON_FONT = "assets/fnts/8bit_wonder.ttf"
SMALL_UI_FONT = "assets/fnts/minecraft.ttf"
PRESS_START_FONT = "assets/fnts/pressstart.ttf"

clock = pygame.time.Clock()
Vec2 = pygame.Vector2

music_index = 0

temp_spritesheet = spritesheet.SpriteSheet("assets/img/images.png", enlarge=2)
mouse_surf_cursor = temp_spritesheet[7]
mouse_surf_aim = temp_spritesheet[8]

pygame.mouse.set_visible(False)

lives = MAX_LIVES
player_spritesheet = spritesheet.SpriteSheet("assets/img/player.png", (16, 16), 2)
level_spritesheet = spritesheet.SpriteSheet("assets/img/images.png", (16, 16), 2)
p = None
l = None


def check_music():  # check to see if next song should play -> call in every part of game
    global music_index

    if not pygame.mixer.music.get_busy():
        music_index += 1
        try:
            pygame.mixer.music.load(MUSIC[music_index])
        except IndexError:
            music_index = 0
            pygame.mixer.music.load(MUSIC[music_index])
        pygame.mixer.music.play()


def check_lives():
    global lives, player_spritesheet, level_spritesheet, p, l

    if lives == 0:
        pygame.mixer.Sound("assets/snd/gameover.wav").play()
        p = player.Player(Vec2(50, 50), Vec2(30, 30), 1, 0.8, 15, 75, player_spritesheet[0])
        lives = MAX_LIVES
        level_num = 0
        l = level.Level(f"assets/lvl/{LEVEL_NAME_PREFIX}{level_num}.lvl", level_spritesheet, LEVEL_POWERUPS)


def draw_mouse(surf=mouse_surf_cursor, offset=Vec2(-2, -2)):
    wn.blit(surf, Vec2(pygame.mouse.get_pos()) + offset)


def main():
    random.shuffle(MUSIC)
    pygame.mixer.music.load(MUSIC[music_index])
    pygame.mixer.music.play()
    pygame.mixer.music.set_volume(MUSIC_VOLUME)

    while True:
        menu_result = menu()

        if menu_result == "game":
            game()
        elif menu_result == "quit":
            exit()
        elif menu_result == "editor":
            editor()


def game():
    global lives, player_spritesheet, level_spritesheet, p, l

    def render():
        wn.fill(WN_COLOR)

        last_frame = clock.get_time() / 1000  # / 1000 to get seconds

        if not completed:
            cloud_particles.update(last_frame)
        cloud_particles.draw(wn)

        to_destroy = []
        for particle in enemy_particles:
            particle.update(last_frame)
            particle.draw(wn)

            if len(particle.particles) == 0:
                to_destroy.append(particle)

        for particle in powerup_particles:
            particle.update(last_frame)
            particle.draw(wn)

            if len(particle.particles) == 0:
                to_destroy.append(particle)

        for particle in to_destroy:
            try:
                enemy_particles.remove(particle)
            except ValueError:
                powerup_particles.remove(particle)

            print("Particle system destroyed")

        if not completed:
            p.update(l, last_frame)
        p.draw(wn)

        rel = pygame.mouse.get_rel()

        to_destroy = []
        for block in l:
            block.update(rel, last_frame)
            block.draw(wn)

            if block.destroy:
                to_destroy.append(block)

        for block in to_destroy:
            l.data.remove(block)

        for x in range(lives):
            wn.blit(level_spritesheet[6], (10 + x * 40, 10))

        if completed:
            ui.dralpha(wn, (0, 0, 0, 100), (0, 0, WN_WIDTH, WN_HEIGHT))

            ui.write(wn, "Level completed", (0, -100), pos_config.center, size=45, font=BUTTON_FONT)
            ui.write(wn, f"Time taken: {round(end_time-start_time)} seconds", (0, -50), pos_config.center, size=20,
                     font=PRESS_START_FONT)

            next_level_button.draw(wn)
            menu_button.draw(wn)

            draw_mouse()
        else:
            draw_mouse(mouse_surf_aim, Vec2(0, 0) - Vec2(mouse_surf_aim.get_size())/2)

    run = True

    level_num = 0

    p = player.Player(Vec2(50, 50), Vec2(30, 30), 1, 0.8, 15, 75, player_spritesheet[0])
    l = level.Level(f"assets/lvl/{LEVEL_NAME_PREFIX}{level_num}.lvl", level_spritesheet, LEVEL_POWERUPS)

    enemy_particles = []
    powerup_particles = []
    cloud_particles = particles.Clouds(Vec2(WN_WIDTH, WN_HEIGHT))

    pos_config = ui.Positions(wn)

    next_level_button = ui.TextButton("Next Level", (0, 0), pos_config.center, ((219, 255, 253), (33, 192, 255)), font=BUTTON_FONT)
    menu_button = ui.TextButton("Menu", (0, 50), pos_config.center, ((219, 255, 253), (73, 142, 215)), font=BUTTON_FONT)

    completed = False

    start_time = time.time()
    end_time = 0

    lives = MAX_LIVES
    last_lost_lives = time.time()

    while run:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if completed:
                    if next_level_button.pressed(event):
                        completed = False
                        p = player.Player(Vec2(50, 50), Vec2(30, 30), 1, 0.8, 15, 75, player_spritesheet[0])

                        level_num += 1
                        lives = MAX_LIVES
                        start_time = time.time()
                        try:
                            l = level.Level(f"assets/lvl/{LEVEL_NAME_PREFIX}{level_num}.lvl", level_spritesheet, LEVEL_POWERUPS)
                        except FileNotFoundError:
                            # finished the game
                            return
                    elif menu_button.pressed(event):
                        run = False
                else:
                    p.shoot()

        enemies = []
        powerups = []

        for block in l:
            if type(block) == level.Enemy:
                enemies.append(block)
            elif type(block) == level.Powerup:
                powerups.append(block)

        for powerup in powerups:
            if p.physics.get_rect(p.size).colliderect(powerup.rect):
                t = POWERUP_MAP[powerup.image_num]

                """
                jump   9
                speed  10
                gun    11
                """

                if t[0] == "jump":
                    p.physics.jump_height *= 1.5
                elif t[0] == "speed":
                    p.move_speed *= 2
                elif t[0] == "gun":
                    p.gun.triple_shoot = True

                pygame.mixer.Sound("assets/snd/powerup.wav").play()
                offset = Vec2(powerup.rect.w/2, powerup.rect.h/2)
                powerup_particles.append(particles.PowerupCollect(powerup.position + offset, t[1]))

                l.data.remove(powerup)
                break

        for bullet in p.gun.bullets:
            for block in l:
                if block.rect.collidepoint(bullet.position):
                    if type(block) == level.Enemy:
                        block.destroy = True
                        pygame.mixer.Sound("assets/snd/hurt.wav").play()
                        enemy_particles.append(particles.EnemyDestroy(block.position + Vec2(block.rect.w, block.rect.h)))

                        l.enemy_count -= 1

                        print("Enemy destroyed")
                        print("Particle system created")

                        if l.enemy_count == 0:
                            completed = True
                            end_time = time.time()
                            print("Level completed")
                    else:
                        bullet.destroy = True

        if time.time() - ENEMY_DAMAGE_WAIT > last_lost_lives:
            if p.physics.is_colliding(enemies, p.size, True):  # true allows the collider to detect enemies
                lives -= 1
                last_lost_lives = time.time()
                pygame.mixer.Sound("assets/snd/fall.wav").play()
                p.start_blinking(ENEMY_DAMAGE_WAIT, 0.2)

                p.physics.velocity = Vec2(random.randint(-10, 10), 10)

                check_lives()

        if p.physics.pos.x < 0:
            p.physics.pos.x = 0
            p.physics.velocity.x = 0
        elif p.physics.pos.x > WN_WIDTH - p.size.x:
            p.physics.pos.x = WN_WIDTH - p.size.x
            p.physics.velocity.x = 0

        if p.physics.pos.y > WN_WIDTH + 150:
            pygame.mixer.Sound("assets/snd/fall.wav").play()
            p = player.Player(Vec2(50, 50), Vec2(30, 30), 1, 0.8, 15, 75, player_spritesheet[0])
            lives -= 1

            check_lives()

        check_music()

        render()
        pygame.display.update()


def menu():
    global wn

    def render():
        wn.fill(WN_COLOR)

        ui.write(wn, WN_TITLE, (0, -100), pos_config.center, size=40, font=BUTTON_FONT)

        play_button.draw(wn)
        editor_button.draw(wn)
        quit_button.draw(wn)

        draw_mouse()

    run = True

    pos_config = ui.Positions(wn)

    play_button = ui.TextButton("Play", (0, 0), pos_config.center, ((219, 253, 255), (33, 192, 255)),
                                font=BUTTON_FONT)
    editor_button = ui.TextButton("Editor", (0, 40), pos_config.center, ((255, 255, 255), (240, 240, 240)),
                                  font=BUTTON_FONT)
    quit_button = ui.TextButton("Quit", (0, 80), pos_config.center, ((255, 255, 255), (240, 240, 240)),
                                font=BUTTON_FONT)

    while run:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT or quit_button.pressed(event):
                return "quit"

            elif play_button.pressed(event):
                return "game"

            elif editor_button.pressed(event):
                return "editor"

        check_music()

        render()
        pygame.display.update()


def editor():
    # not really meant to be reusable, just a container for the code
    class PopoutMenu:
        class BlockItem:
            def __init__(self, block_class, position, spritesheet_index):
                self.instance = block_class(position, level_spritesheet[spritesheet_index])
                self.spritesheet_index = spritesheet_index

                r = self.instance.rect
                self.rect = pygame.Rect(r.x - 3, r.y - 3, r.w + 6, r.h + 6)

            def draw(self, wn):
                ui.dralpha(wn, (255, 255, 255, 30), self.rect)
                self.instance.draw(wn)

        class EnemyEditor:
            def __init__(self, position, image):
                self.position = pygame.Vector2(position)
                self.rect = pygame.Rect(*self.position, *image.get_size())
                self.image = image

                self.id = "enemy"

                self._range = [self.position.x, self.position.x]

                self.range_selector1 = pygame.Rect(self.range[0]-15, self.position.y+5, 7, self.rect.h-10)
                self.range_selector2 = pygame.Rect(self.range[0]+self.rect.w+10, self.position.y+5, 7, self.rect.h-10)

                self.updating = False
                self.updating_block = None

            @property
            def range(self):
                return self._range

            @range.setter
            def range(self, value):
                self._range = value

                self.range_selector1.x = self._range[0]
                self.range_selector2.x = self._range[1]

            def update(self, mouse_rel):
                mouse = pygame.mouse.get_pos()
                mouse_down = pygame.mouse.get_pressed(3)[1]  # middle mouse button

                if mouse_down:
                    if self.range_selector1.collidepoint(mouse) or self.updating_block == 1:
                        self.updating = True
                        self.updating_block = 1
                        self.range_selector1.x += mouse_rel[0]
                    elif self.range_selector2.collidepoint(mouse) or self.updating_block == 2:
                        self.updating = True
                        self.updating_block = 2
                        self.range_selector2.x += mouse_rel[0]
                else:
                    self.updating = False
                    self.updating_block = None

                self.range = [self.range_selector1.x, self.range_selector2.x]

            def draw(self, wn):
                wn.blit(self.image, self.position)

                ui.dralpha(wn, (0, 0, 0, 180), self.range_selector1)
                ui.dralpha(wn, (0, 0, 0, 180), self.range_selector2)

                pygame.draw.line(wn, (0, 0, 0), (self.position.x, self.position.y+self.rect.h/2),
                                 (self.range_selector1.x, self.position.y+self.rect.h/2), 3)
                pygame.draw.line(wn, (0, 0, 0), (self.position.x+self.rect.w, self.position.y+self.rect.h/2),
                                 (self.range_selector2.x, self.position.y+self.rect.h / 2), 3)

        def __init__(self):
            self.popout_block_selector_rect = pygame.Rect(0, WN_HEIGHT / 2 - 50, 20, 100)
            self.popout_block_selector_label = pygame.Surface((100, 200), pygame.SRCALPHA)
            self.popout_block_selector_pos_config = ui.Positions(self.popout_block_selector_label)

            ui.write(self.popout_block_selector_label, "Config", (0, 0), self.popout_block_selector_pos_config.center,
                     [255] * 3, 13, font=PRESS_START_FONT, antialias=False)
            self.popout_block_selector_label = pygame.transform.rotate(self.popout_block_selector_label, -90)

            self.hovering_popout_selector = False
            self.opened = False

            self.grass_selector = PopoutMenu.BlockItem(level.Block, (17, 20), 0)
            self.stone_selector = PopoutMenu.BlockItem(level.Block, (57, 20), 1)
            self.dirt_selector = PopoutMenu.BlockItem(level.Block, (97, 20), 2)
            self.spike_selector = PopoutMenu.BlockItem(level.Block, (17, 60), 3)
            self.brick_selector = PopoutMenu.BlockItem(level.Block, (57, 60), 4)
            self.enemy_selector = PopoutMenu.BlockItem(level.Block, (97, 60), 5)

            self.grass_selector.instance.id = "grass"
            self.stone_selector.instance.id = "stone"
            self.dirt_selector.instance.id = "dirt"
            self.spike_selector.instance.id = "spike"
            self.brick_selector.instance.id = "brick"
            self.enemy_selector.instance.id = "enemy"

            self.selected_block = self.grass_selector
            self.selector_blocks = [self.grass_selector, self.stone_selector, self.dirt_selector, self.spike_selector,
                                    self.brick_selector, self.enemy_selector]

            self.popout_menu_pos_config = ui.Positions(pygame.Surface((150, WN_HEIGHT)))

            self.save_button = ui.TextButton("SAVE", (0, 0), self.popout_menu_pos_config.center, [[255]*3, [230]*3],
                                             20, font=PRESS_START_FONT)
            self.load_button = ui.TextButton("OPEN", (0, 30), self.popout_menu_pos_config.center, [[255] * 3, [230] * 3],
                                             20, font=PRESS_START_FONT)

            self.back_button = ui.TextButton("BACK", (0, 150), self.popout_menu_pos_config.center, [[255] * 3, [235, 20, 20]],
                                             20, font=PRESS_START_FONT)

        def draw(self, wn):
            if self.opened:
                ui.dralpha(wn, (0, 0, 0, 120), (0, 0, 150, WN_HEIGHT))

                for block in self.selector_blocks:
                    if self.selected_block == block:
                        ui.dralpha(wn, (255, 255, 255, 90), block.rect)  # the selected block has a lighter background

                    block.draw(wn)

                self.save_button.draw(wn)
                self.load_button.draw(wn)
                self.back_button.draw(wn)

            ui.dralpha(wn, (0, 0, 0, 150 + (self.hovering_popout_selector * 20)), self.popout_block_selector_rect)
            wn.blit(self.popout_block_selector_label,
                    (self.popout_block_selector_rect.x - 92, self.popout_block_selector_rect.y))

            self.hovering_popout_selector = self.popout_block_selector_rect.collidepoint(*pygame.mouse.get_pos())

        def update(self, event):
            if self.opened:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        for block in self.selector_blocks:
                            if block.rect.collidepoint(*pygame.mouse.get_pos()):
                                self.selected_block = block

        def pressed(self, event):
            return self.hovering_popout_selector and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1

        def toggle(self):
            self.opened = not self.opened

            if self.opened:
                self.popout_block_selector_rect = pygame.Rect(150, WN_HEIGHT / 2 - 50, 20, 100)
            else:
                self.popout_block_selector_rect = pygame.Rect(0, WN_HEIGHT / 2 - 50, 20, 100)

    def snap_to_grid(position: Vec2):
        return Vec2(round(position.x / GRID_SIZE[0]) * GRID_SIZE[0], round(position.y / GRID_SIZE[1]) * GRID_SIZE[1])

    def create_grid(surf, color=(255, 255, 255)):
        # top - bottom
        for x in range(0, WN_WIDTH, GRID_SIZE[0]):
            pygame.draw.line(surf, color, (x, 0), (x, surf.get_height()), 1)

        # left - right
        for y in range(0, WN_HEIGHT, GRID_SIZE[1]):
            pygame.draw.line(surf, color, (0, y), (surf.get_width(), y), 1)

    def save_canvas():
        try:
            with tkinter.filedialog.asksaveasfile(defaultextension=".lvl", filetypes=[("LVL Files", ".lvl")]) as f:
                data = ""

                for i, block in enumerate(blocks):
                    if type(block) == PopoutMenu.EnemyEditor:
                        data += f"{block.__class__.__name__},{int(block.position.x)},{int(block.position.y)},{block.id}," \
                                f"{block.range[0]},{block.range[1]}"
                    else:
                        data += f"{block.__class__.__name__},{int(block.position.x)},{int(block.position.y)},{block.id}"

                    if i != len(blocks) - 1:  # if we haven't reached the end, place a colon to seperate each block data
                        data += ":"

                f.write(data)
        except AttributeError as e:  # we pressed cancel
            print(e)

    def open_canvas():
        class Temp:
            EnemyEditor = PopoutMenu.EnemyEditor
            Block = level.Block

        try:
            with tkinter.filedialog.askopenfile(defaultextension=".lvl", filetypes=[("LVL Files", ".lvl")]) as f:
                new_canvas = []
                new_positions = []

                data = f.read()
                data_split = data.split(":")

                for block in data_split:
                    block_info = block.split(",")

                    print(block_info[0])

                    block_class = eval("Temp." + block_info[0])
                    block_id = block_info[3]

                    if block_id == "grass":
                        surf = level_spritesheet[0]
                    elif block_id == "stone":
                        surf = level_spritesheet[1]
                    elif block_id == "dirt":
                        surf = level_spritesheet[2]
                    elif block_id == "spike":
                        surf = level_spritesheet[3]
                    elif block_id == "brick":
                        surf = level_spritesheet[4]
                    elif block_id == "enemy":
                        surf = level_spritesheet[5]

                    if block_class == Temp.EnemyEditor:
                        new = block_class(Vec2(int(block_info[1]), int(block_info[2])), surf)
                        new.range = [int(block_info[4]), int(block_info[5])]
                    else:
                        new = block_class(Vec2(int(block_info[1]), int(block_info[2])), surf)

                    new_canvas.append(new)
                    new_canvas[-1].id = block_id
                    new_positions.append(Vec2(int(block_info[1]), int(block_info[2])))

                return new_canvas, new_positions
        except AttributeError as e:
            print(e)
            return blocks, block_positions

    def render():
        wn.fill(WN_COLOR)

        wn.blit(grid_surf, (0, 0))

        rel = pygame.mouse.get_rel()
        time = clock.get_time()

        for block in blocks:
            try:
                block.update(rel, time / 1000)
            except:
                block.update(rel)
            block.draw(wn)

        popout_menu.draw(wn)

        draw_mouse()

    run = True  # just in case we just want to stop the loop

    grid_surf = pygame.Surface((WN_WIDTH, WN_HEIGHT), pygame.SRCALPHA)
    create_grid(grid_surf, EDITOR_GRID_COLOR)
    level_spritesheet = spritesheet.SpriteSheet("assets/img/images.png", (16, 16), 2)

    popout_menu = PopoutMenu()

    blocks = []
    block_positions = []  # to speed up checking if there is a block already in the position

    while run:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if popout_menu.pressed(event):
                        popout_menu.toggle()
                    elif popout_menu.save_button.pressed(event):
                        save_canvas()
                    elif popout_menu.load_button.pressed(event):
                        blocks, block_positions = open_canvas()
                    elif popout_menu.back_button.pressed(event):
                        run = False

            mouse = Vec2(pygame.mouse.get_pos())
            snapped = snap_to_grid(mouse - Vec2(GRID_SIZE) / 2)

            if pygame.mouse.get_pressed(3)[0]:  # left mouse button
                if popout_menu.opened:
                    if mouse[0] > 150:
                        popout_menu.toggle()
                elif snapped not in block_positions:
                    # create a new instance of selected block
                    if popout_menu.selected_block.instance.id == "enemy":
                        new = PopoutMenu.EnemyEditor(
                            snapped, level_spritesheet[popout_menu.selected_block.spritesheet_index])
                    else:
                        new = popout_menu.selected_block.instance.__class__(
                            snapped, level_spritesheet[popout_menu.selected_block.spritesheet_index])
                        new.id = popout_menu.selected_block.instance.id

                    blocks.append(new)
                    block_positions.append(snapped)
                    print("Block placed.")

            if pygame.mouse.get_pressed(3)[2]:  # right mouse button
                if popout_menu.opened:
                    if mouse[0] > 150:
                        popout_menu.toggle()

                elif snapped in block_positions:
                    # create a new instance of selected block
                    index = block_positions.index(snapped)
                    blocks.pop(index)
                    block_positions.pop(index)
                    print("Block removed.")

            popout_menu.update(event)

        check_music()

        render()
        pygame.display.update()


main()
