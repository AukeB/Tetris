# Imports libraries.
import sys
import pygame as pg
import random as rd
import os

# PyGame initialisations.
pg.display.set_caption('Boom! Tetris!') # This is on purpose not taken from the constans_parameters file.
pg.mixer.pre_init(44100, -16, 1, 1024) # Makes sure sound effects don't have lag.
pg.mixer.init() # Initialise mixer.
pg.init() # Initialiser pygame.

# Import files.
import constants_parameters as C
import menu	

def main():
	# Load the game menu
	menu.main_menu()

if __name__ == '__main__':
	main()
	
'''
TODO.

- Pause function									DONE
- Option menu: Controls 2 player mode				DONE
- Option menu: Hard drop boolean					DONE
- Option menu: Music volume							DONE
- Option menu: Commentary volume					DONE
- Convert all .wav files to .mp3					DONE
- Stat: Tetris counter								DONE
- Add Tetris score lead.							DONE									
- Bug: Always load first stat graph.				DONE
- Bug: There it is in multiplayer					DONE 
- Bug: Score when level up							DONE
- Reorganize commentary channels					DONE
- Add better commentary lines rng					DONE
- GRAPH: Add score distribution						DONE
- Add pace score and tetris lead.					WIP
- Create a list of all possible stats 				WIP
- Different boom tetris sfx for each player			
- Make sure sfx don't interfere						
- Make the game work for different resolutions		
- Add highscore obtained in multiplayer				
	to .txt file.
- Best of 5 mode  									DONE
- Field for hearts in best of five mode 			DONE
- Maybe different colours for the 2 players			DONE
	in multiplayer mode 							DONE
- Compute average chi squared value for different	
	number of blocks, so that you can see how much	
	sigma your chi squared differs from the 		
	average chi squared								

- Create a list of all bugs/small things to fix		
	- Rotation autopct in sdtt graph				DONE
	- sdtt graph: change distribution to line
		clear distribution, and make the
		percentages a fraction of total lines
		cleared.
	- Add pushdown points to sdtt score graph				
	- Number locations in drought plot				
	- Sometimes sfx don't play 						
	- Location of buttons in game-over screen		
		is not dynamic
	- If board size is changed the cover up areas
		also covert up the light gray areas in
		the brick pattern					
	- Maybe a dynamic layout for when certain
		fields are not visible (hearts field)
	- Make a better scalable font size function				

- More commentary modes
- More music
- More boom tetris sfx
	- Harry
	- There it is
	- Tetris ready

Advanced options:
- Change color schemes
- 

EXTRA FEATURES TO ADD.

- Biased generator
- Battle/party mode
- Choose your column with numbers
- New main menu design

Super advanced options:
- Change board size
- Change das delay/auto repeat for NTSC/PAL
'''