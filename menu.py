# Imports libraries.
import pygame as pg
import os, sys
import copy
import random as rd
import numpy as np
import math

# Import files.
import SingleGame
import MultiGame
import AIGame
import Agent
import Renderer
import Board
import Tetromino
import constants_parameters as C
import sfx

 ### INITIALISATIONS ###

#display = pg.display.set_mode((int(C.SURFACE_WIDTH*0.7), int(C.SURFACE_HEIGHT*0.7)))#, pg.FULLSCREEN)
display = pg.display.set_mode((int(C.SURFACE_WIDTH), int(C.SURFACE_HEIGHT)))#, pg.FULLSCREEN)
#display = pg.display.set_mode((C.SURFACE_WIDTH, C.SURFACE_HEIGHT), pg.FULLSCREEN)

main_clock = pg.time.Clock()
tick_time = 60

# Fontsizes.
title_size = 60
larger_size = 50
normal_text_size = 40
title_font = pg.font.Font(C.FONT, title_size)
normal_font = pg.font.Font(C.FONT, normal_text_size)
larger_font = pg.font.Font(C.FONT, larger_size)

# Distance measures.
d1 = 70
d2 = 30

x = display.get_width()/5
y = display.get_height()/10
text_field = pg.Rect(x-d2, y-d2, display.get_width() - 2*(x-d2), display.get_height() - 2*(y-d2))

 # Adjustable variables
preview_tetromino = False
gridline_bool = False
tetris_version = True
same_piecesets = True
hard_drop_bool = True
music_volume = C.MUSIC_VOLUME
commentary_volume = C.SOUND_VOLUME_1

music_queue = []
commentary = 0
num_players = 1
multiplayer_mode = 0

p1_left = C.P1_LEFT
p1_right = C.P1_RIGHT
p1_a = C.P1_A
p1_b = C.P1_B
p1_down = C.P1_DOWN
p1_space = C.P1_SPACE

# Multiplayer, player 1.
p11_left = C.P11_LEFT
p11_right = C.P11_RIGHT
p11_down = C.P11_DOWN
p11_up = C.P11_UP
p11_a = C.P11_A
p11_b = C.P11_B
p11_start = C.P11_START
p11_space = C.P11_SPACE

# Multiplayer, player 2.
p12_left = C.P12_LEFT
p12_right = C.P12_RIGHT
p12_down = C.P12_DOWN
p12_up = C.P12_UP
p12_a = C.P12_A
p12_b = C.P12_B
p12_start = C.P12_START
p12_space = C.P12_SPACE

 ### FUNTIONS ###

def draw_text(text, xy, font, alpha=False, alpha_value=None, button=False, color=C.WHITE, 
	background_color=None, surface=display, shadow=True, shadow_offset=(4, 4)):
	textobj = font.render(text, 1, color, background_color)
	textrect = textobj.get_rect()
	textrect.topleft = xy
	r = 7
	hitbox = (xy[0]-r, xy[1]+r, textrect[2]+2*r, textrect[3]-2*r)
	
	if shadow == True:
		textobj_shadow = font.render(text, 1, C.GREY, background_color)
		textrect_shadow = textobj.get_rect()
		textrect_shadow.topleft = (xy[0]+shadow_offset[0], xy[1]+shadow_offset[1])
		if alpha: textobj_shadow.set_alpha(alpha_value)
		surface.blit(textobj_shadow, textrect_shadow)

	if alpha: textobj.set_alpha(alpha_value)
	surface.blit(textobj, textrect)

	if button == True:
		button = pg.Rect(hitbox[0], hitbox[1], hitbox[2], hitbox[3])
		return button
	
def draw_rect(rect, colour=C.BLACK):
	pg.draw.rect(display, colour, rect)

def draw_borders(block_rect, colour, bw=C.BORDER_WIDTH, colour2=None):
		d = int(bw / 2)

		# Define useful coordinates.
		tl = (block_rect.x - d, block_rect.y - d) # Top left.
		tr = (block_rect.x + block_rect.width + d, block_rect.y - d) # Top right.
		bl = (block_rect.x - d, block_rect.y + block_rect.height + d) # Bottom left.
		br = (block_rect.x + block_rect.width + d, block_rect.y + block_rect.height + d) # Bottom right.

		pg.draw.line(display, colour, tl, tr, bw)
		if colour2 == None: 
			pg.draw.line(display, colour, tr, br, bw)
			pg.draw.line(display, colour, br, bl, bw)
		else:
			pg.draw.line(display, colour2, tr, br, bw)
			pg.draw.line(display, colour2, br, bl, bw)
		pg.draw.line(display, colour, bl, tl, bw)

def draw_menu_background():
	menu_background = pg.image.load('images/menu_background.png')

	while menu_background.get_width() < display.get_width() or menu_background.get_height() < display.get_height():
		menu_background = pg.transform.scale(menu_background, (int(menu_background.get_width()*1.05), int(menu_background.get_height()*1.05)))

	display.blit(menu_background, dest=(0,0), 
		area=(0, 0, menu_background.get_width(), menu_background.get_height()))

def start_game(start_level):
	global num_players
	global menu_music
	global music_queue

	if num_players == 1:
		g = SingleGame.Game(display, start_level, commentary, preview_tetromino, gridline_bool, hard_drop_bool, music_queue, menu_music, tetris_version,
			p1_left, p1_right, p1_a, p1_b, p1_down, p1_space, commentary_volume/10) # Initialize game object.

		queue = 'no_queue'

		while (cur_song := g.update()) != False: # Walrus operator to the rescue.
			queue = cur_song
		
		while len(music_queue) > len(queue):
			music_queue = np.delete(music_queue, 0)

	if num_players == 2:
		g = MultiGame.Game(display, start_level, commentary, preview_tetromino, gridline_bool, hard_drop_bool, music_queue, menu_music, tetris_version, same_piecesets,
			p11_left, p11_right, p11_a, p11_b, p11_down, p11_space, p12_left, p12_right, p12_a, p12_b, p12_down, p12_space, commentary_volume/10,
			multiplayer_mode) # Initialize game object.

		queue = 'no_queue'

		while (cur_song := g.update()) != False:
			queue = cur_song
		
		while len(music_queue) > len(queue):
			music_queue = np.delete(music_queue, 0)

	if num_players == 0:
		Agent.train(display, start_level, commentary, preview_tetromino, gridline_bool, hard_drop_bool, music_queue, menu_music, tetris_version,
			p1_left, p1_right, p1_a, p1_b, p1_down, p1_space, commentary_volume/10)

		#g = AIGame.Game(display, start_level, commentary, preview_tetromino, gridline_bool, hard_drop_bool, music_queue, menu_music, tetris_version,
		#	p1_left, p1_right, p1_a, p1_b, p1_down, p1_space, commentary_volume/10) # Initialize game object.

		#queue = 'no_queue'

		#while (cur_song := g.update()) != False:
		#	queue = cur_song
		
		#while len(music_queue) > len(queue):
		#	music_queue = np.delete(music_queue, 0)

def check_music_queue():
	global music_queue
	global menu_music

	if len(music_queue) == 0:
		pg.mixer.music.load(menu_music)
		pg.mixer.music.set_endevent(pg.USEREVENT)
		pg.mixer.music.play()
	else:
		pg.mixer.music.load(music_queue[0])
		pg.mixer.music.play()
		music_queue = np.delete(music_queue, 0)

def singleplayer_menu():
	click = False
	global num_players
	num_players = 1

	while True:
		# Draw menu background.
		draw_menu_background()
		draw_rect(text_field)
		draw_borders(text_field, C.BC)

		# Draw title.
		draw_text('Select Level!', (int(x), int(y)), title_font)

		play_buttons = []
	
		for i in range(10):
			play_buttons.append(draw_text(f'{i}', (x + ((2*i+1)%10)*d1, y + (2.5+1.2*int(i/5))*d1), larger_font, button=True))

		back_button = draw_text('Back', (int(x) + d1, int(y + 11*d1)), normal_font, button=True)

		# Get current mouse position.
		mx, my = pg.mouse.get_pos()
		keys = pg.key.get_pressed()

		# Actions that will be taken for each option.
		for i in range(10):
			if play_buttons[i].collidepoint((mx, my)):
				draw_text(f'{i}', (x + ((2*i+1)%10)*d1, y + (2.5+1.2*int(i/5))*d1), larger_font, color=C.BLUE)
				if click and (keys[pg.K_a] or keys[pg.K_LSHIFT]):
					C.CLICK_SFX.play()
					start_game(i+10)
				elif click:
					C.CLICK_SFX.play()
					start_game(i)

		if back_button.collidepoint((mx, my)):
			draw_text('Back', (int(x) + d1, int(y + 11*d1)), normal_font, color=C.BLUE)
			if click:
				C.CLICK_SFX.play()
				main_menu()


		click = False

		for event in pg.event.get():
			if event.type == pg.QUIT:
				pg.quit()
				sys.exit()
			if event.type == pg.KEYDOWN:
				if event.key == pg.K_ESCAPE:
					main_menu()
			if event.type == pg.MOUSEBUTTONDOWN:
				if event.button == 1:
					click = True
			if event.type == pg.USEREVENT:
				check_music_queue()

		pg.display.update()
		main_clock.tick(tick_time)


def multiplayer_menu():
	click = False
	global multiplayer_mode
	global num_players
	num_players = 2

	while True:
		# Draw menu background.
		draw_menu_background()
		draw_rect(text_field)
		draw_borders(text_field, C.BC)

		# Draw title.
		draw_text('Select Level!', (int(x), int(y)), title_font)

		play_buttons = []
	
		for i in range(10):
			play_buttons.append(draw_text(f'{i}', (x + ((2*i+1)%10)*d1, y + (2.5+1.2*int(i/5))*d1), larger_font, button=True))

		single_match_button = draw_text('Single match', (int(x) + d1, int(y + 6*d1)), normal_font, button=True)
		best_of_five_button = draw_text('Best of five', (int(x) + d1, int(y + 7*d1)), normal_font, button=True)
		back_button = draw_text('Back', (int(x) + d1, int(y + 11*d1)), normal_font, button=True)
		draw_text('<--', (int(x) + 11*d1, int(y + (6+multiplayer_mode)*d1)), normal_font, color=C.BLUE)

		# Get current mouse position.
		mx, my = pg.mouse.get_pos()
		keys = pg.key.get_pressed()

		# Actions that will be taken for each option.
		for i in range(10):
			if play_buttons[i].collidepoint((mx, my)):
				draw_text(f'{i}', (x + ((2*i+1)%10)*d1, y + (2.5+1.2*int(i/5))*d1), larger_font, color=C.BLUE)
				if click and (keys[pg.K_LSHIFT]):
					C.CLICK_SFX.play()
					start_game(i+10)
				elif click:
					C.CLICK_SFX.play()
					start_game(i)
		if single_match_button.collidepoint((mx, my)):
			draw_text('Single match', (int(x) + d1, int(y + 6*d1)), normal_font, color=C.BLUE)
			if click:
				C.CLICK_SFX.play()
				multiplayer_mode = 0
		if best_of_five_button.collidepoint((mx, my)):
			draw_text('Best of five', (int(x) + d1, int(y + 7*d1)), normal_font, color=C.BLUE)
			if click:
				C.CLICK_SFX.play()
				multiplayer_mode = 1
		if back_button.collidepoint((mx, my)):
			draw_text('Back', (int(x) + d1, int(y + 11*d1)), normal_font, color=C.BLUE)
			if click:
				C.CLICK_SFX.play()
				main_menu()

		click = False

		for event in pg.event.get():
			if event.type == pg.QUIT:
				pg.quit()
				sys.exit()
			if event.type == pg.KEYDOWN:
				if event.key == pg.K_ESCAPE:
					main_menu()
			if event.type == pg.MOUSEBUTTONDOWN:
				if event.button == 1:
					click = True
			if event.type == pg.USEREVENT:
				check_music_queue()

		pg.display.update()
		main_clock.tick(tick_time)

def AIGame_menu():
	click = False
	global num_players
	num_players = 0

	while True:
		# Draw menu background.
		draw_menu_background()
		draw_rect(text_field)
		draw_borders(text_field, C.BC)

		# Draw title.
		draw_text('Select Level!', (int(x), int(y)), title_font)

		play_buttons = []
	
		for i in range(10):
			play_buttons.append(draw_text(f'{i}', (x + ((2*i+1)%10)*d1, y + (2.5+1.2*int(i/5))*d1), larger_font, button=True))

		back_button = draw_text('Back', (int(x) + d1, int(y + 11*d1)), normal_font, button=True)

		# Get current mouse position.
		mx, my = pg.mouse.get_pos()
		keys = pg.key.get_pressed()

		# Actions that will be taken for each option.
		for i in range(10):
			if play_buttons[i].collidepoint((mx, my)):
				draw_text(f'{i}', (x + ((2*i+1)%10)*d1, y + (2.5+1.2*int(i/5))*d1), larger_font, color=C.BLUE)
				if click and (keys[pg.K_a] or keys[pg.K_LSHIFT]):
					C.CLICK_SFX.play()
					start_game(i+10)
				elif click:
					C.CLICK_SFX.play()
					start_game(i)

		if back_button.collidepoint((mx, my)):
			draw_text('Back', (int(x) + d1, int(y + 11*d1)), normal_font, color=C.BLUE)
			if click:
				C.CLICK_SFX.play()
				main_menu()


		click = False

		for event in pg.event.get():
			if event.type == pg.QUIT:
				pg.quit()
				sys.exit()
			if event.type == pg.KEYDOWN:
				if event.key == pg.K_ESCAPE:
					main_menu()
			if event.type == pg.MOUSEBUTTONDOWN:
				if event.button == 1:
					click = True
			if event.type == pg.USEREVENT:
				check_music_queue()

		pg.display.update()
		main_clock.tick(tick_time)

def music_submenu(path):
	global music_queue
	full_path = C.MUSIC_PATH+path
	click = False
	cur_page = 0

	while True:
		# Draw menu background.
		draw_menu_background()
		draw_rect(text_field)
		draw_borders(text_field, C.BC)

		# Draw title.
		draw_text('Select Music!', (int(x), int(y)), title_font)

		songs = os.listdir(full_path)
		songs_pp = 8

		def divide_pages(songs, songs_pp):
			num_pages = math.ceil(len(songs)/songs_pp)
			pages = [[] for _ in range(num_pages)]
			for i in range(num_pages):
				for j in range(songs_pp):
					if i*songs_pp + j < len(songs):
						pages[i].append(songs[i*songs_pp + j])

			return num_pages, pages

		num_pages, pages = divide_pages(songs, songs_pp)

		song_buttons = []

		for i in range(len(pages[cur_page])):
			if len(pages[cur_page][i]) > 33: song_buttons.append(draw_text(pages[cur_page][i][:27]+'...', (int(x) + d1, int(y + (i+2)*d1)), normal_font, button=True))
			else: song_buttons.append(draw_text(pages[cur_page][i][0:-4], (int(x) + d1, int(y + (i+2)*d1)), normal_font, button=True))

		back_button = draw_text('Back', (int(x) + d1, int(y + 11*d1)), normal_font, button=True)
		prev_page = draw_text('', (int(x) + 5*d1, int(y + 11*d1)), normal_font, button=True)
		next_page = draw_text('', (int(x) + 11*d1, int(y + 11*d1)), normal_font, button=True)
		if cur_page != 0: prev_page = draw_text('Prev page', (int(x) + 5*d1, int(y + 11*d1)), normal_font, button=True)
		if cur_page != num_pages - 1: next_page = draw_text('Next page', (int(x) + 11*d1, int(y + 11*d1)), normal_font, button=True)

		# Get current mouse position.
		mx, my = pg.mouse.get_pos()

		# Actions that will be taken for each option.
		for i in range(len(pages[cur_page])):
			if song_buttons[i].collidepoint((mx, my)):
				if len(pages[cur_page][i]) > 33: draw_text(pages[cur_page][i][:27]+'...', (int(x) + d1, int(y + (i+2)*d1)), normal_font, color=C.BLUE)
				else: draw_text(pages[cur_page][i][0:-4], (int(x) + d1, int(y + (i+2)*d1)), normal_font, color=C.BLUE)
				if click:
					C.CLICK_SFX.play()
					pg.mixer.music.load(full_path+'/'+pages[cur_page][i])
					pg.mixer.music.set_volume(music_volume/10)
					pg.mixer.music.play()

					shuffled_songs = copy.deepcopy(songs)
					shuffled_songs = np.delete(shuffled_songs, i)
					np.random.shuffle(shuffled_songs)

					music_queue = []
					for j in range(len(shuffled_songs)):
						music_queue.append(full_path + '/' + shuffled_songs[j])

		if back_button.collidepoint((mx, my)):
			draw_text('Back', (int(x) + d1, int(y + 11*d1)), normal_font, color=C.BLUE)
			if click:
				C.CLICK_SFX.play()
				music_menu()
		if prev_page.collidepoint((mx, my)) and cur_page != 0:
			draw_text('Prev page', (int(x) + 5*d1, int(y + 11*d1)), normal_font, color=C.BLUE)
			if click:
				C.CLICK_SFX.play()
				cur_page -= 1
		if next_page.collidepoint((mx, my)) and cur_page != num_pages - 1:
			draw_text('Next page', (int(x) + 11*d1, int(y + 11*d1)), normal_font, color=C.BLUE)
			if click:
				C.CLICK_SFX.play()
				cur_page += 1

		click = False

		for event in pg.event.get():
			if event.type == pg.QUIT:
				pg.quit()
				sys.exit()
			if event.type == pg.KEYDOWN:
				if event.key == pg.K_ESCAPE:
					music_menu()
			if event.type == pg.MOUSEBUTTONDOWN:
				if event.button == 1:
					click = True
			if event.type == pg.USEREVENT:
				check_music_queue()

		pg.display.update()
		main_clock.tick(tick_time)

def music_menu():
	click = False

	while True:
		# Draw menu background.
		draw_menu_background()
		draw_rect(text_field)
		draw_borders(text_field, C.BC)

		# Draw title.
		draw_text('Select Music!', (int(x), int(y)), title_font)

		music_directories = os.listdir(C.MUSIC_PATH)
		music_buttons = []

		music_directories.remove('Menu Music')

		for i in range(len(music_directories)):
			music_buttons.append(draw_text(music_directories[i], (int(x) + d1, int(y + (i+2)*d1)), normal_font, button=True))

		back_button = draw_text('Back', (int(x) + d1, int(y + 11*d1)), normal_font, button=True)

		# Get current mouse position.
		mx, my = pg.mouse.get_pos()

		# Actions that will be taken for each option.
		for i in range(len(music_directories)):
			if music_buttons[i].collidepoint((mx, my)):
				draw_text(music_directories[i], (int(x) + d1, int(y + (i+2)*d1)), normal_font, color=C.BLUE)
				if click:
					C.CLICK_SFX.play()
					music_submenu(music_directories[i])

		if back_button.collidepoint((mx, my)):
			draw_text('Back', (int(x) + d1, int(y + 11*d1)), normal_font, color=C.BLUE)
			if click:
				C.CLICK_SFX.play()
				main_menu()

		click = False

		for event in pg.event.get():
			if event.type == pg.QUIT:
				pg.quit()
				sys.exit()
			if event.type == pg.KEYDOWN:
				if event.key == pg.K_ESCAPE:
					main_menu()
			if event.type == pg.MOUSEBUTTONDOWN:
				if event.button == 1:
					click = True
			if event.type == pg.USEREVENT:
				check_music_queue()

		pg.display.update()
		main_clock.tick(tick_time)

def press_a_key(key):
	click = False
	key_detection = False
	select_key = key

	def draw_select_key_screen():
		draw_text('Press a key', (int(x) + 5*d1, int(y + 5*d1)), larger_font, color=C.WHITE)

	while key_detection == False:
		# Draw menu background.
		draw_menu_background()
		draw_rect(text_field)
		draw_borders(text_field, C.BC)
		draw_select_key_screen()

		pressed = pg.key.get_pressed()

		for key in C.ALLOWED_KEYS:
			if pressed[key]:
				select_key = key
				key_detection = True

		for event in pg.event.get():
			if event.type == pg.QUIT:
				pg.quit()
				sys.exit()
			if event.type == pg.USEREVENT:
				check_music_queue()

		pg.display.update()
		main_clock.tick(tick_time)		

	return select_key

def singleplayer_controls_menu():
	click = False

	global p1_left
	global p1_right
	global p1_a
	global p1_b
	global p1_down
	global p1_space

	while True:
		# Draw menu background.
		draw_menu_background()
		draw_rect(text_field)
		draw_borders(text_field, C.BC)

		# Draw title.
		draw_text('Controls!', (int(x), int(y)), title_font)

		draw_text('Move right', (int(x) + d1, int(y + 2*d1)), normal_font, button=False)
		draw_text('Move left', (int(x) + d1, int(y + 3*d1)), normal_font, button=False)
		draw_text('Rotate right', (int(x) + d1, int(y + 4*d1)), normal_font, button=False)
		draw_text('Rotate left', (int(x) + d1, int(y + 5*d1)), normal_font, button=False)
		draw_text('Soft drop', (int(x) + d1, int(y + 6*d1)), normal_font, button=False)
		draw_text('Hard drop', (int(x) + d1, int(y + 7*d1)), normal_font, button=False)

		back_button = draw_text('Back', (int(x) + d1, int(y + 11*d1)), normal_font, button=True)

		p1_right_button = draw_text(pg.key.name(p1_right), (int(x) + 12*d1, int(y + 2*d1)), normal_font, button=True)
		p1_left_button = draw_text(pg.key.name(p1_left), (int(x) + 12*d1, int(y + 3*d1)), normal_font, button=True)
		p1_a_button = draw_text(pg.key.name(p1_a), (int(x) + 12*d1, int(y + 4*d1)), normal_font, button=True)
		p1_b_button = draw_text(pg.key.name(p1_b), (int(x) + 12*d1, int(y + 5*d1)), normal_font, button=True)
		p1_down_button = draw_text(pg.key.name(p1_down), (int(x) + 12*d1, int(y + 6*d1)), normal_font, button=True)
		p1_space_button = draw_text(pg.key.name(p1_space), (int(x) + 12*d1, int(y + 7*d1)), normal_font, button=True)

	
		# Get current mouse position.
		mx, my = pg.mouse.get_pos()

		# Actions that will be taken for each option.
		if back_button.collidepoint((mx, my)):
			draw_text('Back', (int(x) + d1, int(y + 11*d1)), normal_font, color=C.BLUE)
			if click:
				C.CLICK_SFX.play()
				options_menu()
		if p1_right_button.collidepoint((mx, my)):
			draw_text(pg.key.name(p1_right), (int(x) + 12*d1, int(y + 2*d1)), normal_font, color=C.BLUE)
			if click:
				C.CLICK_SFX.play()
				p1_right = press_a_key(p1_right)
		if p1_left_button.collidepoint((mx, my)):
			draw_text(pg.key.name(p1_left), (int(x) + 12*d1, int(y + 3*d1)), normal_font, color=C.BLUE)
			if click:
				C.CLICK_SFX.play()
				p1_left = press_a_key(p1_left)
		if p1_a_button.collidepoint((mx, my)):
			draw_text(pg.key.name(p1_a), (int(x) + 12*d1, int(y + 4*d1)), normal_font, color=C.BLUE)
			if click:
				C.CLICK_SFX.play()
				p1_a = press_a_key(p1_a)
		if p1_b_button.collidepoint((mx, my)):
			draw_text(pg.key.name(p1_b), (int(x) + 12*d1, int(y + 5*d1)), normal_font, color=C.BLUE)
			if click:
				C.CLICK_SFX.play()
				p1_b = press_a_key(p1_b)
		if p1_down_button.collidepoint((mx, my)):
			draw_text(pg.key.name(p1_down), (int(x) + 12*d1, int(y + 6*d1)), normal_font, color=C.BLUE)
			if click:
				C.CLICK_SFX.play()
				p1_down = press_a_key(p1_down)
		if p1_space_button.collidepoint((mx, my)):
			draw_text(pg.key.name(p1_space), (int(x) + 12*d1, int(y + 7*d1)), normal_font, color=C.BLUE)
			if click:
				C.CLICK_SFX.play()
				p1_space = press_a_key(p1_space)

		click = False

		for event in pg.event.get():
			if event.type == pg.QUIT:
				pg.quit()
				sys.exit()
			if event.type == pg.KEYDOWN:
				if event.key == pg.K_ESCAPE:
					options_menu()
			if event.type == pg.MOUSEBUTTONDOWN:
				if event.button == 1:
					click = True
			if event.type == pg.USEREVENT:
				check_music_queue()

		pg.display.update()
		main_clock.tick(tick_time)

def multiplayer_controls_menu():
	click = False
	page = True

	global p11_left
	global p11_right
	global p11_a
	global p11_b
	global p11_down
	global p11_space

	global p12_left
	global p12_right
	global p12_a
	global p12_b
	global p12_down
	global p12_space

	while True:
		# Draw menu background.
		draw_menu_background()
		draw_rect(text_field)
		draw_borders(text_field, C.BC)

		# Draw title.
		draw_text('Controls!', (int(x), int(y)), title_font)

		draw_text('Move right', (int(x) + d1, int(y + 2*d1)), normal_font, button=False)
		draw_text('Move left', (int(x) + d1, int(y + 3*d1)), normal_font, button=False)
		draw_text('Rotate right', (int(x) + d1, int(y + 4*d1)), normal_font, button=False)
		draw_text('Rotate left', (int(x) + d1, int(y + 5*d1)), normal_font, button=False)
		draw_text('Soft drop', (int(x) + d1, int(y + 6*d1)), normal_font, button=False)
		draw_text('Hard drop', (int(x) + d1, int(y + 7*d1)), normal_font, button=False)

		back_button = draw_text('Back', (int(x) + d1, int(y + 11*d1)), normal_font, button=True)
		p1_button = draw_text('P1', (int(x) + 7*d1, int(y + 11*d1)), normal_font, button=True)
		p2_button = draw_text('P2', (int(x) + 11*d1, int(y + 11*d1)), normal_font, button=True)

	
		# Get current mouse position.
		mx, my = pg.mouse.get_pos()

		# Actions that will be taken for each option.
		if back_button.collidepoint((mx, my)):
			draw_text('Back', (int(x) + d1, int(y + 11*d1)), normal_font, color=C.BLUE)
			if click:
				C.CLICK_SFX.play()
				options_menu()
		if p1_button.collidepoint((mx, my)):
			draw_text('P1', (int(x) + 7*d1, int(y + 11*d1)), normal_font, color=C.BLUE)
			if click:
				C.CLICK_SFX.play()
				page = True
		if p2_button.collidepoint((mx, my)):
			draw_text('P2', (int(x) + 11*d1, int(y + 11*d1)), normal_font, color=C.BLUE)
			if click:
				C.CLICK_SFX.play()
				page = False

		if page:
			p11_right_button = draw_text(pg.key.name(p11_right), (int(x) + 11*d1, int(y + 2*d1)), normal_font, button=True)
			p11_left_button = draw_text(pg.key.name(p11_left), (int(x) + 11*d1, int(y + 3*d1)), normal_font, button=True)
			p11_a_button = draw_text(pg.key.name(p11_a), (int(x) + 11*d1, int(y + 4*d1)), normal_font, button=True)
			p11_b_button = draw_text(pg.key.name(p11_b), (int(x) + 11*d1, int(y + 5*d1)), normal_font, button=True)
			p11_down_button = draw_text(pg.key.name(p11_down), (int(x) + 11*d1, int(y + 6*d1)), normal_font, button=True)
			p11_space_button = draw_text(pg.key.name(p11_space), (int(x) + 11*d1, int(y + 7*d1)), normal_font, button=True)
		else:
			p12_right_button = draw_text(pg.key.name(p12_right), (int(x) + 11*d1, int(y + 2*d1)), normal_font, button=True)
			p12_left_button = draw_text(pg.key.name(p12_left), (int(x) + 11*d1, int(y + 3*d1)), normal_font, button=True)
			p12_a_button = draw_text(pg.key.name(p12_a), (int(x) + 11*d1, int(y + 4*d1)), normal_font, button=True)
			p12_b_button = draw_text(pg.key.name(p12_b), (int(x) + 11*d1, int(y + 5*d1)), normal_font, button=True)
			p12_down_button = draw_text(pg.key.name(p12_down), (int(x) + 11*d1, int(y + 6*d1)), normal_font, button=True)
			p12_space_button = draw_text(pg.key.name(p12_space), (int(x) + 11*d1, int(y + 7*d1)), normal_font, button=True)

		if page:
			if p11_right_button.collidepoint((mx, my)):
				draw_text(pg.key.name(p11_right), (int(x) + 11*d1, int(y + 2*d1)), normal_font, color=C.BLUE)
				if click:
					C.CLICK_SFX.play()
					p11_right = press_a_key(p11_right)
			if p11_left_button.collidepoint((mx, my)):
				draw_text(pg.key.name(p11_left), (int(x) + 11*d1, int(y + 3*d1)), normal_font, color=C.BLUE)
				if click:
					C.CLICK_SFX.play()
					p11_left = press_a_key(p11_left)
			if p11_a_button.collidepoint((mx, my)):
				draw_text(pg.key.name(p11_a), (int(x) + 11*d1, int(y + 4*d1)), normal_font, color=C.BLUE)
				if click:
					C.CLICK_SFX.play()
					p11_a = press_a_key(p11_a)
			if p11_b_button.collidepoint((mx, my)):
				draw_text(pg.key.name(p11_b), (int(x) + 11*d1, int(y + 5*d1)), normal_font, color=C.BLUE)
				if click:
					C.CLICK_SFX.play()
					p11_b = press_a_key(p11_b)
			if p11_down_button.collidepoint((mx, my)):
				draw_text(pg.key.name(p11_down), (int(x) + 11*d1, int(y + 6*d1)), normal_font, color=C.BLUE)
				if click:
					C.CLICK_SFX.play()
					p11_down = press_a_key(p11_down)
			if p11_space_button.collidepoint((mx, my)):
				draw_text(pg.key.name(p11_space), (int(x) + 11*d1, int(y + 7*d1)), normal_font, color=C.BLUE)
				if click:
					C.CLICK_SFX.play()
					p11_space = press_a_key(p11_space)
		else:
			if p12_right_button.collidepoint((mx, my)):
				draw_text(pg.key.name(p12_right), (int(x) + 11*d1, int(y + 2*d1)), normal_font, color=C.BLUE)
				if click:
					C.CLICK_SFX.play()
					p12_right = press_a_key(p12_right)
			if p12_left_button.collidepoint((mx, my)):
				draw_text(pg.key.name(p12_left), (int(x) + 11*d1, int(y + 3*d1)), normal_font, color=C.BLUE)
				if click:
					C.CLICK_SFX.play()
					p12_left = press_a_key(p12_left)
			if p12_a_button.collidepoint((mx, my)):
				draw_text(pg.key.name(p12_a), (int(x) + 11*d1, int(y + 4*d1)), normal_font, color=C.BLUE)
				if click:
					C.CLICK_SFX.play()
					p12_a = press_a_key(p12_a)
			if p12_b_button.collidepoint((mx, my)):
				draw_text(pg.key.name(p12_b), (int(x) + 11*d1, int(y + 5*d1)), normal_font, color=C.BLUE)
				if click:
					C.CLICK_SFX.play()
					p12_b = press_a_key(p12_b)
			if p12_down_button.collidepoint((mx, my)):
				draw_text(pg.key.name(p12_down), (int(x) + 11*d1, int(y + 6*d1)), normal_font, color=C.BLUE)
				if click:
					C.CLICK_SFX.play()
					p12_down = press_a_key(p12_down)
			if p12_space_button.collidepoint((mx, my)):
				draw_text(pg.key.name(p12_space), (int(x) + 11*d1, int(y + 7*d1)), normal_font, color=C.BLUE)
				if click:
					C.CLICK_SFX.play()
					p12_space = press_a_key(p12_space)

		click = False

		for event in pg.event.get():
			if event.type == pg.QUIT:
				pg.quit()
				sys.exit()
			if event.type == pg.KEYDOWN:
				if event.key == pg.K_ESCAPE:
					options_menu()
			if event.type == pg.MOUSEBUTTONDOWN:
				if event.button == 1:
					click = True
			if event.type == pg.USEREVENT:
				check_music_queue()

		pg.display.update()
		main_clock.tick(tick_time)

def options_menu():
	click = False
	scroll_up = False
	scroll_down = False

	global preview_tetromino
	global gridline_bool
	global tetris_version
	global same_piecesets
	global hard_drop_bool
	global music_volume
	global commentary_volume

	e1 = 13

	while True:
		# Draw menu background.
		draw_menu_background()
		draw_rect(text_field)
		draw_borders(text_field, C.BC)

		# Draw title.
		draw_text('Options!', (int(x), int(y)), title_font)
	
		draw_text('Tetromino preview', (int(x) + d1, int(y + 2*d1)), normal_font, button=False)
		draw_text('Gridlines', (int(x) + d1, int(y + 3*d1)), normal_font, button=False)
		draw_text('Hard drop', (int(x) + d1, int(y + 4*d1)), normal_font, button=False)
		draw_text('Tetris version', (int(x) + d1, int(y + 5*d1)), normal_font, button=False)
		draw_text('Same piecesets', (int(x) + d1, int(y + 6*d1)), normal_font, button=False)
		draw_text('Music volume', (int(x) + d1, int(y + 7*d1)), normal_font, button=False)
		draw_text('Commentary volume', (int(x) + d1, int(y + 8*d1)), normal_font, button=False)
		
		if preview_tetromino == True: preview_button = draw_text('On', (int(x) + e1*d1, int(y + 2*d1)), normal_font, button=True)
		if preview_tetromino == False: preview_button = draw_text('Off', (int(x) + e1*d1, int(y + 2*d1)), normal_font, button=True)
		if gridline_bool == True: gridline_button = draw_text('On', (int(x) + e1*d1, int(y + 3*d1)), normal_font, button=True)
		if gridline_bool == False: gridline_button = draw_text('Off', (int(x) + e1*d1, int(y + 3*d1)), normal_font, button=True)
		if hard_drop_bool == True: hard_drop_button = draw_text('On', (int(x) + e1*d1, int(y + 4*d1)), normal_font, button=True)
		if hard_drop_bool == False: hard_drop_button = draw_text('Off', (int(x) + e1*d1, int(y + 4*d1)), normal_font, button=True)
		if tetris_version == True: tetris_version_button = draw_text('NTSC', (int(x) + e1*d1, int(y + 5*d1)), normal_font, button=True)
		if tetris_version == False: tetris_version_button = draw_text('PAL', (int(x) + e1*d1, int(y + 5*d1)), normal_font, button=True)
		if same_piecesets == True: same_piecesets_button = draw_text('On', (int(x) + e1*d1, int(y + 6*d1)), normal_font, button=True)
		if same_piecesets == False: same_piecesets_button = draw_text('Off', (int(x) + e1*d1, int(y + 6*d1)), normal_font, button=True)

		music_volume_button = draw_text(f'{int(music_volume)}', (int(x) + e1*d1, int(y + 7*d1)), normal_font, button=True)
		commentary_volume_button = draw_text(f'{int(commentary_volume)}', (int(x) + e1*d1, int(y + 8*d1)), normal_font, button=True)

		singleplayer_controls_button = draw_text('Singleplayer Controls', (int(x) + d1, int(y + 9*d1)), normal_font, button=True)
		multiplayer_controls_button = draw_text('Multiplayer Controls', (int(x) + d1, int(y + 10*d1)), normal_font, button=True)
		advanced_options_button = draw_text('Advanced options', (int(x) + d1, int(y + 11*d1)), normal_font, button=True)

		back_button = draw_text('Back', (int(x) + e1*d1, int(y + 11*d1)), normal_font, button=True)

		# Get current mouse position.
		mx, my = pg.mouse.get_pos()

		#print(pg.mouse.get_pressed(num_buttons=5))

		# Actions that will be taken for each option.
		if music_volume_button.collidepoint((mx, my)):
			draw_text(f'{int(music_volume)}', (int(x) + e1*d1, int(y + 7*d1)), normal_font, color=C.BLUE)
			if scroll_up:
				if music_volume < 10: music_volume = int(music_volume + 1)
				pg.mixer.music.set_volume(music_volume/10)
			if scroll_down:
				if music_volume > 0: music_volume = int(music_volume - 1)
				pg.mixer.music.set_volume(music_volume/10)
		if commentary_volume_button.collidepoint((mx, my)):
			draw_text(f'{int(commentary_volume)}', (int(x) + e1*d1, int(y + 8*d1)), normal_font, color=C.BLUE)
			if scroll_up:
				if commentary_volume < 10: commentary_volume = int(commentary_volume + 1)
			if scroll_down:
				if commentary_volume > 0: commentary_volume = int(commentary_volume - 1)
		if back_button.collidepoint((mx, my)):
			draw_text('Back', (int(x) + e1*d1, int(y + 11*d1)), normal_font, color=C.BLUE)
			if click:
				C.CLICK_SFX.play()
				main_menu()
		if preview_tetromino == True:
			if preview_button.collidepoint((mx, my)):
				draw_text('On', (int(x) + e1*d1, int(y + 2*d1)), normal_font, color=C.BLUE)
				if click:
					C.CLICK_SFX.play()
					preview_tetromino = False
		elif preview_tetromino == False:
			if preview_button.collidepoint((mx, my)):
				draw_text('Off', (int(x) + e1*d1, int(y + 2*d1)), normal_font, color=C.BLUE)
				if click:
					C.CLICK_SFX.play()
					preview_tetromino = True
		if gridline_bool == True:
			if gridline_button.collidepoint((mx, my)):
				draw_text('On', (int(x) + e1*d1, int(y + 3*d1)), normal_font, color=C.BLUE)
				if click:
					C.CLICK_SFX.play()
					gridline_bool = False
		elif gridline_bool == False:
			if gridline_button.collidepoint((mx, my)):
				draw_text('Off', (int(x) + e1*d1, int(y + 3*d1)), normal_font, color=C.BLUE)
				if click:
					C.CLICK_SFX.play()
					gridline_bool = True
		if hard_drop_bool == True:
			if hard_drop_button.collidepoint((mx, my)):
				draw_text('On', (int(x) + e1*d1, int(y + 4*d1)), normal_font, color=C.BLUE)
				if click:
					C.CLICK_SFX.play()
					hard_drop_bool = False
		elif hard_drop_bool == False:
			if hard_drop_button.collidepoint((mx, my)):
				draw_text('Off', (int(x) + e1*d1, int(y + 4*d1)), normal_font, color=C.BLUE)
				if click:
					C.CLICK_SFX.play()
					hard_drop_bool = True
		if tetris_version == True:
			if tetris_version_button.collidepoint((mx, my)):
				draw_text('NTSC', (int(x) + e1*d1, int(y + 5*d1)), normal_font, color=C.BLUE)
				if click:
					C.CLICK_SFX.play()
					tetris_version = False
		elif tetris_version == False:
			if tetris_version_button.collidepoint((mx, my)):
				draw_text('PAL', (int(x) + e1*d1, int(y + 5*d1)), normal_font, color=C.BLUE)
				if click:
					C.CLICK_SFX.play()
					tetris_version = True
		if same_piecesets == True:
			if same_piecesets_button.collidepoint((mx, my)):
				draw_text('On', (int(x) + e1*d1, int(y + 6*d1)), normal_font, color=C.BLUE)
				if click:
					C.CLICK_SFX.play()
					same_piecesets = False
		elif same_piecesets == False:
			if same_piecesets_button.collidepoint((mx, my)):
				draw_text('Off', (int(x) + e1*d1, int(y + 6*d1)), normal_font, color=C.BLUE)
				if click:
					C.CLICK_SFX.play()
					same_piecesets = True
		if singleplayer_controls_button.collidepoint((mx, my)):
			draw_text('Singleplayer Controls', (int(x) + d1, int(y + 9*d1)), normal_font, color=C.BLUE)
			if click:
				C.CLICK_SFX.play()
				singleplayer_controls_menu()
		if multiplayer_controls_button.collidepoint((mx, my)):
			draw_text('Multiplayer Controls', (int(x) + d1, int(y + 10*d1)), normal_font, color=C.BLUE)
			if click:
				C.CLICK_SFX.play()
				multiplayer_controls_menu()
		if advanced_options_button.collidepoint((mx, my)):
			draw_text('Advanced options', (int(x) + d1, int(y + 11*d1)), normal_font, color=C.BLUE)
			if click:
				C.CLICK_SFX.play()
				pass

		click = False
		scroll_up = False
		scroll_down = False

		for event in pg.event.get():
			if event.type == pg.QUIT:
				pg.quit()
				sys.exit()
			if event.type == pg.KEYDOWN:
				if event.key == pg.K_ESCAPE:
					main_menu()
			if event.type == pg.MOUSEBUTTONDOWN:
				if event.button == 1: click = True
				if event.button == 4: scroll_up = True
				if event.button == 5: scroll_down = True
			if event.type == pg.USEREVENT:
				check_music_queue()

		pg.display.update()
		main_clock.tick(tick_time)


def commentary_boom_tetris_menu():
	global commentary
	click = False

	while True:
		# Draw menu background.
		draw_menu_background()
		draw_rect(text_field)
		draw_borders(text_field, C.BC)

		# Draw title.
		draw_text('Boom! Tetris for ...!', (int(x), int(y)), title_font)

		jeff_button = draw_text('Jeff!', (int(x) + d1, int(y + 2*d1)), normal_font, button=True)
		jonas_button = draw_text('Jonas!', (int(x) + d1, int(y + 3*d1)), normal_font, button=True)
		buco_button = draw_text('BUUUCOOOOOOO!', (int(x) + d1, int(y + 4*d1)), normal_font, button=True)
		quaid_button = draw_text('Quaid!', (int(x) + d1, int(y + 5*d1)), normal_font, button=True)
		harry_button = draw_text('Harry!', (int(x) + d1, int(y + 6*d1)), normal_font, button=True)

		back_button = draw_text('Back', (int(x) + d1, int(y + 11*d1)), normal_font, button=True)
	
		# Get current mouse position.
		mx, my = pg.mouse.get_pos()

		# Actions that will be taken for each option.
		if jeff_button.collidepoint((mx, my)):
			draw_text('Jeff!', (int(x) + d1, int(y + 2*d1)), normal_font, color=C.BLUE)
			if click:
				local_sfx = pg.mixer.Sound(C.TETRIS_FOR_JEFF_PATH + rd.choice(C.TETRIS_FOR_JEFF_LIST))
				local_sfx.set_volume(commentary_volume/10)
				local_sfx.play()
				C.CLICK_SFX.play()
				commentary = 0
				commentary_menu()
		if jonas_button.collidepoint((mx, my)):
			draw_text('Jonas!', (int(x) + d1, int(y + 3*d1)), normal_font, color=C.BLUE)
			if click:
				local_sfx = pg.mixer.Sound(C.TETRIS_FOR_JONAS_PATH + rd.choice(C.TETRIS_FOR_JONAS_LIST))
				local_sfx.set_volume(commentary_volume/10)
				local_sfx.play()
				C.CLICK_SFX.play()
				commentary = 1
				commentary_menu()
		if buco_button.collidepoint((mx, my)):
			draw_text('BUUUCOOOOOOO!', (int(x) + d1, int(y + 4*d1)), normal_font, color=C.BLUE)
			if click:
				local_sfx = pg.mixer.Sound(C.TETRIS_FOR_BUCO_PATH + rd.choice(C.TETRIS_FOR_BUCO_LIST))
				local_sfx.set_volume(commentary_volume/10)
				local_sfx.play()
				C.CLICK_SFX.play()
				commentary = 2
				commentary_menu()
		if quaid_button.collidepoint((mx, my)):
			draw_text('Quaid!', (int(x) + d1, int(y + 5*d1)), normal_font, color=C.BLUE)
			if click:
				local_sfx = pg.mixer.Sound(C.TETRIS_FOR_QUAID_PATH + rd.choice(C.TETRIS_FOR_QUAID_LIST))
				local_sfx.set_volume(commentary_volume/10)
				local_sfx.play()
				C.CLICK_SFX.play()
				commentary = 3
				commentary_menu()
		if harry_button.collidepoint((mx, my)):
			draw_text('Harry!', (int(x) + d1, int(y + 6*d1)), normal_font, color=C.BLUE)
			if click:
				local_sfx = pg.mixer.Sound(C.TETRIS_FOR_HARRY_PATH + rd.choice(C.TETRIS_FOR_HARRY_LIST))
				local_sfx.set_volume(commentary_volume/10)
				local_sfx.play()
				C.CLICK_SFX.play()
				commentary = 4
				commentary_menu()
		if back_button.collidepoint((mx, my)):
			draw_text('Back', (int(x) + d1, int(y + 11*d1)), normal_font, color=C.BLUE)
			if click:
				C.CLICK_SFX.play()
				commentary_menu()

		click = False

		for event in pg.event.get():
			if event.type == pg.QUIT:
				pg.quit()
				sys.exit()
			if event.type == pg.KEYDOWN:
				if event.key == pg.K_ESCAPE:
					commentary_menu()
			if event.type == pg.MOUSEBUTTONDOWN:
				if event.button == 1:
					click = True
			if event.type == pg.USEREVENT:
				check_music_queue()

		pg.display.update()
		main_clock.tick(tick_time)


def commentary_menu():
	global commentary
	click = False

	while True:
		# Draw menu background.
		draw_menu_background()
		draw_rect(text_field)
		draw_borders(text_field, C.BC)

		keys = pg.key.get_pressed()

		# Draw title.
		draw_text('Select Commentary!', (int(x), int(y)), title_font)

		# Draw main menu options.
		boom_button = draw_text('Boom! Tetris for Jeff!', (int(x) + d1, int(y + 2*d1)), normal_font, button=True)
		ch_button = draw_text('The Tetris God', (int(x) + d1, int(y + 3*d1)), normal_font, button=True)
		wk_2010_button = draw_text('World Cup 2010', (int(x) + d1, int(y + 4*d1)), normal_font, button=True)
		back_button = draw_text('Back', (int(x) + d1, int(y + 11*d1)), normal_font, button=True)

		# Get current mouse position.
		mx, my = pg.mouse.get_pos()

		# Actions that will be taken for each option.
		if boom_button.collidepoint((mx, my)):
			draw_text('Boom! Tetris for Jeff!', (int(x) + d1, int(y + 2*d1)), normal_font, color=C.BLUE)
			if click:
				C.CLICK_SFX.play()
				commentary_boom_tetris_menu()
		if ch_button.collidepoint((mx, my)):
			draw_text('The Tetris God', (int(x) + d1, int(y + 3*d1)), normal_font, color=C.BLUE)
			if click:
				local_sfx = pg.mixer.Sound(C.CH_PATH + 'longbar/' + rd.choice(C.CH_LONGBAR))
				local_sfx.set_volume(commentary_volume/10)
				local_sfx.play()
				C.CLICK_SFX.play()
				commentary = 5
				main_menu()
		if wk_2010_button.collidepoint((mx, my)):
			draw_text('World Cup 2010', (int(x) + d1, int(y + 4*d1)), normal_font, color=C.BLUE)
			if click:
				local_sfx = pg.mixer.Sound(C.WK_2010_GOAL_PATH + rd.choice(C.WK_2010_GOAL_LIST))
				local_sfx.set_volume(commentary_volume/10)
				local_sfx.play()
				C.CLICK_SFX.play()
				commentary = 6
				main_menu()	
		if back_button.collidepoint((mx, my)):
			draw_text('Back', (int(x) + d1, int(y + 11*d1)), normal_font, color=C.BLUE)
			if click:
				C.CLICK_SFX.play()
				main_menu()		

		click = False

		for event in pg.event.get():
			if event.type == pg.QUIT:
				pg.quit()
				sys.exit()
			if event.type == pg.KEYDOWN:
				if event.key == pg.K_ESCAPE:
					main_menu()
			if event.type == pg.MOUSEBUTTONDOWN:
				if event.button == 1:
					click = True
			if event.type == pg.USEREVENT:
				check_music_queue()

		pg.display.update()
		main_clock.tick(tick_time)

def main_menu():
	global menu_music
	click = False

	while True:
		# Draw menu background.
		draw_menu_background()
		draw_rect(text_field)
		draw_borders(text_field, C.BC)

		# Draw title.
		draw_text('Boom! Tetris!', (int(x), int(y)), title_font)

		# Draw main menu options.
		singleplayer_button = draw_text('Singleplayer', (int(x) + d1, int(y + 2*d1)), normal_font, button=True)
		multiplayer_button = draw_text('Multiplayer', (int(x) + d1, int(y + 3*d1)), normal_font, button=True)
		AI_button = draw_text('AI Game', (int(x) + d1, int(y + 4*d1)), normal_font, button=True)
		options_button = draw_text('Options', (int(x) + d1, int(y + 5*d1)), normal_font, button=True)
		music_button = draw_text('Music', (int(x) + d1, int(y + 6*d1)), normal_font, button=True)
		commnentary_button = draw_text('Commentary', (int(x) + d1, int(y + 7*d1)), normal_font, button=True)
		quit_button = draw_text('Quit', (int(x) + d1, int(y + 8*d1)), normal_font, button=True)

		# Get current mouse position.
		mx, my = pg.mouse.get_pos()

		# Actions that will be taken for each option.
		if singleplayer_button.collidepoint((mx, my)):
			draw_text('Singleplayer', (int(x) + d1, int(y + 2*d1)), normal_font, color=C.RED)
			if click:
				C.CLICK_SFX.play()
				singleplayer_menu()

		if multiplayer_button.collidepoint((mx, my)):
			draw_text('Multiplayer', (int(x) + d1, int(y + 3*d1)), normal_font, color=C.RED)
			if click:
				C.CLICK_SFX.play()
				multiplayer_menu()

		if AI_button.collidepoint((mx, my)):
			draw_text('AI Game', (int(x) + d1, int(y + 4*d1)), normal_font, color=C.RED)
			if click:
				C.CLICK_SFX.play()
				AIGame_menu()

		if options_button.collidepoint((mx, my)):
			draw_text('Options', (int(x) + d1, int(y + 5*d1)), normal_font, color=C.RED)
			if click:
				C.CLICK_SFX.play()
				options_menu()

		if music_button.collidepoint((mx, my)):
			draw_text('Music', (int(x) + d1, int(y + 6*d1)), normal_font, color=C.RED)
			if click:
				C.CLICK_SFX.play()
				music_menu()

		if commnentary_button.collidepoint((mx, my)):
			draw_text('Commentary', (int(x) + d1, int(y + 7*d1)), normal_font, color=C.RED)
			if click:
				C.CLICK_SFX.play()
				commentary_menu()

		if quit_button.collidepoint((mx, my)):
			draw_text('Quit', (int(x) + d1, int(y + 8*d1)), normal_font, color=C.RED)
			if click:
				C.CLICK_SFX.play()
				pg.quit()
				sys.exit()

		click = False

		for event in pg.event.get():
			if event.type == pg.QUIT:
				pg.quit()
				sys.exit()
			if event.type == pg.KEYDOWN:
				if event.key == pg.K_ESCAPE:
					pg.quit()
					sys.exit()
			if event.type == pg.MOUSEBUTTONDOWN:
				if event.button == 1:
					click = True
			if event.type == pg.USEREVENT:
				check_music_queue()

		pg.display.update()
		main_clock.tick(tick_time)

def start_up_screen():
	def draw_start_up_screen(timer, t_end, play_sfx):
		display.fill(color=(0, 0, 0))
		jeff_img = pg.image.load('images/jeff_black.png')
		sunglasses = pg.image.load('images/sunglasses_grey.png')
		if timer > t_end/1.9: sunglasses = pg.image.load('images/sunglasses.png')
		sfx_path = 'music_and_sfx/sfx/boom_tetris/tetris_for_jeff/TetrisForJeff_1.mp3'
		txt_str = 'Boom! Tetris!    |    Developed by Auke Bruinsma'

		s = 1.9; r = 17 # Scaler and roration value.
		x_offset = 30; y_offset=30
		t1 = 4.5e3
		start_height = 0.1
		a = 5
		fade_out_time = 1000

		sunglasses = pg.transform.scale(sunglasses, (int(sunglasses.get_width()/s), int(sunglasses.get_height()/s)))
		sunglasses = pg.transform.rotate(sunglasses, r)

		jeff_width = jeff_img.get_width()
		jeff_height = jeff_img.get_height()

		x = (C.SURFACE_WIDTH - jeff_width)/2
		y = (C.SURFACE_HEIGHT - jeff_height)/2

		if timer < 255*a:
			jeff_img.set_alpha(timer/a)
			sunglasses.set_alpha(timer/a)
			draw_text(txt_str, (50, int(display.get_height()-80)), normal_font, alpha=True, alpha_value=timer/a)
		if timer > 255*a and timer < t_end - 255*a - fade_out_time: draw_text(txt_str, (50, int(display.get_height()-80)), normal_font)
		if timer > t_end - 255*a - fade_out_time:
			jeff_img.set_alpha((t_end - timer - fade_out_time) / a)
			sunglasses.set_alpha((t_end - timer - fade_out_time) / a)
			draw_text(txt_str, (50, int(display.get_height()-80)), normal_font, alpha=True, alpha_value=(t_end - timer - fade_out_time) / a)

		display.blit(jeff_img, (x, y))

		if timer < t1: display.blit(sunglasses, (x + x_offset, y + y_offset + start_height*(timer-t1) ))
		else: display.blit(sunglasses, (x + x_offset, y + y_offset))
		if timer > t1 and timer <= t1 + 35:
			sfx = pg.mixer.Sound(sfx_path)
			sfx.set_volume(C.SOUND_VOLUME_1)
			sfx.play()

		pg.display.flip()
		pg.time.delay(20)

	clock = pg.time.Clock()
	timer = 0
	t_end = 7e3

	sfx_path = 'music_and_sfx/sfx/boom_tetris/321/MoreTetrisThanYouCanHandle.mp3'
	sfx = pg.mixer.Sound(sfx_path)
	sfx.set_volume(C.SOUND_VOLUME_1)
	sfx.play()

	while timer < t_end:
		clock.tick()
		timer += clock.get_rawtime()
		draw_start_up_screen(timer, t_end, True)
		pg.display.update()

#start_up_screen()

# Choose menu song.
menu_music = C.MENU_MUSIC_PATH + rd.choice(C.MENU_MUSIC)
pg.mixer.music.load(menu_music) # Load the song.
pg.mixer.music.set_volume(music_volume/10) # Set the volume.
pg.mixer.music.set_endevent(pg.USEREVENT) # Create end event.
pg.mixer.music.play() # Play the song.

'''
def controls_menu():
	click = False

	while True:
		# Draw menu background.
		draw_menu_background()
		draw_rect(text_field)
		draw_borders(text_field, C.BC)

		# Draw title.
		draw_text('Controls!', (int(x), int(y)), title_font)

		back_button = draw_text('Back', (int(x) + d1, int(y + 11*d1)), normal_font, button=True)
	
		# Get current mouse position.
		mx, my = pg.mouse.get_pos()

		# Actions that will be taken for each option.
		if back_button.collidepoint((mx, my)):
			draw_text('Back', (int(x) + d1, int(y + 11*d1)), normal_font, color=C.BLUE)
			if click:
				C.CLICK_SFX.play()
				main_menu()

		
		click = False

		for event in pg.event.get():
			if event.type == pg.QUIT:
				pg.quit()
				sys.exit()
			if event.type == pg.KEYDOWN:
				if event.key == pg.K_ESCAPE:
					main_menu()
			if event.type == pg.MOUSEBUTTONDOWN:
				if event.button == 1:
					click = True
			if event.type == pg.USEREVENT:
				check_music_queue()

		pg.display.update()
		main_clock.tick(tick_time)
'''