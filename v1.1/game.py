import pygame
import pygame.freetype
import random
import os
import sys

# ---------- PYINSTALLER RESOURCE PATH ----------
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)
# -----------------------------------------------

pygame.init()
pygame.freetype.init()
pygame.key.start_text_input()

WIDTH, HEIGHT = 1500, 1000
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Game")
clock = pygame.time.Clock()

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

font = pygame.freetype.Font(resource_path("NotoSansSC-Light.ttf"), 28)

background_orig = pygame.image.load(resource_path("background.jpg")).convert()
santa = pygame.image.load(resource_path("santa.png")).convert_alpha()
background = pygame.transform.scale(background_orig, (WIDTH, HEIGHT))
santa = pygame.transform.scale(
    santa, (santa.get_width() // 2, santa.get_height() // 2)
)

PRESENT_SIZE = (150, 150)
presents = []
for name in ["rp1.png", "bp1.png", "gp1.png", "yp1.png"]:
    img = pygame.image.load(resource_path(name)).convert_alpha()
    presents.append(pygame.transform.scale(img, PRESENT_SIZE))

pygame.mixer.music.load(resource_path("jinglebell.mp3"))
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1)
music_paused = False

# =================== Words ====================== #
ORIGINAL_WORDS = [
    "我 xiǎng hē chá。",
    "nǐ xiǎng 吃 bīng qí lín ma?",
    "我 xiǎng 吃 qiǎo kè lì。",
    "我 xiǎng 吃 yuè bǐng。",
    "George xiǎng 去 yì dà lì。",
    "Zoey xiǎng 吃 cǎo méi。",
    "Ford xiǎng 去 rì běn。",
    "Evan和Eli xiǎng 去 yì dà lì 吃 pī sà, bīng qí lín和yuè bǐng。",
    "Sam xiǎng hē kě lè。",
    "Jaimee和King Penguin xiǎng 去 zhōng guó hē nǎi chá。",
    "Finley和Sam xiǎng 去 xià wēi yí。",
    "Francis xiǎng 去 xià wēi yí。",
    "Lennox和Nixon xiǎng 吃 pī sà。",
    "Rune和Lennox xiǎng 去 jiā ná dà 吃 pī sà。",
    "gāo lǎo shī和gāo lǎo shī de nǎi nai pá Mt. Everest.",
    "Kira de bǎo bao xiǎng 去 Iraq。",
    "Lev, Eli和Evan xiǎng 去 xǐ shǒu jiān。"
]
words = ORIGINAL_WORDS.copy()
# ================================================ #

falling_speed = 3
present_y = 0
stop = False

menu_open = False
menu_paused_game = False
input_text = ""
cursor_pos = 0

cursor_visible = True
cursor_timer = 0.0

input_scroll_x = 0

word_rects = []
scroll_offset = 0
scroll_velocity = 0

# -------------- Functions --------------
def random_present():
    return random.choice(presents)

def random_word():
    return random.choice(words)

def random_x(text_width):
    margin = max(40, text_width // 2 + 20)
    return random.randint(margin, WIDTH - PRESENT_SIZE[0] - margin)

current_present = random_present()
current_text = random_word()
present_x = random_x(font.get_rect(current_text).width)

# -------------- Main Loop --------------
running = True
while running:
    dt = clock.tick(60) / 1000

    # -------------- Events --------------
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            if not menu_open:
                stop = not stop

        if event.type == pygame.KEYDOWN and event.key == pygame.K_s and not menu_open:
            pygame.mixer.music.pause() if not music_paused else pygame.mixer.music.unpause()
            music_paused = not music_paused

        if event.type == pygame.KEYDOWN and not menu_open:
            if event.key == pygame.K_UP:
                falling_speed = min(falling_speed + 1, 50)
            elif event.key == pygame.K_DOWN:
                falling_speed = max(falling_speed - 1, 0)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            if menu_open:
                clicked_word = False
                for rect, word in word_rects:
                    if rect.collidepoint(event.pos):
                        if word in words:
                            if len(words) > 1:
                                words.remove(word)
                            else:
                                pass
                        clicked_word = True
                        break
                if not clicked_word:
                    menu_open = False
                    scroll_offset = scroll_velocity = 0
                    if menu_paused_game:
                        stop = False
                        menu_paused_game = False
            else:
                menu_open = True
                input_text = ""
                cursor_pos = 0
                scroll_offset = scroll_velocity = 0
                if not stop:
                    stop = True
                    menu_paused_game = True

        if event.type == pygame.MOUSEWHEEL and menu_open:
            scroll_velocity += event.y * 600

        if event.type == pygame.TEXTINPUT and menu_open:
            input_text = (
                input_text[:cursor_pos] + event.text + input_text[cursor_pos:]
            )
            cursor_pos += len(event.text)

        if event.type == pygame.KEYDOWN and menu_open:
            if event.key == pygame.K_RETURN:
                if input_text.strip():
                    words.append(input_text.strip())
                input_text = ""
                cursor_pos = 0
            elif event.key == pygame.K_BACKSPACE and cursor_pos > 0:
                input_text = input_text[:cursor_pos - 1] + input_text[cursor_pos:]
                cursor_pos -= 1
            elif event.key == pygame.K_DELETE and cursor_pos < len(input_text):
                input_text = input_text[:cursor_pos] + input_text[cursor_pos + 1:]
            elif event.key == pygame.K_LEFT:
                cursor_pos = max(0, cursor_pos - 1)
            elif event.key == pygame.K_RIGHT:
                cursor_pos = min(len(input_text), cursor_pos + 1)
            elif event.key == pygame.K_v and (pygame.key.get_mods() & pygame.KMOD_META):
                import pyperclip
                paste = pyperclip.paste()
                input_text = (
                    input_text[:cursor_pos] + paste + input_text[cursor_pos:]
                )
                cursor_pos += len(paste)
            elif event.key == pygame.K_c and (pygame.key.get_mods() & pygame.KMOD_META):
                import pyperclip
                pyperclip.copy(input_text)

        if event.type == pygame.VIDEORESIZE:
            WIDTH, HEIGHT = event.w, event.h
            screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
            background = pygame.transform.scale(background_orig, (WIDTH, HEIGHT))

    scroll_velocity *= 0.85
    scroll_offset += scroll_velocity * dt
    scroll_offset = min(0, scroll_offset)

    # -------------- Draw --------------
    screen.blit(background, (0, 0))
    screen.blit(santa, ((WIDTH - santa.get_width()) // 2, HEIGHT - santa.get_height()))
    screen.blit(current_present, (present_x, present_y))

    rect = font.get_rect(current_text)
    tx = present_x + (PRESENT_SIZE[0] - rect.width) // 2
    ty = present_y + (PRESENT_SIZE[1] - rect.height) // 2
    pygame.draw.rect(screen, WHITE, (tx - 8, ty - 6, rect.width + 16, rect.height + 12))
    font.render_to(screen, (tx, ty), current_text, BLACK)

    if not stop:
        present_y += falling_speed

    if present_y > HEIGHT:
        present_y = 0
        current_present = random_present()
        current_text = random_word()
        present_x = random_x(font.get_rect(current_text).width)

    # -------------- Menu --------------
    if menu_open:
        
        # ---------- Boxes ----------
        panel = pygame.Rect(150, 150, WIDTH - 300, HEIGHT - 300)
        pygame.draw.rect(screen, (247, 175, 236), panel)
        pygame.draw.rect(screen, BLACK, panel, 4)

        input_box = pygame.Rect(panel.x + 40, panel.y + 30, panel.width - 80, 50)
        pygame.draw.rect(screen, (200, 255, 200), input_box)
        pygame.draw.rect(screen, BLACK, input_box, 2)

        # Update blinking cursor timer
        if menu_open:
            cursor_timer += dt
            if cursor_timer >= 0.5:
                cursor_visible = not cursor_visible
                cursor_timer -= 0.5
        else:
            cursor_visible = False
            cursor_timer = 0.0

        prefix_rect = font.get_rect(input_text[:cursor_pos])
        prefix_w = prefix_rect.width
        total_rect = font.get_rect(input_text)
        total_w = total_rect.width

        visible_w = input_box.width - 20
        if prefix_w - input_scroll_x > visible_w:
            input_scroll_x = prefix_w - visible_w
        if prefix_w - input_scroll_x < 0:
            input_scroll_x = max(0, prefix_w)
        max_scroll_x = max(0, total_w - visible_w)
        input_scroll_x = max(0, min(input_scroll_x, max_scroll_x))

        fh = font.get_rect("Ay").height
        text_y = input_box.y + (input_box.height - fh) // 2

        screen.set_clip(input_box)
        font.render_to(screen, (input_box.x + 10 - input_scroll_x, text_y), input_text, BLACK)

        if cursor_visible:
            cursor_x = input_box.x + 10 + prefix_w - input_scroll_x
            pygame.draw.rect(screen, BLACK, (cursor_x, text_y, 2, fh))
        screen.set_clip(None)
        clip = pygame.Rect(
            panel.x + 40,
            input_box.bottom + 30,
            panel.width - 80,
            panel.height - 140,
        )

        pygame.draw.rect(screen, (255, 255, 255), clip)

        inner_pad = 12

        line_heights = []
        for word in words:
            rect = font.get_rect("• " + word)
            line_heights.append(rect.height + 10)

        content_height = sum(line_heights)

        inner_height = clip.height - inner_pad * 2

        max_scroll = min(0, inner_height - content_height)
        scroll_offset = max(max_scroll, min(0, scroll_offset))

        content_surf_w = max(0, clip.width - inner_pad * 2)
        content_surf_h = max(0, inner_height)
        content_surf = pygame.Surface((content_surf_w, content_surf_h))
        content_surf.fill((255, 255, 255))

        word_rects.clear()

        y = scroll_offset
        for word in words:
            text = "• " + word
            rect = font.get_rect(text)
            rect.topleft = (inner_pad, y)

            if rect.bottom >= 0 and rect.top <= content_surf_h:
                font.render_to(content_surf, rect.topleft, text, BLACK)
                screen_rect = pygame.Rect(clip.x + inner_pad + rect.left, clip.y + inner_pad + rect.top, rect.width, rect.height)
                word_rects.append((screen_rect, word))

            y += rect.height + 10

        screen.blit(content_surf, (clip.x + inner_pad, clip.y + inner_pad))

        if content_height > content_surf_h and content_height > 0:
            scrollbar_width = 12
            track_padding = 6
            track_rect = pygame.Rect(
                clip.right - scrollbar_width - track_padding,
                clip.y + track_padding,
                scrollbar_width,
                clip.height - track_padding * 2,
            )
            pygame.draw.rect(screen, (230, 230, 230), track_rect)
            pygame.draw.rect(screen, BLACK, track_rect, 1)

            visible_frac = content_surf_h / content_height
            thumb_height = max(int(track_rect.height * visible_frac), 20)

            scroll_range = content_height - content_surf_h
            if scroll_range > 0:
                thumb_y = track_rect.y + int((-scroll_offset) / scroll_range * (track_rect.height - thumb_height))
            else:
                thumb_y = track_rect.y

            thumb_rect = pygame.Rect(track_rect.x + 2, thumb_y, track_rect.width - 4, thumb_height)
            pygame.draw.rect(screen, (180, 180, 180), thumb_rect)
            pygame.draw.rect(screen, BLACK, thumb_rect, 1)

        pygame.draw.rect(screen, BLACK, clip, 2)

    if stop:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 50))
        screen.blit(overlay, (0, 0))
        font.render_to(screen, ((WIDTH - 100) // 2, 60), "PAUSED", WHITE)

    pygame.display.flip()

pygame.quit()
sys.exit()
