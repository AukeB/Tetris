import numpy as np
import matplotlib.pyplot as plt
import warnings; warnings.filterwarnings("ignore")
from matplotlib.ticker import FuncFormatter
from matplotlib.ticker import MaxNLocator
import matplotlib.patches as mpatches
import seaborn as sns

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

def compute_shifted_coordinates(ax, arr):
	xy_pixels = ax.transData.transform(np.vstack([np.arange(len(arr)), arr]).T)
	#print(xy_pixels)

	for i in range(len(xy_pixels)): 
		xy_pixels[i][1] -= bar_pixel_shift

	inv = ax.transData.inverted()
	text_coor = inv.transform(xy_pixels)

	return text_coor

def plot_drought(drought):
	def compute_drougths(drought):
		droughts = []

		for i in range(1, len(drought)):
			if drought[i] == 0:
				droughts.append(drought[i-1])

		while len(droughts) < 10:
			droughts.append(0)

		droughts = np.sort(droughts)
		droughts = droughts[::-1]
		droughts = droughts[:10]

		return droughts

	fig, ax = plt.subplots(figsize=figsize)

	if isinstance(drought[0], list) == False:
		droughts = compute_drougths(drought);
		text_coor = compute_shifted_coordinates(ax, droughts)
		ax.bar(np.arange(len(droughts)), droughts, 0.65, color='tomato', edgecolor='firebrick', linewidth=1)
		plt.xticks(np.arange(len(droughts)), (1, 2, 3, 4, 5, 6, 7, 8, 9, 10))
		for i in range(len(droughts)):
			if droughts[i] > 0:
				plt.text(x=text_coor[i][0], y=text_coor[i][1] , s=int(droughts[i]), fontsize=7, ha='center', weight='bold')
	elif isinstance(drought[0], list) == True:
		droughts_1 = compute_drougths(drought[0]); droughts_2 = compute_drougths(drought[1])
		ax.bar(np.arange(len(droughts_1)), droughts_1, 0.65/2, label=label_p1, color='tomato', edgecolor='firebrick', linewidth=1)
		ax.bar(np.arange(len(droughts_2)) + 0.65/2, droughts_2, 0.65/2, label=label_p2, color='lightsteelblue', edgecolor='midnightblue', linewidth=1)
		plt.xticks(np.arange(len(droughts_1)) + 0.65/4, (1, 2, 3, 4, 5, 6, 7, 8, 9, 10))
		for i in range(len(droughts_1)):
			if droughts_1[i] > 0: plt.text(x=i, y=bar_ratio*droughts_1[i], s=int(droughts_1[i]), fontsize=7, rotation=90, ha='center', weight='bold')
			if droughts_2[i] > 0: plt.text(x=i, y=bar_ratio*droughts_2[i], s=int(droughts_2[i]), fontsize=7, rotation=90, ha='center', weight='bold')
		legend = plt.legend(loc=1, prop={"size": 4})
		frame = legend.get_frame()
		frame.set_color('lightgray')
		frame.set_linewidth(10)

	ax.set_title('10 largest droughts', fontsize=title_fontsize)
	ax.set_xlabel('Drought number', fontsize=axes_fontsize)
	ax.set_ylabel('Drought size', fontsize=axes_fontsize)
	ax.yaxis.set_major_locator(MaxNLocator(integer=True))	
	
	plt.tight_layout()
	plt.savefig('after_game_stats/droughts.png', dpi=300)
	plt.close()

def plot_tetris_rate(tetris_rate):
	fig, ax = plot_data_over_number_of_blocks(tetris_rate)

	ax.set_title('Tetris rate', fontsize=title_fontsize)
	ax.set_ylim(-2, 102)
	ax.set_xlabel('Number of blocks', fontsize=axes_fontsize)
	ax.set_ylabel('Tetris rate (%)', fontsize=axes_fontsize)
	ax.yaxis.set_major_formatter(FuncFormatter(lambda y, _: '{:.0%}'.format(y/100))) 
	plt.tight_layout()

	plt.savefig('after_game_stats/tetris_rate.png', dpi=300)
	plt.close()

def plot_score(score):
	fig, ax = plot_data_over_number_of_blocks(score)

	ax.set_title('Score', fontsize=title_fontsize)
	ax.set_xlabel('Number of blocks', fontsize=axes_fontsize)
	ax.set_ylabel('Score', fontsize=axes_fontsize)
	plt.tight_layout()

	plt.savefig('after_game_stats/score.png', dpi=300)
	plt.close()

def plot_score_difference(score_difference):
	def insert_zeroes(score_difference):
		indices = []
		arr = list(np.arange(len(score_difference)))

		for i in range(len(score_difference)-1):
			if (score_difference[i+1] < 0 and score_difference[i]) > 0 or (score_difference[i+1] > 0 and score_difference[i] < 0):
				indices.append(i)

		indices = np.array(indices)
		counter = 0

		for i in range(len(indices)):
			indices += 1
			score_difference.insert(indices[i], 0)
			arr.insert(indices[i], int(indices[i]) - 0.5 - counter)
			counter += 1

		return arr, score_difference

	indices, score_difference = insert_zeroes(score_difference)

	fig, ax = plt.subplots(figsize=figsize)

	for i in range(len(score_difference)-1):
		if score_difference[i+1] > 0 or (score_difference[i] > 0 and score_difference[i+1] == 0):
			ax.plot(indices[i:i+2], score_difference[i:i+2], color=color_p1)
			ax.fill_between(x=indices[i:i+2], y1=np.zeros(2), y2=score_difference[i:i+2], color='indianred')
		elif score_difference[i+1] < 0 or (score_difference[i] < 0 and score_difference[i+1] == 0):
			ax.plot(indices[i:i+2], score_difference[i:i+2], color=color_p2)
			ax.fill_between(x=indices[i:i+2], y1=np.zeros(2), y2=score_difference[i:i+2], color='silver')

	ax.axhline(linestyle='--', color='dimgray')

	#custom_lines = [Line2D([0], [0], color='r', lw=4), Line2D([0], [0], color='k', lw=4)],
	label_player_1 = mpatches.Patch(color='r', label=label_p1)
	label_player_2 = mpatches.Patch(color='k', label=label_p2)

	legend = plt.legend(loc=1, handles=[label_player_1, label_player_2], prop={"size": 4})
	frame = legend.get_frame()
	frame.set_color('lightgray')
	frame.set_linewidth(10)

	ax.set_title('Score difference', fontsize=title_fontsize)
	ax.set_xlabel('Number of blocks', fontsize=axes_fontsize)
	ax.set_ylabel('Score difference', fontsize=axes_fontsize)
	ax.set_xlim(0, len(score_difference)-1)
	ax.xaxis.set_major_locator(MaxNLocator(integer=True))
	ax.set_yticklabels([str(int(abs(x))) for x in ax.get_yticks()])

	plt.tight_layout()
	plt.savefig('after_game_stats/score_difference.png', dpi=300)
	plt.close()

def plot_data_over_number_of_blocks(data):
	fig, ax = plt.subplots(figsize=figsize)

	if isinstance(data[0], list) == False:
		ax.plot(np.arange(len(data)), data, color=color_p1)
	elif isinstance(data[0], list):
		ax.plot(np.arange(len(data[0])), data[0], label=label_p1, color=color_p1)
		ax.plot(np.arange(len(data[1])), data[1], label=label_p2, color=color_p2, alpha=0.5)
		legend = plt.legend(loc=2, prop={"size": 4})
		frame = legend.get_frame()
		frame.set_color('lightgray')
		frame.set_linewidth(10)

	return fig, ax

def plot_tetromino_distribution(dif_block_counter):
	def chi_squared(data):
		a = np.sum(data)/len(data)
		chi_squared = 0
		for x in data: chi_squared += (x-a)**2/a
		return chi_squared

	fig, ax = plt.subplots(figsize=figsize)
	r = r"$\chi^2$"
	r1 = r"$\chi^2_{p1}$"
	r2 = r"$\chi^2_{p2}$"

	if len(dif_block_counter) == 7:
		ax.bar(np.arange(len(dif_block_counter)), dif_block_counter, 0.65, color='tomato', edgecolor='firebrick', linewidth=1)
		plt.xticks(np.arange(len(dif_block_counter)), 
			('T-block', 'Square', 'Longbar', 'L-block', 'Reverse L-block', 'Squiggly', 'Reverse squiggly'), rotation=-20)
		chi_squared = chi_squared(dif_block_counter)
		plt.text(np.argmin(dif_block_counter)-0.65/1.6, 0.98*np.max(dif_block_counter), s=f'{r} = {chi_squared:.2f}' )
		for i in range(len(dif_block_counter)):
			if dif_block_counter[i]: plt.text(x=i, y=bar_ratio*dif_block_counter[i], s=int(dif_block_counter[i]), fontsize=7, rotation=90, ha='center', weight='bold')
	elif len(dif_block_counter) == 2:
		ax.bar(np.arange(len(dif_block_counter[0])), dif_block_counter[0], 0.65/2, label=label_p1, color='tomato', edgecolor='firebrick', linewidth=1)
		ax.bar(np.arange(len(dif_block_counter[1])) + 0.65/2, dif_block_counter[1], 0.65/2, label=label_p2, color='lightsteelblue', edgecolor='midnightblue', linewidth=1)
		chi_squared_1 = chi_squared(dif_block_counter[0]); chi_squared_2 = chi_squared(dif_block_counter[1])
		plt.xticks(np.arange(len(dif_block_counter[0])) + 0.65/4, 
			('T-block', 'Square', 'Longbar', 'L-block', 'Reverse L-block', 'Squiggly', 'Reverse squiggly'), rotation=-20)
		plt.text(np.argmin(dif_block_counter[0]+dif_block_counter[1])-0.65/1.6, 0.98*np.max([dif_block_counter[0], dif_block_counter[1]]), s=f'{r1} = {chi_squared_1:.2f}' )
		plt.text(np.argmin(dif_block_counter[0]+dif_block_counter[1])-0.65/1.6, 0.9*np.max([dif_block_counter[0], dif_block_counter[1]]), s=f'{r2} = {chi_squared_2:.2f}' )
		for i in range(len(dif_block_counter)):
			if dif_block_counter[0][i] > 0: plt.text(x=i, y=bar_ratio*dif_block_counter[0][i], s=int(dif_block_counter[0][i]), fontsize=7, rotation=90, ha='center', weight='bold')
			if dif_block_counter[1][i] > 0: plt.text(x=i, y=bar_ratio*dif_block_counter[1][i], s=int(dif_block_counter[1][i]), fontsize=7, rotation=90, ha='center', weight='bold')
		legend = plt.legend(loc=3, prop={"size": 4})
		frame = legend.get_frame()
		frame.set_color('lightgray')
		frame.set_linewidth(10)


	ax.set_title('Tetromino distribution', fontsize=title_fontsize)
	ax.set_xlabel('Tetrominoes', fontsize=axes_fontsize)
	ax.set_ylabel('Occurence', fontsize=axes_fontsize)
	ax.yaxis.set_major_locator(MaxNLocator(integer=True))	
	
	plt.tight_layout()
	plt.savefig('after_game_stats/tetromino_distribution.png', dpi=300)
	plt.close()

def plot_sdtt_dist(arr, score_arr):
	e = 0.03 # Explode
	explode_arr_1 = [e, e, e, e] 
	explode_arr_2 = [e, e, e, e] 
	labels_1 = ['Singles', 'Doubles', 'Triples', 'Tetris']
	labels_2 = ['Singles', 'Doubles', 'Triples', 'Tetris']
	pie_colours_1 = ['gold', 'cornflowerblue', 'yellowgreen', 'r']
	pie_colours_2 = ['gold', 'cornflowerblue', 'yellowgreen', 'r']
	ld = 1.05

	def remove_zero_elements(arr, explode_arr, labels, pie_colours, score_arr):
		for i in range(len(arr)-1, -1, -1):
			if arr[i] == 0:
				del arr[i]; del explode_arr[i]; del labels[i]; del pie_colours[i]
				del score_arr[i]

	plt.rcParams.update({'font.size': 4})

	if isinstance(arr[0], list) == False:
		remove_zero_elements(arr, explode_arr_1, labels_1, pie_colours_1, score_arr)
		fig, axs = plt.subplots(1, 2, figsize=figsize)

		ps1, ls1, ts1 = axs[0].pie(x=arr, explode=explode_arr_1, labels=labels_1, colors=pie_colours_1,
			autopct=lambda p : '{:,.0f} ({:.1f}%)'.format(p * sum(arr)/100, p),
			pctdistance=0.6, shadow=True, labeldistance=ld, rotatelabels=True, startangle=90,
			wedgeprops = {'linewidth': 1, 'edgecolor': 'k'}, center=(0, 0))
		ps2, ls2, ts2 = axs[1].pie(x=score_arr, explode=explode_arr_1, labels=labels_1, colors=pie_colours_1,
			autopct=lambda p : '{:,.0f} ({:.1f}%)'.format(p * sum(score_arr)/100, p),
			pctdistance=0.7, shadow=True, labeldistance=ld, rotatelabels=True, startangle=90,
			wedgeprops = {'linewidth': 1, 'edgecolor': 'k'}, center=(0, 0))
		for l1, t1, l2, t2 in zip(ls1, ts1, ls2, ts2):
			t1.set_rotation(l1.get_rotation())
			t2.set_rotation(l2.get_rotation())

		axs[0].set_title('Distribution', fontsize=title_fontsize-3)
		axs[1].set_title('Score distribution', fontsize=title_fontsize-3)

	elif isinstance(arr[0], list) == True:
		remove_zero_elements(arr[0], explode_arr_1, labels_1, pie_colours_1, score_arr[0])
		remove_zero_elements(arr[1], explode_arr_2, labels_2, pie_colours_2, score_arr[1])
		fig, axs = plt.subplots(2, 2, figsize=figsize)

		ps1, ls1, ts1 = axs[0, 0].pie(x=arr[0], explode=explode_arr_1, labels=labels_1, colors=pie_colours_1,
			autopct=lambda p : '{:,.0f} ({:.1f}%)'.format(p * sum(arr[0])/100, p),
			pctdistance=0.6, shadow=True, labeldistance=ld, rotatelabels=True, startangle=90,
			wedgeprops = {'linewidth': 1, 'edgecolor': 'k'}, center=(0, 0))
		ps2, ls2, ts2= axs[0, 1].pie(x=score_arr[0], explode=explode_arr_1, labels=labels_1, colors=pie_colours_1,
			autopct=lambda p : '{:,.0f} ({:.1f}%)'.format(p * sum(score_arr[0])/100, p),
			pctdistance=0.7, shadow=True, labeldistance=ld, rotatelabels=True, startangle=90,
			wedgeprops = {'linewidth': 1, 'edgecolor': 'k'}, center=(0, 0))
		ps3, ls3, ts3 = axs[1, 0].pie(x=arr[1], explode=explode_arr_2, labels=labels_2, colors=pie_colours_2,
			autopct=lambda p : '{:,.0f} ({:.1f}%)'.format(p * sum(arr[1])/100, p),
			pctdistance=0.6, shadow=True, labeldistance=ld, rotatelabels=True, startangle=90,
			wedgeprops = {'linewidth': 1, 'edgecolor': 'k'}, center=(0, 0))
		ps4, ls4, ts4 = axs[1, 1].pie(x=score_arr[1], explode=explode_arr_2, labels=labels_2, colors=pie_colours_2,
			autopct=lambda p : '{:,.0f} ({:.1f}%)'.format(p * sum(score_arr[1])/100, p),
			pctdistance=0.7, shadow=True, labeldistance=ld, rotatelabels=True, startangle=90,
			wedgeprops = {'linewidth': 1, 'edgecolor': 'k'}, center=(0, 0))
		for l1, t1, l2, t2, l3, t3, l4, t4 in zip(ls1, ts1, ls2, ts2, ls3, ts3, ls4, ts4):
			t1.set_rotation(l1.get_rotation())
			t2.set_rotation(l2.get_rotation())
			t3.set_rotation(l3.get_rotation())
			t4.set_rotation(l4.get_rotation())

		axs[0, 0].set_title('P1 distribution', fontsize=title_fontsize-4)
		axs[0, 1].set_title('P1 score distribution', fontsize=title_fontsize-4)
		axs[1, 0].set_title('P2 distribution', fontsize=title_fontsize-4)
		axs[1, 1].set_title('P2 score distribution', fontsize=title_fontsize-4)

	plt.rcParams.update({'font.size': 7})

	plt.tight_layout()
	plt.savefig('after_game_stats/sdtt_dist.png', dpi=300)
	plt.close()

def generate_after_game_stats(num_blocks, drought, tetris_rate, score, dif_block_counter, sdtt_dist, score_sdtt_dist,
		score_difference=None):

	plot_drought(drought)
	plot_tetris_rate(tetris_rate)
	plot_score(score)
	plot_tetromino_distribution(dif_block_counter)
	plot_sdtt_dist(sdtt_dist, score_sdtt_dist)
	if score_difference != None: plot_score_difference(score_difference)