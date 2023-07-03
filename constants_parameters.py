'''
This file contains all fundamental settings, constants and parameters, some of them may
be altered, which will have a large impact on the dynamics of the game. Examples are the
screen resolution, the framerate, the number of frames per second, the colour schemes
per level and number of columns and rows in the tetris matrix.

These constants and parameters can be divided in the following categories:

	- Screen resolution.
	- Screen layout.
	- Controller settings and allowed keys.
	- Texts, fonts and fonts colours.
	- Initial game settings.
	- Tetromino definitions.
	- Frame settings and delays.
	- NES Score system (number of points you get for singles, doubles, etc...).
	- Tetromino colour schemes and other colour settings.
	- Border widths.
	- Universal functions.
	- Directory and file paths.
'''

# Imports.
from collections import namedtuple
import pygame as pg
import os, glob, sys
import random as rd


 ### SCREEN RESOLUTION ###


infoObject = pg.display.Info() # Obtain screen resolution
SURFACE_WIDTH = infoObject.current_w / 1.2# Screen width.
SURFACE_HEIGHT = infoObject.current_h / 1.2# Screen height.


 ### SCREEN LAYOUT ###


# Board size.
BOARD_INVIS_ROWS = 2 # Invisible rows exist to make sure a longbar can be rotated immediately at spawn.
BOARD_VIS_ROWS = 20 # NES = 20. Number of visible rows, fun to change to, for example, 40, to see how it affects your playstyle.
BOARD_NROWS = BOARD_VIS_ROWS + BOARD_INVIS_ROWS # Total number of rows.
BOARD_NCOLUMNS = 10 # NES = 10. Number of columns.

# Layout ratio's.
N = (1/36) * SURFACE_HEIGHT # A defined measurement unit, which is used for the space between different ...
# ... fields in the game. Corresponds to 30 pixels if height is 1080 pixels.
LINE_BOARD_TOP = N # Y-coordinate of the top of the field where the number of lines cleared is displayed.
LINE_BOARD_HEIGHT = 0.1 * SURFACE_HEIGHT # Height of the line board field.

BOARD_TOP = N + LINE_BOARD_HEIGHT + N # Y-coordinate of the top of the tetris board.

BOARD_HEIGHT = SURFACE_HEIGHT - BOARD_TOP - N # Board height.
BOARD_TOP -= (BOARD_INVIS_ROWS / BOARD_NROWS) * BOARD_HEIGHT # Rescaling due to invisible rows.
BOARD_HEIGHT = SURFACE_HEIGHT - BOARD_TOP - N # Rescaling due to invisible rows.

BOARD_WIDTH = BOARD_HEIGHT / (BOARD_NROWS / BOARD_NCOLUMNS) # Board width is a function of the ratio of the number ...
# ... columns and rows, and the board height. This is the make sure each cell in the grid is exactly a square, and not a rectangle.

# The following is the make sure there isn't and 'leftover' space when dividing the matrix up into the number of columns/rows.
BSR = BOARD_HEIGHT % BOARD_NROWS # Board Scaling factor rows
BSC = BOARD_WIDTH % BOARD_NCOLUMNS # Board scaling factor columns
BOARD_HEIGHT -= BSR # To make it nice and even, and the gridlines fit properly.
BOARD_WIDTH -= BSC # Same but for columns.

# Horizontal location of the board in singleplayer mode.
BOARD_LEFT = 0.5 * (SURFACE_WIDTH - BOARD_WIDTH) # Board left is defined so that the middle of the board is in the middle of the screen.
LINE_BOARD_LEFT = BOARD_LEFT # Lineboard definition according ...
LINE_BOARD_WIDTH = BOARD_WIDTH # ... the horizontal board location.

# Horizontal location of the boards in multiplayer mode.
BOARD_2P_HORIZONTAL_SCALER = 0.19 # Determines how close the boards are to each other. Should become a function of board size and screen resolution.
BOARD_2P_LINEAR_SHIFTER = -240 # Linear shift to make sure everything is visible on the screen.
BOARD_LEFT_2P1 = BOARD_2P_HORIZONTAL_SCALER * (SURFACE_WIDTH - BOARD_WIDTH) + BOARD_2P_LINEAR_SHIFTER # Board left player 1.
BOARD_LEFT_2P2 = (1 - BOARD_2P_HORIZONTAL_SCALER) * (SURFACE_WIDTH - BOARD_WIDTH) + BOARD_2P_LINEAR_SHIFTER # Board left player 2.
LINE_BOARD_LEFT_2P1 = BOARD_LEFT_2P1 # Lineboard left player 1.
LINE_BOARD_LEFT_2P2 = BOARD_LEFT_2P2 # Lineboard left player 2.

# If the width of the board is larger than the surface, this error message will be shown.
assert BOARD_WIDTH < SURFACE_WIDTH, "Board is larger than surface, change the sizes."


 ### CONTROLLER SETTINGS AND ALLOWED KEYS ###


# Singleplayer, player 1.
P1_LEFT = pg.K_a 
P1_RIGHT = pg.K_d
P1_DOWN = pg.K_s
P1_UP = pg.K_w
P1_A = pg.K_RIGHT
P1_B = pg.K_LEFT
P1_START = pg.K_RETURN
P1_SPACE = pg.K_SPACE

# Multiplayer, player 1.
P11_LEFT = pg.K_a
P11_RIGHT = pg.K_d
P11_DOWN = pg.K_s
P11_UP = pg.K_w
P11_A = pg.K_b
P11_B = pg.K_c
P11_START = pg.K_RETURN
P11_SPACE = pg.K_SPACE

# Multiplayer, player 2.
P12_LEFT = pg.K_l
P12_RIGHT = pg.K_QUOTE
P12_DOWN = pg.K_SEMICOLON
P12_UP = pg.K_p
P12_A = pg.K_RIGHT
P12_B = pg.K_LEFT
P12_START = pg.K_RETURN
P12_SPACE = pg.K_RCTRL

# List of allowed keys.
CHARACTER_ARR = [pg.K_a, pg.K_b, pg.K_c, pg.K_d, pg.K_e, pg.K_f, pg.K_i, pg.K_l, pg.K_m, pg.K_n, pg.K_o, pg.K_p, pg.K_q, 
	pg.K_s, pg.K_u, pg.K_v, pg.K_w, pg.K_x, pg.K_z] # y, t, r, g, h, j and k are exluded because they fulfill other functions.
DIGIT_ARR = [pg.K_0, pg.K_1, pg.K_2, pg.K_3, pg.K_4, pg.K_5, pg.K_6, pg.K_7, pg.K_8, pg.K_9, pg.K_KP0, pg.K_KP1, pg.K_KP2, pg.K_KP3, pg.K_KP4,
	pg.K_KP5, pg.K_KP6, pg.K_KP7, pg.K_KP8, pg.K_KP9]
ARROW_ARR = [pg.K_UP, pg.K_DOWN, pg.K_RIGHT, pg.K_LEFT]
OTHER_KEY_ARR = [pg.K_BACKSPACE, pg.K_TAB, pg.K_ESCAPE, pg.K_SPACE, pg.K_DELETE, pg.K_MINUS, pg.K_EQUALS, pg.K_COMMA, pg.K_PERIOD, pg.K_SLASH, 
	pg.K_SEMICOLON, pg.K_LEFTBRACKET, pg.K_RIGHTBRACKET, pg.K_KP_PERIOD, pg.K_KP_DIVIDE, pg.K_KP_MULTIPLY, pg.K_KP_MINUS, pg.K_KP_PLUS, 
	pg.K_KP_ENTER, pg.K_KP_EQUALS, pg.K_INSERT, pg.K_HOME, pg.K_END, pg.K_PAGEUP, pg.K_PAGEDOWN, pg.K_RSHIFT, pg.K_LSHIFT, pg.K_RCTRL, 
	pg.K_LCTRL, pg.K_RALT, pg.K_LALT, pg.K_QUOTE, pg.K_QUOTEDBL]

ALLOWED_KEYS = CHARACTER_ARR + DIGIT_ARR + ARROW_ARR + OTHER_KEY_ARR


 ### TEXTS, FONTS AND FONT COLOURS ###


GAME_TITLE = 'Boom! Tetris!' # Visible in the window bar (if not played in full screen mode).
FONT = 'fonts/8-bit-pusab.ttf' # A font which has a bit of an 8-bit style.
STATS_FONT = 'fonts/NewsCycle-Regular.ttf'
FONT_SIZE = int(BOARD_NCOLUMNS / BOARD_VIS_ROWS * 66) #33 # Font size is a function of the ratio of the number of ...
# ... columns and rows. Doesn't work properly yet, needs to be improved.
FC = (255, 255, 255) # Font colour, white as text color.


 ### INITIAL GAME SETTINGS ###


START_LINES = 0 # You start the game with zero lines ...
START_SCORE = 0 # ... and zero points.
DROUGHT_BOUNDARY = 0 # You are droughted if there has not been a longbar in 13 tetrominos.
SEED = rd.randint(0, 1e9) + 1e6 # A seed with a billion different values with a linear shift of a million.
MUSIC_VOLUME = 0#3 # Ranges from 0-10.
SOUND_VOLUME_1 = 10 # Volume used for commentary, ranges from 0-10.
SOUND_VOLUME_2 = 0.2 # Volume used for the movement and rotation sound effects.
VUVUZUELA_VOLUME = 0.1 # Volume used for the World Cup 2010 commentary mode, is set really low because vuvuzuelas are inherently loud.


 ### TETROMINO DEFINITIONS ###


Block = namedtuple('Block', 'x y val')
T_BLOCK = [Block(-1, 0, 1), Block(0, 0, 1), Block(1, 0, 1), Block(0, 1, 1)] # Each block consists of three value. The x-coordiantes,
SQUARE = [Block(-1, 0, 1), Block(0, 0, 1), Block(-1, 1, 1), Block(0, 1, 1)] # the y-coordinate and the value. If the value is 0,
LONGBAR = [Block(-2, 0, 1), Block(-1, 0, 1), Block(0, 0, 1), Block(1, 0, 1)] # the cell is empty, and if the value is 1, the cell is
L_BLOCK = [Block(-1, 0, 1), Block(0, 0, 1), Block(1, 0, 1), Block(-1, 1, 1)] # part of the tetromino. Changing the values will change,
REVERSE_L_BLOCK = [Block(-1, 0, 1), Block(0, 0, 1), Block(1, 0, 1), Block(1, 1, 1)] # the tetromino shape.
SQUIGGLY = [Block(-1, 0, 1), Block(0, 0, 1), Block(0, 1, 1), Block(1, 1, 1)]
REVERSE_SQUIGGLY = [Block(1, 0, 1), Block(0, 0, 1), Block(0, 1, 1), Block(-1, 1, 1)]

# These blocks only have 2 rotations, not 4, so I defined them instead of using a rotation matrix.
LONGBAR_ROT = [Block(0, -2, 1), Block(0, -1, 1), Block(0, 0, 1), Block(0, 1, 1)]
SQUIGGLY_ROT = [Block(1, -1, 1), Block(1, 0, 1), Block(0, 0, 1), Block(0, 1, 1)]
REVERSE_SQUIGGLY_ROT = [Block(0, -1, 1), Block(0, 0, 1), Block(1, 0, 1), Block(1, 1, 1)]

# List of all the different tetrominos.
BLOCKS = [T_BLOCK, SQUARE, LONGBAR, L_BLOCK, REVERSE_L_BLOCK, SQUIGGLY, REVERSE_SQUIGGLY]
N_BLOCKS = len(BLOCKS) # Number of different tetrominos in the game.


 ### DELAYS AND FRAME SETTINGS ###


# Framerates for the two different versions of NES Tetris.
FRAMERATE_NTSC = 60.0988 # Frames per second NTSC, National Television System Committe.
FRAMERATE_PAL = 50.0070 # Frames per second PAL, Phase Alternating Line.

LEVELS_FRAMES_NTSC = [48, 43, 38, 33, 28, 23, 18, 13, 8, 6, # Number of frames before a piece drops one cell.
				5, 5, 5, 4, 4, 4, 3, 3,	3, # Each entry in the list corresponds to a level.
				0.25, 2, 2, 2, 2, 2, 2, 2, 2, 2, 
				1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1] # Goes up to level 40, so the game will crash of level 41 is reached.
LEVELS_FRAMES_PAL =  [36, 32, 29, 25, 22, 18, 15, 11, 7, 5, # Same but for PAL.
				4, 4, 4, 3, 3, 3, 2, 2, 2,
				1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]

# Delay autoshift settings for both NTSC and PAL.
DAS_DELAY_FRAMES_NTSC = 16 # Number of frames before the piece moves a second time when holding the key.
DAS_DELAY_FRAMES_PAL = 12 # Same but for PAL.
DAS_AUTO_REPEAT_FRAMES_NTSC = 6 # Number of frames before the piece moves after the DAS delay.
DAS_AUTO_REPEAT_FRAMES_PAL = 4 # Same but for PAL.

# Other delays.
LINE_CLEAR_DELAY = 18 # Number of frames before the game drops the next piece after a line clear ...
# ... Contrary to NES Tetris, this is set to constant value.
ARE_DELAY = 18 # Appearance delay. Initial value for this is set to 18 frames delay.
# ... This value will be changed in the code as a function of place height.


 ### NES SCORE SYSTEM ###


SINGLE_POINTS = 40 # Points for a single on level 0
DOUBLE_POINTS = int(2.5 * SINGLE_POINTS) # Points for a double, 25% increase w.r.t a single.
TRIPLE_POINTS = int(3 * DOUBLE_POINTS) # Points for a triple, 150% increase w.r.t. a single, 100% w.r.t a double.
TETRIS_POINTS = int(4 * TRIPLE_POINTS) # Points for a tetris, 650% increase w.r.t a single, 500% w.r.t a double, 200% w.r.t a triple.

SOFT_DROP_POINTS_PER_LINE = 1 # Soft drop points is set to 1 per each line dropped down.
HARD_DROP_POINTS_PER_LINE = 1 * SOFT_DROP_POINTS_PER_LINE # No more points for hard drop w.r.t. soft drop.


 ### TETROMINO COLOUR SCHEMES AND OTHER COLOUR SETTINGS ###


# Some general colour definitions.
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
LIGHTGREY = (192, 192, 192)
GREY = (128, 128, 128)
DARKGREY = (64, 64, 64)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)

PIECE_COLOURS = [ # 3 different colours for each level.
	[(255, 255, 255), (0, 87, 246), (62, 190, 255)],
	[(255, 255, 255), (0, 168, 0), (128, 208, 16)],
	[(255, 255, 255), (219, 0, 205), (248, 120, 248)],
	[(255, 255, 255), (0, 88, 248), (91, 219, 87)],
	[(255, 255, 255), (231, 0, 91), (88, 248, 152)],
	[(255, 255, 255), (200, 191, 231), (107, 136, 255)],
	[(255, 255, 255), (248, 56, 0), (127, 127, 127)],
	[(255, 255, 255), (107, 71, 255), (171, 0, 35)],
	[(255, 255, 255), (0, 88, 248), (248, 56, 0)],
	[(255, 255, 255), (248, 56, 0), (255, 163, 71)]
]

# Colours for specific game design elements.
SBC = (100, 100, 100) # Surface background colour, grey.
BBC = (0, 0, 0) # Board background colour, black.
BC = (150, 150, 150) # Border colour, lightgrey.
P1BC = (204, 255, 204) # In multiplayer mode this is the player 1 border colour.
P2BC = (153, 153, 255) # Player 2 border colour.
STATISTICS_COLOUR = (119, 67, 45) # Colour used for piece statistics and single player mode.
GRIDLINES_COLOUR = (50, 50, 50) # Colour of the gridlines, darkgrey.


 ### BORDER WIDTHS ###


# Border widths are defined in number of pixels. 
GRIDLINES_WIDTH = 1 # Width of the optional gridlines is set to 1 pixel.
BLACK_BORDER_WIDTH = 2 # The border between the blocks a tetrmino consists of.
COLOURED_BORDER_WIDTH = 5 # The coloured border width the white tetrominos have on their sides.
BORDER_WIDTH = 9 # The border width used around fields.
BACKGROUND_BORDER_WIDTH = 5 # The border width used in the background for the brick pattern.


 ### UNIVERSAL FUNCTIONS ###


def compute_milliseconds(system: float, fpgc: float) -> float:
	"""
	Converts a value from a specific system to milliseconds.
	Computes number of milliseconds in a frame.

	Args:
		system (float): The value in the specific system (e.g., frames per second).
		fpgc (float): The value in the given system (e.g., frames per game cycle).

	Returns:
		float: The equivalent value in milliseconds.
	"""

	return fpgc / system * 10**3

def compute_start_level(start_level:int) -> int:
	"""
	Computes the starting level for the game based on the given start_level value.

	The starting level is calculated as follows:
	- If start_level is less than or equal to 10, the starting level is start_level * 10 + 10.
	- If start_level is greater than 10, the starting level is max(100, start_level * 10 - 50).

	Args:
		start_level (int): The specified start level for the game.

	Returns:
		int: The computed starting level.
	"""

	return min(start_level * 10 + 10, max(100, start_level * 10 - 50))

# Computes the tetris lead, the pace score lead and the pace tetris lead.
def compute_leads(score_difference: int, level: int, line_counter: list) -> tuple:
	"""
	Computes the tetris lead, pace score lead, and pace tetris lead based on the score difference,
	current level, and line counter.

	The tetris lead represents the number of Tetris line clears needed to achieve a certain score
	difference based on the scoring rate, current level, and line counter.

	The pace score lead represents the additional score needed to maintain a certain lead in the game
	based on the score difference and the current level. It takes into account the scoring rate and the
	level progression.

	Args:
		score_difference (int): The difference in score between the player and the opponent.
		level (int): The current level of the game.
		line_counter (list): A list containing the number of lines cleared by each player.

	Returns:
		A tuple containing the tetris lead, pace score lead, and pace tetris lead.
	"""

	# Compute the score difference, minimum and maximum number of line clears.
	score_difference = abs(score_difference)
	lower_lines = min(line_counter[0], line_counter[1])
	upper_lines = max(line_counter[0], line_counter[1])

	def compute_tetris_lead(score_difference: int, level: int, line_counter: int) -> float:
		"""
		Computes the tetris lead based on the score difference, current level, and line counter.

		The tetris lead represents the number of Tetris line clears needed to achieve a certain score
		difference based on the scoring rate, current level, and line counter.

		Args:
			score_difference: The difference in score between the player and the opponent.
			level: The current level of the game.
			line_counter: The number of lines cleared.

		Returns:
			The number of Tetris line clears needed to achieve the score difference.
		"""

		tetris_lead = 0
		score_lead = 0

		while score_lead < score_difference:
			if int((line_counter + 4)/10) > int(line_counter/10):
				level += 1

			line_counter += 4
			score_lead += TETRIS_POINTS * (level + 1)
			tetris_lead += 1

		tetris_lead -= (score_lead - score_difference) / (TETRIS_POINTS * (level + 1))
		return tetris_lead

	def compute_pace_score_lead(score_difference: int, level: int) -> float:
		"""
		Computes the pace score lead based on the score difference and the current level.

		The pace score lead represents the additional score needed to maintain a certain lead in the game
		based on the score difference and the current level. It takes into account the scoring rate and the
		level progression.

		Args:
			score_difference (int): The difference in score between the player and the opponent.
			level (int): The current level of the game.

		Returns:
			The additional score needed to maintain the score difference.
		"""

		line_lead = lower_lines
		pace_score_lead = 0

		while line_lead < upper_lines:
			if int((line_lead + 4)/10) > int(line_lead/10):
				level += 1

			line_lead += 4
			pace_score_lead += TETRIS_POINTS * (level + 1)

		if line_lead > upper_lines:
			pace_score_lead -= (TETRIS_POINTS * (level + 1)) / (line_lead - upper_lines)

		return pace_score_lead

	# Compute the current tetris lead, pace lead, and the pace lead in tetrises.
	tetris_lead = compute_tetris_lead(score_difference, level, lower_lines)
	pace_score_lead = compute_pace_score_lead(score_difference, level)
	pace_tetris_lead = compute_tetris_lead(pace_score_lead, level, lower_lines)

	return tetris_lead, pace_score_lead, pace_tetris_lead


 ### DIRECTORY AND FILE PATHS ###


HIGHSCORES_PATH = 'highscores/highscores.txt'
MENU_BACKGROUND_PATH = 'images/menu_background.png'
MUSIC_PATH = 'music_and_sfx/music/'
MENU_MUSIC_PATH = MUSIC_PATH + 'Menu Music/'
MENU_MUSIC = os.listdir(MENU_MUSIC_PATH)

PATH = 'music_and_sfx/sfx/movement/'
SFX_MOVE = pg.mixer.Sound(PATH + 'move.mp3')
SFX_ROTATION = pg.mixer.Sound(PATH + 'rotation.mp3')
SFX_GAME_OVER = pg.mixer.Sound(PATH + 'game_over.mp3')
SFX_LAND_BLOCK = pg.mixer.Sound(PATH + 'land_block.mp3')
SFX_LEVEL_UP = pg.mixer.Sound(PATH + 'level_up.mp3')
SFX_LINE_CLEAR = pg.mixer.Sound(PATH + 'line_clear.mp3')
SFX_PAUSE = pg.mixer.Sound('music_and_sfx/sfx/pause.mp3')
CLICK_SFX = pg.mixer.Sound('music_and_sfx/sfx/click.mp3')

SFX_MOVE.set_volume(SOUND_VOLUME_2)
SFX_ROTATION.set_volume(SOUND_VOLUME_2)
SFX_LAND_BLOCK.set_volume(SOUND_VOLUME_2)
SFX_LINE_CLEAR.set_volume(SOUND_VOLUME_2)
SFX_LEVEL_UP.set_volume(SOUND_VOLUME_2)
SFX_PAUSE.set_volume(SOUND_VOLUME_2)

TETRIS_FOR_JEFF_PATH = 'music_and_sfx/sfx/boom_tetris/tetris_for_jeff/'
TETRIS_FOR_JEFF_LIST = [f for f in os.listdir(TETRIS_FOR_JEFF_PATH) if f.endswith('mp3')]
TETRIS_FOR_JONAS_PATH = 'music_and_sfx/sfx/boom_tetris/tetris_for_jonas/'
TETRIS_FOR_JONAS_LIST = [f for f in os.listdir(TETRIS_FOR_JONAS_PATH) if f.endswith('mp3')]
TETRIS_FOR_BUCO_PATH = 'music_and_sfx/sfx/boom_tetris/tetris_for_buco/'
TETRIS_FOR_BUCO_LIST = [f for f in os.listdir(TETRIS_FOR_BUCO_PATH) if f.endswith('mp3')]
TETRIS_FOR_QUAID_PATH = 'music_and_sfx/sfx/boom_tetris/tetris_for_quaid/'
TETRIS_FOR_QUAID_LIST = [f for f in os.listdir(TETRIS_FOR_QUAID_PATH) if f.endswith('mp3')]
TETRIS_FOR_HARRY_PATH = 'music_and_sfx/sfx/boom_tetris/tetris_for_harry/'
TETRIS_FOR_HARRY_LIST = [f for f in os.listdir(TETRIS_FOR_HARRY_PATH) if f.endswith('mp3')]

NEUTRAL_BUCO_PATH = 'music_and_sfx/sfx/boom_tetris/neutral_buco/'
NEUTRAL_BUCO_LIST = [f for f in os.listdir(NEUTRAL_BUCO_PATH) if f.endswith('mp3')]
NEUTRAL_QUAID_PATH = 'music_and_sfx/sfx/boom_tetris/neutral_quaid/'
NEUTRAL_QUAID_LIST = [f for f in os.listdir(NEUTRAL_QUAID_PATH) if f.endswith('mp3')]

BOOM_GAME_START_PATH = 'music_and_sfx/sfx/boom_tetris/321/'
BOOM_GAME_START_LIST = [f for f in os.listdir(BOOM_GAME_START_PATH) if f.endswith('.mp3')]
BOOM_GAME_OVER_PATH = 'music_and_sfx/sfx/boom_tetris/game_over/'
BOOM_GAME_OVER_LIST = [f for f in os.listdir(BOOM_GAME_OVER_PATH) if f.endswith('mp3')]
BOOM_TETRIS_READY_PATH = 'music_and_sfx/sfx/boom_tetris/tetris_ready/'
BOOM_TETRIS_READY_LIST = [f for f in os.listdir(BOOM_TETRIS_READY_PATH) if f.endswith('mp3')]
BOOM_THERE_IT_IS_PATH = 'music_and_sfx/sfx/boom_tetris/there_it_is/'
BOOM_THERE_IT_IS_LIST = [f for f in os.listdir(BOOM_THERE_IT_IS_PATH) if f.endswith('mp3')]
NECK_AND_NECK_PATH = 'music_and_sfx/sfx/boom_tetris/neck_and_neck/'
NECK_AND_NECK_LIST = [f for f in os.listdir(NECK_AND_NECK_PATH) if f.endswith('mp3')]

WK_2010_VUVUZUELA_PATH = 'music_and_sfx/sfx/wk_2010/vuvuzuela/'
WK_2010_NEUTRAL_CROWD_PATH = 'music_and_sfx/sfx/wk_2010/neutral_crowd/'
WK_2010_GOAL_PATH = 'music_and_sfx/sfx/wk_2010/goal/'
WK_2010_VUVUZUELA_LIST = [f for f in os.listdir(WK_2010_VUVUZUELA_PATH) if f.endswith('.mp3')]
WK_2010_NEUTRAL_CROWD_LIST = [f for f in os.listdir(WK_2010_NEUTRAL_CROWD_PATH) if f.endswith('.mp3')]
WK_2010_GOAL_LIST = [f for f in os.listdir(WK_2010_GOAL_PATH) if f.endswith('.mp3')]

CH_PATH = 'music_and_sfx/sfx/collegehumor/'
CH_L_BLOCK = [f for f in os.listdir(CH_PATH+'l_block') if f.endswith('.mp3')]
CH_LONGBAR = [f for f in os.listdir(CH_PATH+'longbar') if f.endswith('.mp3')]
CH_REVERSE_L_BLOCK = [f for f in os.listdir(CH_PATH+'reverse_l_block') if f.endswith('.mp3')]
CH_REVERSE_SQUIGGLY = [f for f in os.listdir(CH_PATH+'reverse_squiggly') if f.endswith('.mp3')]
CH_SQUARE = [f for f in os.listdir(CH_PATH+'square') if f.endswith('.mp3')]
CH_SQUIGGLY = [f for f in os.listdir(CH_PATH+'squiggly') if f.endswith('.mp3')]
CH_T_BLOCK = [f for f in os.listdir(CH_PATH+'t_block') if f.endswith('.mp3')]
CH_GAME_START = [f for f in os.listdir(CH_PATH+'game_start') if f.endswith('.mp3')]