# importing modules
import pygame
from pygame.locals import *
from sys import exit
import math
from settings import *
from weapons import *

# initialise pygame
pygame.init()

# create window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("game project")
clock = pygame.time.Clock()
pygame.mouse.set_visible(False)

# load background image
bg = pygame.transform.scale(pygame.image.load("grassbg.png").convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))

# load images outside of the class to avoid reloading unnecessarily
try:
    player_image = pygame.transform.rotozoom(pygame.image.load("survivorrifle.png").convert_alpha(), 0, PLAYER_SIZE)
    crosshair_image = pygame.transform.rotozoom(pygame.image.load("crosshair.png").convert_alpha(), 0, CROSSHAIR_SIZE)
    bullet_image = pygame.image.load("boolet.png").convert_alpha()
except pygame.error as e:
    print("Error loading images", e)
    pygame.quit()
    exit()

# player class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = player_image.copy()
        self.pos = pygame.math.Vector2(PLAYERSTART_X, PLAYERSTART_Y*0.5)
        # create copy of original, non-transformed image
        self.default = self.image
        self.hitbox = self.default.get_rect(center = self.pos)
        self.rect = self.hitbox.copy()
        self.speed = PLAYER_SPEED
        self.shoot = False
        self.shoot_cooldown = 0

    # detect user input
    def user_input(self):
        self.velocity_x = 0
        self.velocity_y = 0

        # check for key presses
        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_w]:
            self.velocity_y = -self.speed
        if keys[pygame.K_a]:
            self.velocity_x = -self.speed
        if keys[pygame.K_s]:
            self.velocity_y = self.speed
        if keys[pygame.K_d]:
            self.velocity_x = self.speed

        # check for diagonal movement
        if self.velocity_x != 0 and self.velocity_y != 0:
            self.velocity_x /= math.sqrt(2)
            self.velocity_y /= math.sqrt(2)

        # check for mouse button presses
        if pygame.mouse.get_pressed() == (1, 0, 0):
            self.shoot = True
            self.is_shooting()
        else:
            self.shoot = False
    
    # move character
    def move(self):
        self.pos += pygame.math.Vector2(self.velocity_x, self.velocity_y)
        self.hitbox.center = self.pos
        self.rect.center = self.hitbox.center

    # point player sprite in direction of mouse pointer
    def aim(self):
        self.mouse_pos = pygame.mouse.get_pos()
        self.dx = (self.mouse_pos[0] - self.hitbox.centerx)
        self.dy = (self.mouse_pos[1] - self.hitbox.centery)
        self.theta = math.degrees(math.atan2(self.dy, self.dx))
        self.image = pygame.transform.rotate(self.default, -self.theta)
        self.rect = self.image.get_rect(center = self.hitbox.center)

    # refresh shooting cooldown
    def is_shooting(self):
        if self.shoot_cooldown == 0 and self.shoot:
            self.shoot_cooldown = SHOOT_COOLDOWN
            self.create_bullet()
    
    # instantiate a bullet
    def create_bullet(self):
            self.gun_offset = pygame.math.Vector2(GUN_OFFSET_X, GUN_OFFSET_Y)
            self.rotated_gun_offset = self.gun_offset.rotate(self.theta)
            bullet_pos = self.pos + self.rotated_gun_offset
            self.bullet = Bullet(bullet_pos.x, bullet_pos.y, self.theta, bullet_image)
            # add bullet to all sprites and bullet group
            all_sprites_group.add(self.bullet)
            bullet_group.add(self.bullet)

    # update player
    def update(self):
        self.user_input()
        self.move()
        self.aim()

        # reduce time before next shot each tick
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

# crosshair class
class Crosshair(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = crosshair_image.copy()
        self.rect = self.image.get_rect()

    # update crosshair
    def update(self):
        self.rect.center = pygame.mouse.get_pos()

# bullet class
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x ,y, theta, image):
        super().__init__()
        self.image = pygame.transform.rotozoom(image, -theta, BULLET_SIZE)
        self.rect = self.image.get_rect(center=(x, y))
        self.pos = pygame.Vector2(x, y)
        self.theta = theta
        self.speed = BULLET_SPEED
        self.lifetime = BULLET_LIFETIME

    # spawn bullet
    def spawn(self):
        self.spawn_time = pygame.time.get_ticks()
        self.velocity = pygame.Vector2(math.cos(math.radians(self.theta)), math.sin(math.radians(self.theta))) * self.speed

    # bullet movement
    def bullet_move(self):
        self.current_time = pygame.time.get_ticks()
        self.pos += self.velocity
        self.rect.center = self.pos
       
        if self.current_time - self.spawn_time > self.lifetime:
            self.kill()

    # update bullet
    def update(self):
        self.spawn()
        self.bullet_move()

# instantiate classes
player = Player()
crosshair = Crosshair()

# sprites groups and bullets group
all_sprites_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()

# add sprites to groups
all_sprites_group.add(player)
all_sprites_group.add(crosshair)

# main loop
while True:
    keys = pygame.key.get_pressed()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
    
    # blit background to the screen
    screen.blit(bg, (0, 0))

    # draw sprite groups
    all_sprites_group.draw(screen)
    all_sprites_group.update()

    pygame.display.update()
    clock.tick_busy_loop(FPS)

