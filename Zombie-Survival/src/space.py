#class used to create all objects from entities
from entities import *

class Space():
    def __init__(self):
        self.player = Player()
        self.cursor = Cursor()

        self.shop = Shop()

class Level_Manager():
    def __init__(self):
        #TOGGLE WHEN WAVE IS ON OR NOT
        self.zombie_wave = False
        self.level = 0
        self.zombies_to_add = 0 #ZOMBIES TO BE ADDED
        self.zombie_spawn = 0
        self.zombie_count = 0 #ZOMBIES ALREADY ON
    def update(self):
        if self.zombie_count < 20  and self.zombie_wave and self.zombies_to_add > 0: #max of 20 zombies spawned at once
            self.zombie_spawn += 1 #if less than 20 and there are still more zombies to be added then add a zombie -> repeat every iter until all zombies spawned
            self.zombies_to_add -= 1
        if self.zombie_wave and self.zombie_count == 0 and self.zombies_to_add == 0: #if the zombies are all dead whilst wave is happening -> wave is complete
            if self.level % 3 == 0: #only stop waves from continuing at multiples of 3
                self.zombie_wave = False
            else:
                self.new_level() #start a new level


    def new_level(self): #spawn level * 3 amount of zombies 
        self.level += 1
        self.zombies_to_add = 3*self.level
        self.zombie_wave = True

