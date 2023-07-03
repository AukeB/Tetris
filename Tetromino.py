import pygame as pg
import random as rd
import numpy as np
from collections import namedtuple
import constants_parameters as C
import copy


Block = namedtuple('Block', 'x y val')

class Tetromino(object):
	def __init__(self, x, y, block_counter, prev_tetromino, seed=None):
		self.x = x
		self.y = y
		self.type = self.random_generator(block_counter, prev_tetromino, seed)
		#self.max_num_gen = 700
		#self.h = self.max_num_gen / C.N_BLOCKS
		#self.biased_boundaries = [87*1, 87.5*2, 87.5*4, 87*5, 87.5*6, 87*7, 87.5*8]
		#self.type = self.biased_generator()
		self.blocks = C.BLOCKS[self.type]

	def __iter__(self):
		return iter(self.blocks)

	def random_generator(self, block_counter, prev_tetromino, seed):
		if block_counter == 1:
			if seed != None: rd.seed(seed)
			return rd.randint(0, C.N_BLOCKS - 1)
		else:
			prev_roll = prev_tetromino.type
			if seed != None: rd.seed(seed)
			roll = rd.randint(0, C.N_BLOCKS)
			if roll == C.N_BLOCKS or roll == prev_roll:
				roll = rd.randint(0, C.N_BLOCKS - 1)
				return roll
			else:
				return roll

	def biased_generator(self):
		random_number = np.random.randint(0, self.max_num_gen)

		def random_number2roll(r, b):
			if r >= 0 and r < b[0]: return 0
			elif r >= b[0] and r < b[1]: return 1
			elif r >= b[1] and r < b[2]: return 2
			elif r >= b[2] and r < b[3]: return 3
			elif r >= b[3] and r < b[4]: return 4
			elif r >= b[4] and r < b[5]: return 5
			elif r >= b[5] and r < b[6]: return 6

		roll = random_number2roll(random_number, self.biased_boundaries)
		print(roll)
		return roll

	def rotate(self, direction):
		self.blocks = self.get_blocks(direction)

	def get_blocks(self, direction):
		if direction == 0 or C.SQUARE in C.BLOCKS and self.type == C.BLOCKS.index(C.SQUARE): # Don't rotate if direction is - the square.
			return self.blocks

		if direction != 0 and self.type == C.BLOCKS.index(C.LONGBAR): # Longbar rotation. Can be probably be written simpler, but it works.
			if self.blocks == C.LONGBAR: return C.LONGBAR_ROT
			if self.blocks == C.LONGBAR_ROT: return C.LONGBAR

		if direction != 0 and self.type == C.BLOCKS.index(C.SQUIGGLY):
			if self.blocks == C.SQUIGGLY: return C.SQUIGGLY_ROT
			if self.blocks == C.SQUIGGLY_ROT: return C.SQUIGGLY

		if direction != 0 and self.type == C.BLOCKS.index(C.REVERSE_SQUIGGLY):
			if self.blocks == C.REVERSE_SQUIGGLY: return C.REVERSE_SQUIGGLY_ROT
			if self.blocks == C.REVERSE_SQUIGGLY_ROT: return C.REVERSE_SQUIGGLY

		rotation = [Block(-b.y * direction, b.x * direction, b.val)
				for b in self.blocks]

		return rotation

