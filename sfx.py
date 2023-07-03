import constants_parameters as C
import random as rd
import pygame as pg

''' Different commentary channels:

0 	Boom Tetris for Jeff
1 	Boom Tetris for Jonas
2 	Boom Tetris for BUUCCOOO
3 	Boom Tetris for Quaid
4	Boom Tetris for Harry
5 	The Tetris God
6 	WK 2010

'''

 ### START GAME SOUND EFFECTS ###


def play_start_game_sfx(commentary, volume):
	choice = []

	if commentary < 5: choice = C.BOOM_GAME_START_PATH + rd.choice(C.BOOM_GAME_START_LIST)
	if commentary == 5: choice = C.CH_PATH + 'game_start/' + rd.choice(C.CH_GAME_START)
	if commentary == 6: return False

	start_game_sfx = pg.mixer.Sound(choice)
	start_game_sfx.set_volume(volume)
	start_game_sfx.play()


 ### GAME OVER SOUND EFFECTS ###


def play_game_over_sfx(commentary, volume):
	choice = []

	if commentary < 5: choice = C.BOOM_GAME_OVER_PATH + rd.choice(C.BOOM_GAME_OVER_LIST)
	if commentary == 5: return False
	if commentary == 6: return False

	game_over_sfx = pg.mixer.Sound(choice)
	game_over_sfx.set_volume(volume)
	game_over_sfx.play()


 ### TETRIS SOUND EFFECTS ###


def play_tetris_sfx(commentary, volume):
	choice = []

	if commentary == 0: choice = C.TETRIS_FOR_JEFF_PATH + rd.choice(C.TETRIS_FOR_JEFF_LIST)
	if commentary == 1: choice = C.TETRIS_FOR_JONAS_PATH + rd.choice(C.TETRIS_FOR_JONAS_LIST)
	if commentary == 2: choice = C.TETRIS_FOR_BUCO_PATH + rd.choice(C.TETRIS_FOR_BUCO_LIST)
	if commentary == 3: choice = C.TETRIS_FOR_QUAID_PATH + rd.choice(C.TETRIS_FOR_QUAID_LIST)
	if commentary == 4: choice = C.TETRIS_FOR_HARRY_PATH + rd.choice(C.TETRIS_FOR_HARRY_LIST)
	if commentary == 5: return False
	if commentary == 6: return False

	tetris_sfx = pg.mixer.Sound(choice)
	tetris_sfx.set_volume(volume)
	tetris_sfx.play()


 ### TETRIS READY SOUND EFFECTS ###

def P(choice, x, start_value, rdb1, rdb2):
	def f(x, start_value):
		return (x - start_value) * (x - start_value)

	rd_val = rd.randint(rdb1, rdb2)

	#print(x, f(x, start_value), rd_val)

	if x < start_value: x += 1; return x
	if f(x, start_value) >= rd_val: return choice
	else: x += 1; return x

def play_tetris_ready_sfx(commentary, volume, x, t=None):
	choice = []

	if commentary < 5:
		if C.BLOCKS[t] == C.LONGBAR:
			choice = C.BOOM_THERE_IT_IS_PATH + rd.choice(C.BOOM_THERE_IT_IS_LIST)
			if rd.randint(1,2) == 1:
				there_it_is_sfx = pg.mixer.Sound(choice)
				there_it_is_sfx.set_volume(volume)
				there_it_is_sfx.play()
				return x
			else: return x
		else:
			choice = C.BOOM_TETRIS_READY_PATH + rd.choice(C.BOOM_TETRIS_READY_LIST)
			outcome = P(choice, x=x, start_value=5, rdb1=0, rdb2=100)
			if isinstance(outcome, int): return outcome
	if commentary == 5: return False
	if commentary == 6: return False

	tetris_ready_sfx = pg.mixer.Sound(outcome)
	tetris_ready_sfx.set_volume(volume)
	tetris_ready_sfx.play()

	x = 0
	return x

 ### AFTER TETRIS SOUND EFFECTS ###


def play_after_tetris_sfx(commentary, volume):
	choice = []

	if commentary < 5: return False
	if commentary == 5: return False
	if commentary == 6: return False

	after_tetris_sfx = pg.mixer.Sound(choice)
	after_tetris_sfx.set_volume(volume)
	after_tetris_sfx.play()


 ### LEVEL UP SOUND EFFECTS ###


def play_level_up_sfx():
	C.SFX_LEVEL_UP.play()


 ### NEUTRAL SOUND EFFECTS ###

def play_neck_and_neck_sfx(commentary, volume, x, seed):
	choice = []
	if seed != None: seed += 1; rd.seed(seed)

	choice = C.NECK_AND_NECK_PATH + rd.choice(C.NECK_AND_NECK_LIST)
	outcome = P(choice, x=x, start_value=10, rdb1=0, rdb2=100)
	if isinstance(outcome, int): return outcome

	neck_and_neck_sfx = pg.mixer.Sound(choice)
	neck_and_neck_sfx.set_volume(volume)
	neck_and_neck_sfx.play()

	x = 0
	return x

def play_collegehumor_soundeffects(self, volume, t):
	if C.BLOCKS[t] == C.T_BLOCK: return C.CH_PATH + 't_block/' + rd.choice(C.CH_T_BLOCK)
	if C.BLOCKS[t] == C.SQUARE: return C.CH_PATH + 'square/' + rd.choice(C.CH_SQUARE)
	if C.BLOCKS[t] == C.LONGBAR: return C.CH_PATH + 'longbar/' + rd.choice(C.CH_LONGBAR)
	if C.BLOCKS[t] == C.L_BLOCK: return C.CH_PATH + 'l_block/' + rd.choice(C.CH_L_BLOCK)
	if C.BLOCKS[t] == C.REVERSE_L_BLOCK: return C.CH_PATH + 'reverse_l_block/' + rd.choice(C.CH_REVERSE_L_BLOCK)
	if C.BLOCKS[t] == C.SQUIGGLY: return C.CH_PATH + 'squiggly/' + rd.choice(C.CH_SQUIGGLY)
	if C.BLOCKS[t] == C.REVERSE_SQUIGGLY: return C.CH_PATH + 'reverse_squiggly/' + rd.choice(C.CH_REVERSE_SQUIGGLY)

def play_neutral_sfx(commentary, volume, x=None, t=None, seed=None, multiplayer=False):
	choice = []
	if seed != None: seed += 1; rd.seed(seed)

	if commentary < 5: return False
	if commentary == 5:
		choice = play_collegehumor_soundeffects(commentary, volume, t);
		if multiplayer == False: outcome = P(choice, x=x, start_value=5, rdb1=0, rdb2=100)
		else: outcome = P(choice, x=x, start_value=10, rdb1=0, rdb2=100)
		if isinstance(outcome, int): return outcome
	if commentary == 6: choice = C.WK_2010_VUVUZUELA_PATH + rd.choice(C.WK_2010_VUVUZUELA_LIST)

	neutral_sfx = pg.mixer.Sound(choice)
	neutral_sfx.set_volume(volume)
	if commentary == 6: neutral_sfx.set_volume(C.VUVUZUELA_VOLUME)
	neutral_sfx.play()

	x = 0
	return x	


 ### WELL COVER SOUND EFFECTS ###


def play_well_cover_sfx(commentary, volume):
	choice = []

	if commentary < 5: return False
	if commentary == 5: return False
	if commentary == 6: return False

	well_cover_sfx = pg.mixer.Sound(choice)
	well_cover_sfx.set_volume(volume)
	well_cover_sfx.play()