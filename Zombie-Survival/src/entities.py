import pygame
import math
import random

from CONST import *

class Shop():
    def __init__(self):
        self.Open = False
        self.Base_Image = pygame.image.load("assets/Shop_Menu.png")
        self.Base_Image_rect = self.Base_Image.get_rect(center = (SCREEN_WIDTH/2, SCREEN_HEIGHT-150))

        self.possibleBuy = False
        self.possibleSell = False
        #pistol
        self.pistol_toggle_img = pygame.image.load("assets/Pistol_toggle.png")
        self.pistol_toggle_img_rect = self.pistol_toggle_img.get_rect(center = (SCREEN_WIDTH/2 - 310, SCREEN_HEIGHT-195))

        #shotgun
        self.shotgun_toggle_img = pygame.image.load("assets/shotgun_toggle.png")
        self.shotgun_toggle_img_rect = self.shotgun_toggle_img.get_rect(center = (SCREEN_WIDTH/2 -150, SCREEN_HEIGHT-195))

        #AR
        self.AR_toggle_img = pygame.image.load("assets/AR_toggle.png")
        self.AR_toggle_img_rect = self.AR_toggle_img.get_rect(center = (SCREEN_WIDTH/2 +10, SCREEN_HEIGHT-195))

        #Grenade Launcher
        self.grenadeLauncher_toggle_img = pygame.image.load('assets/grenadelauncher_toggle.png')
        self.grenadeLauncher_toggle_img_rect = self.AR_toggle_img.get_rect(center = (SCREEN_WIDTH/2 + 170, SCREEN_HEIGHT-195))

class Player:
    def __init__(self):
        self.game_coord = [SCREEN_WIDTH/2, SCREEN_WIDTH/2] #coord relative to map
        self.screen_coord = [SCREEN_WIDTH/2, SCREEN_WIDTH/2] #coord relative to screen
        self.active_square = [self.game_coord[0]//TILE_WIDTH, self.game_coord[1]//TILE_HEIGHT] #game coord converted to tiles
        self.active_square_screen = [20,20] #screen coord converted to tiles

        self.direction = 0
        self.speed = PLAYER_SPEED
        
        self.Nearby = [] #stores nearby objects that can be accessed

        self.bullets = [] #stores all bullet objects created
        self.reloading = False

        self.Inventory = [Fists()] #STORES OBJECTS 
        self.Inventory_name = ["Fists"] #name of objects in inventory in same order
        self.holding = self.Inventory[0] #current item being held from inventory
        self.holding_name = self.Inventory_name[0] #name of item being held
        self.money = 0
        self.health = PLAYER_HEALTH
        self.regen_time = 5 #time without being attacked in order to regen health
        self.regen_timer = 0 
        self.kills = 0
        #images
        self.img = pygame.image.load("assets/player_prototype.png")
        self.rect = self.img.get_rect(center = self.screen_coord)

        self.rotatedSurf = pygame.transform.rotate(self.img, self.direction)
        self.rotatedRect = self.rotatedSurf.get_rect()
        self.rotatedRect.center = self.screen_coord

    def update(self, dt):

        self.active_square = [int(self.game_coord[0]//TILE_WIDTH), int(self.game_coord[1]//TILE_HEIGHT)] #update active square
        
        #BORDER CONTROL -> dont step out of the map
        if self.game_coord[0] > MAP_WIDTH - SCREEN_WIDTH/2 - TILE_WIDTH*4:
            self.game_coord[0] = MAP_WIDTH - SCREEN_WIDTH/2 - TILE_WIDTH*4
        elif self.game_coord[0] < SCREEN_WIDTH/2 + TILE_WIDTH*4:
            self.game_coord[0] = SCREEN_WIDTH/2 + TILE_WIDTH*4
        
        if self.game_coord[1] > MAP_HEIGHT - SCREEN_HEIGHT/2 - TILE_HEIGHT*4:
            self.game_coord[1] = MAP_HEIGHT - SCREEN_HEIGHT/2 - TILE_HEIGHT*4
        elif self.game_coord[1] < SCREEN_HEIGHT/2 + TILE_HEIGHT*4:
            self.game_coord[1] = SCREEN_HEIGHT/2 + TILE_HEIGHT*4
        
        gun = self.holding
        name = self.holding_name
        if self.reloading: #once reloading
            if name != "Fists": #skip over fists as it does not have following attributes
                self.speed = PLAYER_SPEED - 100 #slow down player once reloading
                gun.reload_timer += dt 
                if gun.reload_timer >= gun.reload_time: #once true then relaod time has been reached
                    if name == "Shotgun": #special case -> shotgun reloads 2 bullets at a time compared to other weapons
                        gun.ammo += 2
                        gun.reload_timer = 0
                        if gun.ammo == gun.max_ammo:
                            self.reloading = False
                    else: #reset variables
                        gun.ammo = gun.max_ammo 
                        self.reloading = False
                        gun.reload_timer = 0
        else:
            if name != "Fists":
                gun.reload_timer = 0
            self.speed = PLAYER_SPEED
        

                
        
        #LOAD IMAGE OF ITEM BEING HELD:
        match self.holding:
            case Fists():
                self.img = pygame.image.load("assets/player_prototype.png")
            case Pistol():
                self.img = pygame.image.load("assets/player_prototype_pistol.png")
            case Shotgun():
                self.img = pygame.image.load("assets/player_prototype_shotgun.png")
            case AR():
                self.img = pygame.image.load("assets/player_prototype_ar.png")
            case GrenadeLauncher():
                self.img = pygame.image.load("assets/player_prototype_grenadelauncher.png")

        self.rotatedSurf = pygame.transform.rotate(self.img, self.direction)
        self.rotatedRect = self.rotatedSurf.get_rect()
        self.rotatedRect.center = self.screen_coord
        self.holding.timer += dt #time of weapon -> used for fire rate


        #ONCE HAVENT BEEN DAMAGED FOR ENOUGH TIME REGEN HEALTH
        self.regen_timer += dt
        if self.regen_time < self.regen_timer: #regen health once certain time is reached
            if self.health < 100:
                self.health += dt * 15
            else:
                self.health = 100
        
    def shoot(self, zombies = None):
        gun = self.holding  
        name = self.holding_name
        fire_distance = self.img.get_height()/2     
        if gun.timer > gun.fire_time: #controls fire rate
            if name == "Shotgun" and gun.ammo > 0:
                #EACH BULLET HAS DIFF DIRECTION
                self.bullets.append(Bullet(gun.speed, gun.damage, gun.range, self.direction +4, [self.screen_coord[0],self.screen_coord[1]],[self.game_coord[0],self.game_coord[1]], fire_distance))
                self.bullets.append(Bullet(gun.speed, gun.damage, gun.range, self.direction+8, [self.screen_coord[0],self.screen_coord[1]],[self.game_coord[0],self.game_coord[1]], fire_distance))
                self.bullets.append(Bullet(gun.speed, gun.damage, gun.range, self.direction, [self.screen_coord[0],self.screen_coord[1]],[self.game_coord[0],self.game_coord[1]], fire_distance))
                self.bullets.append(Bullet(gun.speed, gun.damage, gun.range, self.direction -8, [self.screen_coord[0],self.screen_coord[1]],[self.game_coord[0],self.game_coord[1]], fire_distance))
                self.bullets.append(Bullet(gun.speed, gun.damage, gun.range, self.direction -3, [self.screen_coord[0],self.screen_coord[1]],[self.game_coord[0],self.game_coord[1]], fire_distance))
                gun.ammo -= 2
            elif name == "Fists":
                gun.hit(zombies, self.game_coord, self.direction, self) #seperate function for fists
            elif name == "GrenadeLauncher" and gun.ammo > 0: 
                self.bullets.append(Grenade(gun.speed, gun.damage, gun.range, self.direction, [self.screen_coord[0], self.screen_coord[1]], [self.game_coord[0],self.game_coord[1]], fire_distance))
                gun.ammo -=1
            elif gun.ammo > 0:
                #REGULAR GUNS THAT SHOOT ONE BULLET AT A TIME
                self.bullets.append(Bullet(gun.speed, gun.damage, gun.range, self.direction, [self.screen_coord[0],self.screen_coord[1]],[self.game_coord[0],self.game_coord[1]], fire_distance))
                gun.ammo -= 1
            else:
                self.reloading = True
                
            gun.timer = 0
            
    def take_damage(self, damage): #function to take damage -> resets regen timer
        self.health -= damage
        self.regen_timer = 0 
class Zombie:
    def __init__(self, spawn_tile, speed = Z_SPEED, health = Z_HEALTH, full_health = Z_HEALTH):
        self.direction = 0
        self.full_health = full_health
        self.health = health
        self.speed = speed
        self.damage = 15

        self.moving_h = False #horizontal movement
        self.moving_v = False #vertival movement
        
        self.path = [] #path to move

        self.game_coord = [] 
        self.game_coord.append(spawn_tile[0]*32)
        self.game_coord.append(spawn_tile[1]*32)
        
        self.active_square = [int(self.game_coord[0]//TILE_WIDTH), int(self.game_coord[1]//TILE_HEIGHT)] #game coord in tiles
        self.target = [0,0] #target is location zombie is pathfinding to
        self.target[0] = self.active_square[0]
        self.target[1] = self.active_square[1]

        self.screen_coord = []
        self.screen_coord.append(spawn_tile[0]*32)
        self.screen_coord.append(spawn_tile[1]*32)
        self.active_square_screen = [int(self.screen_coord[0]//TILE_WIDTH), int(self.screen_coord[1]//TILE_HEIGHT)]
        
        self.attacking = False
        self.attack_time = 2 #hit rate of zombie
        self.attack_timer = 0
        self.attacking_timer = 0 
        self.attacked = False #if delt damage then turn true
        ratio = self.health/self.full_health
        if ratio > 0.8: #change image depending on health
            self.img = pygame.image.load("assets/zombie.png")
        elif ratio > 0.5:
            self.img = pygame.image.load("assets/zombie60.png")
        elif ratio > 0.3:
            self.img = pygame.image.load("assets/zombie40.png")
        else:
            self.img = pygame.image.load("assets/zombie20.png")
        
        self.rect = self.img.get_rect(center = self.screen_coord)

        self.rotatedSurf = pygame.transform.rotate(self.img, self.direction)
        self.rotatedRect = self.rotatedSurf.get_rect()
        self.rotatedRect.center = self.screen_coord
    def update(self, offset, dt, player_coord): 
        self.screen_coord[0] = self.game_coord[0] + offset[0] #update screen coord depending on offset
        self.screen_coord[1] = self.game_coord[1] + offset[1]
        self.active_square_screen = [int(self.screen_coord[0]//TILE_WIDTH), int(self.screen_coord[1]//TILE_HEIGHT)]

        self.rotatedSurf = pygame.transform.rotate(self.img, self.direction)
        self.rotatedRect = self.rotatedSurf.get_rect()
        self.rotatedRect.center = self.screen_coord

        self.active_square = [int(self.game_coord[0]//TILE_WIDTH), int(self.game_coord[1]//TILE_HEIGHT)]

        dis = [self.game_coord[0]-player_coord[0],self.game_coord[1]-player_coord[1]] #distance from player
        self.active_square_screen = [int(20 + dis[0]//TILE_WIDTH),int( 20 + dis[1]//TILE_HEIGHT)]


        #depending on location of target tile relative to active tile, move in direction of active tile
        if self.target[0] < self.active_square[0]:
            self.game_coord[0] -= self.speed*dt
            self.moving_h = True
        elif self.target[0] > self.active_square[0]:
            self.game_coord[0] += self.speed*dt
            self.moving_h = True
        else:
            self.moving_h = False
        if self.target[1] < self.active_square[1]:
            self.game_coord[1] -= self.speed*dt
            self.moving_v = True
        elif self.target[1] > self.active_square[1]:
            self.game_coord[1] += self.speed*dt
            self.moving_v = True
        else:
            self.moving_v = False
        
    
    def move(self, path): #move function, takes in a path and translates it by manipulating the target tile
        if self.moving_v == False and self.moving_h == False  and len(path) > 0:
            match path[0]:
                case "up":
                    self.target[1] -=1
                    if path[0]:
                        path.remove(path[0])
                        self.direction = 0
                case "down":
                    self.target[1] +=1
                    if path[0]:
                        path.remove(path[0])
                        self.direction = 180
                case "left":
                    self.target[0] -=1
                    if path[0]:
                        path.remove(path[0])
                        self.direction = 90
                case "right":
                    self.target[0] +=1
                    if path[0]:
                        path.remove(path[0])
                        self.direction = 270
                case "up left":
                    self.target[0] -= 1
                    self.target[1] -= 1
                    if path[0]:
                        path.remove(path[0])
                        self.direction = 45
                case "down left":
                    self.target[0] -= 1
                    self.target[1] += 1
                    if path[0]:
                        path.remove(path[0])
                        self.direction = 135
                case "down right":
                    self.target[0] += 1
                    self.target[1] += 1
                    if path[0]:
                        path.remove(path[0])
                        self.direction = 225
                case "up right":
                    self.target[0] += 1
                    self.target[1] -= 1
                    if path[0]:
                        path.remove(path[0])
                        self.direction = 225 
    def take_damage(self, damage): #change image depending on health remaining and subtract damage
        self.health -= damage
        ratio = self.health/self.full_health
        if ratio > 0.8:
            self.img = pygame.image.load("assets/zombie.png")
        elif ratio > 0.5:
            self.img = pygame.image.load("assets/zombie60.png")
        elif ratio > 0.3:
            self.img = pygame.image.load("assets/zombie40.png")
        else:
            self.img = pygame.image.load("assets/zombie20.png")
        if self.health > 0:
            return False
        else:
            return True #return if zombie is dead or alive
    def attack(self, dt):
        
        self.attacking_timer += dt
        if self.attacking_timer < 0.3: #move towards player
            self.game_coord[0] -= (self.speed + 200)* dt * math.sin(self.direction * math.pi/180)
            self.game_coord[1] -= self.speed * dt * math.cos(self.direction * math.pi/180)
        elif self.attacking_timer < 0.6: #move away from player
            self.game_coord[0] += (self.speed+80) * dt * math.sin(self.direction * math.pi/180)
            self.game_coord[1] += (self.speed+80) * dt * math.cos(self.direction * math.pi/180)
        else:  #reset
            self.attacking_timer = 0
            self.attacking = False     
class Fists:
    def __init__(self):
        self.range = 100
        self.timer = 0.1
        self.damage = 35
        self.fire_time = 0.1
    def hit(self, zombies, player_coord, player_direction, player):
        if zombies != None: #skip case where we hit nothing
            hit = False
            for zombie in zombies:
                if (-zombie.game_coord[0]+player_coord[0]) != 0:
                    angle = math.atan((-player_coord[1]+zombie.game_coord[1])/(-zombie.game_coord[0]+player_coord[0])) * 180/math.pi - 90
                dis = math.sqrt((zombie.game_coord[0]-player_coord[0])**2 + (zombie.game_coord[1]-player_coord[1])**2)
                if dis < self.range and hit == False and abs(angle - player_direction) < 30: #if zombie is within range and the angle of the zombie is within the view of the player -> attack
                    hit = True
                    if zombie.take_damage(self.damage):
                        zombies.remove(zombie)
                        player.money += 15
            hit = False
class Pistol:
    def __init__(self):
        self.fire_time = 1
        self.timer = 1
        self.damage = 25
        self.speed = 800
        self.range = 0.8 
        self.max_ammo = 15
        self.ammo = 15 #current ammo

        self.reload_time = 2
        self.reload_timer = 0
class Shotgun:
    def __init__(self):
        self.fire_time = 2 #time till next bullet
        self.timer = 2
        self.damage = 25
        self.speed = 600
        self.range = 0.4
        self.num_shells = 6
        self.max_ammo = 6
        self.ammo = 6 #current ammo - lose 2 every shot

        self.reload_time = 1.5 #reload 2 at a time
        self.relaod_timer = 0
class AR:
    def __init__(self):
        self.fire_time = 1/8 #time till next bullet
        self.timer = 1/8
        self.damage = 30
        self.speed = 800
        self.range = 0.8
        self.max_ammo = 30
        self.ammo = 30

        self.reload_time = 4
        self.reload_timer = 0
class GrenadeLauncher:
    def __init__(self):
        self.fire_time = 1.1
        self.timer = 1
        self.damage = 140
        self.speed = 280
        self.range = 1
        self.max_ammo = 8
        self.ammo = 8
        self.radius = 100

        self.reload_time = 4
        self.reload_timer = 0
class Grenade:
    def __init__(self, speed, damage, range, direction, screen_coord, game_coord, fire_distance):
        self.speed = speed 
        self.damage = damage 
        self.alive = 0 #takes track of how long grenade has been active for
        self.range = range
        self.direction = direction
        self.screen_coord = screen_coord
        self.game_coord = game_coord
        self.dead = False
        self.name = "Grenade"

        #ADJUST FIRE LOCATION - dont want to fire from center of player, instead we want to fire from gun
        self.game_coord[0] -= fire_distance*math.sin(self.direction*math.pi/180)
        self.game_coord[1] -= fire_distance*math.cos(self.direction*math.pi/180)
        #images
        self.img = pygame.image.load("assets/grenade.png")
        self.rect = self.img.get_rect(center = self.screen_coord)

        self.rotatedSurf = pygame.transform.rotate(self.img, self.direction)
        self.rotatedRect = self.rotatedSurf.get_rect()
        self.rotatedRect.center = self.screen_coord
    def update(self, dt, offset):
        self.alive += dt #increase life time so far

        self.game_coord[0] -= self.speed*dt*math.sin(self.direction*math.pi/180) #move grenade
        self.game_coord[1] -= self.speed*dt*math.cos(self.direction*math.pi/180)

        self.screen_coord[0] = self.game_coord[0] + offset[0]
        self.screen_coord[1] = self.game_coord[1] + offset[1]
        self.rotatedSurf = pygame.transform.rotate(self.img, self.direction)
        self.rotatedRect.center = self.screen_coord   
class Bullet:
    def __init__(self, speed, damage, range, direction, screen_coord, game_coord, fire_distance):
        self.speed = speed
        self.damage = damage
        self.alive = 0
        self.range = range
        self.direction = direction
        self.screen_coord = screen_coord
        self.game_coord = game_coord
        self.dead = False
        self.name = "Bullet"

        #ADJUST FIRE LOCATION - fire from gun not center of player
        self.game_coord[0] -= fire_distance*math.sin(self.direction*math.pi/180) 
        self.game_coord[1] -= fire_distance*math.cos(self.direction*math.pi/180)
        #images
        self.img = pygame.image.load("assets/bullet.png")
        self.rect = self.img.get_rect(center = self.screen_coord)

        self.rotatedSurf = pygame.transform.rotate(self.img, self.direction)
        self.rotatedRect = self.rotatedSurf.get_rect()
        self.rotatedRect.center = self.screen_coord
    def update(self, dt, offset):
        self.alive += dt

        self.game_coord[0] -= self.speed*dt*math.sin(self.direction*math.pi/180) #move bullet
        self.game_coord[1] -= self.speed*dt*math.cos(self.direction*math.pi/180)

        self.screen_coord[0] = self.game_coord[0] + offset[0]
        self.screen_coord[1] = self.game_coord[1] + offset[1]
        self.rotatedSurf = pygame.transform.rotate(self.img, self.direction)
        self.rotatedRect.center = self.screen_coord       
class Tile:
    def __init__(self, game_coord,screen_coord,num, i = 0, Collider = False):
        self.width = TILE_WIDTH
        self.heaight = TILE_WIDTH
        self.num = i
        self.game_coord = game_coord
        self.screen_coord = screen_coord
        self.Collider = Collider
        self.Role = None

        self.Tile_Num = num

        #assign image and attributes
        match i:
            case 1:
                i = random.randint(1,4)
                self.img = pygame.image.load(f"assets/grass{i}.png")
            case 2:
                self.img = pygame.image.load("assets/WoodFloor.png")
            case 3:
                self.img = pygame.image.load("assets/WoodWall.png")
                self.Collider = True
            case 4:
                self.img = pygame.image.load("assets/Weapon_smith.png")
                self.Role = "WEAPON ARMORY"
                self.Collider = True
            case 5:
                self.img = pygame.image.load('assets/Metal_block.png')
                self.Collider = True
            case 6:
                self.img = pygame.image.load('assets/rocks.png')
            case 7:
                self.img = pygame.image.load('assets/flower_pink.png')
            case 8:
                self.img = pygame.image.load('assets/flower_purple.png')
            case 9:
                self.img = pygame.image.load('assets/Wave_controller.png')
                self.Role = "WAVE CONTROLLER"
                self.Collider = True
            case 10:
                self.img = pygame.image.load('assets/treeTrunk.png')
                self.Collider = True
            case 11:
                self.img = pygame.image.load('assets/water.png')
                self.Collider = True
                self.Role = "WATER"
                

        
        self.texture_rect = self.img.get_rect(center = self.screen_coord)          
    
    def update(self, offset): 
        #adjust screen position only - game coord is permanent
        self.screen_coord[0] = self.game_coord[0] + offset[0]
        self.screen_coord[1] = self.game_coord[1] + offset[1]
        self.texture_rect = self.img.get_rect(center = self.screen_coord)
class Cursor:
    def __init__(self):
        self.coord = [0,0]
        self.img = pygame.image.load("assets/cursor.png")
        self.texture_rect = self.img.get_rect(center = self.coord)

    def update(self, coord):
        self.coord = coord
        self.texture_rect = self.img.get_rect(center = self.coord)