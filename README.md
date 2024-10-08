Zombie Survival

The game is designed to see how many rounds of zombies the player can last with increasing amounts of zombies who have improved health and speed as the game progresses. Eliminate zombies to earn cash that can be used to purchase weapons. 
The map is designed using a unique method where a PNG image is transformed into the map. Every pixel in the image is processed and depending on the red value of the color, a corresponding tile is placed. This allowed for a very quick map design which can easily be adjusted and improved
![image](https://github.com/user-attachments/assets/c044445b-16f8-4913-9527-0ac777603c7c) ![image](https://github.com/user-attachments/assets/b6b1e343-a2a4-4491-8e54-e388c10611f7)

Once the player defeats enough zombies and has enough cash to purchase a weapon, they can do so by using the shop.
![image](https://github.com/user-attachments/assets/bbc9d0a3-2874-450e-a5bf-7dce44118dea)
The zombies move using a pathfinding behavior that provides the shortest path to the player. This works by taking a temporary snapshot of the player's location and the surrounding tiles and positions of the zombies. Then starting from the player, the algorithm moves outward checking tile by tile if the tile contains a zombie. If it does, it will pass on the directions it took to reach the zombie, to the zombie, and the zombie will follow those directions in reverse. Since we do this outwards from the player and cover all the tiles, only one iteration is required to provide information to all the zombies on the map. 
![image](https://github.com/user-attachments/assets/836fd3d0-d763-4ae9-848f-ef9a499df4db)
The wave control table seen in the image is used to control the zombie waves. Once activated 3 waves of zombies spawn consecutively. After the third wave, the player is given as much time as they may need to restore their health, reload their weapons, and sort out their inventory. Then once ready, the player can activate the wave control table to take on the next waves of zombies. 


The controls of the game:
WASD - movement

Left click - Fire weapon / Purchase weapon in shop

Right click - Sell weapon in the shop

R - reload weapon

E - access shop / activate waves

1 - Fists

2 - 1st weapon

3 - 2nd weapon
