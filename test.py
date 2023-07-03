import numpy as np
import matplotlib.pyplot as plt
import warnings; warnings.filterwarnings("ignore")
from matplotlib.ticker import FuncFormatter
from matplotlib.ticker import MaxNLocator
import matplotlib.patches as mpatches
import seaborn as sns
import random as rd

# Global variables and initialisations.
figsize = (4, 3)
title_fontsize = 12
axes_fontsize = 9
color_p1 = 'r'; color_p2 = 'k'
label_p1 = 'Player 1'; label_p2 = 'Player 2'
sns.set_style('darkgrid', {'legend.frameon':True})
plt.rcParams.update({'font.size': 7})
bar_pixel_shift = 49
bar_ratio = 0.82

def rng(sample_size, tetris_rng=True, write=False):
	min_lim = 1
	max_lim = 7

	rng_arr = []

	first_roll = rd.randint(min_lim, max_lim)
	if write: print(f'first roll: {first_roll}')
	rng_arr.append(first_roll)
	if write: print(f'rng_arr: {rng_arr}')
	if write: print('')

	if tetris_rng == False:
		for i in range(sample_size-1):
			roll = rd.randint(min_lim, max_lim)
			if write: print(f'roll: {roll}')
			rng_arr.append(roll)
		return rng_arr

	else:
		for i in range(sample_size-1):
			if write:print(f'i: {i}')
			roll = rd.randint(min_lim, max_lim+1)
			if write: print(f'roll: {roll}')
			if write: print(f'prev roll: {rng_arr[-1]}')
			if roll == rng_arr[-1] or roll == max_lim+1:
				if write: print('reroll')
				roll = rd.randint(min_lim, max_lim)
				if write: print(f'roll: {roll}')
			rng_arr.append(roll)
			if write: print(f'rng_arr: {rng_arr}')
			if write: print('')

		return rng_arr

def convert_arr(arr):
	num_arr = np.zeros(7)

	for i in range(len(arr)):
		num_arr[arr[i]-1] += 1

	return num_arr

def compute_chi_squared(sample_size, tetris_rng=True):
	arr = rng(sample_size, tetris_rng)
	num_arr = convert_arr(arr)

	a = np.sum(num_arr) / len(num_arr)
	chi_squared = 0

	for x in num_arr:
		chi_squared += (x-a)**2/a

	return chi_squared

def compute_average_chi_squared(sample_size, sample_size_2, tetris_rng=True):
	chi_squared_arr = []

	for i in range(sample_size_2):
		chi_squared = compute_chi_squared(sample_size, tetris_rng)
		print(chi_squared)
		chi_squared_arr.append(chi_squared)

	avg_chi_squared = np.sum(chi_squared_arr)/len(chi_squared_arr)
	return avg_chi_squared

number_of_blocks = 1
number_of_games = 5000
number_of_blocks_arr = []

def plot():
	#for i in range(number_of_blocks):
	avg_chi_squared = compute_average_chi_squared(sample_size = 1, sample_size_2=number_of_games, tetris_rng=True)
	number_of_blocks_arr.append(avg_chi_squared)
	print(f'Number of blocks: \nNumber of games played: {number_of_games}\navg_chi_squared: {avg_chi_squared}\n')

	plt.plot(np.arange(0, number_of_blocks, 1), number_of_blocks_arr)
	plt.ylim(0, 12)
	plt.show()





plot()

def compute_chi_squared_2(num_arr):
	num_arr

	a = np.sum(num_arr) / len(num_arr)
	chi_squared = 0

	for x in num_arr:
		chi_squared += (x-a)**2/a

	return chi_squared

arr = [1, 0, 0, 0, 0, 0, 0]
hoi = compute_chi_squared_2(arr)
#print(hoi)