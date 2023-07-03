import pygame as pg
import Board
import Renderer
import Tetromino
from collections import namedtuple
import constants_parameters as C
import stats
import sfx
import numpy as np
import sys
import random as rd
import copy

Position = namedtuple('Position', 'x y')
Size = namedtuple('Size', 'width height')

class Game(object):
	def __init__(self, surface, start_level, commentary, preview_tetromino, gridline_boolean, hard_drop_bool, music_queue, menu_music,
			tetris_version, p1_left, p1_right, p1_a, p1_b, p1_down, p1_space, commentary_volume):
		# Initialize all imported pygame modules.
		pg.display.set_caption(C.GAME_TITLE) # Give the game a title.
		pg.mouse.set_visible(True)

		self.surface = surface
		self.clock = pg.time.Clock() 
		self.fall_speed_timer = 0
		self.drought_counter = 0
		self.no_longbar_arr = []
		self.hold_key_timer = 0
		self.ai_timer = 0
		self.soft_drop_counter = 0
		self.hard_drop_counter = 0
		self.line_counter = C.START_LINES
		self.single_counter = 0
		self.double_counter = 0
		self.triple_counter = 0
		self.tetris_counter = 0
		self.single_score = 0
		self.double_score = 0
		self.triple_score = 0
		self.tetris_score = 0
		self.tetris_rate = 0
		self.tetris_rate_arr = []
		self.burn_counter = 0
		self.start_level = start_level
		self.cur_level = self.start_level
		self.first_level_up = C.compute_start_level(self.start_level)
		self.not_leveled_yet = True

		if tetris_version:
			self.framerate = C.FRAMERATE_NTSC
			self.velocity_array = C.LEVELS_FRAMES_NTSC
			self.das_delay_frames = C.DAS_DELAY_FRAMES_NTSC
			self.das_auto_repeat_frames = C.DAS_AUTO_REPEAT_FRAMES_NTSC
		else:
			self.framerate = C.FRAMERATE_PAL
			self.velocity_array = C.LEVELS_FRAMES_PAL
			self.das_delay_frames = C.DAS_DELAY_FRAMES_PAL
			self.das_auto_repeat_frames = C.DAS_AUTO_REPEAT_FRAMES_PAL

		self.start_velocity = self.velocity_array[self.start_level]
		self.score = C.START_SCORE
		self.score_arr = []
		self.highscore = self.check_highscores(score=0, return_topscore=True)
		self.repress = False
		self.gridline_boolean = gridline_boolean
		self.hard_drop_bool = hard_drop_bool
		self.ARE_bool = False
		self.ARE_timer = 0
		self.line_clear_bool = False
		self.line_clear_timer = 0
		self.place_height = C.BOARD_NROWS - C.BOARD_INVIS_ROWS
		self.rows = []
		self.block_counter = 1
		self.game_over = False
		self.game_start = True
		self.game_over_timer = 0
		#self.game_start_timer = 0
		self.back_to_menu = None
		self.dif_block_counter = np.zeros(len(C.BLOCKS))
		self.cur_velocity = self.start_velocity
		self.commentary = commentary
		self.preview_bool = preview_tetromino
		self.tetris_ready = False
		self.well_open = False
		self.after_tetris = False
		self.music_queue = music_queue
		self.menu_music = menu_music
		self.after_game_stats = False
		self.vuvuzuela_timer = 10e3
		self.game_pause = False
		self.commentary_volume = commentary_volume
		self.tetris_ready_prob = 0
		self.neutral_sfx_prob = 0
		self.next_tetromino_bool = False
		self.heights_array = [0]*10
		self.reward = 0
		self.number_of_gaps = 0


		# Controls
		self.p1_left = p1_left
		self.p1_right = p1_right
		self.p1_a = p1_a
		self.p1_b = p1_b
		self.p1_down = p1_down
		self.p1_space = p1_space
		
		# Set up the renderer.
		self.renderer = Renderer.Renderer(C.SURFACE_WIDTH, C.SURFACE_HEIGHT, C.SBC, surface)

		# Set up the board.
		self.board = Board.Board(Size(C.BOARD_NCOLUMNS, C.BOARD_NROWS), pg.Rect(C.BOARD_LEFT, C.BOARD_TOP, C.BOARD_WIDTH, C.BOARD_HEIGHT))
		self.previous_board = []

		# Set up tetromino
		self.tetromino = Tetromino.Tetromino(self.board.dimensions.width // 2, 0 + C.BOARD_INVIS_ROWS, self.block_counter, None)
		self.cur_tetromino_int = self.tetromino.type
		self.preview_tetromino = copy.deepcopy(self.tetromino)

		# Set up next tetromino
		self.next_tetromino = Tetromino.Tetromino(self.board.dimensions.width // 2, 0 + C.BOARD_INVIS_ROWS, self.block_counter,  self.tetromino)

		self.t_block = Tetromino.Tetromino(0, 0, self.block_counter, None); self.t_block.type = 0; self.t_block.blocks = C.BLOCKS[self.t_block.type]
		self.square = Tetromino.Tetromino(0, 0, self.block_counter, None); self.square.type = 1; self.square.blocks = C.BLOCKS[self.square.type]
		self.longbar = Tetromino.Tetromino(0, 0, self.block_counter, None); self.longbar.type = 2; self.longbar.blocks = C.BLOCKS[self.longbar.type]
		self.l_block = Tetromino.Tetromino(0, 0, self.block_counter, None); self.l_block.type = 3; self.l_block.blocks = C.BLOCKS[self.l_block.type]
		self.reverse_l_block = Tetromino.Tetromino(0, 0, self.block_counter, None); self.reverse_l_block.type = 4; self.reverse_l_block.blocks = C.BLOCKS[self.reverse_l_block.type]
		self.squiggly = Tetromino.Tetromino(0, 0, self.block_counter, None); self.squiggly.type = 5; self.squiggly.blocks = C.BLOCKS[self.squiggly.type]
		self.reverse_squiggly = Tetromino.Tetromino(0, 0, self.block_counter, None); self.reverse_squiggly.type = 6; self.reverse_squiggly.blocks = C.BLOCKS[self.reverse_squiggly.type]

		self.block_rect = pg.Rect(0, 0, self.board.rect.width // self.board.dimensions.width, self.board.rect.height // self.board.dimensions.height)
		self.block_rect_small = pg.Rect(0, 0, self.board.rect.width // (self.board.dimensions.width * 1.5), self.board.rect.height // (self.board.dimensions.height * 1.5))
		self.B = self.block_rect.width # To save space.
		self.TB = 20 # Total number of block rect widths that the fields make up in the height.
		self.TA = 4 # Total number of space between all the different fields.
		self.A = (C.SURFACE_HEIGHT - 2*C.N - self.TB*self.B - C.BSR) / self.TA # The space between fields.
		self.S = 1 # Scaling factor if the sum of the heights of all fields is larger than the screen height.
		self.W = C.BOARD_LEFT + C.BOARD_WIDTH + C.N # Some more definitions to save space.

		# If the space between the fields is smaller than the normal boundary size, change the size.
		if self.A < C.N:
			self.A = C.N
			self.B = (C.SURFACE_HEIGHT - 2*C.N - self.TA*self.A - C.BSR) / self.TB

		self.lineboard_field = pg.Rect(C.LINE_BOARD_LEFT, C.LINE_BOARD_TOP, C.LINE_BOARD_WIDTH, C.LINE_BOARD_HEIGHT) # Lineboard field.
		self.statistics_field = pg.Rect(C.BOARD_LEFT - 12*self.B, C.BOARD_TOP + C.BOARD_HEIGHT - 17*self.B, 11*self.B, 17*self.B) # Statistics field.
		self.score_field = pg.Rect(self.W, C.N, 9*self.B, 6*self.B) # Score field.
		self.tetris_rate_field = pg.Rect(self.W, C.N + 6*self.B + self.A, 9*self.B, 3*self.B) # Tetris rate field.
		self.next_tetromino_field = pg.Rect(self.W, C.N + 9*self.B + 2*self.A, 4*self.B, 4*self.B) # Next tetromino field.
		self.tetris_field = pg.Rect(self.W + 5*self.B, C.N + 9*self.B + 2*self.A, 4*self.B, 4*self.B) # Tetris field.
		self.stats_field = pg.Rect(self.W + 5*self.B, C.N + 9*self.B + 2*self.A, 4*self.B, 4*self.B) # Stats field.
		self.level_field = pg.Rect(self.W, C.N + 13*self.B + 3*self.A, 7*self.B, 3*self.B) # Level field.
		self.burn_field = pg.Rect(self.W, C.N + 16*self.B + 4*self.A, 4*self.B, 4*self.B) # Burn field.
		self.drought_field = pg.Rect(self.W + 5*self.B, C.N + 16*self.B + 4*self.A, 4*self.B, 4*self.B) # Drought field.

		self.cover_up_field_1 = pg.Rect(C.BOARD_LEFT, C.BOARD_TOP, C.BOARD_WIDTH, C.BOARD_HEIGHT * (C.BOARD_INVIS_ROWS / (C.BOARD_INVIS_ROWS+C.BOARD_NROWS)) + 6)

		#sfx.play_start_game_sfx(self.commentary, self.commentary_volume)

	def update(self):
		with self.renderer:
			# Draw background pattern.
			self.renderer.draw_background_pattern(self.block_rect)

			if self.after_game_stats == False:
				# Draw previous board phase and the line clear animation.
				if self.line_clear_bool:
					self.renderer.draw_board(self.previous_board, self.tetromino, self.cur_level, C.BBC)	
					self.renderer.draw_line_clear_animation(self.board, self.block_rect, self.framerate, C.BBC, self.rows, self.line_clear_timer)

				# Draw the board (but not after a line clear).
				if self.line_clear_bool == False and self.game_over == False:
					self.renderer.draw_board(self.board, self.tetromino, self.cur_level, C.BBC)

				# Draw gridlines.
				if self.gridline_boolean and self.game_start == False:
					self.renderer.draw_gridlines(self.board, self.block_rect, C.BOARD_LEFT, C.BOARD_TOP, C.GRIDLINES_COLOUR)

				# Draw game over animation.
				if self.game_over:
					#self.renderer.draw_board(self.previous_board, self.tetromino, self.cur_level, C.BBC)
					self.back_to_menu = False#self.renderer.draw_game_over_animation(self.surface, self.board, self.block_rect, C.BBC, C.BBC, 
							#self.game_over_timer, self.score)
				
				# Draw preview of the tetromino.
				if self.ARE_bool == False and self.line_clear_bool == False and self.game_over == False and self.game_start == False:
					if self.preview_bool:
						self.renderer.draw_preview_tetromino(self.preview_tetromino,
							Position(self.board.rect.x + self.preview_tetromino.x * self.block_rect.width,
								self.board.rect.y + self.preview_tetromino.y * self.block_rect.height),
								self.block_rect, self.cur_level)
				
					# Draw the next tetromino on the board.
					self.renderer.draw_tetromino(self.tetromino,
						Position(self.board.rect.x + self.tetromino.x * self.block_rect.width,
									self.board.rect.y + self.tetromino.y * self.block_rect.height),
									self.block_rect, self.cur_level)

				# Draw pause screen.
				if self.game_pause: self.renderer.draw_pause_screen(self.board)				

				# Draw cover ups.
				self.renderer.draw_rect(self.cover_up_field_1, C.SBC)

				# Draw Board border.
				self.renderer.draw_board_borders(self.board, self.block_rect, C.BC)

				# Draw linescore field.
				self.renderer.draw_rect(self.lineboard_field, C.BBC)
				self.renderer.draw_borders(self.lineboard_field, C.BC)
				self.renderer.draw_changing_text('LINES - {:03d}'.format(self.line_counter), self.lineboard_field, C.FC, C.BBC)

				# Draw score field.
				self.renderer.draw_rect(self.score_field, C.BBC)
				self.renderer.draw_borders(self.score_field, C.BC)
				self.renderer.draw_changing_text('HIGHSCORE', pg.Rect(self.W, C.N, 9*self.B, 1.5*self.B), C.FC, C.BBC)
				self.renderer.draw_changing_text(f'{self.highscore:06d}', pg.Rect(self.W, C.N, 9*self.B, 4.5*self.B), C.FC, C.BBC)
				self.renderer.draw_changing_text('SCORE', pg.Rect(self.W, C.N, 9*self.B, 7.5*self.B), C.FC, C.BBC)
				self.renderer.draw_changing_text(f'{self.score:06d}', pg.Rect(self.W, C.N, 9*self.B, 10.5*self.B), C.FC, C.BBC)

				# Draw tetris rate field.
				self.renderer.draw_rect(self.tetris_rate_field, C.BBC)
				self.renderer.draw_borders(self.tetris_rate_field, C.BC)
				self.renderer.draw_changing_text(f'TRT: {self.tetris_rate:.1f}%', self.tetris_rate_field, C.FC, C.BBC)

				# Draw next tetromino field.
				self.renderer.draw_rect(self.next_tetromino_field, C.BBC)
				self.renderer.draw_borders(self.next_tetromino_field, C.BC)
				if self.game_start == False:
					self.renderer.draw_tetromino(self.next_tetromino, 
						Position(self.W + 2*self.B, C.N + 10*self.B + 2*self.A), self.block_rect, self.cur_level)

				# Draw tetris field.
				if not self.game_over:
					self.renderer.draw_rect(self.tetris_field, C.BBC)
					self.renderer.draw_borders(self.tetris_field, C.BC)
					self.renderer.draw_changing_text('TRS',	
						pg.Rect(self.W + 5*self.B, C.N + 9*self.B + 2*self.A, 4*self.B, 2.5*self.B), C.FC, C.BBC) # -1.5 shift.
					self.renderer.draw_changing_text(f'{self.tetris_counter}', 
						pg.Rect(self.W + 5*self.B, C.N + 9*self.B + 2*self.A, 4*self.B, 5.5*self.B), C.FC, C.BBC) # +1.5 shift.

				# Draw stats field.
				#if self.game_over:
				#	self.renderer.draw_rect(self.stats_field, C.BBC)
				#	self.renderer.draw_borders(self.stats_field, C.BC)
				#	self.after_game_stats = self.renderer.draw_stats_button(self.surface, self.stats_field, self.B, self.B)

				# Draw level field.
				self.renderer.draw_rect(self.level_field, C.BBC)
				self.renderer.draw_borders(self.level_field, C.BC)
				self.renderer.draw_changing_text(f'LEVEL {self.cur_level}', self.level_field, C.FC, C.BBC)

				# Draw burn field.
				self.renderer.draw_rect(self.burn_field, C.BBC)
				self.renderer.draw_borders(self.burn_field, C.BC)
				self.renderer.draw_changing_text('BRN', pg.Rect(self.W, C.N + 16*self.B + 4*self.A, 4*self.B, 2.5*self.B), C.FC, C.BBC)
				self.renderer.draw_changing_text(f'{self.burn_counter}', 
					pg.Rect(self.W, C.N + 16*self.B + 4*self.A, 4*self.B, 5.5*self.B), C.FC, C.BBC)

				# Draw drought field.
				if self.drought_counter >= C.DROUGHT_BOUNDARY:
					self.renderer.draw_rect(self.drought_field, C.BBC)
					self.renderer.draw_borders(self.drought_field, C.BC)
					self.renderer.draw_tetromino(self.longbar,
						Position(self.W + 7*self.B, C.N + 18.5*self.B + 4*self.A), self.block_rect_small, self.cur_level)
					self.renderer.draw_changing_text(f'{self.drought_counter}', 
						pg.Rect(self.W + 5*self.B, C.N + 16*self.B + 4*self.A, 4*self.B, 2.5*self.B), C.RED, C.BBC)

				# Draw statistics field. C.BOARD_LEFT - 12*self.B, C.BOARD_TOP + C.BOARD_HEIGHT - 17*self.B, 11*self.B, 17*self.B
				self.renderer.draw_rect(self.statistics_field, C.BBC)
				self.renderer.draw_borders(self.statistics_field, C.BC)
				self.renderer.draw_changing_text('STATISTICS', 
					pg.Rect(C.BOARD_LEFT - 12*self.B, C.BOARD_TOP + C.BOARD_HEIGHT - 17*self.B, 11*self.B, 2*self.B), C.FC, C.BBC)

				self.renderer.draw_tetromino(self.t_block,
					Position(C.BOARD_LEFT - 9*self.block_rect.width, C.BOARD_TOP + 8*self.block_rect.height),
								self.block_rect_small, self.cur_level)
				self.renderer.draw_changing_text(f'{int(self.dif_block_counter[0]):03d}', pg.Rect(C.BOARD_LEFT - 12*self.block_rect.width, C.BOARD_TOP + 8*self.block_rect.height, 
					14*self.block_rect.width, 1*self.block_rect.height),
					C.STATISTICS_COLOUR, C.BBC)

				self.renderer.draw_tetromino(self.square,
					Position(C.BOARD_LEFT - 9*self.block_rect.width, C.BOARD_TOP + 10*self.block_rect.height),
								self.block_rect_small, self.cur_level)
				self.renderer.draw_changing_text(f'{int(self.dif_block_counter[1]):03d}', pg.Rect(C.BOARD_LEFT - 12*self.block_rect.width, C.BOARD_TOP + 10*self.block_rect.height, 
					14*self.block_rect.width, 1*self.block_rect.height),
					C.STATISTICS_COLOUR, C.BBC)

				self.renderer.draw_tetromino(self.longbar,
					Position(C.BOARD_LEFT - 9*self.block_rect.width, C.BOARD_TOP + 12*self.block_rect.height),
								self.block_rect_small, self.cur_level)
				self.renderer.draw_changing_text(f'{int(self.dif_block_counter[2]):03d}', pg.Rect(C.BOARD_LEFT - 12*self.block_rect.width, C.BOARD_TOP + 12*self.block_rect.height, 
					14*self.block_rect.width, 1*self.block_rect.height),
					C.STATISTICS_COLOUR, C.BBC)

				self.renderer.draw_tetromino(self.l_block,
					Position(C.BOARD_LEFT - 9*self.block_rect.width, C.BOARD_TOP + 14*self.block_rect.height),
								self.block_rect_small, self.cur_level)
				self.renderer.draw_changing_text(f'{int(self.dif_block_counter[3]):03d}', pg.Rect(C.BOARD_LEFT - 12*self.block_rect.width, C.BOARD_TOP + 14*self.block_rect.height, 
					14*self.block_rect.width, 1*self.block_rect.height),
					C.STATISTICS_COLOUR, C.BBC)

				self.renderer.draw_tetromino(self.reverse_l_block,
					Position(C.BOARD_LEFT - 9*self.block_rect.width, C.BOARD_TOP + 16*self.block_rect.height),
								self.block_rect_small, self.cur_level)
				self.renderer.draw_changing_text(f'{int(self.dif_block_counter[4]):03d}', pg.Rect(C.BOARD_LEFT - 12*self.block_rect.width, C.BOARD_TOP + 16*self.block_rect.height, 
					14*self.block_rect.width, 1*self.block_rect.height),
					C.STATISTICS_COLOUR, C.BBC)

				self.renderer.draw_tetromino(self.squiggly,
					Position(C.BOARD_LEFT - 9*self.block_rect.width, C.BOARD_TOP + 18*self.block_rect.height),
								self.block_rect_small, self.cur_level)
				self.renderer.draw_changing_text(f'{int(self.dif_block_counter[5]):03d}', pg.Rect(C.BOARD_LEFT - 12*self.block_rect.width, C.BOARD_TOP + 18*self.block_rect.height, 
					14*self.block_rect.width, 1*self.block_rect.height),
					C.STATISTICS_COLOUR, C.BBC)

				self.renderer.draw_tetromino(self.reverse_squiggly,
					Position(C.BOARD_LEFT - 9*self.block_rect.width, C.BOARD_TOP + 20*self.block_rect.height),
								self.block_rect_small, self.cur_level)
				self.renderer.draw_changing_text(f'{int(self.dif_block_counter[6]):03d}', pg.Rect(C.BOARD_LEFT - 12*self.block_rect.width, C.BOARD_TOP + 20*self.block_rect.height, 
					14*self.block_rect.width, 1*self.block_rect.height),
					C.STATISTICS_COLOUR, C.BBC)

				
				# Start game animation and play sound effects.
				if self.game_start:
					countdown = False#self.renderer.draw_start_game_animation(self.surface, self.board, self.block_rect, C.BBC, C.BBC, self.game_start_timer)
					if countdown == False:
						self.fall_speed_timer = 0
						self.game_start = False # Start game animation will only be executed once, when the game starts.
				

			elif self.after_game_stats == True:
				self.after_game_stats = self.renderer.draw_after_game_stats(self.surface, self.board, self.block_rect)

		# Entry/appearance delay.
		#if self.ARE_bool and self.line_clear_bool == False:
		#	self.clock.tick()
		#	self.ARE_timer += self.clock.get_rawtime()

		if self.line_clear_bool:
			if self.line_clear_timer < C.compute_milliseconds(self.framerate, C.LINE_CLEAR_DELAY):
				self.clock.tick()
				self.line_clear_timer += self.clock.get_rawtime()

		#if self.game_over:
		#	self.game_over_timer += self.clock.get_rawtime()

		#if self.game_start:
		#	self.game_start_timer += self.clock.get_rawtime()

		if self.game_pause:
			self.fall_speed_timer = 0

		return self.handle_events()

	#def execute_move(self):

	def handle_events(self):
		pressed = pg.key.get_pressed()

		self.next_tetromino_bool = False

		self.clock.tick()
		self.fall_speed_timer += self.clock.get_rawtime() # Time used in previous tick.

		if self.back_to_menu == True:
			return False

		if self.ARE_bool and self.ARE_timer >= int(self.get_ARE_time(self.place_height)):
			self.fall_speed_timer = 0
			self.vuvuzuela_timer += self.ARE_timer
			self.ARE_timer = 0
			self.ARE_bool = False
			
			if pressed[self.p1_left] or pressed[self.p1_right]: 
				self.hold_key_timer = C.compute_milliseconds(self.framerate, self.das_delay_frames - self.das_auto_repeat_frames)
			else: 
				self.hold_key_timer = 0

		if self.line_clear_bool and self.line_clear_timer > C.compute_milliseconds(self.framerate, C.LINE_CLEAR_DELAY):
			self.line_clear_timer = 0
			self.line_clear_bool = False

		self.preview_tetromino = copy.deepcopy(self.tetromino)
		while not self.board.check_tetromino_colission(self.preview_tetromino, Position(0, +1), 0):
			self.preview_tetromino.y += 1

		# Make a block move down based on the time.
		if self.fall_speed_timer > C.compute_milliseconds(self.framerate, self.velocity_array[self.cur_level]) and self.game_start == False:
			if not self.board.check_tetromino_colission(self.tetromino, Position(0, +1), 0):
				#if self.repress == True or (pressed[C.P1_UP] == False and pressed[self.p1_down] == False):
				if self.repress == True or pressed[self.p1_down] == False:
					self.tetromino.y += 1
					self.fall_speed_timer = 0
			elif self.game_over == False:
				self.next_tetromino_bool = True
				self.get_next_tetromino()		

		if (pressed[self.p1_left] or pressed[self.p1_right] or pressed[self.p1_down]) and (self.game_start == False and self.game_pause == False):# or pressed[C.P1_UP]:
			self.hold_key_timer += self.clock.get_rawtime() # Time used in previous tick.

			# Movement.
			if pressed[self.p1_left] and not self.board.check_tetromino_colission(self.tetromino, Position(-1, 0), 0):				
				if self.hold_key_timer > C.compute_milliseconds(self.framerate, self.das_delay_frames):
					self.tetromino.x -= 1
					C.SFX_MOVE.play()
					self.hold_key_timer = C.compute_milliseconds(self.framerate, self.das_delay_frames - self.das_auto_repeat_frames)
			if pressed[self.p1_right] and not self.board.check_tetromino_colission(self.tetromino, Position(+1, 0), 0):
				if self.hold_key_timer > C.compute_milliseconds(self.framerate, self.das_delay_frames):
					self.tetromino.x += 1
					C.SFX_MOVE.play()
					self.hold_key_timer = C.compute_milliseconds(self.framerate, self.das_delay_frames - self.das_auto_repeat_frames)
			if self.repress == False and pressed[self.p1_down]:
				if not self.board.check_tetromino_colission(self.tetromino, Position(0, +1), 0):
					#if self.hold_key_timer > C.compute_milliseconds(self.framerate, C.DROPPING_SPEED * self.velocity_array[self.cur_level]):
					if self.hold_key_timer > C.compute_milliseconds(self.framerate, self.velocity_array[19]):	
						self.tetromino.y += 1
						self.soft_drop_counter += C.SOFT_DROP_POINTS_PER_LINE
						self.hold_key_timer = 0
				else:
					self.fall_speed_timer = C.compute_milliseconds(self.framerate, self.velocity_array[self.cur_level])
			#if pressed[C.P1_UP] and not self.board.check_tetromino_colission(self.tetromino, Position(0, -1), 0) and self.game_start == False:
			#	if self.hold_key_timer > C.compute_milliseconds(self.framerate, self.velocity_array[19]):
			#		self.tetromino.y -= 1
			#		self.hold_key_timer = 0

		for ev in pg.event.get():
			if ev.type == pg.QUIT or (ev.type == pg.KEYDOWN and ev.key == pg.K_ESCAPE):
				pg.mouse.set_visible(True)
				return False

			if ev.type == pg.KEYUP:
				if ev.key == self.p1_left or ev.key == self.p1_right:
					self.hold_key_timer = 0
				if ev.key == self.p1_down:
					self.soft_drop_counter = 0 # If the dropping key is released, no points are giving for soft dropping.
					self.fall_speed_timer = 0
					self.hold_key_timer = 0
				if ev.key == self.p1_space and self.hard_drop_bool:
					self.hard_drop_counter = 0
				self.repress = False
				
			if ev.type == pg.KEYDOWN:
				# Side movement.
				if ev.key == self.p1_right and not self.board.check_tetromino_colission(self.tetromino, Position(+1, 0), 0) and self.game_start == False and self.game_pause == False and self.ARE_bool == False:
					self.tetromino.x += 1
					C.SFX_MOVE.play()
				if ev.key == self.p1_left and not self.board.check_tetromino_colission(self.tetromino, Position(-1, 0), 0) and self.game_start == False and self.game_pause == False and self.ARE_bool == False:
					self.tetromino.x -= 1
					C.SFX_MOVE.play()

				# Rotation.
				if ev.key == self.p1_a and not self.board.check_tetromino_colission(self.tetromino, Position(0, 0), +1) and self.game_start == False and self.game_pause == False and self.ARE_bool == False:
					self.tetromino.rotate(+1)
					C.SFX_ROTATION.play()
				if ev.key == self.p1_b  and not self.board.check_tetromino_colission(self.tetromino, Position(0, 0), -1) and self.game_start == False and self.game_pause == False and self.ARE_bool == False:
					self.tetromino.rotate(-1)
					C.SFX_ROTATION.play()

				# Hard-drop.
				if ev.key == self.p1_space and self.hard_drop_bool and self.game_start == False and self.game_pause == False:
					#pg.key.set_repeat()
					while not self.board.check_tetromino_colission(self.tetromino, Position(0, +1), 0):
						self.hard_drop_counter += C.HARD_DROP_POINTS_PER_LINE
						self.tetromino.y += 1
					if self.game_over == False:
						self.next_tetromino_bool = True
						self.get_next_tetromino()

				if ev.key == pg.K_g:
					if self.gridline_boolean: self.gridline_boolean = False
					else: self.gridline_boolean = True

				if ev.key == pg.K_h:
					if self.preview_bool: self.preview_bool = False
					else: self.preview_bool = True

				if ev.key == pg.K_y and self.game_start == False and self.game_over == False:
					if self.game_pause == False:
						self.game_pause = True
						C.SFX_PAUSE.play()
					else: self.game_pause = False
			


		#print(self.game_pause, self.fall_speed_timer)

		if self.commentary == 6:
			self.vuvuzuela_timer += self.clock.get_rawtime()
			if self.vuvuzuela_timer >= 4.8e3:
				sfx.play_neutral_sfx(self.commentary, self.commentary_volume)
				self.vuvuzuela_timer = 0
			#print(self.vuvuzuela_timer, self.ARE_timer)

		if self.back_to_menu == False:
			pg.mouse.set_visible(False)
			self.board.empty_board()
			self.fall_speed_timer = 0
			self.drought_counter = 0
			self.hold_key_timer = 0
			self.soft_drop_counter = 0
			self.hard_drop_counter = 0
			self.line_counter = C.START_LINES
			self.single_counter = 0
			self.double_counter = 0
			self.triple_counter = 0
			self.tetris_counter = 0
			self.single_score = 0
			self.double_score = 0
			self.triple_score = 0
			self.tetris_score = 0
			self.tetris_rate = 0
			self.tetris_rate_arr = []
			self.burn_counter = 0
			self.cur_level = self.start_level
			self.not_leveled_yet = True
			self.score = C.START_SCORE
			self.score_arr = []
			self.highscore = self.check_highscores(score=0, return_topscore=True)
			self.repress = False
			self.ARE_bool = False
			self.ARE_timer = 0
			self.line_clear_bool = False
			self.line_clear_timer = 0
			self.place_height = C.BOARD_NROWS - C.BOARD_INVIS_ROWS
			self.rows = []
			self.block_counter = 1
			self.game_over = False
			self.game_start = True
			#self.game_start_timer = 0
			self.game_over_timer = 0
			self.back_to_menu = None
			self.dif_block_counter = np.zeros(len(C.BLOCKS))
			self.cur_velocity = self.start_velocity
			self.preview_tetromino = copy.deepcopy(self.tetromino)
			self.no_longbar_arr = []
			self.vuvuzuela_timer = 10e3
			self.game_pause = False
			self.tetris_ready_prob = 0
			self.neutral_sfx_prob = 0
			self.next_tetromino_bool = False
			self.heights_array = [0]*10
			self.reward = 0
			self.number_of_gaps = 0

			#sfx.play_start_game_sfx(self.commentary, self.commentary_volume)

		return True

	def get_ARE_time(self, place_height):
		ARE_delay = C.ARE_DELAY

		# ARE delay depends on place height according to the following step function.
		if place_height > 6: ARE_delay -= 2
		if place_height > 10: ARE_delay -= 2
		if place_height > 14: ARE_delay -= 2
		if place_height > 18: ARE_delay -= 2
		
		return C.compute_milliseconds(self.framerate, ARE_delay)

	def check_highscores(self, score, return_topscore=False):
		# Open highscores list.
		highscores = []

		# Open file and read into the list.
		file = open(C.HIGHSCORES_PATH, 'r')
		for line in file:
			highscores.append(line)
		file.close()

		# Convert the list to integers
		for i in range(len(highscores)):
			if highscores[i][-1] == '\n':
				highscores[i] = int(highscores[i][0:-1])
			else:
				highscores[i] = int(highscores[i])

		# Compare current score and insert if in the top 10.
		for i in range(len(highscores)):
			if score > highscores[i]:
				for j in range(len(highscores) - 1, i, -1):
					highscores[j] = highscores[j-1]

				highscores[i] = score
				break
		
		# Open file and rewrite highscores.
		file = open(C.HIGHSCORES_PATH, 'w')
		for i in range(len(highscores)):
			if i == len(highscores) - 1:
				file.write(str(highscores[i]))
			else:
				file.write(str(highscores[i]) + '\n')
		file.close()

		if return_topscore:
			return highscores[0]

	def check_music_queue(self):
		if pg.mixer.music.get_busy() == False:
			#print(len(self.music_queue))
			if len(self.music_queue) == 0:
				pg.mixer.music.load(self.menu_music)
				pg.mixer.music.play()
			else:
				pg.mixer.music.load(self.music_queue[0])
				pg.mixer.music.play()
				self.music_queue = np.delete(self.music_queue, 0)

	def level_up(self):
		self.cur_level += 1
		sfx.play_level_up_sfx()

	def play_step(self, final_move):
		#print(final_move)

		self.clock.tick()
		self.ai_timer += self.clock.get_rawtime() # Time used in previous tick.

		horizontal_shift = final_move[0]
		rotation = final_move[1]

		if rotation == -1:
			self.tetromino.rotate(-1)
		elif rotation == 1:
			self.tetromino.rotate(+1)
		elif rotation == 2:
			self.tetromino.rotate(+1)
			self.tetromino.rotate(+1)

		if horizontal_shift > 0:
			while horizontal_shift > 0:
				if not self.board.check_tetromino_colission(self.tetromino, Position(+1, 0), 0):
					self.tetromino.x += 1
				horizontal_shift -= 1
		elif horizontal_shift < 0:
			while horizontal_shift < 0:
				if not self.board.check_tetromino_colission(self.tetromino, Position(-1, 0), 0):
					self.tetromino.x -= 1
				horizontal_shift += 1





	def get_next_tetromino(self):
		# Place a tetromino on the board and obtain place height, which is used for entry delay.
		self.place_height = self.board.place_tetromino(self.tetromino)

		# Check if the player is game over.
		self.game_over = self.board.check_game_over()

		# Check if the player is tetris ready.
		self.tetris_ready = self.board.check_tetris_ready()

		# Check if the music has stopped and load a new track from the queue.
		self.check_music_queue()

		# Actions taken if the player is game over.
		#if self.game_over:
			#pg.mouse.set_visible(True)
			#sfx.play_game_over_sfx(self.commentary, self.commentary_volume) # Play game over sound effect based on the commentary type.
			#self.check_highscores(self.score) # Check and update highscores.

			# Generate after-game statistics.
			#stats.generate_after_game_stats(self.block_counter-1, self.no_longbar_arr, self.tetris_rate_arr, self.score_arr,
			#	self.dif_block_counter, [self.single_counter, self.double_counter, self.triple_counter, self.tetris_counter],
			#	[self.single_score, self.double_score, self.triple_score, self.tetris_score])

		self.previous_board = copy.deepcopy(self.board)
		
		# Remove lines from the board and update parameters.
		line_counter_add, score_add, self.line_clear_bool, self.rows, single_add, double_add, triple_add, tetris_add = self.board.remove_completed_lines(self.cur_level, 
			self.line_clear_bool, self.line_counter, self.commentary, self.commentary_volume)

		# Reward for the Agent.
		self.reward = score_add

		# After lines have been cleared, check if the players needs to level up.
		if self.not_leveled_yet == False and int((self.line_counter + line_counter_add)/10) > int(self.line_counter/10):
			self.level_up()

		# Update block counter, different block counter, score, line counter, burn counter and tetris counter.
		self.block_counter += 1
		self.dif_block_counter[self.tetromino.type] += 1
		self.score += score_add
		self.score += self.soft_drop_counter
		self.score += self.hard_drop_counter
		self.score_arr.append(self.score)
		self.line_counter += line_counter_add
		self.burn_counter += line_counter_add
		self.drought_counter += 1
		
		if single_add != 0: self.single_counter += single_add; self.single_score += score_add
		elif double_add != 0: self.double_counter += double_add; self.double_score += score_add
		elif triple_add != 0: self.triple_counter += triple_add; self.triple_score += score_add
		elif tetris_add != 0:
			self.tetris_counter += tetris_add; self.tetris_score += score_add
			self.tetris_ready_prob = 0

		#print(single_add, double_add, triple_add, tetris_add)
		#print(self.single_counter, self.single_score, self.double_counter, self.double_score, self.triple_counter, self.triple_score, self.tetris_counter, self.tetris_score)

		# Clear burn counter when a tetris is scored; clear no longbar counter when the player gets a longbar.
		if tetris_add != 0: self.burn_counter = 0
		if C.BLOCKS.index(C.LONGBAR) == self.tetromino.type: self.drought_counter = 0

		# Computation of the tetris rate.
		if self.line_counter == 0: self.tetris_rate = 0
		else: self.tetris_rate = 4 * self.tetris_counter / float(self.line_counter) * 100
		self.tetris_rate_arr.append(self.tetris_rate)

		# Add variables to array for the after-game statistics.
		self.no_longbar_arr.append(self.drought_counter)

		# Level up for the first time.
		if self.not_leveled_yet == True and self.line_counter >= self.first_level_up:
			self.level_up()
			self.not_leveled_yet = False

		# Adjust tetromino falling velocity based on the current level.
		self.cur_velocity = self.velocity_array[self.cur_level]
    
		# Obtain tetromino's
		self.tetromino = self.next_tetromino
		self.cur_tetromino_int = self.tetromino.type
		self.next_tetromino = Tetromino.Tetromino(self.board.dimensions.width // 2, 0 + C.BOARD_INVIS_ROWS, self.block_counter, self.tetromino)
		
		if self.commentary != 6:
			self.neutral_sfx_prob = sfx.play_neutral_sfx(self.commentary, self.commentary_volume, self.neutral_sfx_prob, self.tetromino.type)
		
		# Actions taken if player is tetris ready.
		if self.tetris_ready:
			self.tetris_ready_prob = sfx.play_tetris_ready_sfx(self.commentary, self.commentary_volume, self.tetris_ready_prob, self.tetromino.type)
		
		# Reset timers and booleans.
		self.fall_speed_timer = 0
		self.repress = True
		self.ARE_bool = True

		self.heights_array = self.board.compute_heights_array()
		prev_number_of_gaps = self.number_of_gaps
		self.number_of_gaps = self.board.search_for_gaps()

		if self.number_of_gaps > prev_number_of_gaps:
			self.reward -= 40*(self.cur_level+1)*(self.number_of_gaps-prev_number_of_gaps)
		elif self.number_of_gaps == prev_number_of_gaps:
			self.reward += 40*(self.cur_level+1)
		
