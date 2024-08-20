import pygame
import time
import sys
import math

from CONST import *
from game import Game
from entities import Zombie

class main:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Zombies")
        self.game = Game()

    def mainloop(self):
        #used as game loop switch
        playing = True

        player = self.game.space.player
        game = self.game
        screen = self.screen

        #stores time passed since last iter
        dt = 0
        prev = time.time()

        #default keys
        moveUp = False
        moveDown = False
        moveRight = False
        moveLeft = False
        shoot = False
        shop = game.shop

        #counter used to track time since death -> display end screen after certain time not instantly
        t = 0
        
        
        #MOUSE COORDS (default)
        X_mouse = 500
        Y_mouse = 500

        while playing:    
            #SHOW EVERYTHING
            game.load_game(screen, dt)
            game.show_bullet(screen,player.bullets,dt)
            game.show_player(screen, dt)
            game.level_manager.update()
            game.show_zombies(screen, dt)
            
            #shop switch -> render shop when shop is open
            if shop:
                game.load_shop(screen)
            
            game.show_cursor(screen, [X_mouse, Y_mouse])

            #calculate delta time
            now = time.time()
            dt = now - prev
            prev = time.time()


            #KEYS
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_w:
                        moveUp = True
                    if event.key == pygame.K_a:
                        moveLeft = True
                    if event.key == pygame.K_d:
                        moveRight = True
                    if event.key == pygame.K_s:
                        moveDown = True
                    #if not shooting and use "R" -> reload
                    if event.key == pygame.K_r and shoot == False:
                        player.reloading  = True
                    #player.nearby stores objects in range of player that can be accessed
                    for nearby in player.Nearby:
                        if nearby[0] == "WEAPON ARMORY":
                            #if shop already open use "E" to close, if shop closed use "E" to open
                            if event.key == pygame.K_e and shop == False:
                                shop = True
                            elif event.key == pygame.K_e and shop == True:
                                shop = False
                        else:
                            #automatically clsoe shop if player is near different object
                            shop = False
                        if nearby[0] == "WAVE CONTROLLER":
                            #access wave controller by using "E" but zombie wave must be off
                            if event.key == pygame.K_e and game.level_manager.zombie_wave == False:
                                game.level_manager.new_level()

                    #switching weapons in inventory
                    #player.inventory -> stores objects (weapons)
                    #player.inventory_name -> stores names of objects in same order as objects -> should have used one array to store both
                    #player.holding stores the single object held by player from inventory
                    if event.key == pygame.K_1:
                        player.holding = player.Inventory[0]
                        player.holding_name = player.Inventory_name[0]
                        #cancel any reload once weapon is switched
                        player.reloading = False
                    elif event.key == pygame.K_2 and len(player.Inventory) >= 2: #keys 2 and 3 wont work if length of inventory doesnt have 2 or 3 items
                        player.holding = player.Inventory[1]
                        player.holding_name = player.Inventory_name[1]
                        player.reloading  = False 
                    elif event.key == pygame.K_3 and len(player.Inventory) >= 3:
                        player.holding = player.Inventory[2]
                        player.holding_name = player.Inventory_name[2]
                        player.reloading  = False
                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_w:
                        moveUp = False
                    if event.key == pygame.K_a:
                        moveLeft = False
                    if event.key == pygame.K_d:
                        moveRight = False
                    if event.key == pygame.K_s:
                        moveDown = False 

                #shoot is a switch used for player shooting
                if event.type == pygame.MOUSEBUTTONDOWN:
                    shoot = True
                elif event.type == pygame.MOUSEBUTTONUP:
                    shoot = False
            
            #close shop if nothing is nearby
            if player.Nearby == []:
                shop = False
            self.game.space.shop.Open = shop
            
            #CALL FIRE
            if shoot:
                player.shoot(zombies = self.game.zombies)
                if player.holding_name != "Fists" and player.holding.ammo > 0:
                    player.reloading  = False
      
            #MOUSE UPDATE
            X_mouse, Y_mouse = pygame.mouse.get_pos() #STORE MOUSE COORDS
            pygame.mouse.set_visible(False) #HIDE CURSOR

            #MOVEMENT
            if moveUp: 
                player.game_coord[1] -= player.speed*dt
            if moveDown: 
                 player.game_coord[1] += player.speed*dt
            if moveLeft: 
                player.game_coord[0] -= player.speed*dt
            if moveRight: 
                player.game_coord[0] += player.speed*dt
            
            #code used to set direction of player (x cant be 500 to avoid division by zero)
            #cant change direction whilst shop is open
            if X_mouse != 500 and shop == False:
                direction = math.atan((500-Y_mouse)/(X_mouse-500))*180/math.pi
                if X_mouse > 500:
                    direction -= 90
                else:
                    direction += 90
                player.direction = direction
            
            print("UPS:",1/dt)
            #once health is below zero -> set health to zero so to not display negative number, add onto death counter "t", once t is passed 1 second, turn off game switch
            if player.health <= 0:
                t += dt
                if t > 1:
                    playing = False
        
            pygame.display.update()
            
        while playing == False:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            #render end
            
            game.show_end_screen(screen)
        
Main = main()
Main.mainloop()
