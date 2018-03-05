# includes Jumpy 16
import pygame as pg
import random
from os import path


# game options/settings
TITLE = "Jumpy!"
WIDTH = 480
HEIGHT = 600
FPS = 60
FONT_NAME = 'arial'   
HS_FILE = "highscore.txt"
SPRITESHEET = "spritesheet_jumper.png"

# Player properties
PLAYER_ACC = 0.5
PLAYER_FRICTION = -0.12
PLAYER_GRAV = 0.8
PLAYER_JUMP = 20

# Game properties
BOOST_POWER = 400   ###
POW_SPAWN_PCT = 400 ###
MOB_FREQ = 5000
PLAYER_LAYER = 2
PLATFORM_LAYER = 1
POW_LAYER = 1
MOB_LAYER = 2

# Starting platforms

PLATFORM_LIST = [(0, HEIGHT - 60),
                 (WIDTH / 2 - 50, HEIGHT * 3 / 4 - 50),
                 (125, HEIGHT - 350),
                 (350, 200),
                 (175, 100)]      

# define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
LIGHTBLUE = (0, 155, 155)
BGCOLOR = LIGHTBLUE 

vec = pg.math.Vector2



class Spritesheet:
    # utility class for loading and parsing spritesheets
    def __init__(self, filename):
        self.spritesheet = pg.image.load(filename).convert()

    def get_image(self, x, y, width, height):
        # grab an image out of a larger spritesheet
        image = pg.Surface((width, height))
        image.blit(self.spritesheet, (0, 0), (x, y, width, height))
        image = pg.transform.scale(image, (width // 2, height // 2))
        return image



class Player(pg.sprite.Sprite):
    def __init__(self, game):
        self._layer = PLAYER_LAYER  ###########
        self.groups = game.all_sprites      ###
#        pg.sprite.Sprite.__init__(self)
        pg.sprite.Sprite.__init__(self, self.groups)  ####
        self.game = game
        self.walking = False  
        self.jumping = False 
        self.current_frame = 0 
        self.last_update = 0 
        self.load_images() 
        self.image = self.standing_frames[0]
        self.rect = self.image.get_rect()
        self.rect.center = (40, HEIGHT - 100) 
        self.pos = vec(40, HEIGHT - 100) 
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)

    def load_images(self):
        self.standing_frames = [self.game.spritesheet.get_image(614, 1063, 120, 191),
                                self.game.spritesheet.get_image(690, 406, 120, 201)]
        for frame in self.standing_frames:
            frame.set_colorkey(BLACK)
        self.walk_frames_r = [self.game.spritesheet.get_image(678, 860, 120, 201),
                              self.game.spritesheet.get_image(692, 1458, 120, 207)]
        self.walk_frames_l = []
        for frame in self.walk_frames_r:
            frame.set_colorkey(BLACK)
            self.walk_frames_l.append(pg.transform.flip(frame, True, False))
        self.jump_frame = self.game.spritesheet.get_image(382, 763, 150, 181)
        self.jump_frame.set_colorkey(BLACK)


    def jump_cut(self):
        if self.jumping:
            if self.vel.y < -3:
                self.vel.y = -3

        
    def jump(self):
        # jump only if standing on a platform
        self.rect.y += 2 
        hits = pg.sprite.spritecollide(self, self.game.platforms, False)
        self.rect.y -= 2 
        if hits and not self.jumping:   
            self.game.jump_sound.play()
            self.jumping = True         
            self.vel.y = -PLAYER_JUMP   

    def update(self):
        self.animate() 
        self.acc = vec(0, PLAYER_GRAV)
        keys = pg.key.get_pressed()
        if keys[pg.K_LEFT]:
            self.acc.x = -PLAYER_ACC
        if keys[pg.K_RIGHT]:
            self.acc.x = PLAYER_ACC

        # apply friction
        self.acc.x += self.vel.x * PLAYER_FRICTION
        # equations of motion
        self.vel += self.acc
        if abs(self.vel.x) < 0.1:  
            self.vel.x = 0  
        self.pos += self.vel + 0.5 * self.acc
        # wrap around the sides of the screen
        if self.pos.x > WIDTH + self.rect.width / 2:
            self.pos.x = 0 - self.rect.width / 2
        if self.pos.x < 0 - self.rect.width / 2:
            self.pos.x = WIDTH + self.rect.width / 2
        self.rect.midbottom = self.pos


    def animate(self):
        now = pg.time.get_ticks()
        if self.vel.x != 0:             
            self.walking = True        
        else:                          
            self.walking = False       
        # show walk animation          
        if self.walking:               
            if now - self.last_update > 180:       
                self.last_update = now             
                self.current_frame = (self.current_frame + 1) % len(self.walk_frames_l)  
                bottom = self.rect.bottom          
                if self.vel.x > 0:                 
                    self.image = self.walk_frames_r[self.current_frame]        
                else:                              
                    self.image = self.walk_frames_l[self.current_frame]        
                self.rect = self.image.get_rect()  
                self.rect.bottom = bottom          
        # show idle animation
        if not self.jumping and not self.walking:
            if now - self.last_update > 350:
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(self.standing_frames)
                bottom = self.rect.bottom
                self.image = self.standing_frames[self.current_frame]
                self.rect = self.image.get_rect()
                self.rect.bottom = bottom


class Platform(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self._layer = PLATFORM_LAYER   ###############
        self.groups = game.all_sprites, game.platforms  #####
#        pg.sprite.Sprite.__init__(self)
        pg.sprite.Sprite.__init__(self, self.groups)    #####        
        self.game = game 
        images = [self.game.spritesheet.get_image(0, 288, 380, 94),
                  self.game.spritesheet.get_image(213, 1662, 201, 100)] 
        self.image = random.choice(images)
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        if random.randrange(100) < POW_SPAWN_PCT:  ###
            Pow(self.game, self)            ###


###########
class Pow(pg.sprite.Sprite):
    def __init__(self, game, plat):
        self._layer = POW_LAYER
        self.groups = game.all_sprites, game.powerups
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.plat = plat
        self.type = random.choice(['boost'])
        self.image = self.game.spritesheet.get_image(820, 1805, 71, 70)
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.centerx = self.plat.rect.centerx
        self.rect.bottom = self.plat.rect.top - 5

    def update(self):
        self.rect.bottom = self.plat.rect.top - 5
        if not self.game.platforms.has(self.plat):
            self.kill()


class Mob(pg.sprite.Sprite):
    def __init__(self, game):
        self._layer = MOB_LAYER
        self.groups = game.all_sprites, game.mobs
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image_up = self.game.spritesheet.get_image(566, 510, 122, 139)
        self.image_up.set_colorkey(BLACK)
        self.image_down = self.game.spritesheet.get_image(568, 1534, 122, 135)
        self.image_down.set_colorkey(BLACK)
        self.image = self.image_up
        self.rect = self.image.get_rect()
        self.rect.centerx = random.choice([-100, HEIGHT + 100])
        self.vy = random.randrange(1, 4)
        if self.rect.centery > HEIGHT:
            self.vx *= -1
        self.rect.x = random.randrange(WIDTH / 2)
        self.vx = 0
        self.dx = 0.5

    def update(self):
        self.rect.y += self.vy
        self.vx += self.dx
        if self.vx > 3 or self.vx < -3:
            self.dx *= -1
        center = self.rect.center
        if self.dx < 0:
            self.image = self.image_up
        else:
            self.image = self.image_down
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.rect.x += self.vx
        if self.rect.left > WIDTH + 100 or self.rect.right < -100:
            self.kill()
###########

            
class Game:
    def __init__(self):
        # initialize game window, etc
        pg.init()
        pg.mixer.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        self.running = True
        self.font_name = pg.font.match_font(FONT_NAME)
        self.load_data()   

    def load_data(self):
        # load high score
        self.dir = path.dirname(__file__)
        with open(path.join(self.dir, HS_FILE), 'r') as f:
            try:
                self.highscore = int(f.read())
            except:
                self.highscore = 0
        # load spritesheet image
        self.spritesheet = Spritesheet(path.join(self.dir, SPRITESHEET)) 
        self.jump_sound = pg.mixer.Sound(path.join(self.dir, 'Jump33.wav')) 
        self.boost_sound = pg.mixer.Sound(path.join(self.dir, 'Boost16.wav'))###



    def new(self):
        # start a new game
        self.score = 0
        self.all_sprites = pg.sprite.Group()
        self.platforms = pg.sprite.Group()
        self.powerups = pg.sprite.Group() ####
        self.mobs = pg.sprite.Group()   ############
        self.player = Player(self)
 #       self.all_sprites.add(self.player)
        for plat in PLATFORM_LIST:
            Platform(self, *plat)
#            p = Platform(self, *plat)  
#            self.all_sprites.add(p)
#            self.platforms.add(p)
        self.mob_timer = 0      ##############
        pg.mixer.music.load(path.join(self.dir, 'Happy Tune.ogg')) 
        self.run()

    def run(self):
        # Game Loop
        pg.mixer.music.play(loops=-1) 
        self.playing = True
        while self.playing:
            self.clock.tick(FPS)
            self.events()
            self.update()
            self.draw()
        pg.mixer.music.fadeout(500)  

    def update(self):
        # Game Loop - Update
        self.all_sprites.update()
        # spawn a mob?
        now = pg.time.get_ticks()   ##############
        if now - self.mob_timer > 5000 + random.choice([-1000, -500, 0, 500, 1000]):  ###########
            self.mob_timer = now  ##############
            Mob(self)       ############
        # hit mobs?
        mob_hits = pg.sprite.spritecollide(self.player, self.mobs, False)          ############
        if mob_hits:          ############
            self.playing = False              ###########


        
        # check if player hits a platform - only if falling
        if self.player.vel.y > 0:
            hits = pg.sprite.spritecollide(self.player, self.platforms, False) 
            if hits:
                lowest = hits[0]    
                for hit in hits:        
                    if hit.rect.bottom > lowest.rect.bottom:
                        lowest = hit
                if self.player.pos.x < lowest.rect.right + 10 and \
                   self.player.pos.x > lowest.rect.left - 10:           ###
                    if self.player.pos.y < lowest.rect.centery:  # >
                        self.player.pos.y = hits[0].rect.top        # >
                        self.player.vel.y = 0                   # >
                        self.player.jumping = False             # >

        # if player reaches top 1/4 of screen
        if self.player.rect.top <= HEIGHT / 4:
            self.player.pos.y += max(abs(self.player.vel.y),2)
            for mob in self.mobs:       ############
                mob.rect.y += max(abs(self.player.vel.y), 2) ##########
            for plat in self.platforms:
                plat.rect.y += max(abs(self.player.vel.y),2) 
                if plat.rect.top >= HEIGHT:
                    plat.kill()
                    self.score += 10   
#######
        # if player hits powerup
        pow_hits = pg.sprite.spritecollide(self.player, self.powerups, True)
        for pow in pow_hits:
            if pow.type == 'boost':
                self.boost_sound.play()
                self.player.vel.y = -BOOST_POWER
                self.player.jumping = False
#######
        # Die!
        if self.player.rect.bottom > HEIGHT:
            for sprite in self.all_sprites:
                sprite.rect.y -= max(self.player.vel.y, 10)
                if sprite.rect.bottom < 0:
                    sprite.kill()
        if len(self.platforms) == 0:
            self.playing = False

        # spawn new platforms to keep same average number
        while len(self.platforms) < 6:
            width = random.randrange(50, 100)
            Platform(self, random.randrange(0, WIDTH - width),
                     random.randrange(-75, -30))   #####
#            p = Platform(self, random.randrange(0, WIDTH - width),
#                         random.randrange(-75, -30))
#            self.platforms.add(p)
#            self.all_sprites.add(p)

    def events(self):
        # Game Loop - events
        for event in pg.event.get():
            # check for closing window
            if event.type == pg.QUIT:
                if self.playing:
                    self.playing = False
                self.running = False
            if event.type == pg.KEYDOWN:
                if (event.key == pg.K_SPACE) or (event.key == pg.K_UP): 
                    self.player.jump()      
            if event.type == pg.KEYUP:      
                if (event.key == pg.K_SPACE) or (event.key == pg.K_UP): 
                    self.player.jump_cut()          


    def draw(self):
        # Game Loop - draw
        self.screen.fill(BGCOLOR)  
        self.all_sprites.draw(self.screen)
        self.screen.blit(self.player.image, self.player.rect)  
        self.draw_text(str(self.score), 22, WHITE, WIDTH / 2, 15)  
        # *after* drawing everything, flip the display
        pg.display.flip()

    def show_start_screen(self):
        # game splash/start screen
        pg.mixer.music.load(path.join(self.dir, 'Yippee.ogg')) 
        pg.mixer.music.play(loops=-1)  
        self.screen.fill(BGCOLOR)
        self.draw_text(TITLE, 48, WHITE, WIDTH / 2, HEIGHT / 4)
        self.draw_text("Arrows to move, Space to jump", 22, WHITE, WIDTH / 2, HEIGHT / 2)
        self.draw_text("Press a key to play", 22, WHITE, WIDTH / 2, HEIGHT * 3 / 4)
        self.draw_text("High Score: " + str(self.highscore), 22, WHITE, WIDTH / 2, 15)
        pg.display.flip()
        self.wait_for_key()  
        pg.mixer.music.fadeout(500)     

    def show_go_screen(self):      
        # game over/continue
        if not self.running:
            return
        pg.mixer.music.load(path.join(self.dir, 'Yippee.ogg')) 
        pg.mixer.music.play(loops=-1)  
        self.screen.fill(BGCOLOR)  
        self.draw_text("GAME OVER", 48, WHITE, WIDTH / 2, HEIGHT / 4)
        self.draw_text("Score: " + str(self.score), 22, WHITE, WIDTH / 2, HEIGHT / 2)
        self.draw_text("Press a key to play again", 22, WHITE, WIDTH / 2, HEIGHT * 3 / 4)
        if self.score > self.highscore:
            self.highscore = self.score
            self.draw_text("NEW HIGH SCORE!", 22, WHITE, WIDTH / 2, HEIGHT / 2 + 40)
            with open(path.join(self.dir, HS_FILE), 'w') as f:
                f.write(str(self.score))
        else:
            self.draw_text("High Score: " + str(self.highscore), 22, WHITE, WIDTH / 2, HEIGHT / 2 + 40)
        pg.display.flip()
        self.wait_for_key()
        pg.mixer.music.fadeout(500)        


    def wait_for_key(self):
        waiting = True
        while waiting:
            self.clock.tick(FPS)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    waiting = False
                    self.running = False
                if event.type == pg.KEYUP:
                    waiting = False
                    
    def draw_text(self, text, size, color, x, y):
        font = pg.font.Font(self.font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x, y)
        self.screen.blit(text_surface, text_rect)

g = Game()
g.show_start_screen()
while g.running:
    g.new()
    g.show_go_screen()

pg.quit()
