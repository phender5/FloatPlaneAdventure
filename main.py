import pygame
import os
import time
import random
pygame.font.init()

WIDTH, HEIGHT = 750, 750
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Float Plane Adventure")

# Load images
TWO_CLICK = pygame.image.load(os.path.join("assets", "double_click.png"))
TWO_CLICK = pygame.transform.scale(TWO_CLICK, (150,150))

# Player player
FLOAT_PLANE = pygame.image.load(os.path.join("assets", "airplane.gif"))

# Lasers
LASER = pygame.image.load(os.path.join("assets", "laser.png"))

# Ken
KEN = pygame.image.load(os.path.join("assets", "ken.png"))
KEN = pygame.transform.scale(KEN, (300,300))

# Background
BG = pygame.transform.scale(pygame.image.load(os.path.join("assets", "cloud_background.webp")), (WIDTH, HEIGHT))

class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y += vel

    def off_screen(self, height):
        return not(self.y <= height and self.y >= 0)

    def collision(self, obj):
        return collide(self, obj)


class Plane:
    COOLDOWN = 25

    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.plane_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0

    def draw(self, window):
        window.blit(self.plane_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

    def move_lasers(self, vel, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser)

    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x-15, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

    def get_width(self):
        return self.plane_img.get_width()

    def get_height(self):
        return self.plane_img.get_height()


class Player(Plane):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.plane_img = FLOAT_PLANE
        self.laser_img = LASER
        self.mask = pygame.mask.from_surface(self.plane_img)
        self.max_health = health

    def move_lasers(self, vel, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
                return False
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        if laser in self.lasers:
                            self.lasers.remove(laser)
                        return True

    def draw(self, window):
        super().draw(window)
        self.healthbar(window)

    def healthbar(self, window):
        pygame.draw.rect(window, ('red'), (self.x, self.y + self.plane_img.get_height() + 10, self.plane_img.get_width(), 10))
        pygame.draw.rect(window, ('green'), (self.x, self.y + self.plane_img.get_height() + 10, self.plane_img.get_width() * (self.health/self.max_health), 10))


class Enemy(Plane):

    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.plane_img = TWO_CLICK
        self.mask = pygame.mask.from_surface(self.plane_img)

    def move(self, vel):
        self.y += vel

class Ken(Plane):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.plane_img = KEN
        self.mask = pygame.mask.from_surface(self.plane_img)



def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None

def main():
    run = True
    FPS = 60
    level = 0
    lives = 5
    money = 0
    main_font = pygame.font.SysFont("comicsans", 50)
    message_font = pygame.font.SysFont("comicsans", 60)
    small_font = pygame.font.SysFont("comicsans", 30)


    enemies = []
    wave_length = 5
    enemy_vel = 1

    player_vel = 5
    laser_vel = 5

    player = Player(300, 630)
    
    ken = Ken(WIDTH/2-175, HEIGHT/2-250)

    clock = pygame.time.Clock()

    lost = False
    lost_count = 0

    won = False
    won_count = 0

    ken_mode = False
    advance_mode = False

    def redraw_window():
        WIN.blit(BG, (0,0))
        # draw text
        lives_label = main_font.render(f"Lives: {lives}", 1, ("white"))
        money_label = main_font.render(f"${money}", 1, ("gold"))
        level_label = main_font.render(f"Level: {level}", 1, ("white"))

        WIN.blit(lives_label, (10, 10))
        WIN.blit(money_label, (WIDTH/2 - money_label.get_width()/2, 10))
        WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))

        for enemy in enemies:
            enemy.draw(WIN)

        player.draw(WIN)
        if (ken_mode):
            ken.draw(WIN)

        if lost:
            lost_label = message_font.render("You Lost!!", 1, ("indigo"))
            WIN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 300))

        if money >= 1000000:
            won_label = message_font.render("We're going to Pender!!", 1, ("darkorange"))
            WIN.blit(won_label, (WIDTH/2 - won_label.get_width()/2, HEIGHT/2 - won_label.get_height()/2+50))

        if advance_mode:
            advance_label = small_font.render("Advance Mode Activated", 1, ("red"))
            WIN.blit(advance_label, (WIDTH/2 - advance_label.get_width()/2, HEIGHT - advance_label.get_height()))

        pygame.display.update()

    while run:
        clock.tick(FPS)
        redraw_window()

        if money >= 1000000 and not advance_mode:
            for enemy in enemies:
                enemies.remove(enemy)
            won = True
            won_count += 1
        if won:
            if won_count > FPS * 6:
                run = False
            else:
                continue
        

        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1

        if lost:
            if lost_count > FPS * 4:
                run = False
            else:
                continue

        if len(enemies) == 0:
            level += 1
            wave_length += 5
            if advance_mode:
                enemy_vel += 1
                player_vel += 2
                player.COOLDOWN -= 5
            for _ in range(wave_length):
                enemy = Enemy(random.randrange(50, WIDTH-100), random.randrange(-1500, -100))
                enemies.append(enemy)

        if collide(ken, player) and ken_mode:
            for enemy in enemies:
                enemies.remove(enemy)
                money += 10000

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and player.x - player_vel > 0: # left
            player.x -= player_vel
        if keys[pygame.K_d] and player.x + player_vel + player.get_width() < WIDTH: # right
            player.x += player_vel
        if keys[pygame.K_w] and player.y - player_vel > 0: # up
            player.y -= player_vel
        if keys[pygame.K_s] and player.y + player_vel + player.get_height() + 15 < HEIGHT: # down
            player.y += player_vel
        if keys[pygame.K_SPACE]:
            player.shoot()
        if keys[pygame.K_k]:
            ken_mode = True
        if keys[pygame.K_l]:
            advance_mode = True

        for enemy in enemies[:]:
            enemy.move(enemy_vel)

            if collide(enemy, player):
                player.health -= 10
                enemies.remove(enemy)
            elif enemy.y + enemy.get_height() > HEIGHT:
                lives -= 1
                enemies.remove(enemy)

        if (player.move_lasers(-laser_vel, enemies)):
            money += 10000

def main_menu():
    title_font = pygame.font.SysFont("comicsans", 70)
    run = True
    while run:
        WIN.blit(BG, (0,0))
        title_label = title_font.render("Click to start...", 1, ('indigo'))
        WIN.blit(title_label, (WIDTH/2 - title_label.get_width()/2, 350))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()
    pygame.quit()


main_menu()