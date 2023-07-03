import pygame as pg
import random as rd
import itertools
from collections import namedtuple
import constants_parameters as C
import sfx
import os
import numpy as np

Position = namedtuple('Position', 'x y')

class Board(object):
	def __init__(self, dimensions, rect):
		self.dimensions = dimensions # Initialize board dimensions.
		self.rect = rect
		self.blocks = [[0] * self.dimensions.width
						for y in range(self.dimensions.height)]

	def __iter__(self):
		return itertools.product(range(self.dimensions.width),
			range(self.dimensions.height))

	def empty_board(self):
		self.blocks = [[0] * self.dimensions.width
						for y in range(self.dimensions.height)]

	def check_tetromino_colission(self, tetromino, offset, rotation):
		for block in tetromino.get_blocks(rotation):
			pos = Position(tetromino.x + block.x + offset.x,
							tetromino.y + block.y + offset.y)

			if (
				pos.x < 0 or pos.x >= self.dimensions.width or
				pos.y >= self.dimensions.height or pos.y < 0
			):
				return True

			if self.blocks[pos.y][pos.x] != 0:
				return True

	def compute_heights_array(self) -> list:
		highest_locations = []
		for col_idx in range(len(self.blocks[0])):
			highest_location = 0
			for row_idx in range(len(self.blocks)):
				if self.blocks[row_idx][col_idx] > 0:
					highest_location = C.BOARD_NROWS - row_idx
					break

			highest_locations.append(highest_location)

		return highest_locations

	def search_for_gaps(self) -> int:
		number_of_gaps = 0

		for col_idx in range(len(self.blocks[0])):
			for row_idx in range(len(self.blocks)):
				if self.blocks[row_idx][col_idx] > 0:
					remaining_rows = [row[col_idx] for row in self.blocks[row_idx:]]
					# Count the number of zero's/gaps in the rows.
					number_of_gaps += remaining_rows.count(0)
					break

		return number_of_gaps



	def check_game_over(self):
		if self.blocks[2][4] != 0 or self.blocks[2][5] != 0:
			return True
		else:
			return False

	def check_tetris_ready(self):
		numpy_blocks = np.array(self.blocks)
		area_1 = numpy_blocks[-4:,:C.BOARD_NCOLUMNS-1]
		area_2 = numpy_blocks[-4:,-1]
		area_3 = numpy_blocks[0:-4,-1]

		if np.count_nonzero(area_2) == 0 and np.count_nonzero(area_3) == 0 and np.count_nonzero(area_1) == len(area_1) * len(area_1[0]):
			return True
		else:
			return False

	def place_tetromino(self, tetromino):
		for block in tetromino:
			if tetromino.type in (C.BLOCKS.index(C.LONGBAR), C.BLOCKS.index(C.SQUARE), C.BLOCKS.index(C.T_BLOCK)):
				self.blocks[tetromino.y + block.y][tetromino.x + block.x] = 1
			if tetromino.type in (C.BLOCKS.index(C.REVERSE_L_BLOCK), C.BLOCKS.index(C.REVERSE_SQUIGGLY)):
				self.blocks[tetromino.y + block.y][tetromino.x + block.x] = 2
			if tetromino.type in (C.BLOCKS.index(C.L_BLOCK), C.BLOCKS.index(C.SQUIGGLY)):
				self.blocks[tetromino.y + block.y][tetromino.x + block.x] = 3

		#C.SFX_LAND_BLOCK.play()
		
		return tetromino.y

	def level_multiplier(self, score, level):
		return score * (level + 1)

	def compute_score(self, lines, level, commentary, volume):
		if lines == 0: return 0
		elif lines == 1: 
			C.SFX_LINE_CLEAR.play()
			return self.level_multiplier(C.SINGLE_POINTS, level)
		elif lines == 2:
			C.SFX_LINE_CLEAR.play()
			return self.level_multiplier(C.DOUBLE_POINTS, level)
		elif lines == 3:
			C.SFX_LINE_CLEAR.play()
			return self.level_multiplier(C.TRIPLE_POINTS, level)
		elif lines == 4:
			sfx.play_tetris_sfx(commentary, volume)
			return self.level_multiplier(C.TETRIS_POINTS, level)

	def remove_completed_lines(self, level, line_clear_bool, line_counter, commentary, volume):
		line_counter_add = 0
		rows = []
		single, double, triple, tetris = 0, 0, 0, 0

		for index, row in enumerate(self.blocks[:]):
			if not 0 in row:
				self.blocks.remove(row)
				line_clear_bool = True
				self.blocks.insert(0, [0] * self.dimensions.width)
				line_counter_add += 1
				rows.append(index)

		if line_counter_add == 1: single = 1
		elif line_counter_add == 2: double = 1
		elif line_counter_add == 3: triple = 1
		elif line_counter_add == 4: tetris = 1
				
		#print(level, line_counter, line_counter_add, int((line_counter + line_counter_add)/10), int(line_counter/10))
		
		if int((line_counter + line_counter_add)/10) > int(line_counter/10):
			score = self.compute_score(line_counter_add, level+1, commentary, volume)
		else:
			score = self.compute_score(line_counter_add, level, commentary, volume)

		return line_counter_add, score, line_clear_bool, rows, single, double, triple, tetris