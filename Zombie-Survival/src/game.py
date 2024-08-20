import pygame
import math
import numpy
import random

from CONST import *
from config import Config
from space import Space, Level_Manager
from entities import *


class Game:
    def __init__(self):
        #fonts used
        self.text_font = pygame.font.SysFont(None, 24)
        self.text_font2 = pygame.font.SysFont(None, 32) 
        self.text_font3 = pygame.font.SysFont(None, 72)

        self.config = Config()
        self.config.create_tiles()
        
        self.center = [SCREEN_WIDTH/2, SCREEN_HEIGHT/2]

        #space script manages every entitiy spawned onto game / level manager controls amount of zombies spawned
        self.space = Space()
        self.level_manager = Level_Manager()

        '''
        Everything has a game coord, however when rendered on the screen, since the player must stay at the center, 
        regardless of its game coord it's screen coord must be in the center
        Therefor the x and y off set are used to calculate what must be added on to 
        the game coord of other objects in order to create a screen coord which is the correct orientation away from the center
        '''
        self.x_offset = self.center[0] - self.space.player.game_coord[0]
        self.y_offset = self.center[1] - self.space.player.game_coord[1]

        self.shop = False        
        self.grid = []
        l = int(self.space.player.active_square[0] - SCREEN_WIDTH/64) 
        r = int(self.space.player.active_square[0] + SCREEN_WIDTH/64)
        u = int(self.space.player.active_square[1] - SCREEN_HEIGHT/64)
        d = int(self.space.player.active_square[1] + SCREEN_HEIGHT/64) 
        for row in range(u-3, d+3):
            a = []
            for col in range(l-3,r+3):
                a.append(self.config.tiles[row][col])
            self.grid.append(a)

        self.path_find_timer = 0
        
        self.zombies = []
        self.zombies_saved = []
        self.zombies_to_add = 0
        self.explosion = []






    def random_spawn(self):
        point = [self.space.player.active_square[0],self.space.player.active_square[1]]
        side = random.randint(1,2)
        match side:
            case 1: #top
                point[1] -= 15
                point[0] += random.randint(-16,16)
            case 2: #bottom
                point[1] += 15
                point[0] += random.randint(-16,16)
            case 3: #right
                point[0] -= 15
                point[1] += random.randint(-16,16)
            case 4: #left
                point[1] += 15
                point[0] += random.randint(-16,16)
        
        return point
            

        
    def load_game(self, surface, dt):
        #zombie spawner
        self.level_manager.zombie_count = len(self.zombies) + len(self.zombies_saved) #zombie count stores total zombies -> zombies on map and zombies that were out of render
        
        for i in range(self.level_manager.zombie_spawn): #spawn all the zombies in zombie_spawn -> contains new zombies to be spawned and old zombies which were rendered out
            #random spawn finds a location to spawn the zombie outside of the screen view
            self.zombies.append(Zombie(self.random_spawn(), speed = random.randint(int(100 * self.level_manager.level/5),int(300 * self.level_manager.level/5)), health= Z_HEALTH + self.level_manager.level*5))

        self.level_manager.zombie_spawn = 0 # reset counter

        #load zombies that went out of boubnds
        for zombie in self.zombies_saved:
            self.zombies.append(Zombie(self.random_spawn(), health = zombie[0], speed = zombie[1], full_health= Z_HEALTH + self.level_manager.level*5))
            self.zombies_saved.remove(zombie)
        self.zombies_to_add = 0

        #grid of tiles on the screen and very close surroundings used for path finding
        self.path_grid = []

        #grid holds the tiles that are on the screen -> constantly updated in order to save time by not rendering tiles outside of screen and going through them in for loops
        self.grid = []

        
        #border of screen
        l = int(self.space.player.active_square[0] - SCREEN_WIDTH/64)
        r = int(self.space.player.active_square[0] + SCREEN_WIDTH/64)
        u = int(self.space.player.active_square[1] - SCREEN_HEIGHT/64)
        d = int(self.space.player.active_square[1] + SCREEN_HEIGHT/64)

        #iter through rows and cols in screen and few cols and rows outside of it
        for row in range(u-3, d+3):
            a = [] #holds tiles to be rendered -> holds tile objects
            p = [] #holds tiles to be used onto pathfinding grid -> holds int 0 or 1 based on tile collider 
            for col in range(l-3,r+3):
                a.append(self.config.tiles[row][col])
                if self.config.tiles[row][col].Collider:
                    p.append(1)
                else:
                    p.append(0)
            self.grid.append(a)
            self.path_grid.append(p)
        
        #PATHFINDING VECTOR GRID
        self.vector_grid = numpy.zeros_like(self.path_grid)
        
        #start at player
        self.points_to_check = [self.space.player.active_square_screen]
        self.points_checked = []
        
        
        #recalc offset
        self.x_offset = self.center[0] - self.space.player.game_coord[0]
        self.y_offset = self.center[1] - self.space.player.game_coord[1]

        
        #iter through all tiles in grid
        for row in self.grid:
            for tile in row:
                distance = math.sqrt((self.space.player.game_coord[0]-tile.game_coord[0])**2 + (self.space.player.game_coord[1]-tile.game_coord[1])**2)
                
                #update the tile position and render it
                tile.update([self.x_offset,self.y_offset])
                surface.blit(tile.img, tile.texture_rect)
                
                #check collision - NEEDS IMPROVEMENT
                if tile.Collider and distance < 50: #only check tiles with distance to save space and time
                    if pygame.Rect.colliderect(self.space.player.rotatedRect, tile.texture_rect):
                        #Y AXIS COLLISION
                        if tile.game_coord[1] > self.space.player.game_coord[1]:
                            self.space.player.game_coord[1] -= PLAYER_SPEED *dt
                        else:
                            self.space.player.game_coord[1] += PLAYER_SPEED *dt

                            
                        #X AXIS COLLISION
                        if tile.game_coord[0] > self.space.player.game_coord[0]:
                            self.space.player.game_coord[0] -= PLAYER_SPEED *dt
                        else:
                            self.space.player.game_coord[0] += PLAYER_SPEED *dt
                    
                #CODE FOR ARMORY
                if tile.Role == "WEAPON ARMORY":
                    if distance < 50:
                        tile.img = pygame.image.load("assets/Weapon_smith2.png") #when close to armory display image with "E" on it
                        #WEAPON SHOP CODE
                        if ("WEAPON ARMORY", tile.Tile_Num) not in self.space.player.Nearby: #Tile num used to tell the difference between the same tiles -> there are multiple armories, dont want all to activate together
                            self.space.player.Nearby.append(("WEAPON ARMORY", tile.Tile_Num))
                    else:
                        tile.img = pygame.image.load("assets/Weapon_smith.png")
                        if ("WEAPON ARMORY", tile.Tile_Num) in self.space.player.Nearby:
                            self.space.player.Nearby.remove(("WEAPON ARMORY", tile.Tile_Num)) #remove the armory if nearby list because player is out of the distance
                #similar process to above
                elif tile.Role == "WAVE CONTROLLER":
                    if distance < 50 and self.level_manager.zombie_wave == False:
                        tile.img = pygame.image.load("assets/Wave_controller2.png")
                        #WAVE CONTROLLER CODE
                        if ("WAVE CONTROLLER", tile.Tile_Num) not in self.space.player.Nearby:
                            self.space.player.Nearby.append(("WAVE CONTROLLER", tile.Tile_Num))
                    else:
                        tile.img = pygame.image.load("assets/Wave_controller.png")
                        if ("WAVE CONTROLLER", tile.Tile_Num) in self.space.player.Nearby:
                            self.space.player.Nearby.remove(("WAVE CONTROLLER", tile.Tile_Num))
                              
                
                for zombie in self.zombies:
                    Zdistance = math.sqrt((zombie.game_coord[0]-tile.game_coord[0])**2 + (zombie.game_coord[1]-tile.game_coord[1])**2)
                    #check collision - NEEDS IMPROVEMENT
                    if tile.Collider and Zdistance < 50:
                        if pygame.Rect.colliderect(zombie.rotatedRect, tile.texture_rect):
                            zombie.target = zombie.active_square
                            zombie.path = [] #zombie.path is the path they must take - here we are emptying it because it is incorrect since the zombie is colliding


                            #COLLISION WITH TILES -> happens because pathfinding grid might not be accurate because player is moving whilst it is being made

                            #Y AXIS COLLISION
                            if tile.game_coord[1] >zombie.game_coord[1]:
                                zombie.game_coord[1] -= 14
                            else:
                                zombie.game_coord[1] += 14
                            #X AXIS COLLISION
                            if tile.game_coord[0] > zombie.game_coord[0]:
                                zombie.game_coord[0] -= 14
                            else:
                                zombie.game_coord[0] += 14
        img = self.text_font2.render(f"{self.level_manager.level}",True, "RED")
        if self.level_manager.zombie_wave: #display wave level
            surface.blit(img, (SCREEN_WIDTH/2, 50))
        
    def Julia(self,points): #PATHFINDING ALGORITHIM
        """
        we pass points to check, then check the tile next to it to see if it is within the border
        -> if it is within then check if tile does not have a collider (value on path grid is 0) and tile is not already being checked
        -> set value onto vector grid, this value tells us to go left, right, up, down, or diagonal in any of the 4 directions
        -> append this tile onto points in order to check tiles around - works like a recursive function
        * algorithim begins on tile of player, then expands outward
        """
        for point in points:
            y = point[1]
            x = point[0]
            if y < 37:
                if self.path_grid[y+1][x] != 1  and (x,y+1) not in  self.points_checked:
                    self.vector_grid[y+1][x] = 2
                    self.points_checked.append((x,y+1))
                    self.points_to_check.append([x,y+1])
            if y> 0:
                if self.path_grid[y-1][x] != 1 and (x,y-1) not in  self.points_checked:
                    self.vector_grid[y-1][x] = 1
                    self.points_checked.append((x,y-1))
                    self.points_to_check.append([x,y-1])
            if x < 37:
                if self.path_grid[y][x+1] != 1  and (x+1,y) not in  self.points_checked:
                    self.vector_grid[y][x+1] = 4
                    
                    self.points_checked.append((x+1,y))
                    self.points_to_check.append([x+1,y])
            if x > 0:
                if self.path_grid[y][x-1] != 1 and (x-1,y) not in  self.points_checked:
                    self.vector_grid[y][x-1] = 3
                    self.points_checked.append((x-1,y))
                    self.points_to_check.append([x-1,y])
            if x < 37 and y < 37: #bottom right
                if self.path_grid[y+1][x+1] !=1  and self.path_grid[y+1][x] != 1 and self.path_grid[y][x+1] != 1 and (x+1,y+1) not in self.points_checked:
                    self.vector_grid[y+1][x+1] = 5
                    self.points_checked.append((x+1,y+1))
                    self.points_to_check.append([x+1,y+1])
            if x < 37 and y > 0: #top right
                if self.path_grid[y-1][x+1] !=1 and self.path_grid[y-1][x] != 1 and self.path_grid[y][x+1] != 1 and (x+1,y-1) not in self.points_checked:
                    self.vector_grid[y-1][x+1] = 6
                    self.points_checked.append((x+1,y-1))
                    self.points_to_check.append([x+1,y-1])
            if x > 0 and y > 0: #top left
                if self.path_grid[y-1][x-1] !=1 and self.path_grid[y-1][x] != 1 and self.path_grid[y][x-1] != 1 and (x-1,y-1) not in self.points_checked:
                    self.vector_grid[y-1][x-1] = 7
                    self.points_checked.append((x-1,y-1))
                    self.points_to_check.append([x-1,y-1])
            if x > 0 and y < 0: #bottm left
                if self.path_grid[y+1][x-1] !=1 and self.path_grid[y+1][x] != 1 and self.path_grid[y][x-1] != 1 and (x-1,y+1) not in self.points_checked:
                    self.vector_grid[y+1][x-1] = 8
                    self.points_checked.append((x-1,y+1))
                    self.points_to_check.append([x-1,y+1])
    
    def read_path(self,enemyCoord,playerCoord,vectors):
        """
        used to read the grid produced by the pathfinding algorithim. called for every zombie
        """
        x = enemyCoord[0]
        y = enemyCoord[1]
        path = [] #reset path
        if vectors[enemyCoord[1]][enemyCoord[0]] not in (1,2,3,4,5,6,7,8): #make sure that zombie is not currently in a tile that has a collider
            return []
        else:
            #keep going until we reach the palyer coord
            while [x,y] != playerCoord:
                match vectors[y][x]:
                    case 1:
                        path.append("down")
                        y += 1
                    case 2:
                        path.append("up")
                        y-=1
                    case 3:
                        path.append("right")
                        x+=1
                    case 4:
                        path.append("left")
                        x-=1
                    case 5:
                        path.append("up left")
                        y-=1
                        x-=1
                    case 6:
                        path.append("down left")
                        y+=1
                        x-=1
                    case 7:
                        path.append("down right")
                        y+=1
                        x+=1
                    case 8:
                        path.append("up right")
                        y-=1
                        x+=1
                    #after converting grid with int values for directions and appending it onto an array, return it
            return path
    

    def show_zombies(self, surface, dt): #code used to render zombies and also update them, dt is the deltatime calculated in main

        pfind = False

        #counter used to keep track of time since last path find -> dont want to constantly pathfind as it affects performance
        self.path_find_timer += dt

        if P_TIME < self.path_find_timer: 
            self.path_find_timer = 0
            #once timer above set time, call pathfinding algorithim
            self.Julia(self.points_to_check)
            pfind = True #indicates that we have already used the pathfind algorithim this iter
        for zombie in self.zombies: #render the zombies
            surface.blit(zombie.rotatedSurf, zombie.rotatedRect)
            zombie.update([self.x_offset,self.y_offset], dt, self.space.player.game_coord) #update zombies
            

            #if our zombie is outside the render distance, we want to remove it and store its current health and speed in order to readd it to the map with its same stats but inside the render distance
            if zombie.active_square_screen[1] < 1 or zombie.active_square_screen[1] > 36 or zombie.active_square_screen[0] < 1 or zombie.active_square_screen[0] > 36:
                self.zombies_saved.append([zombie.health, zombie.speed])
                self.zombies.remove(zombie)
                

            if pfind and zombie.attacking == False: #read the path of the zombie using the function above and set it as path value in zombie (zombies wont move to path if they are currently attacking)
                zombie.path = self.read_path(zombie.active_square_screen, self.space.player.active_square_screen, self.vector_grid)
            zombie.move(zombie.path) #function which moves zombie according ot path

            distance = math.sqrt((self.space.player.game_coord[0]-zombie.game_coord[0])**2+(self.space.player.game_coord[1]-zombie.game_coord[1])**2)  
            if distance < Z_ATTACK_RANGE: #attack range of zombie
                zombie.attack_timer += dt #time since last attack
                if zombie.attack_timer > zombie.attack_time: #if true then can attack
                    zombie.attacking = True
                    zombie.attacked = False
                    zombie.attack_timer = 0
                    if (zombie.game_coord[0]-self.space.player.game_coord[0]) != 0:
                        if zombie.game_coord[0] <= self.space.player.game_coord[0]:
                            zombie.direction = math.atan((self.space.player.game_coord[1]-zombie.game_coord[1])/(zombie.game_coord[0]-self.space.player.game_coord[0])) * 180/math.pi - 90
                        else:
                            zombie.direction = math.atan((self.space.player.game_coord[1]-zombie.game_coord[1])/(zombie.game_coord[0]-self.space.player.game_coord[0])) * 180/math.pi + 90
            if zombie.attacking:
                zombie.attack(dt)
                zombie.path = [] #clear the path when attacking -> seperate movement is implemented during this stage
                zombie.target = zombie.active_square
                if zombie.attacked == False and pygame.Rect.colliderect(zombie.rotatedRect, self.space.player.rotatedRect):
                    self.space.player.take_damage(zombie.damage) #if we collide with the palyer during the attck, deal damage and turn the attacked switch on to avoid multiple attacks being done at once
                    zombie.attacked = True
        
        pfind = False   
            
    def load_shop(self, surface): #called when shop is on
        player = self.space.player
        shop = self.space.shop #object contains images loaded
        
        #render the base image
        surface.blit(shop.Base_Image, shop.Base_Image_rect)

        gun_num = len(player.Inventory) #number of guns in inventory (max of 2 plus fist -> inventory max of 3)
        #PISTOL BUTTON
        if pygame.Rect.colliderect(self.space.cursor.texture_rect, shop.pistol_toggle_img_rect):
            surface.blit(shop.pistol_toggle_img, shop.pistol_toggle_img_rect) #show different image to indicate mouse hovering over an image
            for event in pygame.event.get():
                #check if mouse clicked and if money is sufficient and if there less than 3 guns (max of 2)
                if event.type == pygame.MOUSEBUTTONDOWN and player.money >= PRICES["Pistol"] and (event.button == 1 or event.button == 3) and gun_num < 3: 
                    #swithces used to buy or sell if player releases
                    shop.possibleBuy = True
                    shop.possibleSell = True

                    shop.pistol_toggle_img = pygame.image.load("assets/Pistol_toggle2.png")

                if shop.possibleBuy == True and event.type == pygame.MOUSEBUTTONUP and event.button == 1: #if mouse left click is released -> confirm purchase
                    shop.pistol_toggle_img = pygame.image.load("assets/Pistol_toggle.png")
                    shop.possibleBuy = False
                    if "Pistol" not in player.Inventory_name:
                        #subtract price from money and append object and name of weapon into inventory and inventory names
                        player.money -= PRICES["Pistol"]
                        player.Inventory.append(Pistol())
                        player.Inventory_name.append("Pistol") 
                if shop.possibleSell == True and event.type == pygame.MOUSEBUTTONUP and event.button == 3: #if mouse right click released -> confirm selll
                    shop.pistol_toggle_img = pygame.image.load("assets/Pistol_toggle.png")
                    shop.possibleSell = False
                    if "Pistol" in player.Inventory_name:
                        #add half of the cost back
                        player.money += PRICES["Pistol"]/2
                        #set the player holding to fists incase the player was holding the gun before selling
                        player.holding = player.Inventory[0]
                        player.holding_name = player.Inventory_name[0]

                        #remove the object and name of lists
                        i = player.Inventory_name.index("Pistol")
                        player.Inventory_name.remove("Pistol")
                        del player.Inventory[i]
        
        #EXACT SAME CODE

        #SHOTGUN BUTTON
        elif pygame.Rect.colliderect(self.space.cursor.texture_rect, shop.shotgun_toggle_img_rect):
            surface.blit(shop.shotgun_toggle_img, shop.shotgun_toggle_img_rect)
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN and player.money >= PRICES["Shotgun"] and (event.button == 1 or event.button == 3) and gun_num < 3:
                    shop.possibleBuy = True
                    shop.possibleSell = True
                    shop.shotgun_toggle_img = pygame.image.load("assets/shotgun_toggle2.png")
                if shop.possibleBuy == True and event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    shop.shotgun_toggle_img = pygame.image.load("assets/shotgun_toggle.png")
                    shop.possibleBuy = False
                    if "Shotgun" not in player.Inventory_name:
                        player.money -= PRICES["Shotgun"]
                        player.Inventory.append(Shotgun())
                        player.Inventory_name.append("Shotgun")
                if shop.possibleSell == True and event.type == pygame.MOUSEBUTTONUP and event.button == 3:
                    shop.shotgun_toggle_img = pygame.image.load("assets/shotgun_toggle.png")
                    shop.possibleSell = False
                    if "Shotgun" in player.Inventory_name:
                        player.money += PRICES["Shotgun"]/2
                        player.holding = player.Inventory[0]
                        player.holding_name = player.Inventory_name[0]
                        i = player.Inventory_name.index("Shotgun")
                        player.Inventory_name.remove("Shotgun")
                        del player.Inventory[i]
        #AR BUTTON
        elif pygame.Rect.colliderect(self.space.cursor.texture_rect, shop.AR_toggle_img_rect):
            surface.blit(shop.AR_toggle_img, shop.AR_toggle_img_rect)
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN and player.money >= PRICES["AR"] and (event.button == 1 or event.button == 3) and gun_num < 3:
                    shop.possibleBuy = True
                    shop.possibleSell = True
                    shop.AR_toggle_img = pygame.image.load("assets/AR_toggle2.png")
                if shop.possibleBuy == True and event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    shop.AR_toggle_img = pygame.image.load("assets/AR_toggle.png")
                    shop.possibleBuy = False
                    if "AR" not in player.Inventory_name:
                        player.money -= PRICES["AR"]
                        player.Inventory.append(AR())
                        player.Inventory_name.append("AR")
                if shop.possibleSell == True and event.type == pygame.MOUSEBUTTONUP and event.button == 3:
                    shop.AR_toggle_img = pygame.image.load("assets/AR_toggle.png")
                    shop.possibleSell = False
                    if "AR" in player.Inventory_name:
                        player.money += PRICES["AR"]/2
                        player.holding = player.Inventory[0]
                        player.holding_name = player.Inventory_name[0]
                        i = player.Inventory_name.index("AR")
                        player.Inventory_name.remove("AR")
                        del player.Inventory[i]
        elif pygame.Rect.colliderect(self.space.cursor.texture_rect, shop.grenadeLauncher_toggle_img_rect):
            surface.blit(shop.grenadeLauncher_toggle_img, shop.grenadeLauncher_toggle_img_rect)
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN and player.money >= PRICES["GrenadeLauncher"] and (event.button == 1 or event.button == 3) and gun_num < 3:
                    shop.possibleBuy = True
                    shop.possibleSell = True
                    shop.AR_toggle_img = pygame.image.load("assets/grenadelauncher_toggle2.png")
                if shop.possibleBuy == True and event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    shop.AR_toggle_img = pygame.image.load("assets/grenadelauncher_toggle.png")
                    shop.possibleBuy = False
                    if "GrenadeLauncher" not in player.Inventory_name:
                        player.money -= PRICES["GrenadeLauncher"]
                        player.Inventory.append(GrenadeLauncher())
                        player.Inventory_name.append("GrenadeLauncher")
                if shop.possibleSell == True and event.type == pygame.MOUSEBUTTONUP and event.button == 3:
                    shop.AR_toggle_img = pygame.image.load("assets/grenadelauncher_toggle.png")
                    shop.possibleSell = False
                    if "GrenadeLauncher" in player.Inventory_name:
                        player.money += PRICES["GrenadeLauncher"]/2
                        player.holding = player.Inventory[0]
                        player.holding_name = player.Inventory_name[0]
                        i = player.Inventory_name.index("GrenadeLauncher")
                        player.Inventory_name.remove("GrenadeLauncher")
                        del player.Inventory[i]
        else:
            shop.possibleBuy = False
            shop.pistol_toggle_img = pygame.image.load("assets/Pistol_toggle.png")
            shop.shotgun_toggle_img = pygame.image.load("assets/shotgun_toggle.png")
            shop.AR_toggle_img = pygame.image.load("assets/AR_toggle.png")
            shop.grenadeLauncher_toggle_img = pygame.image.load("assets/grenadelauncher_toggle.png")

    def show_bullet(self, surface, bullets, dt): #render bullets and update them                                     
        for bullet in bullets:
            bullet.update(dt, [self.x_offset,self.y_offset])
            surface.blit(bullet.rotatedSurf, bullet.rotatedRect)
            if bullet.alive > bullet.range:
                if bullet and bullet.dead == False: 
                    bullet.dead = True
                    if bullet.name == "Grenade":
                        self.explosion.append(bullet.game_coord)
                    bullets.remove(bullet)


            #CHECK COLLISION WITH TILES

            #iter through all the tiles
            for row in self.grid:
                for tile in row:
                    distance = math.sqrt((tile.game_coord[0]-bullet.game_coord[0])**2 + (tile.game_coord[1]-bullet.game_coord[1])**2)
                    if tile.Collider and distance < 100 and tile.Role != "WATER": #only check tiles that are close -> exempt tiles with colliders that are water
                        if pygame.Rect.colliderect(tile.texture_rect, bullet.rotatedRect):
                            if bullet and bullet.dead == False:
                                self.explosion.append(bullet.game_coord) #applies for grenades
                                bullet.dead = True
                                bullets.remove(bullet) #remove the bullet if it collides with a wall
                                
            #we want to treat zombies like walls, collision removes bullet
            for zombie in self.zombies:
                if pygame.Rect.colliderect(zombie.rotatedRect, bullet.rotatedRect):
                    if bullet and bullet.dead == False:
                        if zombie.take_damage(bullet.damage/(bullet.alive+1)): #bullet does less damage the longer it is alive for. Take Damage function returns if zombie still has sufficient health
                            self.space.player.money += 15 #if the function returns true -> add money to player and remove zombie 
                            self.zombies.remove(zombie)
                            self.space.player.kills += 1
                        bullet.dead = True
                        bullets.remove(bullet)
                        if bullet.name ==  "Grenade": #if the bullet is a grenade then append to explosion array which deals with explosion effect
                            self.explosion.append(bullet.game_coord)
            for explode in self.explosion:
                if bullet.name == "Grenade":
                    for zombie in self.zombies: #check all zombies because explosion effects all in area
                        distance = math.sqrt((explode[0]-zombie.game_coord[0])**2 + (explode[1]-zombie.game_coord[1])**2) #distance of zombie to explosion center
                        damage = bullet.damage - distance/2 #damage decreases further away from center
                        if damage < 0:
                            damage = 0
                        if zombie.take_damage(damage): #apply damage funciton to zombie
                            self.space.player.money += 15
                            if zombie:
                                self.zombies.remove(zombie)
                                self.space.player.kills += 1
                    self.explosion.remove(explode) #remove explosion

                         
        
    def show_player(self, surface,dt): #render and update player
        player = self.space.player
        surface.blit(player.rotatedSurf, player.rotatedRect)
        player.update(dt)
        if player.holding_name != "Fists": #display ammo if holding a gun
            img = self.text_font.render(f"{player.holding.ammo}/{player.holding.max_ammo}",True, "white")
            surface.blit(img, (SCREEN_WIDTH - 50,SCREEN_HEIGHT-50))
        img1 = self.text_font2.render(str(int(player.health)), True, "red")
        img2 = self.text_font2.render(str(int(player.money)), True, 'purple')
        surface.blit(img1, (50, SCREEN_HEIGHT-50)) #display health
        surface.blit(img2, (50, SCREEN_HEIGHT-30))
        if player.health < 0:
            player.health = 0
    def show_cursor(self, surface, coord):
        cursor = self.space.cursor
        surface.blit(cursor.img, cursor.texture_rect)
        cursor.update(coord)
    def show_end_screen(self, surface): #render the end screen with stats
        img = pygame.image.load("assets/End_Screen.png")
        img_rect = img.get_rect(center=(SCREEN_WIDTH/2,SCREEN_HEIGHT/2))
        img1 = self.text_font3.render(str(self.space.player.kills), True, "black")
        img2 = self.text_font3.render(str(self.level_manager.level), True, "black")
        surface.blit(img, img_rect)
        surface.blit(img1, (SCREEN_WIDTH/2 + 250, 250))
        surface.blit(img2, (SCREEN_WIDTH/2 -150, 250))
        print("here")

        

