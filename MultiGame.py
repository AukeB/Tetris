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
			tetris_version, same_piecesets, p1_left, p1_right, p1_a, p1_b, p1_down, p1_space, p2_left, p2_right, p2_a, p2_b, p2_down, p2_space,
			commentary_volume, mode):

		# Initialize all imported pygame modules.
		pg.display.set_caption(C.GAME_TITLE) # Give the game a title.
		pg.mouse.set_visible(False) # Make sure the mouse is not visible when the game is initialized.

		self.surface = surface # Create surface object.
		self.clock = pg.time.Clock() # Initialize a timer.

		# Timers and counter.
		self.fall_speed_timer = [0, 0] # Timer that determines when the block should move one cell down.
		self.drought_counter = [0, 0] # Counts the number of blocks until a longbar is given. Used to calculate droughts.
		self.hold_key_timer = [0, 0] # Times how long a key is pressed, used for the implementatation of DAS.
		self.soft_drop_counter = [0, 0] # Count
		self.hard_drop_counter = [0, 0]
		self.line_counter = [C.START_LINES, C.START_LINES] # When the game starts, zero lines have been cleared.
		self.single_counter = [0, 0] # Counts number of singles scored.
		self.double_counter = [0, 0] # Same, but for doubles.
		self.triple_counter = [0, 0] # Triples
		self.tetris_counter = [0, 0] # Tetrises.
		self.single_score = [0, 0] # Counts the total score achieved with only singles.
		self.double_score = [0, 0] # Same, but for doubles.
		self.triple_score = [0, 0] # Triples
		self.tetris_score = [0, 0] # Tetrises.
		self.tetris_rate = [0, 0] # Tetris percentage rate.
		self.burn_counter = [0, 0] # Counts how many lines you been burned since the last tetris.
		self.start_level = start_level # Level to start on.
		self.cur_level = [self.start_level, self.start_level] # The current level the player is playing on.
		self.first_level_up = C.compute_start_level(self.start_level) # Determines the number of lines when the first level up will happen.
		self.not_leveled_yet = [True, True] # Boolean variable that states True if the player has not yet changed level.

		# Arrays over time and for plotting.
		self.no_longbar_arr = [[],[]] # Droughts will be stored in this array, so after the game the largest droughts can be plotted.
		self.tetris_rate_arr = [[],[]] # The tetris rate over time will be stored here.

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
		self.score = [C.START_SCORE, C.START_SCORE]
		self.score_arr = [[],[]]
		self.score_difference = self.score[0] - self.score[1]
		self.score_difference_arr = []
		self.score_dif_idx = 1
		self.score_switch = True
		self.pace_switch = 0

		#self.highscore = self.check_highscores(score=0, return_topscore=True)
		self.repress = [False, False]
		self.gridline_boolean = [gridline_boolean, gridline_boolean]
		self.hard_drop_bool = hard_drop_bool
		self.ARE_bool = [False, False]
		self.ARE_timer = [0, 0]
		self.line_clear_bool = [False, False]
		self.line_clear_timer = [0, 0]
		self.place_height = [C.BOARD_NROWS - C.BOARD_INVIS_ROWS, C.BOARD_NROWS - C.BOARD_INVIS_ROWS]
		self.rows = [[],[]]
		self.block_counter = [1, 1]
		self.same_piecesets = same_piecesets
		if self.same_piecesets:
			self.seed = self.block_counter[0] * C.SEED
			self.seed_2 = rd.randint(0, 1e6)
			self.seed -= self.seed_2
		else:
			self.seed = None
		self.game_over = [False, False]
		self.game_start = True
		self.game_over_timer = [0, 0]
		self.game_start_timer = 0
		self.back_to_menu = [None, None]
		self.dif_block_counter = [np.zeros(len(C.BLOCKS)), np.zeros(len(C.BLOCKS))]
		self.cur_velocity = [self.start_velocity, self.start_velocity]
		self.commentary = commentary
		self.preview_bool = [preview_tetromino, preview_tetromino]
		self.tetris_ready = [False, False]
		self.well_open = [False, False]
		self.after_tetris = [False, False]
		self.music_queue = music_queue
		self.menu_music = menu_music
		self.after_game_stats = False
		self.multiplayer = True
		self.vuvuzuela_timer = 10e3
		self.game_pause = False
		self.commentary_volume = commentary_volume
		self.neutral_sfx_prob = 0
		self.tetris_ready_prob_1 = 0
		self.tetris_ready_prob_2 = 0
		self.neck_and_neck_prob = 0
		self.mode = mode
		self.match_score = [0, 0]

		# Controls
		self.p1_left = p1_left
		self.p1_right = p1_right
		self.p1_a = p1_a
		self.p1_b = p1_b
		self.p1_down = p1_down
		self.p1_space = p1_space

		self.p2_left = p2_left
		self.p2_right = p2_right
		self.p2_a = p2_a
		self.p2_b = p2_b
		self.p2_down = p2_down
		self.p2_space = p2_space
		
		# Set up the renderer.
		self.renderer = Renderer.Renderer(C.SURFACE_WIDTH, C.SURFACE_HEIGHT, C.SBC, surface)

		# Set up the boards.
		self.board_1 = Board.Board(Size(C.BOARD_NCOLUMNS, C.BOARD_NROWS), pg.Rect(C.BOARD_LEFT_2P1, C.BOARD_TOP, C.BOARD_WIDTH, C.BOARD_HEIGHT))
		self.board_2 = Board.Board(Size(C.BOARD_NCOLUMNS, C.BOARD_NROWS), pg.Rect(C.BOARD_LEFT_2P2, C.BOARD_TOP, C.BOARD_WIDTH, C.BOARD_HEIGHT))

		self.previous_board_1 = []
		self.previous_board_2 = []

		# Set up tetromino
		self.tetromino_1 = Tetromino.Tetromino(self.board_1.dimensions.width // 2, 0 + C.BOARD_INVIS_ROWS, self.block_counter[0], None, self.seed)
		self.tetromino_2 = Tetromino.Tetromino(self.board_2.dimensions.width // 2, 0 + C.BOARD_INVIS_ROWS, self.block_counter[1], None, self.seed)

		self.preview_tetromino_1 = copy.deepcopy(self.tetromino_1)
		self.preview_tetromino_2 = copy.deepcopy(self.tetromino_2)

		# Set up next tetromino
		self.next_tetromino_1 = Tetromino.Tetromino(self.board_1.dimensions.width // 2, 0 + C.BOARD_INVIS_ROWS, self.block_counter[0],  self.tetromino_1, self.seed)
		self.next_tetromino_2 = Tetromino.Tetromino(self.board_2.dimensions.width // 2, 0 + C.BOARD_INVIS_ROWS, self.block_counter[1],  self.tetromino_2, self.seed)

		#self.t_block = Tetromino.Tetromino(0, 0, self.block_counter[0], None); self.t_block.type = 0; self.t_block.blocks = C.BLOCKS[self.t_block.type]
		#self.square = Tetromino.Tetromino(0, 0, self.block_counter[0], None); self.square.type = 1; self.square.blocks = C.BLOCKS[self.square.type]
		self.longbar = Tetromino.Tetromino(0, 0, self.block_counter[0], None); self.longbar.type = 2; self.longbar.blocks = C.BLOCKS[self.longbar.type]
		#self.l_block = Tetromino.Tetromino(0, 0, self.block_counter[0], None); self.l_block.type = 3; self.l_block.blocks = C.BLOCKS[self.l_block.type]
		#self.reverse_l_block = Tetromino.Tetromino(0, 0, self.block_counter[0], None); self.reverse_l_block.type = 4; self.reverse_l_block.blocks = C.BLOCKS[self.reverse_l_block.type]
		#self.squiggly = Tetromino.Tetromino(0, 0, self.block_counter[0], None); self.squiggly.type = 5; self.squiggly.blocks = C.BLOCKS[self.squiggly.type]
		#self.reverse_squiggly = Tetromino.Tetromino(0, 0, self.block_counter[0], None); self.reverse_squiggly.type = 6; self.reverse_squiggly.blocks = C.BLOCKS[self.reverse_squiggly.type]

		self.block_rect = pg.Rect(0, 0, self.board_1.rect.width // self.board_1.dimensions.width, self.board_1.rect.height // self.board_1.dimensions.height)
		self.block_rect_small = pg.Rect(0, 0, self.board_1.rect.width // (self.board_1.dimensions.width * 1.5), self.board_1.rect.height // (self.board_1.dimensions.height * 1.5))
		self.B = self.block_rect.width # To save space.
		self.TB = 22 # Total number of block rect widths that the fields make up in the height.
		self.TA = 5 # Total number of space between all the different fields.
		self.A = (C.SURFACE_HEIGHT - 2*C.N - self.TB*self.B - C.BSR) / self.TA # The space between fields.
		self.S = 1 # Scaling factor if the sum of the heights of all fields is larger than the screen height.
		self.W1 = C.BOARD_LEFT_2P1 + C.BOARD_WIDTH + C.N # Some more definitions to save space.
		self.W2 = C.BOARD_LEFT_2P2 + C.BOARD_WIDTH + C.N # Some more definitions to save space.

		# If the space between the fields is smaller than the normal boundary size, change the size.
		if self.A < C.N:
			self.A = C.N
			self.B = (C.SURFACE_HEIGHT - 2*C.N - self.TA*self.A - C.BSR) / self.TB

		# Lineboard fields.
		self.lineboard_field_1 = pg.Rect(C.LINE_BOARD_LEFT_2P1, C.N, C.LINE_BOARD_WIDTH, C.LINE_BOARD_HEIGHT)
		self.lineboard_field_2 = pg.Rect(C.LINE_BOARD_LEFT_2P2, C.N, C.LINE_BOARD_WIDTH, C.LINE_BOARD_HEIGHT)

		# Score fields.
		self.score_field_1 = pg.Rect(self.W1, C.N, 9*self.B, 5*self.B)
		self.score_field_2 = pg.Rect(self.W2, C.N, 9*self.B, 5*self.B)

		# Tetris rate fields.
		self.tetris_rate_field_1 = pg.Rect(self.W1, C.N + 5*self.B + self.A, 9*self.B, 3*self.B)
		self.tetris_rate_field_2 = pg.Rect(self.W2, C.N + 5*self.B + self.A, 9*self.B, 3*self.B)

		# Heart fields.
		self.heart_field_1 = pg.Rect(self.W1, C.N + 8*self.B + 2*self.A, 9*self.B, 3*self.B)
		self.heart_field_2 = pg.Rect(self.W2, C.N + 8*self.B + 2*self.A, 9*self.B, 3*self.B)

		# Next tetromino fields.
		self.next_tetromino_field_1 = pg.Rect(self.W1, C.N + 11*self.B + 3*self.A, 4*self.B, 4*self.B)
		self.next_tetromino_field_2 = pg.Rect(self.W2, C.N + 11*self.B + 3*self.A, 4*self.B, 4*self.B)

		# Tetris fields.
		self.tetris_field_1 = pg.Rect(self.W1 + 5*self.B, C.N + 11*self.B + 3*self.A, 4*self.B, 4*self.B)
		self.tetris_field_2 = pg.Rect(self.W2 + 5*self.B, C.N + 11*self.B + 3*self.A, 4*self.B, 4*self.B)

		# Stats field.
		self.stats_field = pg.Rect(self.W1 + 5*self.B, C.N + 11*self.B + 3*self.A, 4*self.B, 4*self.B)

		# Level fields.
		self.level_field_1 = pg.Rect(self.W1, C.N + 15*self.B + 4*self.A, 7*self.B, 3*self.B)
		self.level_field_2 = pg.Rect(self.W2, C.N + 15*self.B + 4*self.A, 7*self.B, 3*self.B)

		# Burn fields.
		self.burn_field_1 = pg.Rect(self.W1, C.N + 18*self.B + 5*self.A, 4*self.B, 4*self.B)
		self.burn_field_2 = pg.Rect(self.W2, C.N + 18*self.B + 5*self.A, 4*self.B, 4*self.B)

		# Drought fields.
		self.drought_field_1 = pg.Rect(self.W1 + 5*self.B, C.N + 18*self.B + 5*self.A, 4*self.B, 4*self.B)
		self.drought_field_2 = pg.Rect(self.W2 + 5*self.B, C.N + 18*self.B + 5*self.A, 4*self.B, 4*self.B)

		# Cover up fields.
		self.cover_up_field_1 = pg.Rect(C.BOARD_LEFT_2P1, C.BOARD_TOP, C.BOARD_WIDTH, C.BOARD_HEIGHT * (C.BOARD_INVIS_ROWS / (C.BOARD_INVIS_ROWS+C.BOARD_NROWS)) + 6)
		self.cover_up_field_2 = pg.Rect(C.BOARD_LEFT_2P2, C.BOARD_TOP, C.BOARD_WIDTH, C.BOARD_HEIGHT * (C.BOARD_INVIS_ROWS / (C.BOARD_INVIS_ROWS+C.BOARD_NROWS)) + 6)

		self.tetris_lead, self.pace_score_lead, self.pace_tetris_lead = C.compute_leads(self.score_difference, min(self.cur_level[0], self.cur_level[1]), self.line_counter)

		self.score_dif_matrix = [[f'+{self.score_difference:06d}', C.GREEN, f'+{self.tetris_lead:.2f}'],
								 [f'{self.score_difference:06d}', C.FC, f'{self.tetris_lead:.2f}'],
								 [f'-{-1*self.score_difference:06d}', C.RED, f'-{self.tetris_lead:.2f}'],
								 [f'-{self.score_difference:06d}', C.RED, f'-{self.tetris_lead:.2f}'],
								 [f'{self.score_difference:06d}', C.FC, f'{self.tetris_lead:.2f}'],
								 [f'+{-1*self.score_difference:06d}', C.GREEN, f'+{self.tetris_lead:.2f}']]

		sfx.play_start_game_sfx(self.commentary, self.commentary_volume)

	def update(self):
		with self.renderer:
			# Draw background pattern.
			self.renderer.draw_background_pattern(self.block_rect)

			if self.after_game_stats == False:
				# Draw previous board phase and the line clear animation.
				if self.line_clear_bool[0]:
					self.renderer.draw_board(self.previous_board_1, self.tetromino_1, self.cur_level[0], C.BBC)	
					self.renderer.draw_line_clear_animation(self.board_1, self.block_rect, self.framerate,
						C.BBC, self.rows[0], self.line_clear_timer[0])
				if self.line_clear_bool[1]:
					self.renderer.draw_board(self.previous_board_2, self.tetromino_2, self.cur_level[1], C.BBC)
					self.renderer.draw_line_clear_animation(self.board_2, self.block_rect, self.framerate,
						C.BBC, self.rows[1], self.line_clear_timer[1])

				# Draw the board (but not after a line clear).
				if self.line_clear_bool[0] == False and self.game_over[0] == False:
					self.renderer.draw_board(self.board_1, self.tetromino_1, self.cur_level[0], C.BBC)
				if self.line_clear_bool[1] == False and self.game_over[1] == False:
					self.renderer.draw_board(self.board_2, self.tetromino_2, self.cur_level[1], C.BBC)

				# Draw gridlines.
				if self.game_start == False:
					if self.gridline_boolean[0]:
						self.renderer.draw_gridlines(self.board_1, self.block_rect, C.BOARD_LEFT_2P1, C.BOARD_TOP, C.GRIDLINES_COLOUR)
					if self.gridline_boolean[1]:
						self.renderer.draw_gridlines(self.board_2, self.block_rect, C.BOARD_LEFT_2P2, C.BOARD_TOP, C.GRIDLINES_COLOUR)

				# Draw game over animation.
				if self.game_over[0]:
					self.renderer.draw_board(self.previous_board_1, self.tetromino_1, self.cur_level[0], C.BBC)	
					self.back_to_menu[0] = self.renderer.draw_game_over_animation(self.surface, self.board_1, self.block_rect,
						C.BBC, C.BBC, self.game_over_timer[0], self.score[0], self.game_over[1],
						self.mode, self.match_score, p1=True)
				if self.game_over[1]:
					self.renderer.draw_board(self.previous_board_2, self.tetromino_2, self.cur_level[1], C.BBC)	
					self.back_to_menu[1] = self.renderer.draw_game_over_animation(self.surface, self.board_2, self.block_rect, C.BBC, C.BBC, 
							self.game_over_timer[1], self.score[1], self.game_over[0], self.mode, self.match_score, p1=False)


				# Draw preview of the tetromino.
				if self.ARE_bool[0] == False and self.line_clear_bool[0] == False and self.game_over[0] == False and self.game_start == False:
					if self.preview_bool[0]:
						self.renderer.draw_preview_tetromino(self.preview_tetromino_1,
							Position(self.board_1.rect.x + self.preview_tetromino_1.x * self.block_rect.width,
											self.board_1.rect.y + self.preview_tetromino_1.y * self.block_rect.height),
											self.block_rect, self.cur_level[0])
					# Draw the next tetromino on the board.
					self.renderer.draw_tetromino(self.tetromino_1,
						Position(self.board_1.rect.x + self.tetromino_1.x * self.block_rect.width,
									self.board_1.rect.y + self.tetromino_1.y * self.block_rect.height),
									self.block_rect, self.cur_level[0])
				if self.ARE_bool[1] == False and self.line_clear_bool[1] == False and self.game_over[1] == False and self.game_start == False:
					if self.preview_bool[1]:
						self.renderer.draw_preview_tetromino(self.preview_tetromino_2,
							Position(self.board_2.rect.x + self.preview_tetromino_2.x * self.block_rect.width,
											self.board_2.rect.y + self.preview_tetromino_2.y * self.block_rect.height),
											self.block_rect, self.cur_level[1])
					# Draw the next tetromino on the board.
					self.renderer.draw_tetromino(self.tetromino_2,
						Position(self.board_2.rect.x + self.tetromino_2.x * self.block_rect.width,
									self.board_2.rect.y + self.tetromino_2.y * self.block_rect.height),
									self.block_rect, self.cur_level[1])

				# Draw pause screen.
				if self.game_pause:
					if self.game_over[0] == False: self.renderer.draw_pause_screen(self.board_1)
					if self.game_over[1] == False: self.renderer.draw_pause_screen(self.board_2)	

				# Draw cover ups.
				self.renderer.draw_rect(self.cover_up_field_1, C.SBC)
				self.renderer.draw_rect(self.cover_up_field_2, C.SBC)


				# Draw Board border.
				self.renderer.draw_board_borders(self.board_1, self.block_rect, C.P1BC)
				self.renderer.draw_board_borders(self.board_2, self.block_rect, C.P2BC)


				# Draw linescore field.
				self.renderer.draw_rect(self.lineboard_field_1, C.BBC)
				self.renderer.draw_borders(self.lineboard_field_1, C.P1BC)
				self.renderer.draw_changing_text('LINES - {:03d}'.format(self.line_counter[0]), self.lineboard_field_1, C.FC, C.BBC)
				self.renderer.draw_rect(self.lineboard_field_2, C.BBC)
				self.renderer.draw_borders(self.lineboard_field_2, C.P2BC)
				self.renderer.draw_changing_text('LINES - {:03d}'.format(self.line_counter[1]), self.lineboard_field_2,	C.FC, C.BBC)


				# Draw score field.
				self.renderer.draw_rect(self.score_field_1, C.BBC)
				self.renderer.draw_borders(self.score_field_1, C.P1BC)
				self.renderer.draw_changing_text(f'{self.score[0]:06d}', pg.Rect(self.W1, C.N, 9*self.B, 5*self.B), C.FC, C.BBC)

				if self.pace_switch == 0:
					self.renderer.draw_changing_text('SCORE', pg.Rect(self.W1, C.N, 9*self.B, 2*self.B), C.FC, C.BBC)
				elif self.pace_switch == 1:
					self.renderer.draw_changing_text(f'{self.pace_score_lead}', pg.Rect(self.W1, C.N, 9*self.B, 2*self.B), C.FC, C.BBC)
				elif self.pace_switch == 2:
					self.renderer.draw_changing_text(f'{self.pace_tetris_lead}', pg.Rect(self.W1, C.N, 9*self.B, 2*self.B), C.FC, C.BBC)

				if self.score_difference > 0: self.score_dif_idx = 0
				elif self.score_difference == 0: self.score_dif_idx = 1
				elif self.score_difference < 0: self.score_dif_idx = 2

				if self.score_switch:
					self.renderer.draw_changing_text(self.score_dif_matrix[self.score_dif_idx][0], pg.Rect(self.W1, C.N, 9*self.B, 8*self.B),
						self.score_dif_matrix[self.score_dif_idx][1], C.BBC)
				else:
					self.renderer.draw_changing_text(self.score_dif_matrix[self.score_dif_idx][2], pg.Rect(self.W1, C.N, 9*self.B, 8*self.B),
						self.score_dif_matrix[self.score_dif_idx][1], C.BBC)
			
				self.renderer.draw_rect(self.score_field_2, C.BBC)
				self.renderer.draw_borders(self.score_field_2, C.P2BC)
				self.renderer.draw_changing_text(f'{self.score[1]:06d}', pg.Rect(self.W2, C.N, 9*self.B, 5*self.B), C.FC, C.BBC)

				self.renderer.draw_changing_text('SCORE', pg.Rect(self.W2, C.N, 9*self.B, 2*self.B), C.FC, C.BBC)

				if self.score_difference > 0: self.score_dif_idx = 3
				elif self.score_difference == 0: self.score_dif_idx = 4
				elif self.score_difference < 0: self.score_dif_idx = 5

				if self.score_switch:
					self.renderer.draw_changing_text(self.score_dif_matrix[self.score_dif_idx][0], pg.Rect(self.W2, C.N, 9*self.B, 8*self.B),
						self.score_dif_matrix[self.score_dif_idx][1], C.BBC)
				else:
					self.renderer.draw_changing_text(self.score_dif_matrix[self.score_dif_idx][2], pg.Rect(self.W2, C.N, 9*self.B, 8*self.B),
						self.score_dif_matrix[self.score_dif_idx][1], C.BBC)


				# Draw tetris rate field.
				self.renderer.draw_rect(self.tetris_rate_field_1, C.BBC)
				self.renderer.draw_borders(self.tetris_rate_field_1, C.P1BC)
				self.renderer.draw_changing_text(f'TRT: {self.tetris_rate[0]:.1f}%', self.tetris_rate_field_1, C.FC, C.BBC)
				self.renderer.draw_rect(self.tetris_rate_field_2, C.BBC)
				self.renderer.draw_borders(self.tetris_rate_field_2, C.P2BC)
				self.renderer.draw_changing_text(f'TRT: {self.tetris_rate[1]:.1f}%', self.tetris_rate_field_2, C.FC, C.BBC)


				# Draw heart fields.
				if self.mode == 1:
					self.renderer.draw_rect(self.heart_field_1, C.BBC)
					self.renderer.draw_borders(self.heart_field_1, C.P1BC)
					self.renderer.draw_heart(self.surface, self.board_1, self.heart_field_1, self.B, self.B, self.match_score[0])
					self.renderer.draw_rect(self.heart_field_2, C.BBC)
					self.renderer.draw_borders(self.heart_field_2, C.P2BC)					
					self.renderer.draw_heart(self.surface, self.board_2, self.heart_field_2, self.B, self.B, self.match_score[1])


				# Draw next tetromino field.
				self.renderer.draw_rect(self.next_tetromino_field_1, C.BBC)
				self.renderer.draw_borders(self.next_tetromino_field_1, C.P1BC)
				self.renderer.draw_rect(self.next_tetromino_field_2, C.BBC)
				self.renderer.draw_borders(self.next_tetromino_field_2, C.P2BC)
				if self.game_start == False:
					self.renderer.draw_tetromino(self.next_tetromino_1, Position(self.W1 + 2*self.B, C.N + 12*self.B + 3*self.A),
						self.block_rect, self.cur_level[0], block_rect_width=self.B, block_rect_height=self.B)
					self.renderer.draw_tetromino(self.next_tetromino_2, Position(self.W2 + 2*self.B, C.N + 12*self.B + 3*self.A),
						self.block_rect, self.cur_level[0], block_rect_width=self.B, block_rect_height=self.B)


				# Draw tetris field.
				if self.game_over[0] == False or self.game_over[1] == False:
					self.renderer.draw_rect(self.tetris_field_1, C.BBC)
					self.renderer.draw_borders(self.tetris_field_1, C.P1BC)
					self.renderer.draw_changing_text('TRS',	
						pg.Rect(self.W1 + 5*self.B, C.N + 11*self.B + 3*self.A, 4*self.B, 2.5*self.B), C.FC, C.BBC) # -1.5 shift.
					self.renderer.draw_changing_text(f'{self.tetris_counter[0]}',
						pg.Rect(self.W1 + 5*self.B, C.N + 11*self.B + 3*self.A, 4*self.B, 5.5*self.B), C.FC, C.BBC) # + 1.5 shift.

				self.renderer.draw_rect(self.tetris_field_2, C.BBC)
				self.renderer.draw_borders(self.tetris_field_2, C.P2BC)
				self.renderer.draw_changing_text('TRS', 
						pg.Rect(self.W2 + 5*self.B, C.N + 11*self.B + 3*self.A, 4*self.B, 2.5*self.B), C.FC, C.BBC)
				self.renderer.draw_changing_text(f'{self.tetris_counter[1]}', 
					pg.Rect(self.W2 + 5*self.B, C.N + 11*self.B + 3*self.A, 4*self.B, 5.5*self.B), C.FC, C.BBC)


				# Draw stats field.
				if self.game_over[0] and self.game_over[1]:						
					self.renderer.draw_rect(self.stats_field, C.BBC)
					self.renderer.draw_borders(self.stats_field, C.P1BC)
					self.after_game_stats = self.renderer.draw_stats_button(self.surface, self.stats_field, self.B, self.B)


				# Draw level field.
				self.renderer.draw_rect(self.level_field_1, C.BBC)
				self.renderer.draw_borders(self.level_field_1, C.P1BC)
				self.renderer.draw_changing_text(f'LEVEL {self.cur_level[0]}', self.level_field_1, C.FC, C.BBC)
				self.renderer.draw_rect(self.level_field_2, C.BBC)
				self.renderer.draw_borders(self.level_field_2, C.P2BC)
				self.renderer.draw_changing_text(f'LEVEL {self.cur_level[1]}', self.level_field_2, C.FC, C.BBC)
				

				# Draw burn field.
				self.renderer.draw_rect(self.burn_field_1, C.BBC)
				self.renderer.draw_borders(self.burn_field_1, C.P1BC)
				self.renderer.draw_changing_text('BRN', pg.Rect(self.W1, C.N + 18*self.B + 5*self.A, 4*self.B, 2.5*self.B), C.FC, C.BBC)
				self.renderer.draw_changing_text(f'{self.burn_counter[0]}', 
					pg.Rect(self.W1, C.N + 18*self.B + 5*self.A, 4*self.B, 5.5*self.B),	C.FC, C.BBC)
				self.renderer.draw_rect(self.burn_field_2, C.BBC)
				self.renderer.draw_borders(self.burn_field_2, C.P2BC)
				self.renderer.draw_changing_text('BRN', pg.Rect(self.W2, C.N + 18*self.B + 5*self.A, 4*self.B, 2.5*self.B),	C.FC, C.BBC)
				self.renderer.draw_changing_text(f'{self.burn_counter[1]}', 
					pg.Rect(self.W2, C.N + 18*self.B + 5*self.A, 4*self.B, 5.5*self.B),	C.FC, C.BBC)

				# Draw drought fields
				if self.drought_counter[0] >= C.DROUGHT_BOUNDARY:
					self.renderer.draw_rect(self.drought_field_1, C.BBC)
					self.renderer.draw_borders(self.drought_field_1, C.P1BC)
					self.renderer.draw_tetromino(self.longbar, Position(self.W1 + 7*self.B, C.N + 20.5*self.B + 5*self.A), 
						self.block_rect_small, self.cur_level[0], block_rect_width=self.B/1.5, block_rect_height=self.B/1.5)
					self.renderer.draw_changing_text(f'{self.drought_counter[0]}',
						pg.Rect(self.W1 + 5*self.B, C.N + 18*self.B + 5*self.A, 4*self.B, 2.5*self.B), C.RED, C.BBC)

				if self.drought_counter[1] >= C.DROUGHT_BOUNDARY:
					self.renderer.draw_rect(self.drought_field_2, C.BBC)
					self.renderer.draw_borders(self.drought_field_2, C.P2BC)
					self.renderer.draw_tetromino(self.longbar, Position(self.W2 + 7*self.B, C.N + 20.5*self.B + 5*self.A), 
						self.block_rect_small, self.cur_level[0], block_rect_width=self.B/1.5, block_rect_height=self.B/1.5)
					self.renderer.draw_changing_text(f'{self.drought_counter[1]}',
						pg.Rect(self.W2 + 5*self.B, C.N + 18*self.B + 5*self.A, 4*self.B, 2.5*self.B), C.RED, C.BBC)

				# Start game animation and play sound effects.
				if self.game_start:
					countdown_1 = self.renderer.draw_start_game_animation(self.surface, self.board_1, self.block_rect, C.BBC, C.BBC, self.game_start_timer)
					countdown_2 = self.renderer.draw_start_game_animation(self.surface, self.board_2, self.block_rect, C.BBC, C.BBC, self.game_start_timer)

					if countdown_1 == False:
						self.fall_speed_timer[0] = 0
						self.fall_speed_timer[1] = 0
						self.game_start = False # Start game animation will only be executed once, when the game starts.

				

			elif self.after_game_stats == True and self.multiplayer:
				self.after_game_stats = self.renderer.draw_after_game_stats(self.surface, self.board_1, self.block_rect, self.multiplayer)

		# Entry/appearance delay.
		if self.ARE_bool[0] and self.line_clear_bool[0] == False:
			self.ARE_timer[0] += self.clock.get_rawtime()
		if self.ARE_bool[1] and self.line_clear_bool[1] == False:
			self.ARE_timer[1] += self.clock.get_rawtime()

		#print(self.fall_speed_timer, self.line_clear_timer)

		if self.line_clear_bool[0]:
			if self.line_clear_timer[0] < C.compute_milliseconds(self.framerate, C.LINE_CLEAR_DELAY):
				self.line_clear_timer[0] += self.clock.get_rawtime()
		if self.line_clear_bool[1]:
			if self.line_clear_timer[1] < C.compute_milliseconds(self.framerate, C.LINE_CLEAR_DELAY):
				self.line_clear_timer[1] += self.clock.get_rawtime()

		if self.game_over[0]:
			self.game_over_timer[0] += self.clock.get_rawtime()
		if self.game_over[1]:
			self.game_over_timer[1] += self.clock.get_rawtime()

		if self.game_start:
			self.game_start_timer += self.clock.get_rawtime()

		if self.game_pause:
			self.fall_speed_timer[0] = 0
			self.fall_speed_timer[1] = 0

		return self.handle_events()

	def handle_events(self):
		pressed = pg.key.get_pressed()

		self.clock.tick()
		self.fall_speed_timer[0] += self.clock.get_rawtime() # Time used in previous tick.
		self.fall_speed_timer[1] += self.clock.get_rawtime()

		if self.back_to_menu[0] or self.back_to_menu[1]:
			return False

		if self.ARE_bool[0] and self.ARE_timer[0] >= int(self.get_ARE_time(self.place_height[0])):
			self.fall_speed_timer[0] = 0
			self.vuvuzuela_timer += self.ARE_timer[0]
			self.ARE_timer[0] = 0
			self.ARE_bool[0] = False
			if pressed[self.p1_left] or pressed[self.p1_right]: 
				self.hold_key_timer[0] = C.compute_milliseconds(self.framerate, self.das_delay_frames - self.das_auto_repeat_frames)
			else: self.hold_key_timer[0] = 0

		if self.ARE_bool[1] and self.ARE_timer[1] >=  int(self.get_ARE_time(self.place_height[1])):
			self.fall_speed_timer[1] = 0
			self.vuvuzuela_timer += self.ARE_timer[1]
			self.ARE_timer[1] = 0
			self.ARE_bool[1] = False

			if pressed[self.p2_left] or pressed[self.p2_right]: 
				self.hold_key_timer[1] = C.compute_milliseconds(self.framerate, self.das_delay_frames - self.das_auto_repeat_frames)
			else: self.hold_key_timer[1] = 0

		if self.line_clear_bool[0] and self.line_clear_timer[0] > C.compute_milliseconds(self.framerate, C.LINE_CLEAR_DELAY):
			self.line_clear_timer[0] = 0
			self.line_clear_bool[0] = False
		if self.line_clear_bool[1] and self.line_clear_timer[1] > C.compute_milliseconds(self.framerate, C.LINE_CLEAR_DELAY):
			self.line_clear_timer[1] = 0
			self.line_clear_bool[1] = False

		self.preview_tetromino_1 = copy.deepcopy(self.tetromino_1)
		self.preview_tetromino_2 = copy.deepcopy(self.tetromino_2)
		while not self.board_1.check_tetromino_colission(self.preview_tetromino_1, Position(0, +1), 0):
			self.preview_tetromino_1.y += 1
		while not self.board_2.check_tetromino_colission(self.preview_tetromino_2, Position(0, +1), 0):
			self.preview_tetromino_2.y += 1

		# Make a block move down based on the time.
		if self.fall_speed_timer[0] > C.compute_milliseconds(self.framerate, self.velocity_array[self.cur_level[0]]) and self.game_start == False and self.ARE_bool[0] == False:
			if not self.board_1.check_tetromino_colission(self.tetromino_1, Position(0, +1), 0):
				#if self.repress[0] == True or (pressed[C.P1_UP] == False and pressed[self.p1_down] == False):
				if self.repress[0] == True or pressed[self.p1_down] == False:
					self.tetromino_1.y += 1
					self.fall_speed_timer[0] = 0
			elif self.game_over[0] == False:
				self.get_next_tetromino(0)
		if self.fall_speed_timer[1] > C.compute_milliseconds(self.framerate, self.velocity_array[self.cur_level[1]]) and self.game_start == False and self.ARE_bool[1] == False:
			if not self.board_2.check_tetromino_colission(self.tetromino_2, Position(0, +1), 0):
				#if self.repress[1] == True or (pressed[C.P2_UP] == False and pressed[self.p2_down] == False):
				if self.repress[1] == True or pressed[self.p2_down] == False:
					self.tetromino_2.y += 1
					self.fall_speed_timer[1] = 0
			elif self.game_over[1] == False:
				self.get_next_tetromino(1)	

		if pressed[self.p1_left] or pressed[self.p1_right] or pressed[self.p1_down] and (self.game_start == False and self.game_pause == False):# or pressed[C.P11_UP]:
			self.hold_key_timer[0] += self.clock.get_rawtime() # Time used in previous tick.

			# Movement.
			if pressed[self.p1_left] and not self.board_1.check_tetromino_colission(self.tetromino_1, Position(-1, 0), 0) and self.ARE_bool[0] == False:				
				if self.hold_key_timer[0] > C.compute_milliseconds(self.framerate, self.das_delay_frames):
					self.tetromino_1.x -= 1
					C.SFX_MOVE.play()
					self.hold_key_timer[0] = C.compute_milliseconds(self.framerate, self.das_delay_frames - self.das_auto_repeat_frames)
			if pressed[self.p1_right] and not self.board_1.check_tetromino_colission(self.tetromino_1, Position(+1, 0), 0) and self.ARE_bool[0] == False:
				if self.hold_key_timer[0] > C.compute_milliseconds(self.framerate, self.das_delay_frames):
					self.tetromino_1.x += 1
					C.SFX_MOVE.play()
					self.hold_key_timer[0] = C.compute_milliseconds(self.framerate, self.das_delay_frames - self.das_auto_repeat_frames)
			if self.repress[0] == False and pressed[self.p1_down] and self.ARE_bool[0] == False:
				if not self.board_1.check_tetromino_colission(self.tetromino_1, Position(0, +1), 0):
					#if self.hold_key_timer[0] > C.compute_milliseconds(self.framerate, C.DROPPING_SPEED * self.velocity_array[self.cur_level[0]]):
					if self.hold_key_timer[0] > C.compute_milliseconds(self.framerate, self.velocity_array[19]):	
						self.tetromino_1.y += 1
						self.soft_drop_counter[0] += C.SOFT_DROP_POINTS_PER_LINE
						self.hold_key_timer[0] = 0
				else:
					self.fall_speed_timer[0] = C.compute_milliseconds(self.framerate, self.velocity_array[self.cur_level[0]])
			#if pressed[C.P1_UP] and not self.board_1.check_tetromino_colission(self.tetromino_1, Position(0, -1), 0) and self.game_start == False:
			#	if self.hold_key_timer[0] > C.compute_milliseconds(self.framerate, self.velocity_array[19]):
			#		self.tetromino_1.y -= 1
			#		self.hold_key_timer[0] = 0

		if pressed[self.p2_left] or pressed[self.p2_right] or pressed[self.p2_down] and (self.game_start == False and self.game_pause == False):# or pressed[C.P12_UP]:
			self.hold_key_timer[1] += self.clock.get_rawtime() # Time used in previous tick.

			# Movement.
			if pressed[self.p2_left] and not self.board_2.check_tetromino_colission(self.tetromino_2, Position(-1, 0), 0) and self.ARE_bool[1] == False:				
				if self.hold_key_timer[1] > C.compute_milliseconds(self.framerate, self.das_delay_frames):
					self.tetromino_2.x -= 1
					C.SFX_MOVE.play()
					self.hold_key_timer[1] = C.compute_milliseconds(self.framerate, self.das_delay_frames - self.das_auto_repeat_frames)
			if pressed[self.p2_right] and not self.board_2.check_tetromino_colission(self.tetromino_2, Position(+1, 0), 0) and self.ARE_bool[1] == False:
				if self.hold_key_timer[1] > C.compute_milliseconds(self.framerate, self.das_delay_frames):
					self.tetromino_2.x += 1
					C.SFX_MOVE.play()
					self.hold_key_timer[1] = C.compute_milliseconds(self.framerate, self.das_delay_frames - self.das_auto_repeat_frames)
			if self.repress[1] == False and pressed[self.p2_down] and self.ARE_bool[1] == False:
				if not self.board_2.check_tetromino_colission(self.tetromino_2, Position(0, +1), 0):
					#if self.hold_key_timer[1] > C.compute_milliseconds(self.framerate, C.DROPPING_SPEED * self.velocity_array[self.cur_level[1]]):
					if self.hold_key_timer[1] > C.compute_milliseconds(self.framerate, self.velocity_array[19]):	
						self.tetromino_2.y += 1
						self.soft_drop_counter[1] += C.SOFT_DROP_POINTS_PER_LINE
						self.hold_key_timer[1] = 0
				else:
					self.fall_speed_timer[1] = C.compute_milliseconds(self.framerate, self.velocity_array[self.cur_level[1]])
			#if pressed[C.P2_UP] and not self.board_2.check_tetromino_colission(self.tetromino_2, Position(0, -1), 0) and self.game_start == False:
			#	if self.hold_key_timer[1] > C.compute_milliseconds(self.framerate, self.velocity_array[19]):
			#		self.tetromino_2.y -= 1
			#		self.hold_key_timer[1] = 0

		for ev in pg.event.get():
			if ev.type == pg.QUIT or (ev.type == pg.KEYDOWN and ev.key == pg.K_ESCAPE):
				pg.mouse.set_visible(True)
				return False

			if ev.type == pg.KEYUP:
				if ev.key == self.p1_left or ev.key == self.p1_right:
					self.hold_key_timer[0] = 0
				if ev.key == self.p2_left or ev.key == self.p2_right:
					self.hold_key_timer[1] = 0
				if ev.key == self.p1_down:
					self.soft_drop_counter[0] = 0 # If the dropping key is released, no points are giving for soft dropping.
					self.fall_speed_timer[0] = 0
					self.hold_key_timer[0] = 0
				if ev.key == self.p2_down:
					self.soft_drop_counter[1] = 0
					self.fall_speed_timer[1] = 0
					self.hold_key_timer[1] = 0
				if ev.key == self.p1_space and self.hard_drop_bool:
					self.hard_drop_counter[0] = 0
				if ev.key == self.p2_space and self.hard_drop_bool:
					self.hard_drop_counter[1] = 0
				self.repress[0] = False
				self.repress[1] = False
				
			if ev.type == pg.KEYDOWN:
				# Side movement.
				if ev.key == self.p1_right and not self.board_1.check_tetromino_colission(self.tetromino_1, Position(+1, 0), 0) and self.game_start == False and self.game_pause == False and self.ARE_bool[0] == False:
					self.tetromino_1.x += 1
					C.SFX_MOVE.play()
				if ev.key == self.p1_left and not self.board_1.check_tetromino_colission(self.tetromino_1, Position(-1, 0), 0) and self.game_start == False and self.game_pause == False and self.ARE_bool[0] == False:
					self.tetromino_1.x -= 1
					C.SFX_MOVE.play()
				if ev.key == self.p2_right and not self.board_2.check_tetromino_colission(self.tetromino_2, Position(+1, 0), 0) and self.game_start == False and self.game_pause == False and self.ARE_bool[1] == False:
					self.tetromino_2.x += 1
					C.SFX_MOVE.play()
				if ev.key == self.p2_left and not self.board_2.check_tetromino_colission(self.tetromino_2, Position(-1, 0), 0) and self.game_start == False and self.game_pause == False and self.ARE_bool[1] == False:
					self.tetromino_2.x -= 1
					C.SFX_MOVE.play()

				# Rotation.
				if ev.key == self.p1_a and not self.board_1.check_tetromino_colission(self.tetromino_1, Position(0, 0), +1) and self.game_start == False and self.game_pause == False and self.ARE_bool[0] == False:
					self.tetromino_1.rotate(+1)
					C.SFX_ROTATION.play()
				if ev.key == self.p1_b  and not self.board_1.check_tetromino_colission(self.tetromino_1, Position(0, 0), -1) and self.game_start == False and self.game_pause == False and self.ARE_bool[0] == False:
					self.tetromino_1.rotate(-1)
					C.SFX_ROTATION.play()
				if ev.key == self.p2_a and not self.board_2.check_tetromino_colission(self.tetromino_2, Position(0, 0), +1) and self.game_start == False and self.game_pause == False and self.ARE_bool[1] == False:
					self.tetromino_2.rotate(+1)
					C.SFX_ROTATION.play()
				if ev.key == self.p2_b  and not self.board_2.check_tetromino_colission(self.tetromino_2, Position(0, 0), -1) and self.game_start == False and self.game_pause == False and self.ARE_bool[1] == False:
					self.tetromino_2.rotate(-1)
					C.SFX_ROTATION.play()

				# Hard-drop.
				if ev.key == self.p1_space and self.hard_drop_bool and self.game_start == False and self.game_pause == False:
					#pg.key.set_repeat()
					while not self.board_1.check_tetromino_colission(self.tetromino_1, Position(0, +1), 0):
						self.hard_drop_counter[0] += C.HARD_DROP_POINTS_PER_LINE
						self.tetromino_1.y += 1
					if self.game_over[0] == False:
						self.get_next_tetromino(0)
				if ev.key == self.p2_space and self.hard_drop_bool and self.game_start == False and self.game_pause == False:
					#pg.key.set_repeat()
					while not self.board_2.check_tetromino_colission(self.tetromino_2, Position(0, +1), 0):
						self.hard_drop_counter[1] += C.HARD_DROP_POINTS_PER_LINE
						self.tetromino_2.y += 1
					if self.game_over[1] == False:
						self.get_next_tetromino(1)

				if ev.key == pg.K_g:
					if self.gridline_boolean[0]: self.gridline_boolean[0] = False
					else: self.gridline_boolean[0] = True
				if ev.key == pg.K_h:
					if self.preview_bool[0]: self.preview_bool[0] = False
					else: self.preview_bool[0] = True
				if ev.key == pg.K_j:
					if self.gridline_boolean[1]: self.gridline_boolean[1] = False
					else: self.gridline_boolean[1] = True
				if ev.key == pg.K_k:
					if self.preview_bool[1]: self.preview_bool[1] = False
					else: self.preview_bool[1] = True

				# Switch score display between points difference and Tetris difference.
				if ev.key == pg.K_t:
					if self.score_switch == True: self.score_switch = False
					elif self.score_switch == False: self.score_switch = True

				if ev.key == pg.K_r:
					self.pace_switch += 1
					self.pace_switch %= 3

				if ev.key == pg.K_y and self.game_start == False:
					if self.game_pause == False:
						self.game_pause = True
						C.SFX_PAUSE.play()
					else: self.game_pause = False

		if self.commentary == 6:
			self.vuvuzuela_timer += self.clock.get_rawtime()
			if self.vuvuzuela_timer >= 4.8e3:
				sfx.play_neutral_sfx(self.commentary, self.commentary_volume)
				self.vuvuzuela_timer = 0

		if self.back_to_menu[0] == False or self.back_to_menu[1] == False:
			pg.mouse.set_visible(False)
			if self.game_over[0] == False: self.get_next_tetromino(0)
			if self.game_over[1] == False: self.get_next_tetromino(1)
			self.board_1.empty_board()
			self.board_2.empty_board()
			self.fall_speed_timer = [0, 0]
			self.drought_counter = [0, 0]
			self.no_longbar_arr = [[],[]]
			self.hold_key_timer = [0, 0]
			self.soft_drop_counter = [0, 0]
			self.hard_drop_counter = [0, 0]
			self.line_counter = [C.START_LINES, C.START_LINES]
			self.single_counter = [0, 0]
			self.double_counter = [0, 0]
			self.triple_counter = [0, 0]
			self.tetris_counter = [0, 0]
			self.single_score = [0, 0]
			self.double_score = [0, 0]
			self.triple_score = [0, 0]
			self.tetris_score = [0, 0]
			self.tetris_rate = [0, 0]
			self.tetris_rate_arr = [[],[]]
			self.burn_counter = [0, 0]
			self.cur_level = [self.start_level, self.start_level]
			self.not_leveled_yet = [True, True]
			self.score = [C.START_SCORE, C.START_SCORE]
			self.score_arr = [[],[]]
			self.score_difference = self.score[0] - self.score[1]
			self.score_difference_arr = []
			self.tetris_lead, self.pace_score_lead, self.pace_tetris_lead = C.compute_leads(self.score_difference, min(self.cur_level[0], self.cur_level[1]), self.line_counter)

			self.score_dif_matrix = [[f'+{self.score_difference:06d}', C.GREEN, f'+{self.tetris_lead:.2f}'],
								 [f'{self.score_difference:06d}', C.FC, f'{self.tetris_lead:.2f}'],
								 [f'-{-1*self.score_difference:06d}', C.RED, f'-{self.tetris_lead:.2f}'],
								 [f'-{self.score_difference:06d}', C.RED, f'-{self.tetris_lead:.2f}'],
								 [f'{self.score_difference:06d}', C.FC, f'{self.tetris_lead:.2f}'],
								 [f'+{-1*self.score_difference:06d}', C.GREEN, f'+{self.tetris_lead:.2f}']]

			#self.highscore = self.check_highscores(score=0, return_topscore=True)
			self.repress = [False, False]
			self.ARE_bool = [False, False]
			self.ARE_timer = [0, 0]
			self.line_clear_bool = [False, False]
			self.line_clear_timer = [0, 0]
			self.place_height = [C.BOARD_NROWS - C.BOARD_INVIS_ROWS, C.BOARD_NROWS - C.BOARD_INVIS_ROWS]
			self.rows = [[],[]]
			self.block_counter = [1, 1]
			if self.same_piecesets:
				self.seed = self.block_counter[0] * C.SEED
				self.seed_2 = rd.randint(1, 1e6)
				self.seed -= self.seed_2
			else:
				self.seed = None
			self.game_over = [False, False]
			self.game_start = True
			self.game_start_timer = 0
			self.game_over_timer = [0, 0]
			self.back_to_menu = [None, None]
			self.dif_block_counter = [np.zeros(len(C.BLOCKS)), np.zeros(len(C.BLOCKS))]
			self.cur_velocity = [self.start_velocity, self.start_velocity]
			self.preview_tetromino_1 = copy.deepcopy(self.tetromino_1)
			self.preview_tetromino_2 = copy.deepcopy(self.tetromino_2)
			self.multiplayer = True
			self.vuvuzuela_timer = 10e3
			self.game_pause = False
			self.neutral_sfx_prob = 0
			self.tetris_ready_prob_1 = 0
			self.tetris_ready_prob_2 = 0
			self.neck_and_neck_prob = 0
			if self.match_score[0] == 3 or self.match_score[1] == 3:
				self.match_score = [0, 0]

			sfx.play_start_game_sfx(self.commentary, self.commentary_volume)

		return self.music_queue

	def get_ARE_time(self, place_height):
		ARE_delay = C.ARE_DELAY

		# ARE delay depends on place height according to the following step function.
		if place_height > 6: ARE_delay -= 2
		if place_height > 10: ARE_delay -= 2
		if place_height > 14: ARE_delay -= 2
		if place_height > 18: ARE_delay -= 2
		
		return C.compute_milliseconds(self.framerate, ARE_delay)

	def check_winner(self, score):
		if score[0] > score[1]: self.match_score[0] += 1
		elif score[1] > score[0]: self.match_score[1] += 1
		elif score[0] == score[1]: pass


	"""
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
	"""

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

	def get_next_tetromino(self, i):
		if i == 0:
			# Place a tetromino on the board and obtain place height, which is used for entry delay.
			self.place_height[i] = self.board_1.place_tetromino(self.tetromino_1)

			# Check if the player is game over.
			self.game_over[i] = self.board_1.check_game_over()

			# Check if the player is tetris ready.
			self.tetris_ready[i] = self.board_1.check_tetris_ready()

			# Check if the music has stopped and load a new track from the queue.
			self.check_music_queue()

			if self.same_piecesets: self.seed = self.block_counter[0] * C.SEED - self.seed_2

		if i == 1:
			self.place_height[i] = self.board_2.place_tetromino(self.tetromino_2)
			self.game_over[i] = self.board_2.check_game_over()
			self.tetris_ready[i] = self.board_2.check_tetris_ready()
		
			self.check_music_queue()

			if self.same_piecesets: self.seed = self.block_counter[1] * C.SEED - self.seed_2;

		# Actions taken if the player is game over.
		if self.game_over[i]:
			sfx.play_game_over_sfx(self.commentary, self.commentary_volume) # Play game over sound effect based on the commentary type.
			#self.check_highscores(self.score[0]) # Check and update highscores.

		if self.game_over[0] and self.game_over[1]:
			pg.mouse.set_visible(True)

			# Check who won in best of five mode.
			if self.mode == 1:
				self.check_winner(self.score)

			# Generate after-game statistics.
			stats.generate_after_game_stats(self.block_counter[0]-1, self.no_longbar_arr, self.tetris_rate_arr, self.score_arr,
				self.dif_block_counter, [[self.single_counter[0], self.double_counter[0], self.triple_counter[0], self.tetris_counter[0]],
				[self.single_counter[1], self.double_counter[1], self.triple_counter[1], self.tetris_counter[1]]], [[self.single_score[0], 
				self.double_score[0], self.triple_score[0], self.tetris_score[0]], [self.single_score[1], self.double_score[1],
				self.triple_score[1], self.tetris_score[1]]], self.score_difference_arr)

		if i == 0:
			self.previous_board_1 = copy.deepcopy(self.board_1)

			# Remove lines from the board and update parameters.
			line_counter_add_1, score_add_1, self.line_clear_bool[i], self.rows[i], single_add_1, double_add_1, triple_add_1, tetris_add_1 = self.board_1.remove_completed_lines(self.cur_level[i],
				self.line_clear_bool[i], self.line_counter[i], self.commentary, self.commentary_volume)
		
			# After lines have been cleared, check if the players needs to level up.
			if self.not_leveled_yet[i] == False and int((self.line_counter[i] + line_counter_add_1)/10) > int(self.line_counter[i]/10):
				self.cur_level[i] += 1
				sfx.play_level_up_sfx()

			# Update block counter, different block counter, score, line counter, burn counter and tetris counter.
			self.block_counter[0] += 1
			self.dif_block_counter[0][self.tetromino_1.type] += 1
			self.score[0] += score_add_1
			self.score[0] += self.soft_drop_counter[0]
			self.score[0] += self.hard_drop_counter[0]
			self.score_arr[0].append(self.score[0])
			self.score_difference = self.score[0] - self.score[1]
			self.score_difference_arr.append(self.score_difference)
			self.tetris_lead, self.pace_score_lead, self.pace_tetris_lead = C.compute_leads(self.score_difference, min(self.cur_level[0], self.cur_level[1]), self.line_counter)
			self.score_dif_matrix = [[f'+{self.score_difference:06d}', C.GREEN, f'+{self.tetris_lead:.2f}'],
								 [f'{self.score_difference:06d}', C.FC, f'{self.tetris_lead:.2f}'],
								 [f'-{-1*self.score_difference:06d}', C.RED, f'-{self.tetris_lead:.2f}'],
								 [f'-{self.score_difference:06d}', C.RED, f'-{self.tetris_lead:.2f}'],
								 [f'{self.score_difference:06d}', C.FC, f'{self.tetris_lead:.2f}'],
								 [f'+{-1*self.score_difference:06d}', C.GREEN, f'+{self.tetris_lead:.2f}']]

			self.line_counter[0] += line_counter_add_1
			self.burn_counter[0] += line_counter_add_1
			self.drought_counter[0] += 1

			if single_add_1 != 0: self.single_counter[0] += single_add_1; self.single_score[0] += score_add_1
			elif double_add_1 != 0: self.double_counter[0] += double_add_1; self.double_score[0] += score_add_1
			elif triple_add_1 != 0: self.triple_counter[0] += triple_add_1; self.triple_score[0] += score_add_1
			elif tetris_add_1 != 0:
				self.tetris_counter[0] += tetris_add_1; self.tetris_score[0] += score_add_1
				self.tetris_ready_prob_1 = 0

			# Clear burn counter when a tetris is scored; clear no longbar counter when the player gets a longbar.
			if tetris_add_1 != 0: self.burn_counter[0] = 0
			if C.BLOCKS.index(C.LONGBAR) == self.tetromino_1.type: self.drought_counter[0] = 0

			# Computation of the tetris rate.
			if self.line_counter[0] == 0: self.tetris_rate[0] = 0
			else: self.tetris_rate[0] = 4 * self.tetris_counter[0] / float(self.line_counter[0]) * 100
			self.tetris_rate_arr[0].append(self.tetris_rate[0])

			# Add variables to array for the after-game statistics.		
			self.no_longbar_arr[0].append(self.drought_counter[0])

			# Level up for the first time.
			if self.not_leveled_yet[0] == True and self.line_counter[0] >= self.first_level_up:
				self.cur_level[0] += 1
				sfx.play_level_up_sfx()
				self.not_leveled_yet[0] = False

			# Adjust tetromino falling velocity based on the current level.
			self.cur_velocity[0] = self.velocity_array[self.cur_level[0]]

			# Obtain tetromino's
			self.tetromino_1 = self.next_tetromino_1
			self.next_tetromino_1 = Tetromino.Tetromino(self.board_1.dimensions.width // 2, 0 + C.BOARD_INVIS_ROWS, self.block_counter[0], self.tetromino_1, self.seed)

			# Neutral sound effects.
			if self.commentary != 6:
				self.neutral_sfx_prob = sfx.play_neutral_sfx(self.commentary, self.commentary_volume, self.neutral_sfx_prob, self.tetromino_1.type, self.seed, self.multiplayer)
			if self.commentary < 5 and self.tetris_lead <= 1 and self.score[0] > C.TETRIS_POINTS * (self.start_level + 1) and self.score[1] > C.TETRIS_POINTS * (self.start_level + 1):
				self.neck_and_neck_prob = sfx.play_neck_and_neck_sfx(self.commentary, self.commentary_volume, self.neck_and_neck_prob, self.seed)

			# Actions taken if player is tetris ready.
			if self.tetris_ready[i]:
				self.tetris_ready_prob_1 = sfx.play_tetris_ready_sfx(self.commentary, self.commentary_volume, self.tetris_ready_prob_1, self.tetromino_1.type)
			
			# Reset timers and booleans.
			self.fall_speed_timer[0] = 0
			self.repress[0] = True
			self.ARE_bool[0] = True

		if i == 1:
			self.previous_board_2 = copy.deepcopy(self.board_2)
			line_counter_add_2, score_add_2, self.line_clear_bool[i], self.rows[i], single_add_2, double_add_2, triple_add_2, tetris_add_2 = self.board_2.remove_completed_lines(self.cur_level[i],
				self.line_clear_bool[i], self.line_counter[i], self.commentary, self.commentary_volume)
			if self.not_leveled_yet[i] == False and int((self.line_counter[i] + line_counter_add_2)/10) > int(self.line_counter[i]/10):
				self.cur_level[i] += 1
				sfx.play_level_up_sfx()
		
			self.block_counter[1] += 1
			self.dif_block_counter[1][self.tetromino_2.type] += 1
			self.score[1] += score_add_2
			self.score[1] += self.soft_drop_counter[1]
			self.score[1] += self.hard_drop_counter[1]
			self.score_arr[1].append(self.score[1])
			self.score_difference = self.score[0] - self.score[1]
			self.score_difference_arr.append(self.score_difference)
			self.tetris_lead, self.pace_score_lead, self.pace_tetris_lead = C.compute_leads(self.score_difference, min(self.cur_level[0], self.cur_level[1]), self.line_counter)
			self.score_dif_matrix = [[f'+{self.score_difference:06d}', C.GREEN, f'+{self.tetris_lead:.2f}'],
								 [f'{self.score_difference:06d}', C.FC, f'{self.tetris_lead:.2f}'],
								 [f'-{-1*self.score_difference:06d}', C.RED, f'-{self.tetris_lead:.2f}'],
								 [f'-{self.score_difference:06d}', C.RED, f'-{self.tetris_lead:.2f}'],
								 [f'{self.score_difference:06d}', C.FC, f'{self.tetris_lead:.2f}'],
								 [f'+{-1*self.score_difference:06d}', C.GREEN, f'+{self.tetris_lead:.2f}']]
								 
			self.line_counter[1] += line_counter_add_2
			self.burn_counter[1] += line_counter_add_2
			self.drought_counter[1] += 1

			if single_add_2 != 0: self.single_counter[1] += single_add_2; self.single_score[1] += score_add_2
			elif double_add_2 != 0: self.double_counter[1] += double_add_2; self.double_score[1] += score_add_2
			elif triple_add_2 != 0: self.triple_counter[1] += triple_add_2; self.triple_score[1] += score_add_2
			elif tetris_add_2 != 0:
				self.tetris_counter[1] += tetris_add_2; self.tetris_score[1] += score_add_2
				self.tetris_ready_prob_2 = 0

			if tetris_add_2 != 0: self.burn_counter[1] = 0
			if C.BLOCKS.index(C.LONGBAR) == self.tetromino_2.type: self.drought_counter[1] = 0

			if self.line_counter[1] == 0: self.tetris_rate[1] = 0
			else: self.tetris_rate[1] = 4 * self.tetris_counter[1] / float(self.line_counter[1]) * 100
			self.tetris_rate_arr[1].append(self.tetris_rate[1])

			# Add variables to array for the after-game statistics.		
			self.no_longbar_arr[1].append(self.drought_counter[1])

			if self.not_leveled_yet[1] == True and self.line_counter[1] >= self.first_level_up:
				self.cur_level[1] += 1
				sfx.play_level_up_sfx()
				self.not_leveled_yet[1] = False

			self.cur_velocity[1] = self.velocity_array[self.cur_level[1]]

			# Obtain tetromino's
			self.tetromino_2 = self.next_tetromino_2
			self.next_tetromino_2 = Tetromino.Tetromino(self.board_2.dimensions.width // 2, 0 + C.BOARD_INVIS_ROWS, self.block_counter[1], self.tetromino_2, self.seed)
			
			# Neutral sound effects.
			if self.commentary != 6:
				self.neutral_sfx_prob = sfx.play_neutral_sfx(self.commentary, self.commentary_volume, self.neutral_sfx_prob, self.tetromino_2.type, self.seed, self.multiplayer)
			if self.commentary < 5 and self.tetris_lead <= 1 and self.score[0] > C.TETRIS_POINTS * (self.start_level + 1) and self.score[1] > C.TETRIS_POINTS * (self.start_level + 1):
				self.neck_and_neck_prob = sfx.play_neck_and_neck_sfx(self.commentary, self.commentary_volume, self.neck_and_neck_prob, self.seed)


			# Actions taken if player is tetris ready.
			if self.tetris_ready[i]:
				self.tetris_ready_prob_2 = sfx.play_tetris_ready_sfx(self.commentary, self.commentary_volume, self.tetris_ready_prob_2, self.tetromino_2.type)
			


			# Reset timers and booleans.
			self.fall_speed_timer[1] = 0
			self.repress[1] = True
			self.ARE_bool[1] = True