import pygame
import random

pygame.init()

# ───── Window & colours ───────────────────
WIDTH, HEIGHT = 800, 600
display_width = 800
display_height = 600
asphalt       = (40, 40, 40)
dash_colour   = (200, 200, 200)
black         = (0, 0, 0)
white         = (255, 255, 255)
red           = (255, 0, 0)
green         = (0, 255, 0)
block_colour  = (53, 115, 255)
gameDisplay = pygame.display.set_mode((display_width,display_height), pygame.SCALED)

# dash pattern (lane markers)
DASH_LEN   = 40
GAP_LEN    = 60
DASH_CYCLE = DASH_LEN + GAP_LEN
SCROLL_SPEED = 5   # pixels per frame downward

# ───── Assets ─────────────────────────────
crash_sound = pygame.mixer.Sound("Crash.mp3")
pygame.mixer.music.load("game_music.mp3")

intro_bg = pygame.transform.scale(
    pygame.image.load("game_introbackground.png"), (WIDTH, HEIGHT)
)
mic_img  = pygame.transform.scale(
    pygame.image.load("microphone.png"), (40, 40)
)
car_img   = pygame.image.load("racecar.png")
truck_img = pygame.image.load("truck.png")   # 150 × 300 px – keep as‑is
sedan_img = pygame.image.load("sedan.png")   # 100 × 200 px – keep as‑is
car_icon  = pygame.image.load("icon.png")
pygame.display.set_icon(car_icon)

# ───── Pygame init ────────────────────────
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ultra Racing Car Game")
clock  = pygame.time.Clock()

# ───── Global flags ───────────────────────
pause       = False
music_muted = False
high_score  = 0


# ───── Helpers ────────────────────────────
def load_high_score():
    global high_score
    try:
        with open("highscore.txt", "r") as f:
            high_score = int(f.read())
    except (FileNotFoundError, ValueError):
        high_score = 0  # Default to 0 if file doesn't exist or is invalid
def save_high_score():
    with open("highscore.txt", "w") as f:
        f.write(str(high_score))

def text_obj(txt, font, col):
    surf = font.render(txt, True, col)
    return surf, surf.get_rect()

def circle_hit(pos, cx, cy, r=40):
    dx, dy = pos[0]-cx, pos[1]-cy
    return dx*dx + dy*dy <= r*r

def draw_road(offset):
    """Draw asphalt and two dashed lane lines scrolling *downward*."""
    screen.fill(asphalt)
    lane_x = [WIDTH//4, WIDTH*3//4]
    for x in lane_x:
        y = offset          # start a dash at current offset
        while y < HEIGHT:
            pygame.draw.rect(screen, dash_colour, (x-3, y, 6, DASH_LEN))
            y += DASH_CYCLE
        # also draw one dash just above top edge to cover gap
        pygame.draw.rect(screen, dash_colour,
                         (x-3, offset - DASH_CYCLE, 6, DASH_LEN))

def draw_mic_button():
    # Draw background circle
    pygame.draw.circle(gameDisplay, white, (760, 40), 30)

    # Draw mic image
    gameDisplay.blit(mic_img, (740, 20))

    # If muted, draw a red slash over the mic
    if music_muted:
        pygame.draw.line(gameDisplay, red, (740, 20), (780, 60), 5)

def handle_mic_click(mouse_pos):
    global music_muted
    dx = mouse_pos[0] - 760
    dy = mouse_pos[1] - 40
    distance = (dx**2 + dy**2) ** 0.5
    if distance <= 25:
        music_muted = not music_muted
        if music_muted:
            pygame.mixer.music.set_volume(0)
        else:
            pygame.mixer.music.set_volume(1)

def things(rect):
    pygame.draw.rect(screen, block_colour, rect)

def draw_car(x, y):
    screen.blit(car_img, (x, y))

def dodged_counter(n):
    f = pygame.font.SysFont(None, 25)
    screen.blit(f.render(f"Dodged: {n}", True, white), (0, 0))

# ───── Screens ────────────────────────────
def intro_screen():
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); return
            if e.type == pygame.MOUSEBUTTONDOWN:
                if circle_hit(e.pos, 325, 230): game_loop(); return
                if circle_hit(e.pos, 460, 230): pygame.quit(); return

        screen.blit(intro_bg, (0, 0))
        font = pygame.font.Font("ComicRelief-Bold.ttf", 35)
        txt, rect = text_obj("Ultra Racing Car Game", font, red)
        rect.center = (WIDTH//2, int(HEIGHT*0.2))
        screen.blit(txt, rect)

        pygame.draw.circle(screen, black, (325, 230), 45)
        pygame.draw.circle(screen, green, (325, 230), 40)
        pygame.draw.polygon(screen, white, ((310,205), (310,255), (350,230)))
        pygame.draw.circle(screen, black, (460, 230), 45)
        pygame.draw.circle(screen, red,   (460, 230), 40)
        pygame.draw.line(screen, white, (440,210), (480,250), 10)
        pygame.draw.line(screen, white, (440,250), (480,210), 10)

        pygame.display.update()
        clock.tick(60)

def pause_screen():
    global pause
    pygame.mixer.music.pause()
    while pause:
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); return
            if e.type == pygame.MOUSEBUTTONDOWN:
                if circle_hit(e.pos, 325, 230): pause=False; pygame.mixer.music.unpause()
                if circle_hit(e.pos, 460, 230): pygame.quit(); return

        screen.blit(intro_bg, (0, 0))
        f = pygame.font.Font("ComicRelief-Bold.ttf", 35)
        txt, rect = text_obj("Game Paused", f, red)
        rect.center = (WIDTH//2, int(HEIGHT*0.2))
        screen.blit(txt, rect)

        pygame.draw.circle(screen, black, (325, 230), 45)
        pygame.draw.circle(screen, green, (325, 230), 40)
        pygame.draw.polygon(screen, white, ((310,205), (310,255), (350,230)))
        pygame.draw.circle(screen, black, (460, 230), 45)
        pygame.draw.circle(screen, red,   (460, 230), 40)
        pygame.draw.line(screen, white, (440,210), (480,250), 10)
        pygame.draw.line(screen, white, (440,250), (480,210), 10)

        pygame.display.update()
        clock.tick(60)

def crash_screen():
    pygame.mixer.music.stop()
    pygame.mixer.Sound.play(crash_sound)
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); return
            if e.type == pygame.MOUSEBUTTONDOWN:
                if circle_hit(e.pos, 325, 230): game_loop(); return
                if circle_hit(e.pos, 460, 230): pygame.quit(); return

        f = pygame.font.Font("ComicRelief-Bold.ttf", 35)
        txt, rect = text_obj("Game Over, Try Again?", f, white)
        rect.center = (WIDTH//2, int(HEIGHT*0.2))
        screen.blit(txt, rect)

        pygame.draw.circle(screen, black, (325, 230), 45)
        pygame.draw.circle(screen, green, (325, 230), 40)
        pygame.draw.polygon(screen, white, ((310,205), (310,255), (350,230)))
        pygame.draw.circle(screen, black, (460, 230), 45)
        pygame.draw.circle(screen, red,   (460, 230), 40)
        pygame.draw.line(screen, white, (440,210), (480,250), 10)
        pygame.draw.line(screen, white, (440,250), (480,210), 10)

        pygame.display.update()
        clock.tick(60)

def game_loop():
    global pause, music_muted, high_score  # Declare high_score as global
    load_high_score()  # Load high score at the start
    pygame.mixer.music.play(-1)

    # Setup player car
    car_w = car_img.get_width()
    car_h = car_img.get_height()
    x = WIDTH // 2 - car_w // 2  # Center horizontally
    y = HEIGHT * 0.8
    x_change = 0

    # Initialize game state
    traffic = []
    scroll = 0
    dodged = 0

    def spawn_vehicle():
        """Create new traffic vehicle with collision avoidance"""
        vehicle_img = random.choice([truck_img, sedan_img])
        rect = vehicle_img.get_rect()
        rect.x = random.randint(0, WIDTH - rect.width)
        rect.y = -rect.height
        speed = random.uniform(3, 6)
        
        if not any(rect.inflate(20, 40).colliderect(v[1]) for v in traffic):
            traffic.append([vehicle_img, rect, speed])
    
    def draw_road(offset):
        """Draw scrolling road with lane markers"""
        screen.fill(asphalt)
        lane_x = [WIDTH//4, WIDTH*3//4]
        for x in lane_x:
            y = offset
            while y < HEIGHT:
                pygame.draw.rect(screen, dash_colour, (x-3, y, 6, DASH_LEN))
                y += DASH_CYCLE
            pygame.draw.rect(screen, dash_colour, (x-3, offset-DASH_CYCLE, 6, DASH_LEN))

    # Initialize traffic
    for _ in range(3):
        spawn_vehicle()

    running = True
    while running:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT: x_change = -10
                if event.key == pygame.K_RIGHT: x_change = 10
                if event.key == pygame.K_p:
                    pause = True
                    pause_screen()
                    
            if event.type == pygame.KEYUP:
                if event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                    x_change = 0
                    
            if event.type == pygame.MOUSEBUTTONDOWN:
                handle_mic_click(pygame.mouse.get_pos())

        # Update player (full screen movement)
        x = max(0, min(WIDTH - car_w, x + x_change))

        # Update traffic
        for vehicle in traffic:
            vehicle[1].y += vehicle[2]

        # Remove exited vehicles and update dodged count
        dodged += len([v for v in traffic if v[1].top > HEIGHT])
        traffic = [v for v in traffic if v[1].top <= HEIGHT]

        # Maintain traffic density
        while len(traffic) < 6:
            spawn_vehicle()

        # Prevent vehicle collisions
        traffic.sort(key=lambda v: v[1].y)
        for i in range(1, len(traffic)):
            if traffic[i][1].colliderect(traffic[i-1][1]):
                traffic[i][1].y = traffic[i-1][1].bottom + 5
                traffic[i][2] = min(traffic[i][2], traffic[i-1][2] * 0.95)

        # Player collision
        player_rect = pygame.Rect(x, y, car_w, car_h)
        if any(player_rect.colliderect(v[1]) for v in traffic):
            crash_screen()
            return

        # Update high score
        if dodged > high_score:
            high_score = dodged
            save_high_score()  # Save the new high score

        # Rendering
        draw_road(scroll)
        scroll = (scroll + SCROLL_SPEED) % DASH_CYCLE
        
        for vehicle in traffic:
            screen.blit(vehicle[0], vehicle[1])
        
        screen.blit(car_img, (x, y))  # Player car
    
        # UI elements
        font = pygame.font.SysFont(None, 36)
        screen.blit(font.render(f"Dodged: {dodged}", True, white), (0, 0))
        screen.blit(font.render(f"High Score: {high_score}", True, white), (0, 30))  # Display high score
        
        draw_mic_button()  # Draw mic button
        pygame.display.update()
        clock.tick(60)

    pygame.quit()


# ───── Run ────────────────────────────────
intro_screen()
game_loop()
pygame.quit()
