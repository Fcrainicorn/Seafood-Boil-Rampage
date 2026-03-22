import pygame
from pygame import mixer
from pygame.locals import *
import random
import sys
import os
import datetime

# ---------------------------
# Pygame initialization
# ---------------------------
pygame.mixer.pre_init(44100, -16, 2, 512)
mixer.init()
pygame.init()

clock = pygame.time.Clock()
FPS = 60

SCREEN_W = 800
SCREEN_H = 600
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("SEAFOOD BOIL RAMPAGE")

# ---------------------------
# Font loading helper
# ---------------------------
def load_pixel_font(size):
    try:
        return pygame.font.Font("img/pixel_font.ttf", size)
    except:
        return pygame.font.SysFont("Courier", size, bold=True)

font16 = load_pixel_font(16)
font20 = load_pixel_font(20)
font24 = load_pixel_font(24)
font32 = load_pixel_font(32)
font48 = load_pixel_font(48)

# ---------------------------
# Load sounds & music
# ---------------------------
try:
    explosion_fx = pygame.mixer.Sound("img/explosion.wav")
    explosion_fx.set_volume(0.25)
    explosion2_fx = pygame.mixer.Sound("img/explosion2.wav")
    explosion2_fx.set_volume(0.25)
    laser_fx = pygame.mixer.Sound("img/laser.wav")
    laser_fx.set_volume(0.25)
except:
    pass 

gameplay_music = "img/m.mp3"
win_music = "img/winner_dinner_end_music.mp3"

RED   = (255, 0, 0)
GREEN = (0, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# ---------------------------
# Game layout / tuning constants
# ---------------------------
ROWS = 5
COLS = 7
ISLE_COOLDOWN = 900
LOBSTER_COOLDOWN   = 6000
LOBSTER_SPEED      = 2

PLAYER_COOLDOWN = 500
PLAYER_SPEED    = 6

BULLET_SPEED_PLAYER = -6
BULLET_SPEED_SHOPPER  = 3

POINTS_TABLE = {
    1: 10,
    2: 20,
    3: 40,
    4: 75,
    5: 100,
}

STATE_TITLE      = "title"
STATE_DIFF       = "difficulty"
STATE_GAME       = "game"
STATE_GAMEOVER   = "gameover"

game_state = STATE_TITLE
game_over_reason = None
win_music_started = False
lobsters_caught = 0

difficulties = ["WEEKDAY", "WEEKEND", "HOLIDAY"]
diff_index = 0

ingredient_move_speed_by_diff = {
    "WEEKDAY":   9,
    "WEEKEND": 12,
    "HOLIDAY":   30
}

# ---------------------------
# Background images setup
# ---------------------------
try:
    bg = pygame.image.load("img/bg.png").convert()
    bg = pygame.transform.scale(bg, (SCREEN_W, SCREEN_H))
except: bg = None

win_bg = None
try: 
    win_bg = pygame.image.load("img/seafoodboil.png").convert()
    win_bg = pygame.transform.scale(win_bg, (SCREEN_W, SCREEN_H))
except: pass

def draw_bg():
    if bg: screen.blit(bg, (0, 0))
    else: screen.fill(BLACK)

# ---------------------------
# Text & External File Helpers
# ---------------------------
def draw_text_center(text, font, color, y):
    img = font.render(text, True, color)
    rect = img.get_rect(center=(SCREEN_W // 2, y))
    screen.blit(img, rect)
    return rect

def draw_text_topleft(text, font, color, x, y):
    img = font.render(text, True, color)
    rect = img.get_rect(topleft=(x, y))
    screen.blit(img, rect)
    return rect

def generate_gold_receipt():
    global lobsters_caught
    
    now = datetime.datetime.now()
    date_str = now.strftime("%m/%d/%Y")
    time_str = now.strftime("%I:%M %p")
    
    # Prices converted: 10 points = $1.00
    lobster_sub = lobsters_caught * 10.00
    total_cost = 108.50 + lobster_sub
    
    receipt_content = f"""          COASTAL CATCH 
      501 OCEAN AVENUE NORTH
         JERSEY SHORE, NJ
    --------------------------------
    {date_str}  {time_str}   STORE: 07
    REG: 04               OP: 77
    --------------------------------
    
    14  EGGS           1.00       14.00
    07  CORN           2.00       14.00
    07  SHRIMP         4.00       28.00
    07  BLUE CRAB      7.50       52.50
    {lobsters_caught:02d}  LOBSTER       10.00       {lobster_sub:.2f}
    
    --------------------------------
    TOTAL                       ${total_cost:.2f}
    --------------------------------
    
    PAYMENT TYPE: SKILL
    
    *** GOLD STANDARD STATUS ***
    
    --------------------------------
    THANK YOU FOR SHOPPING.
    --------------------------------"""

    with open("receipt.txt", "w") as f:
        f.write(receipt_content)
        
    try:
        if os.name == 'nt':
            os.startfile("receipt.txt")
        else:
            os.system("open receipt.txt")
    except Exception as e:
        print(f"Could not open receipt: {e}")

# ---------------------------
# Sprite Groups
# ---------------------------
shopping_cart_group   = pygame.sprite.Group()
bullet_group          = pygame.sprite.Group()
ingredients_group     = pygame.sprite.Group()
shopper_bullet_group  = pygame.sprite.Group()
explosion_group       = pygame.sprite.Group()
lobster_group         = pygame.sprite.Group()

last_shopper = 0
last_lobster_spawn = 0
score = 0
countdown = 3
last_count = 0
can_shoot = False

ingredient_dir = 1
ingredient_step_down = 16
ingredient_move_timer = 0
ingredient_move_delay = 20

# ---------------------------
# CLASSES
# ---------------------------
class Shopping_cart(pygame.sprite.Sprite):
    def __init__(self, x, y, health):
        super().__init__()
        try:
            self.image = pygame.image.load("img/shoppingcart.png")
        except:
            self.image = pygame.Surface((40, 40))
            self.image.fill(GREEN)
            
        self.rect = self.image.get_rect(center=(x, y))
        self.health_start = health
        self.health_remaining = health
        self.last_shot = pygame.time.get_ticks()

    def update(self):
        global game_state, game_over_reason
        key = pygame.key.get_pressed()

        if key[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= PLAYER_SPEED
        if key[pygame.K_RIGHT] and self.rect.right < SCREEN_W:
            self.rect.x += PLAYER_SPEED

        now = pygame.time.get_ticks()
        if can_shoot and key[pygame.K_SPACE] and now - self.last_shot > PLAYER_COOLDOWN:
            try: laser_fx.play()
            except: pass
            bullet = PlayerBullet(self.rect.centerx, self.rect.top)
            bullet_group.add(bullet)
            self.last_shot = now

        self.mask = pygame.mask.from_surface(self.image)
        bar_w = self.rect.width
        bar_x = self.rect.x
        bar_y = self.rect.bottom + 6

        pygame.draw.rect(screen, RED, (bar_x, bar_y, bar_w, 10))
        if self.health_remaining > 0:
            pygame.draw.rect(screen, GREEN, (bar_x, bar_y, int(bar_w * (self.health_remaining / self.health_start)), 10))
        else:
            explosion_group.add(Explosion(self.rect.centerx, self.rect.centery, 3))
            self.kill()
            
            # --- SILENCE MUSIC ON DEATH ---
            pygame.mixer.music.stop()
            game_state = STATE_GAMEOVER
            game_over_reason = "lose"

class PlayerBullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        try:
            self.image = pygame.image.load("img/bullet.png")
        except:
            self.image = pygame.Surface((5, 15))
            self.image.fill(WHITE)
        self.rect = self.image.get_rect(center=(x, y))

    def update(self):
        global score, lobsters_caught
        self.rect.y += BULLET_SPEED_PLAYER
        if self.rect.bottom < 0:
            self.kill()
            return

        hits = pygame.sprite.spritecollide(self, ingredients_group, True, pygame.sprite.collide_mask)
        if hits:
            self.kill()
            try: explosion_fx.play()
            except: pass
            for ingredient in hits:
                explosion_group.add(Explosion(self.rect.centerx, self.rect.centery, 2))
                score += POINTS_TABLE.get(ingredient.ingredient_type, 0)

        hits_lobster = pygame.sprite.spritecollide(self, lobster_group, True, pygame.sprite.collide_mask)
        if hits_lobster:
            self.kill()
            try: explosion_fx.play()
            except: pass
            for lobster in hits_lobster:
                explosion_group.add(Explosion(self.rect.centerx, self.rect.centery, 2))
                score += POINTS_TABLE.get(lobster.ingredient_type, 0)
                lobsters_caught += 1 

class Ingredient(pygame.sprite.Sprite):
    def __init__(self, x, y, ingredient_type):
        super().__init__()
        self.ingredient_type = ingredient_type
        try:
            self.image = pygame.image.load(f"img/ingredient{ingredient_type}.png")
        except:
            self.image = pygame.Surface((30, 30))
            self.image.fill(WHITE)
        self.rect = self.image.get_rect(center=(x, y))
        self.mask = pygame.mask.from_surface(self.image)

    def shift(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

class LOBSTER(pygame.sprite.Sprite):
    def __init__(self, y=50):
        super().__init__()
        self.ingredient_type = 5
        try:
            self.image = pygame.image.load("img/ingredient5.png")
        except:
            self.image = pygame.Surface((40, 40))
            self.image.fill(RED)
        self.rect = self.image.get_rect(midleft=(-60, y))
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        self.rect.x += LOBSTER_SPEED
        if self.rect.left > SCREEN_W + 60:
            self.kill()

class OtherShoppers(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        try:
            self.image = pygame.image.load("img/shopper.png")
        except:
            self.image = pygame.Surface((15, 15))
            self.image.fill(RED)
        self.rect = self.image.get_rect(center=(x, y))

    def update(self):
        self.rect.y += BULLET_SPEED_SHOPPER
        if self.rect.top > SCREEN_H:
            self.kill()
            return

        hit_ship = pygame.sprite.spritecollide(self, shopping_cart_group, False, pygame.sprite.collide_mask)
        if hit_ship:
            self.kill()
            try: explosion2_fx.play()
            except: pass
            for ship in hit_ship:
                ship.health_remaining -= 1
            explosion_group.add(Explosion(self.rect.centerx, self.rect.centery, 1))

class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, size):
        super().__init__()
        self.images = []
        for num in range(1, 6):
            try:
                img = pygame.image.load(f"img/exp{num}.png")
                if size == 1: img = pygame.transform.scale(img, (20, 20))
                elif size == 2: img = pygame.transform.scale(img, (40, 40))
                elif size == 3: img = pygame.transform.scale(img, (120, 120))
                self.images.append(img)
            except: pass
        
        if not self.images:
            surf = pygame.Surface((20, 20))
            surf.fill(RED)
            self.images.append(surf)

        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect(center=(x, y))
        self.counter = 0

    def update(self):
        explosion_speed = 3
        self.counter += 1
        if self.counter >= explosion_speed and self.index < len(self.images) - 1:
            self.counter = 0
            self.index += 1
            self.image = self.images[self.index]
        if self.index >= len(self.images) - 1 and self.counter >= explosion_speed:
            self.kill()

# ---------------------------
# Logic Helpers
# ---------------------------
def get_ingredient_bounds():
    xs = [a.rect.x for a in ingredients_group]
    rs = [a.rect.right for a in ingredients_group]
    ys = [a.rect.bottom for a in ingredients_group]
    if not xs: return 0, 0, 0
    return min(xs), max(rs), max(ys)

def move_ingredient_block(move_speed):
    global ingredient_dir, ingredient_step_down
    if len(ingredients_group) == 0: return

    left_edge, right_edge, _ = get_ingredient_bounds()
    hit_right_wall = (ingredient_dir > 0 and right_edge + move_speed >= SCREEN_W - 20)
    hit_left_wall  = (ingredient_dir < 0 and left_edge  - move_speed <= 20)

    if hit_right_wall or hit_left_wall:
        ingredient_dir *= -1
        for ingredient in ingredients_group:
            ingredient.shift(0, ingredient_step_down)
    else:
        for ingredient in ingredients_group:
            ingredient.shift(move_speed * ingredient_dir, 0)

def check_player_loss_by_closing():
    global game_state, game_over_reason
    if len(ingredients_group) == 0: return
    _, _, lowest_y = get_ingredient_bounds()

    if lowest_y >= SCREEN_H - 140:
        pygame.mixer.music.stop()
        game_state = STATE_GAMEOVER
        game_over_reason = "lose"

def create_ingredients():
    ingredients_group.empty()
    start_x, start_y = 120, 100
    x_gap, y_gap = 70, 50

    for row in range(ROWS):
        if row <= 1: i_type = 1
        elif row == 2: i_type = 2
        elif row == 3: i_type = 3
        else: i_type = 4

        for col in range(COLS):
            x = start_x + col * x_gap
            y = start_y + row * y_gap
            ingredients_group.add(Ingredient(x, y, i_type))

def reset_game(selected_diff_name):
    global score, countdown, last_count, last_shopper, last_lobster_spawn, can_shoot
    global ingredient_dir, ingredient_move_delay, ingredient_move_timer, ingredient_step_down
    global win_music_started, lobsters_caught
    
    pygame.mixer.music.stop()
    try:
        pygame.mixer.music.load(gameplay_music)
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)
    except: pass
    
    win_music_started = False
    score = 0
    lobsters_caught = 0
    countdown = 3
    last_count = pygame.time.get_ticks()
    can_shoot = False

    last_shopper = pygame.time.get_ticks()
    last_lobster_spawn  = pygame.time.get_ticks()

    ingredient_dir = 1
    ingredient_move_timer = 0

    if selected_diff_name == "WEEKDAY":
        ingredient_move_delay = 28
        ingredient_step_down  = 16
    elif selected_diff_name == "WEEKEND":
        ingredient_move_delay = 18
        ingredient_step_down  = 24
    else:
        ingredient_move_delay = 8
        ingredient_step_down  = 32

    shopping_cart_group.empty()
    bullet_group.empty()
    ingredients_group.empty()
    shopper_bullet_group.empty()
    explosion_group.empty()
    lobster_group.empty()

    ship = Shopping_cart(SCREEN_W // 2, SCREEN_H - 80, 3)
    shopping_cart_group.add(ship)
    create_ingredients()

# ---------------------------
# Drawing functions
# ---------------------------
def draw_title_screen():
    screen.fill(BLACK)
    rows_y = [150, 195, 240, 285, 330]
    pt_vals = ["    10 PTS", "    20 PTS", "    40 PTS", "    75 PTS", "   100 PTS"]
    ingredient_imgs = ["ingredient1.png", "ingredient2.png", "ingredient3.png", "ingredient4.png", "ingredient5.png"]

    for i, y in enumerate(rows_y):
        try:
            img = pygame.image.load("img/" + ingredient_imgs[i])
            img_rect = img.get_rect()
            img_rect.centerx = SCREEN_W // 2 - 70
            img_rect.centery = y
            screen.blit(img, img_rect)
        except: pass
        draw_text_center(pt_vals[i], font24, WHITE, y)

    draw_text_center("PLAY SEAFOOD BOIL RAMPAGE", font32, WHITE, 80)
    draw_text_center("PRESS ENTER", font24, WHITE, 420)

def draw_difficulty_screen(selected_i):
    screen.fill(BLACK)
    draw_text_center("SELECT DIFFICULTY", font32, WHITE, 200)

    for i, name in enumerate(difficulties):
        color = WHITE if i == selected_i else (100, 100, 100)
        draw_text_center(name, font32, color, 260 + i * 40)
    draw_text_center("ARROWS TO MOVE  •  ENTER TO START", font16, WHITE, 380)

def draw_gameover_screen(reason):
    if reason == "win":
        if win_bg: screen.blit(win_bg, (0, 0))
        else: screen.fill(BLACK)
        draw_text_center("SEASONED TO PERFECTION!", font32, WHITE, SCREEN_H // 2 - 40)
        draw_text_center("Press ENTER to return your cart", font24, WHITE, SCREEN_H // 2 + 50)
    else:
        screen.fill(BLACK)
        draw_text_center("GAME OVER", font48, RED, SCREEN_H // 2 - 50)
        draw_text_center("Press ENTER to return your cart", font24, WHITE, SCREEN_H // 2 + 50)
        draw_text_center(f"SCORE: {score}", font24, WHITE, SCREEN_H // 2 + 90)

# ---------------------------
# MAIN LOOP
# ---------------------------
running = True
while running:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        if event.type == KEYDOWN:
            if game_state == STATE_TITLE:
                if event.key == K_RETURN: game_state = STATE_DIFF
            elif game_state == STATE_DIFF:
                if event.key == K_UP: diff_index = (diff_index - 1) % len(difficulties)
                elif event.key == K_DOWN: diff_index = (diff_index + 1) % len(difficulties)
                elif event.key == K_RETURN:
                    reset_game(difficulties[diff_index])
                    game_state = STATE_GAME
                    game_over_reason = None
            elif game_state == STATE_GAMEOVER:
                if event.key == K_RETURN: game_state = STATE_DIFF

    if game_state == STATE_TITLE:
        draw_title_screen()
        pygame.display.update()
        continue

    if game_state == STATE_DIFF:
        draw_difficulty_screen(diff_index)
        pygame.display.update()
        continue

    if game_state == STATE_GAME:
        draw_bg()

        if countdown > 0:
            shopping_cart_group.update()
            bullet_group.update()
            ingredients_group.update()
            shopper_bullet_group.update()
            lobster_group.update()
            explosion_group.update()

            shopping_cart_group.draw(screen)
            bullet_group.draw(screen)
            ingredients_group.draw(screen)
            shopper_bullet_group.draw(screen)
            lobster_group.draw(screen)
            explosion_group.draw(screen)

            draw_text_topleft(f"SCORE: {score}", font20, WHITE, 20, 20)
            
            draw_text_center("GET READY!", font48, WHITE, SCREEN_H // 2 - 30)
            draw_text_center(str(countdown), font48, WHITE, SCREEN_H // 2 + 30)

            now = pygame.time.get_ticks()
            if now - last_count > 1000:
                countdown -= 1
                last_count = now
                if countdown <= 0:
                    countdown = 0
                    can_shoot = True

            pygame.display.update()
            continue

        now = pygame.time.get_ticks()

        if (now - last_shopper > ISLE_COOLDOWN and len(shopper_bullet_group) < 4 and len(ingredients_group) > 0):
            attacker = random.choice(ingredients_group.sprites())
            shopper_bullet_group.add(OtherShoppers(attacker.rect.centerx, attacker.rect.bottom))
            last_shopper = now

        if now - last_lobster_spawn > LOBSTER_COOLDOWN:
            if random.random() < 0.4 and len(lobster_group) == 0:
                lobster_group.add(LOBSTER())
            last_lobster_spawn = now

        ingredient_move_timer += 1
        if ingredient_move_timer >= ingredient_move_delay:
            ingredient_move_timer = 0
            move_ingredient_block(ingredient_move_speed_by_diff[difficulties[diff_index]])

        check_player_loss_by_closing()
        
        # Check if the player won
        if len(ingredients_group) == 0 and len(shopping_cart_group) > 0:
            
            if not win_music_started: 
                pygame.mixer.music.stop()
                try:
                    pygame.mixer.music.load(win_music) 
                    pygame.mixer.music.set_volume(0.4)
                    pygame.mixer.music.play(-1)
                except: pass
                
                # TRIGGER RECEIPT IF LOBSTER CAUGHT
                if lobsters_caught > 0:
                    generate_gold_receipt()
                
                win_music_started = True           
                
            game_state = STATE_GAMEOVER
            game_over_reason = "win"

        if game_state == STATE_GAMEOVER:
            draw_gameover_screen(game_over_reason)
            pygame.display.update()
            continue

        shopping_cart_group.update()
        bullet_group.update()
        ingredients_group.update()
        shopper_bullet_group.update()
        lobster_group.update()
        explosion_group.update()

        shopping_cart_group.draw(screen)
        bullet_group.draw(screen)
        ingredients_group.draw(screen)
        shopper_bullet_group.draw(screen)
        lobster_group.draw(screen)
        explosion_group.draw(screen)

        draw_text_topleft(f"SCORE: {score}", font20, WHITE, 20, 20)
        
        pygame.display.update()
        continue

    if game_state == STATE_GAMEOVER:
        draw_gameover_screen(game_over_reason)
        pygame.display.update()
        continue

pygame.quit()
sys.exit()
