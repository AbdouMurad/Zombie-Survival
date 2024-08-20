import random
import pygame
import numpy

from CONST import *
from entities import *


class Config:
    def __init__(self):
        self.tiles = []
        #access map image, and create an array holding the red value of every pixel - that value will be used to determine which tile is which 
        self.img = pygame.image.load("assets/Map.png")
        self.Pixels = pygame.surfarray.array_red(self.img)
              
        
        
        
    def create_tiles(self):
        '''
        loop through every tiles based on the size of the map and the size of tiles
        create tile object in each location and assign it a "i" value based on its corresponding red value in the map image
        '''
        i = 0
        for y in range(int(MAP_HEIGHT/TILE_HEIGHT)):
            row = []
            for x in range(int(MAP_WIDTH/TILE_WIDTH)):
              row.append(Tile([x*TILE_WIDTH, y*TILE_HEIGHT],[x*TILE_WIDTH,y*TILE_HEIGHT],i, i = self.Pixels[x,y]))
              i+=1
            self.tiles.append(row)

            