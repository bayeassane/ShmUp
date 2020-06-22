import pygame
import random
from os import path


img_dir = path.join(path.dirname(__file__), 'img')
snd_dir = path.join(path.dirname(__file__), 'snd')

WIDTH = 480  # la largeur de notre fenêtre de jeu
HEIGHT = 600  # la hauteur de notre fenêtre de jeu
FPS = 60  # images par seconde

# Couleurs en RGB
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# powerup
POWER_TIME = 5000

# initialiser les modules de pygame et créer une fenêtre
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Shmup!')
clock = pygame.time.Clock()

# charger les images
background = pygame.image.load(path.join(img_dir, 'starfield.png')).convert()
background_rect = background.get_rect()
player_img = pygame.image.load(path.join(img_dir, 'playerShip1_orange.png')).convert()
meteor_img = pygame.image.load(path.join(img_dir, 'meteorBrown_med1.png')).convert()
bullet_img = pygame.image.load(path.join(img_dir, 'laserRed16.png')).convert()

player_mini_img = pygame.transform.scale(player_img, (25, 19))
player_mini_img.set_colorkey(BLACK)

# charger les images de méteors
meteor_images = []
meteor_list = [
    'meteorBrown_big1.png','meteorBrown_med1.png',
    'meteorBrown_med3.png',
    'meteorBrown_small1.png','meteorBrown_small2.png',
    'meteorBrown_tiny1.png'
]
for m in meteor_list:
    meteor_images.append(pygame.image.load(path.join(img_dir, m)).convert())

# charger les images de l'animation
explosion_anim = {}
explosion_anim['lg'] = []
explosion_anim['sm'] = []
explosion_anim['player'] = []
for i in range(9):
    file_name = f'regularExplosion0{i}.png'
    img = pygame.image.load(path.join(img_dir, file_name)).convert()
    img.set_colorkey(BLACK)
    img_lg = pygame.transform.scale(img, (75, 75))
    explosion_anim['lg'].append(img_lg)
    img_sm = pygame.transform.scale(img, (32, 32))
    explosion_anim['sm'].append(img_sm)
    file_name = f'sonicExplosion0{i}.png'
    img = pygame.image.load(path.join(img_dir, file_name)).convert()
    img.set_colorkey(BLACK)
    explosion_anim['player'].append(img)

powerup_images = {}
powerup_images['shield'] = pygame.image.load(path.join(img_dir, 'shield_gold.png')).convert()
powerup_images['gun'] = pygame.image.load(path.join(img_dir, 'bolt_gold.png')).convert()

# définir le font
font_name = pygame.font.match_font('arial')

# charger les sons
shoot_sound = pygame.mixer.Sound(path.join(snd_dir, 'pew.wav'))
power_sound = pygame.mixer.Sound(path.join(snd_dir, 'sound_power.wav'))
expl_sounds = []
for snd in ['expl3.wav', 'expl6.wav']:
    expl_sounds.append(pygame.mixer.Sound(path.join(snd_dir, snd)))
pygame.mixer.music.load(path.join(snd_dir, 'tgfcoder-FrozenJam-SeamlessLoop.ogg'))
pygame.mixer.music.set_volume(0.4)

# classes 
class Player(pygame.sprite.Sprite):

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = player_img
        self.image = pygame.transform.scale(self.image, (50, 38))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH/2, HEIGHT/2)
        self.rect.bottom = HEIGHT - 10
        self.speed_x = 0
        self.shield = 100
        self.max_shield = 100
        self.shoot_delay = 250
        self.last_shoot = pygame.time.get_ticks()
        self.lives = 3
        self.hidden = False
        self.hide_timer = pygame.time.get_ticks()
        self.power = 1
        self.power_time = pygame.time.get_ticks()
    
    def powerup(self):
        self.power += 1
        self.power_time = pygame.time.get_ticks()
    
    def hide(self):
        """masquer le player pendant un laps de temps"""
        self.hidden = True
        self.hide_timer = pygame.time.get_ticks()
        self.rect.center = (WIDTH/2, HEIGHT+200)

    def bar_shield(self, surf, x, y):
        if self.shield >= 0:
            BAR_WIDTH = self.max_shield
            BAR_HEIGHT = 10
            default = pygame.Rect(x, y, BAR_WIDTH, BAR_HEIGHT)
            for_player = pygame.Rect(x, y, self.shield, BAR_HEIGHT)
            pygame.draw.rect(surf, WHITE, default)
            pygame.draw.rect(surf, GREEN, for_player)
    
    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shoot > self.shoot_delay:
            self.last_shoot = now 
            if self.power == 1:
                bullet = Bullet(self.rect.centerx, self.rect.top)
                bullets.add(bullet)
                all_sprites.add(bullet)
                shoot_sound.play()
            if self.power >= 2:
                bullet1 = Bullet(self.rect.left, self.rect.centery)
                bullet2 = Bullet(self.rect.right, self.rect.centery)
                all_sprites.add(bullet1)
                all_sprites.add(bullet2)
                bullets.add(bullet1)
                bullets.add(bullet2)
                shoot_sound.play()

    def update(self):
        if self.hidden and pygame.time.get_ticks() - self.hide_timer > 1000:
            self.hidden = False
            self.rect.centerx = WIDTH/2
            self.rect.bottom = HEIGHT - 10
        
        # powerup time
        if self.power >=2 and pygame.time.get_ticks() - self.power_time > POWER_TIME:
            self.power_time = pygame.time.get_ticks()
            self.power -= 1
        self.speed_x = 0
        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_LEFT]:
            self.speed_x = -8
        if keystate[pygame.K_RIGHT]:
            self.speed_x = 8
        self.rect.x += self.speed_x
        if keystate[pygame.K_SPACE]:
            self.shoot()
        
        # rester sur l'écran
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0

# mob
class Mob(pygame.sprite.Sprite):

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image_orig = random.choice(meteor_images)
        self.image_orig.set_colorkey(BLACK)
        self.image = self.image_orig.copy()
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(WIDTH - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        self.speedy = random.randrange(1, 8)
        self.speedx = random.randrange(-3, 3)
        # le rayon 
        self.radius = (self.rect.width * .85) // 2
        # rotation
        self.rot = 0
        self.rot_speed = random.randrange(-8, 8)
        self.last_update = pygame.time.get_ticks()
    
    def rotate(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > 50:
            self.last_update = now
            # tourner le météors
            self.rot = (self.rot + self.rot_speed) % 360
            old_center = self.rect.center  # on garde l'ancien centre 
            self.image = pygame.transform.rotate(self.image_orig, self.rot)
            self.rect = self.image.get_rect()
            self.rect.center = old_center


    def update(self):
        self.rotate()
        self.rect.y += self.speedy
        self.rect.x += self.speedx
        if self.rect.top > HEIGHT + 10 or self.rect.right < -25 or self.rect.left > WIDTH + 20:
            self.rect.x = random.randrange(WIDTH - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.speedy = random.randrange(1, 8)


#bullet
class Bullet(pygame.sprite.Sprite):

    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = bullet_img
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.speedy = -10

    def update(self):
        self.rect.y += self.speedy
        if self.rect.bottom < 0:
            self.kill()

# explosion
class Explosion(pygame.sprite.Sprite):

    def __init__(self, center, size):
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        self.image = explosion_anim[self.size][0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 50
    
    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(explosion_anim[self.size]):
                self.kill()
            else:
                center = self.rect.center
                self.image = explosion_anim[self.size][self.frame]
                self.rect = self.image.get_rect()
                self.rect.center = center

# powerup
#bullet
class Pow(pygame.sprite.Sprite):

    def __init__(self, center):
        pygame.sprite.Sprite.__init__(self)
        self.type = random.choice(['shield', 'gun'])
        self.image = powerup_images[self.type]
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.speedy = 2

    def update(self):
        self.rect.y += self.speedy
        if self.rect.bottom < 0:
            self.kill()

# définir les fonctions
def draw_text(surf, text, size, x, y):
    font = pygame.font.Font(font_name, size)
    text_surf = font.render(text, True, WHITE)
    text_rect = text_surf.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surf, text_rect)

# créer un nouveau mob
def new_mob():
    m = Mob()
    all_sprites.add(m)
    mobs.add(m)

# afficher le compteur de vie
def draw_lives(surf, x, y, lives, img):
    for i in range(lives):
        img_rect = img.get_rect()
        img_rect.x = x + 30*i
        img_rect.y = y
        surf.blit(img, img_rect)

def show_go_screen():
    screen.blit(background, background_rect)
    draw_text(screen, "SHMUP!", 64, WIDTH / 2, HEIGHT / 4)
    draw_text(screen, "Arrow keys move, Space to fire", 22, WIDTH / 2, HEIGHT / 2)
    draw_text(screen, "Press a key to begin", 18, WIDTH / 2, HEIGHT * 3 / 4)
    pygame.display.flip()
    waiting = True
    while waiting:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYUP:
                waiting = False


# définir le groupe de sprites
all_sprites = pygame.sprite.Group()
mobs = pygame.sprite.Group()
bullets = pygame.sprite.Group()
powerups = pygame.sprite.Group()

player = Player()
all_sprites.add(player)

for i in range(8):
    new_mob()

# score 
score = 0
pygame.mixer.music.play(loops=-1)

# boucle de jeu
game_over = True
running = True
while running:
    if game_over:
        show_go_screen()
        game_over = False
        all_sprites = pygame.sprite.Group()
        mobs = pygame.sprite.Group()
        bullets = pygame.sprite.Group()
        powerups = pygame.sprite.Group()
        player = Player()
        all_sprites.add(player)
        for i in range(8):
            new_mob()
        score = 0
    # la vitesse de la boucle
    clock.tick(FPS)

    # événemenents
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
    # mise à jour
    all_sprites.update()

    # collision enntre les balles et les énenmies
    hits_mob_bullet = pygame.sprite.groupcollide(mobs, bullets, True, True)
    for hit in hits_mob_bullet:
        score += 50 - hit.radius  # on soustraie 50 du rayon du méteor
        random.choice(expl_sounds).play( )
        expl = Explosion(hit.rect.center, 'lg')
        all_sprites.add(expl)
        if random.random() > 0.9:
            pow = Pow(hit.rect.center)
            powerups.add(pow)
            all_sprites.add(pow) 
        # on crée un autre mob pour chaque mob tué
        new_mob()

    # collision entre   le joueur et les énemies
    hits = pygame.sprite.spritecollide(player, mobs, True, pygame.sprite.collide_mask)
    for hit in hits:
        player.shield -= hit.radius
        expl = Explosion(hit.rect.center, 'sm')
        all_sprites.add(expl)
        new_mob()
        if player.shield <= 0:
            death_expl = Explosion(player.rect.center, 'player')
            all_sprites.add(death_expl)
            player.hide()
            player.lives -= 1
            player.shield = 100
    
    # vérifier si le joueur est en collision avec le powerup
    hits = pygame.sprite.spritecollide(player, powerups, True)
    for hit in hits:
        power_sound.play()
        if hit.type == 'shield':
            player.shield += random.randrange(10, 30)
            if player.shield >= 100:
                player.shield = 100
        if hit.type == 'gun':
            player.powerup()

    
    # vérifier si le joueur est mort et l'explosion est terminée
    if player.lives == 0 and not death_expl.alive():
        game_over = True

    # dessiner
    screen.blit(background, background_rect)
    all_sprites.draw(screen)
    draw_text(screen, str(int(score)), 18, WIDTH / 2, 10)
    player.bar_shield(screen, 10, 10)
    draw_lives(screen, WIDTH - 100, 5, player.lives, player_mini_img)
    pygame.display.flip()

pygame.quit()