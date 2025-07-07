import pygame
import sys
import random
import time
import math 

pygame.init()
pygame.mixer.init()

# Constants
WIDTH, HEIGHT = 1000, 750
GRID_SIZE = 25
GRID_WIDTH = WIDTH // GRID_SIZE
GRID_HEIGHT = HEIGHT // GRID_SIZE
FPS = 10

# Global state variables for audio and game status
is_global_muted = False    
global_volume = 0.5        # مستوى الصوت العام للموسيقى 
sound_effects_list = []    

game_over_sound_played_once = False 
game_over_channel = None 
game_over_reason = None    

current_playing_music_path = None # مسار الموسيقى الخلفية النشطة حاليًا

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Game")
clock = pygame.time.Clock()

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)
MAGENTA = (255, 0, 255)
GRAY = (128, 128, 128)
DARK_GRAY = (60, 60, 60) # For smoke particles

# --- Load Assets (Images and Sounds) ---
background_image = None
try:
    background_image = pygame.image.load("backgroud.png").convert_alpha()
    background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))
except pygame.error as e:
    print(f"Error loading background image 'backgroud.png': {e}. Please ensure the file exists.")
    background_image = pygame.Surface((WIDTH, HEIGHT))
    background_image.fill(BLACK)

eat_sound = None
coin_sound = None
game_over_sound = None
move_sound = None
shield_pickup_sound = None 
shield_deactivate_sound = None 
shield_spawn_sound = None 
extra_life_sound = None


try:
    eat_sound = pygame.mixer.Sound("eat.mp3")
    eat_sound.set_volume(1.0) # صوت الأكل دائمًا بكامل حجمه (لا يتأثر بالكتم العام)
except pygame.error as e:
    print(f"Error loading sound 'eat.mp3': {e}. Please ensure the file exists.")

try:
    coin_sound = pygame.mixer.Sound("coin.mp3")
    coin_sound.set_volume(1.0) # صوت العملة دائمًا بكامل حجمه (لا يتأثر بالكتم العام)
except pygame.error as e:
    print(f"Error loading sound 'coin.mp3': {e}. Please ensure the file exists.")

try:
    game_over_sound = pygame.mixer.Sound("gameOver.mp3")
    #sound_effects_list.append(game_over_sound) # هذا الصوت يتأثر بالكتم العام ومستوى الصوت
    game_over_sound.set_volume(1.0)
except pygame.error as e:
    print(f"Error loading sound 'gameOver.mp3': {e}. Please ensure the file exists.")

try:
    move_sound = pygame.mixer.Sound("move.mp3")
    move_sound.set_volume(1.0) # صوت التنقل دائمًا بكامل حجمه (لا يتأثر بالكتم العام)
except pygame.error as e:
    print(f"Error loading sound 'move.mp3': {e}. Please ensure the file exists.")

# NEW: Load Shield Pickup, Deactivation, and Spawn Sounds
try:
    shield_pickup_sound = pygame.mixer.Sound("shield.mp3") 
    shield_pickup_sound.set_volume(1.0) # لا يتأثر بالكتم العام
except pygame.error as e:
    print(f"Error loading sound 'shield.mp3': {e}. Please ensure the file exists.")

try:
    shield_deactivate_sound = pygame.mixer.Sound("shield_deactivate.mp3") 
    shield_deactivate_sound.set_volume(1.0) # لا يتأثر بالكتم العام
except pygame.error as e:
    print(f"Error loading sound 'shield_deactivate.mp3': {e}. Please ensure the file exists.")

try:
    shield_spawn_sound = pygame.mixer.Sound("shield_spawn.mp3") # NEW: New sound for spawning
    shield_spawn_sound.set_volume(1.0) # لا يتأثر بالكتم العام
except pygame.error as e:
    print(f"Error loading sound 'shield_spawn.mp3': {e}. Please ensure the file exists.")
try:
    extra_life_sound = pygame.mixer.Sound("extra_life.mp3") 
    extra_life_sound.set_volume(1.0) # Always at full volume
    
except pygame.error as e:
    print(f"Error loading sound 'extra_life.mp3': {e}")
life_pickup_sound = None

try:
    life_pickup_sound = pygame.mixer.Sound("life_pickup.mp3")
    life_pickup_sound.set_volume(1.0)
except pygame.error as e:
    print(f"Error loading sound 'life_pickup.mp3': {e}")

background_music_path = "backgroundSound.wav"
run_music_path = "runGame.mp3"

# Player and Food Configurations
PLAYER_COLORS_INFO = [
    {"name": "Red", "color": RED},
    {"name": "Green", "color": GREEN},
    {"name": "Blue", "color": BLUE},
    {"name": "Yellow", "color": YELLOW},
    {"name": "Purple", "color": PURPLE},
    {"name": "Cyan", "color": CYAN}
]

FOOD_TYPES = [
    {"name": "Apple", "color": RED, "score": 1, "lifetime": 15, "image_path": "apple.png", "image_surface": None, "sound_type": None},
    {"name": "Banana", "color": YELLOW, "score": 2, "lifetime": 12, "image_path": "banana.png", "image_surface": None, "sound_type": None},
    {"name": "Orange", "color": ORANGE, "score": 3, "lifetime": 10, "image_path": "orange.png", "image_surface": None, "sound_type": None},
    {"name": "Grape", "color": PURPLE, "score": 4, "lifetime": 8, "image_path": "grape.png", "image_surface": None, "sound_type": None},
    {"name": "Cherry", "color": MAGENTA, "score": 5, "lifetime": 7, "image_path": "cherry.jpeg", "image_surface": None, "sound_type": None},
    {"name": "Lime", "color": GREEN, "score": 6, "lifetime": 6, "image_path": "lime.webp", "image_surface": None, "sound_type": None},
    {"name": "Blueberry", "color": BLUE, "score": 7, "lifetime": 5, "image_path": "blueberry.png", "image_surface": None, "sound_type": None},
    {"name": "Coin", "color": YELLOW, "score": 8, "lifetime": 4, "image_path": "coin.jpg", "image_surface": None, "sound_type": "coin"},
    # Shield Power-up with its specific sound type
    {"name": "Shield", "color": BLUE, "score": 0, "lifetime": 8, "image_path": "https://placehold.co/25x25/ADD8E6/000000?text=S", "image_surface": None, "sound_type": "shield"},
    {"name": "Extra Life", "color": MAGENTA, "score": 0, "lifetime": 10, "image_path": "https://placehold.co/25x25/FF00FF/FFFFFF?text=L", "image_surface": None, "sound_type": "extra_life"}
]

for food_item in FOOD_TYPES:
    if food_item["image_path"]:
        try:
            # If it's a URL, use a placeholder. Otherwise, load from file.
            if food_item["image_path"].startswith("http"):
                # For placeholder images, we just create a surface of the specified color/size
                img_surface = pygame.Surface((GRID_SIZE, GRID_SIZE), pygame.SRCALPHA)
                img_surface.fill(food_item["color"]) 
                font_icon = pygame.font.SysFont('Arial', GRID_SIZE - 5, bold=True)
                text_surf = font_icon.render(food_item["image_path"].split('text=')[1], True, BLACK) 
                text_rect = text_surf.get_rect(center=(GRID_SIZE // 2, GRID_SIZE // 2))
                img_surface.blit(text_surf, text_rect)
                food_item["image_surface"] = img_surface
            else:
                img = pygame.image.load(food_item["image_path"]).convert_alpha()
                food_item["image_surface"] = pygame.transform.scale(img, (GRID_SIZE, GRID_SIZE))
        except pygame.error as e:
            print(f"Error loading food image '{food_item['image_path']}': {e}. Please ensure the file exists or URL is valid.")
            food_item["image_surface"] = None

# Fonts
font_large = pygame.font.SysFont('Arial', 60)
font_medium = pygame.font.SysFont('Arial', 35)
font_small = pygame.font.SysFont('Arial', 25)
font_winner = pygame.font.SysFont('Arial', 55, bold=True)
font_score_summary = pygame.font.SysFont('Arial', 30)
font_info_title = pygame.font.SysFont('Arial', 45, bold=True)
font_food_item = pygame.font.SysFont('Arial', 28)
font_instructions = pygame.font.SysFont('Arial', 22)
font_color_name = pygame.font.SysFont('Arial', 30)
font_mute_indicator = pygame.font.SysFont('Arial', 20)
font_volume_indicator = pygame.font.SysFont('Arial', 20)
font_game_over_reason = pygame.font.SysFont('Arial', 30, bold=True)

# Particle Class for explosion effects
class Particle:
    def __init__(self, x, y, color, size, speed_x, speed_y, decay_rate):
        self.x = x
        self.y = y
        self.color = list(color) 
        self.size = size
        self.speed_x = speed_x
        self.speed_y = speed_y
        self.decay_rate = decay_rate 
        self.alpha = 255 
        self.is_alive = True

    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y
        self.size *= 0.95 
        self.alpha -= self.decay_rate 
        if self.alpha < 0 or self.size < 1:
            self.is_alive = False

    def grow(self, points):
        self.grow_to += points
        self.score += points 

    def draw(self, surface):
        if self.is_alive:
            draw_color = self.color[:3] + [max(0, int(self.alpha))]
            s = pygame.Surface((int(self.size * 2), int(self.size * 2)), pygame.SRCALPHA)
            pygame.draw.circle(s, draw_color, (int(self.size), int(self.size)), int(self.size))
            surface.blit(s, (self.x - self.size, self.y - self.size))


def draw_mute_indicator(surface):
    # يعرض مؤشر كتم/تشغيل الصوت
    global is_global_muted
    indicator_text = "Mute (M)" if is_global_muted else "Sound On (M)"
    text_color = RED if is_global_muted else GREEN # Or any colors you prefer
    indicator_surface = font_small.render(indicator_text, True, text_color)
    screen.blit(indicator_surface, (WIDTH - indicator_surface.get_width() - 10, 10))


def draw_volume_indicator(surface):
    # يعرض مؤشر مستوى الصوت
    global global_volume
    volume_text = f"Vol: {int(global_volume * 100)}% (+/-)"
    text_surface = font_volume_indicator.render(volume_text, True, WHITE)
    mute_indicator_rect = font_mute_indicator.render("Muted (M)", True, RED).get_rect(topright=(WIDTH - 10, 10))
    text_rect = text_surface.get_rect(topright=(WIDTH - 10, mute_indicator_rect.bottom + 5))
    surface.blit(text_surface, text_rect)

def apply_global_volume():
    # يطبق مستوى الصوت العام على الموسيقى والأصوات المتأثرة
    global is_global_muted, global_volume, sound_effects_list
    
    if pygame.mixer.get_init():
        if is_global_muted:
            pygame.mixer.music.set_volume(0)
        else:
            pygame.mixer.music.set_volume(global_volume)
       
        for sound_obj in sound_effects_list:
            if sound_obj:
                if is_global_muted:
                    sound_obj.set_volume(0)
                else:
                    sound_obj.set_volume(global_volume)
        
def play_background_music(path):
    # يتحكم في تشغيل موسيقى الخلفية بين الشاشات
    global current_playing_music_path, is_global_muted, global_volume
    
    if current_playing_music_path != path or not pygame.mixer.music.get_busy():
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.play(-1)
            current_playing_music_path = path
            if is_global_muted:
                pygame.mixer.music.set_volume(0)
            else:
                pygame.mixer.music.set_volume(global_volume)
        except pygame.error as e:
            print(f"Error playing music '{path}': {e}")
    else:
        if is_global_muted:
            pygame.mixer.music.set_volume(0)
        else:
            pygame.mixer.music.set_volume(global_volume)
        if not pygame.mixer.music.get_busy() and not is_global_muted:
            pygame.mixer.music.unpause()


class Snake:
    def __init__(self, x, y, color, controls):
        self.positions = [(x, y)]
        self.direction = (1, 0)
        self.color = color
        self.controls = controls
        self.score = 0
        self.grow_to = 3
        self.is_alive = True
        self.is_shielded = False 
        self.shield_end_time = 0 
        self.lives = 0
    def get_head_position(self):
        return self.positions[0]
        
    def update(self):
        # تحديث موقع الأفعى وكشف الاصطدامات الذاتية
        if not self.is_alive:
            return True

        # Check and deactivate shield if time is up
        if self.is_shielded and time.time() > self.shield_end_time:
            self.is_shielded = False
            if shield_deactivate_sound: # Play deactivate sound
                shield_deactivate_sound.play()


        head = self.get_head_position()
        x, y = self.direction
        new_x = (head[0] + x) % GRID_WIDTH
        new_y = (head[1] + y) % GRID_HEIGHT
        new_position = (new_x, new_y)
        
        # Self-collision detection
        if new_position in self.positions[:-1]:
            if not self.is_shielded:
                if self.lives > 0:
                    self.lives -= 1
                    self.positions = [self.positions[0]]  # يرجع بحجم صغير
                    self.grow_to = 3
                    if life_pickup_sound: life_pickup_sound.play()
                    return True
                else:
                    self.is_alive = False
                    return False


            
        self.positions.insert(0, new_position)
        if len(self.positions) > self.grow_to:
            self.positions.pop()
        return True # Indicate successful update
        
    def grow(self, points):
        self.grow_to += points
        self.score += points
        
    def change_direction(self, new_dir):
       
        if (new_dir[0] * -1, new_dir[1] * -1) != self.direction:
            self.direction = new_dir
        
    def draw(self, surface):
        # رسم الأفعى ورأسها بالعيون، مع مؤشر الدرع إذا كان نشطاً
        for i, p in enumerate(self.positions):
            rect = pygame.Rect(p[0] * GRID_SIZE, p[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE)
            pygame.draw.rect(surface, self.color, rect)
            pygame.draw.rect(surface, BLACK, rect, 1)

            # Draw eyes on the snake's head
            if i == 0:
                eye_color = BLACK
                eye_size = 4
                eye_offset = GRID_SIZE // 4

                if self.direction == (0, -1): # Up
                    eye1_pos = (rect.centerx - eye_offset, rect.centery - eye_offset)
                    eye2_pos = (rect.centerx + eye_offset, rect.centery - eye_offset)
                elif self.direction == (0, 1): # Down
                    eye1_pos = (rect.centerx - eye_offset, rect.centery + eye_offset)
                    eye2_pos = (rect.centerx + eye_offset, rect.centery + eye_offset)
                elif self.direction == (-1, 0): # Left
                    eye1_pos = (rect.centerx - eye_offset, rect.centery - eye_offset)
                    eye2_pos = (rect.centerx - eye_offset, rect.centery + eye_offset)
                elif self.direction == (1, 0): # Right
                    eye1_pos = (rect.centerx + eye_offset, rect.centery - eye_offset)
                    eye2_pos = (rect.centerx + eye_offset, rect.centery + eye_offset)
                else:
                    eye1_pos = (rect.centerx - eye_offset, rect.centery - eye_offset)
                    eye2_pos = (rect.centerx + eye_offset, rect.centery - eye_offset)
                
                pygame.draw.circle(surface, eye_color, eye1_pos, eye_size // 2)
                pygame.draw.circle(surface, eye_color, eye2_pos, eye_size // 2)

                # Draw shield visual if active (simple pulsing outline around head)
                if self.is_shielded:
                    # Calculate pulsing alpha for glow effect
                    pulse_width = int(2 + 2 * abs(math.sin(time.time() * 5))) # Pulsing width from 2 to 4
                    
                    shield_color = YELLOW
                    # Draw a slightly thicker outline around the head segment
                    pygame.draw.rect(surface, shield_color, rect, pulse_width)


class Food:
    def __init__(self, food_type):
        self.food_type = food_type
        self.position = (0, 0)
        self.color = food_type["color"]
        self.score_value = food_type["score"]
        self.lifetime = food_type["lifetime"]
        self.spawn_time = time.time()
        self.image = food_type["image_surface"]
        self.sound_type = food_type["sound_type"]
        self.randomize_position()

        # Play shield spawn sound if this is a shield food
        if self.sound_type == "shield" and shield_spawn_sound:
            shield_spawn_sound.play()
        
    def randomize_position(self, snake_positions=None, existing_food_positions=None):
        # يحدد موقعًا عشوائيًا للطعام يتجنب الأفاعي والطعام الآخر
        if snake_positions is None:
            snake_positions = []
        if existing_food_positions is None:
            existing_food_positions = []
        
        occupied_positions = set(snake_positions + existing_food_positions)

        while True:
            self.position = (random.randint(0, GRID_WIDTH - 1)),(random.randint(0, GRID_HEIGHT - 1))
            if self.position not in occupied_positions:
                break
        
    def draw(self, surface):
        food_rect = pygame.Rect(self.position[0] * GRID_SIZE, self.position[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE)
        
        if self.image:
            surface.blit(self.image, food_rect.topleft)
        else:
            pygame.draw.rect(surface, self.color, food_rect)
        
        pygame.draw.rect(surface, BLACK, food_rect, 1)

        time_elapsed = time.time() - self.spawn_time
        time_remaining = max(0, self.lifetime - time_elapsed)
        
        bar_max_width = GRID_SIZE
        current_bar_width = int(bar_max_width * (time_remaining / self.lifetime))
        
        bar_height = 6 

        bar_x = self.position[0] * GRID_SIZE
        bar_y = self.position[1] * GRID_SIZE - bar_height - 1

        time_ratio = time_remaining / self.lifetime
        
        r = int(RED[0] + time_ratio * (GREEN[0] - RED[0]))
        g = int(RED[1] + time_ratio * (GREEN[1] - RED[1]))
        b = int(RED[2] + time_ratio * (GREEN[2] - RED[2]))
        
        bar_color = (r, g, b)
        
        pygame.draw.rect(surface, GRAY, (bar_x, bar_y, bar_max_width, bar_height), 0, 2)
        
        if current_bar_width > 0:
            pygame.draw.rect(surface, bar_color, (bar_x, bar_y, current_bar_width, bar_height), 0, 2)

        pygame.draw.rect(surface, BLACK, (bar_x, bar_y, bar_max_width, bar_height), 1, 2)


    def is_expired(self):
        # يتحقق مما إذا انتهى عمر الطعام الافتراضي
        return (time.time() - self.spawn_time) > self.lifetime


class ScorePopUp: 
    def __init__(self, x, y, text, color):
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.start_time = time.time()
        self.lifetime = 1.0 
        self.speed_y = -30 
        self.alpha = 255 
        self.font = font_small 
        self.is_alive = True

    def update(self):
        self.y += self.speed_y * (1 / FPS) 
        time_elapsed = time.time() - self.start_time
        ratio = time_elapsed / self.lifetime
        self.alpha = max(0, 255 - int(ratio * 255)) 
        if ratio >= 1.0:
            self.is_alive = False

    def draw(self, surface):
        if self.is_alive:
            text_surface = self.font.render(self.text, True, self.color)
            text_surface.set_alpha(self.alpha) 
            text_rect = text_surface.get_rect(center=(self.x + GRID_SIZE // 2, self.y)) 
            surface.blit(text_surface, text_rect.topleft)


def draw_grid(surface):
    pass # يمكن تفعيلها لرسم شبكة اللعب إذا لزم الأمر

def show_main_menu():
    # يعرض القائمة الرئيسية ويتعامل مع اختيار المستخدم
    global is_global_muted, global_volume, move_sound, current_playing_music_path

    play_background_music(background_music_path)

    while True:
        screen.blit(background_image, (0, 0))

        title = font_large.render("Snake Game", True, WHITE)
        single_player = font_medium.render("1. Single Player", True, WHITE)
        two_players = font_medium.render("2. Two Players", True, WHITE)
        quit_option = font_medium.render("Q. Exit", True, WHITE)
        
        title_y = HEIGHT * 0.2
        single_player_y = HEIGHT * 0.4
        two_players_y = single_player_y + single_player.get_height() + 20
        quit_option_y = two_players_y + two_players.get_height() + 20
        
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, title_y))
        screen.blit(single_player, (WIDTH // 2 - single_player.get_width() // 2, single_player_y))
        screen.blit(two_players, (WIDTH // 2 - two_players.get_width() // 2, two_players_y))
        screen.blit(quit_option, (WIDTH // 2 - quit_option.get_width() // 2, quit_option_y))
        
        draw_mute_indicator(screen)
        draw_volume_indicator(screen)
        
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_m:
                    is_global_muted = not is_global_muted
                    apply_global_volume()
                    if is_global_muted:
                        pygame.mixer.music.pause()
                    else:
                        if not pygame.mixer.music.get_busy() or pygame.mixer.music.get_pos() == -1:
                            play_background_music(background_music_path)
                        else:
                            pygame.mixer.music.unpause()
                elif event.key == pygame.K_EQUALS:
                    global_volume = min(1.0, round(global_volume + 0.1, 1))
                    apply_global_volume()
                elif event.key == pygame.K_MINUS:
                    global_volume = max(0.0, round(global_volume - 0.1, 1))
                    apply_global_volume()
                elif event.key == pygame.K_1:
                    if move_sound: move_sound.play() 
                    return 1
                elif event.key == pygame.K_2:
                    if move_sound: move_sound.play() 
                    return 2
                elif event.key == pygame.K_q:
                    if move_sound: move_sound.play() 
                    pygame.quit()
                    sys.exit()

def show_color_selection(player_num):
    # تتيح للاعبين اختيار لون الأفعى وأزرار التحكم
    global is_global_muted, global_volume, move_sound, current_playing_music_path
    
    selected_players_data = []
    selected_colors_raw = []
    
    arrow_keys_controls = {
        "up": pygame.K_UP, "down": pygame.K_DOWN,
        "left": pygame.K_LEFT, "right": pygame.K_RIGHT,
        "name": "Arrow Keys"
    }
    wasd_keys_controls = {
        "up": pygame.K_w, "down": pygame.K_s,
        "left": pygame.K_a, "right": pygame.K_d,
        "name": "WASD Keys"
    }

    play_background_music(background_music_path)

    for current_player_idx in range(player_num):
        available_color_info = [
            info for info in PLAYER_COLORS_INFO 
            if info["color"] not in selected_colors_raw
        ]
        
        if not available_color_info:
            print(f"No colors available for Player {current_player_idx + 1}! Using default.")
            default_color = BLUE if BLUE not in selected_colors_raw else MAGENTA
            available_color_info.append({"name": "Default", "color": default_color})

        selected_color_index_in_available = 0
        
        color_selected_this_player = False
        while not color_selected_this_player:
            screen.blit(background_image, (0, 0))
            
            title = font_large.render(f"Player {current_player_idx + 1} - Choose Color", True, WHITE)
            screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT * 0.1))

            color_square_size = 40
            spacing_y = 10
            text_offset_x = 20

            total_block_height = len(available_color_info) * color_square_size + \
                                 (len(available_color_info) - 1) * spacing_y

            max_text_width = 0
            for info in available_color_info:
                text_surface = font_color_name.render(info["name"], True, WHITE)
                max_text_width = max(max_text_width, text_surface.get_width())

            total_row_width = color_square_size + text_offset_x + max_text_width
            start_x_block = WIDTH // 2 - total_row_width // 2
            
            start_y_colors = HEIGHT // 2 - total_block_height // 2
            current_y = start_y_colors
            
            for i, color_info in enumerate(available_color_info):
                color_name = color_info["name"]
                color_rgb = color_info["color"]

                square_x = start_x_block
                text_x = square_x + color_square_size + text_offset_x
                
                pygame.draw.rect(screen, color_rgb, (square_x, current_y, color_square_size, color_square_size))
                
                text_color = WHITE
                if i == selected_color_index_in_available:
                    pygame.draw.rect(screen, color_rgb, (square_x - 3, current_y - 3, color_square_size + 6, color_square_size + 6), 5)
                    text_color = color_rgb
                
                color_name_text_surface = font_color_name.render(color_name, True, text_color)
                text_y = current_y + (color_square_size - color_name_text_surface.get_height()) // 2
                screen.blit(color_name_text_surface, (text_x, text_y))
                
                current_y += color_square_size + spacing_y

            instruction = font_instructions.render("Use UP/DOWN to choose, ENTER to select", True, WHITE)
            screen.blit(instruction, (WIDTH // 2 - instruction.get_width() // 2, HEIGHT * 0.9))
            
            draw_mute_indicator(screen)
            draw_volume_indicator(screen)
            
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.K_ESCAPE:
                    if move_sound: move_sound.play() 
                    return []
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_m:
                        is_global_muted = not is_global_muted
                        apply_global_volume()
                        if is_global_muted:
                            pygame.mixer.music.pause()
                        else:
                            if not pygame.mixer.music.get_busy() or pygame.mixer.music.get_pos() == -1:
                                play_background_music(background_music_path)
                            else:
                                pygame.mixer.music.unpause()
                    elif event.key == pygame.K_EQUALS:
                        global_volume = min(1.0, round(global_volume + 0.1, 1))
                        apply_global_volume()
                    elif event.key == pygame.K_MINUS:
                        global_volume = max(0.0, round(global_volume - 0.1, 1))
                        apply_global_volume()
                    elif event.key == pygame.K_UP:
                        selected_color_index_in_available = (selected_color_index_in_available - 1) % len(available_color_info)
                        if move_sound: move_sound.play() 
                    elif event.key == pygame.K_DOWN:
                        selected_color_index_in_available = (selected_color_index_in_available + 1) % len(available_color_info)
                        if move_sound: move_sound.play() 
                    elif event.key == pygame.K_RETURN:
                        selected_color_info_item = available_color_info[selected_color_index_in_available]
                        selected_color = selected_color_info_item["color"]
                        selected_colors_raw.append(selected_color)
                        
                        control_scheme = {}
                        if current_player_idx == 0:
                            control_scheme = choose_control_with_ui(current_player_idx, selected_color)
                        else:
                            if selected_players_data[0]["controls"]["name"] == "Arrow Keys":
                                control_scheme = wasd_keys_controls
                            else:
                                control_scheme = arrow_keys_controls
                        
                        selected_players_data.append({"color": selected_color, "controls": control_scheme})
                        if move_sound: move_sound.play() 
                        color_selected_this_player = True
                        break
                        
    return selected_players_data

def choose_control_with_ui(player_index, color):
    # تتيح للاعب الأول اختيار أزرار التحكم
    global is_global_muted, global_volume, move_sound, current_playing_music_path

    selected_index = 0
    options = ["Arrow Keys", "WASD Keys"]
    
    has_moved_selection = False

    play_background_music(background_music_path)

    while True:
        screen.blit(background_image, (0, 0))

        title = font_large.render(f"Player {player_index+1} - Choose Controls", True, color)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT * 0.15))

        for i, option in enumerate(options):
            rect_w = 350
            rect_h = 70
            rect_x = WIDTH // 2 - rect_w // 2
            rect_y = HEIGHT * 0.4 + i * (rect_h + 30)
            
            if (i == selected_index and has_moved_selection) or (i == selected_index and not has_moved_selection):
                pygame.draw.rect(screen, color, (rect_x, rect_y, rect_w, rect_h), 3)
            
            text = font_medium.render(option, True, WHITE)
            screen.blit(text, (rect_x + rect_w//2 - text.get_width()//2, rect_y + rect_h//2 - text.get_height()//2))

        instruction = font_instructions.render("Use UP/DOWN to select, ENTER to confirm", True, WHITE)
        screen.blit(instruction, (WIDTH // 2 - instruction.get_width() // 2, HEIGHT * 0.75))
        
        draw_mute_indicator(screen)
        draw_volume_indicator(screen)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_m:
                    is_global_muted = not is_global_muted
                    apply_global_volume()
                    if is_global_muted:
                        pygame.mixer.music.pause()
                    else:
                        if not pygame.mixer.music.get_busy() or pygame.mixer.music.get_pos() == -1:
                            play_background_music(background_music_path)
                        else:
                            pygame.mixer.music.unpause()
                elif event.key == pygame.K_EQUALS:
                    global_volume = min(1.0, round(global_volume + 0.1, 1))
                    apply_global_volume()
                elif event.key == pygame.K_MINUS:
                    global_volume = max(0.0, round(global_volume - 0.1, 1))
                    apply_global_volume()
                elif event.key == pygame.K_UP:
                    selected_index = (selected_index - 1) % len(options)
                    has_moved_selection = True
                    if move_sound: move_sound.play() 
                elif event.key == pygame.K_DOWN:
                    selected_index = (selected_index + 1) % len(options)
                    has_moved_selection = True
                    if move_sound: move_sound.play() 
                elif event.key == pygame.K_RETURN:
                    if move_sound: move_sound.play() 
                    if selected_index == 0:
                        return {
                            "up": pygame.K_UP,
                            "down": pygame.K_DOWN,
                            "left": pygame.K_LEFT,
                            "right": pygame.K_RIGHT,
                            "name": "Arrow Keys" 
                        }
                    else:
                        return {
                            "up": pygame.K_w,
                            "down": pygame.K_s,
                            "left": pygame.K_a,
                            "right": pygame.K_d,
                            "name": "WASD Keys" 
                        }

def show_pre_game_info(players_data):
    # يعرض معلومات اللعبة قبل البدء (أزرار التحكم، نقاط الطعام)
    global is_global_muted, global_volume, current_playing_music_path

    play_background_music(background_music_path)

    screen.blit(background_image, (0, 0))
    
    controls_title = font_info_title.render("Controls", True, WHITE)
    screen.blit(controls_title, (WIDTH // 2 - controls_title.get_width() // 2, HEIGHT * 0.05))
    
    y_offset_controls = HEIGHT * 0.15
    for i, player_data in enumerate(players_data):
        player_text = font_medium.render(f"Player {i+1}: {player_data['controls']['name']}", True, player_data["color"])
        screen.blit(player_text, (WIDTH // 2 - player_text.get_width() // 2, y_offset_controls + i * 50))
    
    food_title = font_info_title.render("Food Score Information", True, WHITE)
    y_offset_food_title = y_offset_controls + len(players_data) * 50 + 50
    screen.blit(food_title, (WIDTH // 2 - food_title.get_width() // 2, y_offset_food_title))
    
    y_start_food_items = y_offset_food_title + food_title.get_height() + 20
    line_height = font_food_item.get_height() + 5
    square_size = GRID_SIZE
    
    max_text_width = 0
    for food_type in FOOD_TYPES:
        info_text = font_food_item.render(f"{food_type['name']}: {food_type['score']} Points (Lifetime: {food_type['lifetime']}s)", True, WHITE)
        max_text_width = max(max_text_width, info_text.get_width())
    
    text_start_x_base = WIDTH // 2 - max_text_width // 2
    square_offset = square_size + 15
    
    for food_type in FOOD_TYPES:
        food_name = food_type["name"]
        food_score = food_type["score"]
        food_color = food_type["color"]
        
        square_x = text_start_x_base - square_offset
        
        if food_type["image_surface"]:
            # Display the pre-loaded image surface directly
            screen.blit(food_type["image_surface"], (square_x, y_start_food_items))
        else:
            pygame.draw.rect(screen, food_color, (square_x, y_start_food_items, square_size, square_size))
        
        pygame.draw.rect(screen, BLACK, (square_x, y_start_food_items, square_size, square_size), 1)

        info_text = font_food_item.render(f"{food_name}: {food_score} Points (Lifetime: {food_type['lifetime']}s)", True, WHITE)
        screen.blit(info_text, (text_start_x_base, y_start_food_items))
        y_start_food_items += line_height
        
    next_info = font_medium.render("Press SPACE to start game", True, WHITE)
    screen.blit(next_info, (WIDTH // 2 - next_info.get_width() // 2, HEIGHT * 0.92))
    
    draw_mute_indicator(screen)
    draw_volume_indicator(screen)
    
    pygame.display.update()
    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_m:
                    is_global_muted = not is_global_muted
                    apply_global_volume()
                    if is_global_muted:
                        pygame.mixer.music.pause()
                    else:
                        if not pygame.mixer.music.get_busy() or pygame.mixer.music.get_pos() == -1:
                            play_background_music(background_music_path)
                        else:
                            pygame.mixer.music.unpause()
                elif event.key == pygame.K_EQUALS:
                    global_volume = min(1.0, round(global_volume + 0.1, 1))
                    apply_global_volume()
                elif event.key == pygame.K_MINUS:
                    global_volume = max(0.0, round(global_volume - 0.1, 1))
                    apply_global_volume()
                if event.key == pygame.K_SPACE:
                    waiting = False
                elif event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()

def game_loop(player_count, players_data):
    # الحلقة الرئيسية للعبة الثعبان
    global is_global_muted, global_volume, game_over_sound_played_once, game_over_channel, game_over_reason, current_playing_music_path

    # إعادة تعيين حالة اللعبة
    game_over_sound_played_once = False
    game_over_channel = None 
    game_over_reason = None

    # List to hold active particles for explosion effects
    particles = []

    show_pre_game_info(players_data) # عرض شاشة معلومات ما قبل اللعب أولاً

    play_background_music(run_music_path) # بعد انتهاء شاشة المعلومات، ابدأ موسيقى اللعب

    snakes = []
    for i in range(player_count):
        start_x = GRID_WIDTH // 4 if i == 0 else GRID_WIDTH * 3 // 4
        snake = Snake(start_x, GRID_HEIGHT // 2, players_data[i]["color"], players_data[i]["controls"])
        snakes.append(snake)

    foods = []
    foods.append(Food(random.choice(FOOD_TYPES))) # Initial food spawn
    
    last_food_spawn_time = time.time()
    FOOD_SPAWN_INTERVAL = 2 # الوقت كل كم
    MAX_FOOD_ON_SCREEN = 8

    paused = False
    game_over = False
    
    dead_snake_positions_for_particles = [] # To store positions of snakes that just died for particle effects

    score_pop_ups = [] 
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    paused = not paused
                    if paused:
                        pygame.mixer.music.pause()
                    else:
                        if not is_global_muted: 
                            pygame.mixer.music.unpause() 
                elif event.key == pygame.K_m:
                    is_global_muted = not is_global_muted
                    apply_global_volume()
                    if is_global_muted:
                        pygame.mixer.music.pause()
                    else:
                        if not paused:
                            pygame.mixer.music.unpause()
                elif event.key == pygame.K_EQUALS:
                    global_volume = min(1.0, round(global_volume + 0.1, 1))
                    apply_global_volume()
                elif event.key == pygame.K_MINUS:
                    global_volume = max(0.0, round(global_volume - 0.1, 1))
                    apply_global_volume()
                elif event.key == pygame.K_q:
                    pygame.mixer.music.stop()
                    play_background_music(background_music_path)
                    return
                    
                if not paused and not game_over:
                    for snake in snakes:
                        if snake.is_alive:
                            if event.key == snake.controls["up"]:
                                snake.change_direction((0, -1))
                            elif event.key == snake.controls["down"]:
                                snake.change_direction((0, 1))
                            elif event.key == snake.controls["left"]:
                                snake.change_direction((-1, 0))
                            elif event.key == snake.controls["right"]:
                                snake.change_direction((1, 0))

        if not paused and not game_over:
            # Food spawning logic
            if time.time() - last_food_spawn_time > FOOD_SPAWN_INTERVAL and len(foods) < MAX_FOOD_ON_SCREEN:
                new_food_type = random.choice(FOOD_TYPES)
                new_food = Food(new_food_type)
                
                all_occupied_positions = []
                for snake in snakes:
                    if snake.is_alive:
                        all_occupied_positions.extend(snake.positions)
                for food_item in foods:
                    all_occupied_positions.append(food_item.position)
                
                new_food.randomize_position(all_occupied_positions)
                foods.append(new_food)
                last_food_spawn_time = time.time()

            foods = [food for food in foods if not food.is_expired()]

            # Update and check self-collisions for each snake
            for i, snake in enumerate(snakes):
                if snake.is_alive:
                    initial_alive_status = snake.is_alive
                    if not snake.update(): # If snake died from self-collision (wasn't shielded)
                        if player_count == 1:
                            game_over_reason = "You hit yourself!"
                        else:
                            game_over_reason = f"Player {i+1} hit themselves!"
                        game_over = True # Set game_over to True if a snake died
                    
                    if not snake.is_alive and initial_alive_status: # If snake just died
                        dead_snake_positions_for_particles.extend(snake.positions) # Store for particles


            # Check collision between snakes (for two players)
            if player_count == 2:
                snake1 = snakes[0]
                snake2 = snakes[1]

                head1 = snake1.get_head_position()
                head2 = snake2.get_head_position()

                # Head-to-head collision
                if head1 == head2:
                    if snake1.is_shielded and snake2.is_shielded:
                        # Both shielded, no one dies
                        pass
                    elif snake1.is_shielded and not snake2.is_shielded:
                        if snake2.is_alive: 
                            snake2.is_alive = False
                            dead_snake_positions_for_particles.extend(snake2.positions) # For particles
                        game_over_reason = "Player 2 ran into Player 1's shield!"
                        game_over = True
                    elif not snake1.is_shielded and snake2.is_shielded:
                        if snake1.is_alive: 
                            snake1.is_alive = False
                            dead_snake_positions_for_particles.extend(snake1.positions) # For particles
                        game_over_reason = "Player 1 ran into Player 2's shield!"
                        game_over = True
                    else: # Both not shielded
                        if snake1.is_alive: 
                            snake1.is_alive = False
                            dead_snake_positions_for_particles.extend(snake1.positions) # For particles
                        if snake2.is_alive: 
                            snake2.is_alive = False
                            dead_snake_positions_for_particles.extend(snake2.positions) # For particles
                        game_over_reason = "Head-to-Head Collision!"
                        game_over = True

                # Body collisions (P1 hits P2's body, P2 hits P1's body)
                # Ensure snake is alive and not shielded before checking body collision
                if snake1.is_alive and not snake1.is_shielded and head1 in snake2.positions[1:]:
                    if snake1.lives > 0:
                        snake1.lives -= 1
                        snake1.positions = [snake1.positions[0]]
                        snake1.grow_to = 3
                        if life_pickup_sound: life_pickup_sound.play()
                    else:
                        snake1.is_alive = False
                        dead_snake_positions_for_particles.extend(snake1.positions)
                        game_over_reason = "Player 1 ran into Player 2!"
                        game_over = True

                
                if snake2.is_alive and not snake2.is_shielded and head2 in snake1.positions[1:]:
                    if snake2.lives > 0:
                        snake2.lives -= 1
                        snake2.positions = [snake2.positions[0]]
                        snake2.grow_to = 3
                        if life_pickup_sound: life_pickup_sound.play()
                    else:
                        snake2.is_alive = False
                        dead_snake_positions_for_particles.extend(snake2.positions)
                        game_over_reason = "Player 2 ran into Player 1!"
                        game_over = True

            
            # Determine if game is over (and if one player won in 2-player mode)
            alive_snake_count = sum(1 for snake in snakes if snake.is_alive) 
            if alive_snake_count == 0:
                if not game_over_reason:
                    game_over_reason = "All players are out!"
                game_over = True
            elif player_count == 2 and alive_snake_count == 1:
                if not game_over_reason:
                    winning_snake = [s for s in snakes if s.is_alive][0]
                    game_over_reason = f"Player {snakes.index(winning_snake)+1} is the last one standing!"
                game_over = True


            # Check for food consumption
            foods_to_remove = []
            for food_item in foods:
                for snake in snakes:
                    if snake.is_alive and snake.get_head_position() == food_item.position:
                        if food_item.sound_type == "coin": 
                            if coin_sound: coin_sound.play()
                            snake.grow(food_item.score_value)
                            score_pop_ups.append(ScorePopUp(food_item.position[0]*GRID_SIZE, food_item.position[1]*GRID_SIZE, f"+{food_item.score_value}", YELLOW))
                        elif food_item.sound_type == "shield":
                            if shield_pickup_sound: shield_pickup_sound.play() # Play pickup sound
                            snake.is_shielded = True
                            SHIELD_DURATION = 5 # seconds
                            snake.shield_end_time = time.time() + SHIELD_DURATION
                            score_pop_ups.append(ScorePopUp(food_item.position[0]*GRID_SIZE, food_item.position[1]*GRID_SIZE, "Shield!", BLUE))
                            # No score for shield, but still remove it.
                        elif food_item.sound_type == "extra_life": 
                            if extra_life_sound:
                               ch = pygame.mixer.find_channel(True)
                               if ch:
                                ch.play(extra_life_sound)

                            snake.lives += 1
                            score_pop_ups.append(ScorePopUp(food_item.position[0]*GRID_SIZE, food_item.position[1]*GRID_SIZE, "Extra Life!", MAGENTA))
                        
                        elif eat_sound:
                            eat_sound.play()
                            snake.grow(food_item.score_value)
                            score_pop_ups.append(ScorePopUp(food_item.position[0]*GRID_SIZE, food_item.position[1]*GRID_SIZE, f"+{food_item.score_value}", GREEN))

                        
                        foods_to_remove.append(food_item)
                        break
            
            for eaten_food in foods_to_remove:
                if eaten_food in foods:
                    foods.remove(eaten_food)
            
        # --- Drawing ---
        screen.blit(background_image, (0, 0))
        draw_grid(screen)
        
        for food_item in foods:
            food_item.draw(screen)
        
        # Draw snakes (alive first)
        for snake in snakes:
            if snake.is_alive:
                snake.draw(screen)
        
        # Update and draw particles (for explosion effect)
        for particle in list(particles): # Iterate over a copy to allow modification during loop
            particle.update()
            particle.draw(screen)
            if not particle.is_alive:
                particles.remove(particle)

        for pop_up in list(score_pop_ups): 
            pop_up.update()
            pop_up.draw(screen)
            if not pop_up.is_alive:
                score_pop_ups.remove(pop_up)
        
        for i, snake in enumerate(snakes):
            score_color = snake.color if snake.is_alive else GRAY
            score_lives_text = f"P{i+1}: {snake.score} | Lives: {snake.lives}"
            score_text = font_small.render(score_lives_text, True, score_color)
            screen.blit(score_text, (10 + i * (score_text.get_width() + 20), 10))

        if paused:
            pause_overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            pause_overlay.fill((0, 0, 0, 150))

            pause_text = font_large.render("PAUSED", True, WHITE)
            resume_text = font_small.render("Press P to resume", True, WHITE)
            quit_text = font_small.render("Q to quit to menu", True, WHITE)

            pause_overlay.blit(pause_text, (WIDTH // 2 - pause_text.get_width() // 2, HEIGHT // 2 - 80))
            pause_overlay.blit(resume_text, (WIDTH // 2 - resume_text.get_width() // 2, HEIGHT // 2 - 10))
            pause_overlay.blit(quit_text, (WIDTH // 2 - quit_text.get_width() // 2, HEIGHT // 2 + 30))
            
            screen.blit(pause_overlay, (0, 0))
            
        if game_over:
            # تشغيل صوت نهاية اللعبة مرة واحدة فقط
            if not game_over_sound_played_once:
                if pygame.mixer.music.get_busy():
                    pygame.mixer.music.stop()

                if game_over_sound:
                    game_over_channel = pygame.mixer.find_channel(True) 
                    if game_over_channel: 
                        game_over_channel.play(game_over_sound)
                        apply_global_volume()
                game_over_sound_played_once = True
                
                # Generate particles for the explosion effect when game over for *all* dead snakes
                for pos in dead_snake_positions_for_particles:
                    center_x = pos[0] * GRID_SIZE + GRID_SIZE // 2
                    center_y = pos[1] * GRID_SIZE + GRID_SIZE // 2
                    for _ in range(30): 
                        speed_x = random.uniform(-3, 3) 
                        speed_y = random.uniform(-3, 3)
                        size = random.uniform(8, 15) 
                        decay = random.uniform(1, 3) 
                        particles.append(Particle(center_x, center_y, DARK_GRAY, size, speed_x, speed_y, decay))
                dead_snake_positions_for_particles.clear() # Clear after generating particles


            # بعد انتهاء صوت نهاية اللعبة، يتم إعادة تشغيل موسيقى القائمة
            if game_over_sound_played_once and \
               (game_over_channel is None or not game_over_channel.get_busy()):
                if not pygame.mixer.music.get_busy():
                    play_background_music(background_music_path)
            
            # Continue drawing particles even after game_over_sound_played_once
            # to allow them to fade out gracefully
            for particle in list(particles): 
                particle.update()
                particle.draw(screen)
                if not particle.is_alive:
                    particles.remove(particle)

            game_over_text = font_large.render("GAME OVER", True, WHITE)
            
            winner_text_render = None
            winner_score_text = None 
            loser_score_text = None

            # عرض سبب نهاية اللعبة
            if game_over_reason:
                reason_text_surface = font_game_over_reason.render(game_over_reason, True, RED)
                screen.blit(reason_text_surface, (WIDTH // 2 - reason_text_surface.get_width() // 2, HEIGHT * 0.3))

            # تحديد وعرض اللاعب الفائز أو التعادل (خاص بوضع لاعبين)
            if player_count == 2:
                if snakes[0].score > snakes[1].score:
                    winner_snake = snakes[0]
                    loser_snake = snakes[1]
                elif snakes[1].score > snakes[0].score:
                    winner_snake = snakes[1]
                    loser_snake = snakes[0]
                else:
                    winner_snake = None
                    loser_snake = None

                if winner_snake:
                    # هذه هي الرسالة التي تظهر "اللاعب X يفوز!"
                    winner_text_render = font_winner.render(f"Player {snakes.index(winner_snake)+1} WINS!", True, winner_snake.color)
                    winner_score_text = font_score_summary.render(f"Winner Score: {winner_snake.score}", True, winner_snake.color)
                    loser_score_text = font_score_summary.render(f"Loser Score: {loser_snake.score}", True, loser_snake.color)
                else:
                    winner_text_render = font_winner.render("IT'S A TIE!", True, WHITE)
                    winner_score_text = font_score_summary.render(f"Player 1 Score: {snakes[0].score}", True, snakes[0].color)
                    loser_score_text = font_score_summary.render(f"Player 2 Score: {snakes[1].score}", True, snakes[1].color)
            else: # وضع اللاعب الفردي
                winner_text_render = font_winner.render(f"Your Score: {snakes[0].score}", True, snakes[0].color)
                winner_score_text = font_score_summary.render(f"Final Score: {snakes[0].score}", True, snakes[0].color)


            game_over_y = HEIGHT * 0.15
            screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, game_over_y))
            
            y_offset = HEIGHT * 0.3 + reason_text_surface.get_height() + 20 if game_over_reason else game_over_y + game_over_text.get_height() + 30


            if winner_text_render:
                screen.blit(winner_text_render, (WIDTH // 2 - winner_text_render.get_width() // 2, y_offset))
                y_offset += winner_text_render.get_height() + 15
            
            if winner_score_text: 
                screen.blit(winner_score_text, (WIDTH // 2 - winner_score_text.get_width() // 2, y_offset))
                y_offset += winner_score_text.get_height() + 5
            
            if loser_score_text: 
                screen.blit(loser_score_text, (WIDTH // 2 - loser_score_text.get_width() // 2, y_offset))
                y_offset += loser_score_text.get_height() + 5
            
            restart_text = font_medium.render("Press R to restart", True, WHITE)
            menu_text = font_medium.render("Press Q to return to menu", True, WHITE)
            
            screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, y_offset + 40))
            screen.blit(menu_text, (WIDTH // 2 - menu_text.get_width() // 2, y_offset + 90))
            
            draw_mute_indicator(screen)
            draw_volume_indicator(screen)
            
            pygame.display.update()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        pygame.mixer.stop()
                        return game_loop(player_count, players_data)
                    elif event.key == pygame.K_q:
                        pygame.mixer.stop()
                        play_background_music(background_music_path)
                        return
            continue 
            
        draw_mute_indicator(screen)
        draw_volume_indicator(screen)
        pygame.display.update()
        clock.tick(FPS)
            
def main():
    global is_global_muted, global_volume

    play_background_music(background_music_path)

    while True:
        player_count = show_main_menu() 
        
        players_data = show_color_selection(player_count) 
        if players_data:
            game_loop(player_count, players_data)
        
if __name__ == "__main__":
    main()
    pygame.quit()
