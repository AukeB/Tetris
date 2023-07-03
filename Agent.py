# Import libraries.
import random as rd 
import numpy as np 
import torch
from collections import deque

# Import files/classes.
import AIGame
from Model import Linear_QNet, QTrainer
#from helper import plot

# Global variables
MAX_MEMORY = 100_000
BATCH_SIZE = 1000
LR = 0.001

class Agent:

	def __init__(self):
		self.n_games = 0 # The number of games.
		self.epsilon = 0 # Parameter for controlling the 'randomness'.
		self.gamma = 0.9 # Discount rate.
		self.memory = deque(maxlen=MAX_MEMORY) # popleft()
		self.model = Linear_QNet(11, 256, 40)
		self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)

	def get_state(self, game):
		state = game.heights_array + [game.cur_tetromino_int]

		return np.array(state, dtype=int)

	def remember(self, state, action, reward, next_state, done):
		# Add to memory.
		# This will also popleft if max memory is reached.
		self.memory.append((state, action, reward, next_state, done))

	def train_long_memory(self):
		if len(self.memory) > BATCH_SIZE:
			min_sample = rd.sample(self.memory, BATCH_SIZE) # List of tuples
			print('hello')
		else:
			min_sample = self.memory
			print('hey')

		states, actions, rewards, next_states, dones = zip(*min_sample)
		print(len(actions))
		print(actions)

		self.trainer.train_step(states, actions, rewards, next_states, dones)

	def train_short_memory(self, state, action, reward, next_state, done):
		print(len(action))
		self.trainer.train_step(state, action, reward, next_state, done)

	def get_action(self, state):
		# Random moves. The trade-off between exploration and exploitation. Should be experimentated with.
		self.epsilon = 100 - self.n_games

		# Initial values. No horizontal shift and rotation of the piece, so nothing happens.
		horizontal_shift = 0
		rotation = 0
		final_move = [horizontal_shift, rotation] # The final move is represented as a list of 2 elements.

		def convert_number_to_move(number):
			shift_value = [(number % 10) - 5, number // 10]
			if shift_value[1] == 3:
				shift_value[1] = -1
			return shift_value

		if rd.randint(0, 175) < self.epsilon:
			#print('Random..')
			horizontal_shift = rd.randint(-5, 4)
			rotation = rd.randint(-1, 2)
			final_move = [horizontal_shift, rotation]
		else:
			#print('Executing')
			state0 = torch.tensor(state, dtype=torch.float)
			prediction = self.model(state0) # Will execute the forward function.
			#print(f'Prediction: {prediction}')
			move = torch.argmax(prediction).item()
			#print(f'move: {move}')
			final_move = convert_number_to_move(move)
			#print(f'Final move: {final_move}')


		return final_move

def train(display, start_level, commentary, preview_tetromino, gridline_bool, hard_drop_bool, music_queue, menu_music, tetris_version,
			p1_left, p1_right, p1_a, p1_b, p1_down, p1_space, commentary_volume):

	plot_scores = []
	plot_mean_scores = []
	total_score = 0
	old_state_bool = True
	record = 0
	agent = Agent()
	game = AIGame.Game(display, start_level, commentary, preview_tetromino, gridline_bool, hard_drop_bool, music_queue, menu_music, tetris_version,
			p1_left, p1_right, p1_a, p1_b, p1_down, p1_space, commentary_volume)

	# Training loop.
	while game.update() != 'EXIT':
		while old_state_bool:
			# Get the old state of the board.
			state_old = agent.get_state(game)
			old_state_bool = False

		if game.next_tetromino_bool == True:
			old_state_bool = True	
			
			# Get move based on current state.
			final_move = agent.get_action(state_old)

			# Perform move and get new state.
			game.play_step(final_move)

			# Obtian reward, score, done parameters.
			reward, score, done = game.reward, game.score, game.game_over

			# Obtain new board state.
			state_new = agent.get_state(game)

			# Train short memory.
			agent.train_short_memory(state_old, final_move, reward, state_new, done)

			# Remember.
			agent.remember(state_old, final_move, reward, state_new, done)

			# If the game is over, train the long-term memory.
			if done:
				# Train long memory.
				agent.n_games += 1
				agent.train_long_memory()

				# Update record.
				if score > record:
					record = score
					agent.model.save()

				print(f'Game: {agent.n_games}')
				print(f'Score: {score}')
				print(f'Record: {record}')

				plot_scores.append(score)
				total_score += score 
				mean_score = total_score / agent.n_games
				plot_mean_scores.append(mean_score)
				#plot(plot_scores, plot_mean_scores)

#if __name__ == '__main__':
#	train()