# Import libraries.
import pygame as pg

# Import files.
import constants_parameters as C

# Global variables.
# After each game, plots are generated with statistics from the previously 
# played game. This filename variable will contain the specific filename for each
# different plot.
filename = None 

class Renderer(object):
	'''
	This class performs the actually rendering of all the objects that are visible
	while playing the game. The drawing is done with PyGame commands, such as
	- pg.display.fill		Fills the display with a certain colour value.
	- pg.draw.line 			Draws a line between two points with a certain width and colour.
	- pg.draw.rect 			Draws a rectangle.
	'''

	def __init__(self, width, height, background_color, surface):
		self.width = width # Set display width.
		self.height = height # Set display height.
		self.background_color = background_color # Set background color.
		self.display_surface = surface # Set surface display.
		self.surface = pg.display.get_surface() # Obtain surface object.
		self.font = pg.font.Font(C.FONT, C.FONT_SIZE) # Set font and fontsize.

	def __enter__(self):
		# Fill the surface with a background color.
		self.surface.fill(self.background_color)

	def draw_background_pattern(self, block_rect) -> None:
		"""
		Draw a background pattern on the surface. This is the pattern that is
		visible behind the actual playfield. The pattern is that of a 
		grey brick wall.

		Args:
			block_rect: The rectangle representing a block in the pattern.

		Returns:
			None
		"""

		i = 0; j = 0 # Loop variables.
		h = i * block_rect.height # Height distance measure
		k = 2 * j * block_rect.width # Width distance measure

		while h <= C.SURFACE_HEIGHT:
			j = 0; k = 2 * j * block_rect.width
			l = (0, h)
			r = (C.SURFACE_WIDTH, h)
			pg.draw.line(self.surface, C.BC, l, r, C.BACKGROUND_BORDER_WIDTH)
			i += 1; h = i * block_rect.height
			if i % 2 == 0:
				while k <= C.SURFACE_WIDTH:
					t = (k, h - block_rect.height)
					b = (k, h)
					pg.draw.line(self.surface, C.BC, t, b, C.BACKGROUND_BORDER_WIDTH)
					j += 1; k = 2 * j * block_rect.width
			else:
				while k <= C.SURFACE_WIDTH:
					t = (k, h - block_rect.height)
					b = (k, h)
					pg.draw.line(self.surface, C.BC, t, b, C.BACKGROUND_BORDER_WIDTH)
					j += 1; k = 2 * j * block_rect.width - block_rect.width

	def draw_black_border(self, block_rect) -> None:
		"""
		Draw a black border around the specified block rectangle on the surface.

		Args:
			block_rect: The rectangle representing the block to be bordered.

		Returns:
			None
		"""

		# Define useful coordinates.
		tl = (block_rect.x, block_rect.y) # Top left.
		tr = (block_rect.x + block_rect.width - C.BLACK_BORDER_WIDTH, block_rect.y) # Top right.
		bl = (block_rect.x, block_rect.y + block_rect.height - C.BLACK_BORDER_WIDTH) # Bottom left.
		br = (block_rect.x + block_rect.width - C.BLACK_BORDER_WIDTH, block_rect.y + block_rect.height - C.BLACK_BORDER_WIDTH) # Bottom right.

		# Draw the borders.
		pg.draw.line(self.surface, C.BLACK, tl, tr, C.BLACK_BORDER_WIDTH)
		pg.draw.line(self.surface, C.BLACK, tr, br, C.BLACK_BORDER_WIDTH)
		pg.draw.line(self.surface, C.BLACK, br, bl, C.BLACK_BORDER_WIDTH)
		pg.draw.line(self.surface, C.BLACK, bl, tl, C.BLACK_BORDER_WIDTH)

	def draw_coloured_border(self, cur_level: int, block_rect) -> None:
		"""
		Draw a colored border around the specified block rectangle on the surface.
		The colour of the border is dependent on the current level the player is
		playing in. All the colours for the different levels are defined in RGB values
		in the constants and parameter files. Because the pattern of colours is
		repeating itself each 10 levels, the modulo operator is used in combination
		with the length of the 2d array containing all the RGB colour values.

		Args:
			cur_level (int): The current level of the game.
			block_rect: The rectangle representing the block to be bordered.

		Returns:
			None
		"""

		# Draw the 4 borders around a block.
		pg.draw.rect(self.surface, C.PIECE_COLOURS[cur_level%len(C.PIECE_COLOURS)][1],
			(block_rect.x + C.COLOURED_BORDER_WIDTH, block_rect.y, block_rect.width - 
			C.COLOURED_BORDER_WIDTH, C.COLOURED_BORDER_WIDTH))
		pg.draw.rect(self.surface, C.PIECE_COLOURS[cur_level%len(C.PIECE_COLOURS)][1],
			(block_rect.x + block_rect.width - C.COLOURED_BORDER_WIDTH,
			block_rect.y, C.COLOURED_BORDER_WIDTH, block_rect.height))
		pg.draw.rect(self.surface, C.PIECE_COLOURS[cur_level%len(C.PIECE_COLOURS)][1],
			(block_rect.x, block_rect.y + block_rect.height - C.COLOURED_BORDER_WIDTH,
			block_rect.width, C.COLOURED_BORDER_WIDTH))
		pg.draw.rect(self.surface, C.PIECE_COLOURS[cur_level%len(C.PIECE_COLOURS)][1],
			(block_rect.x, block_rect.y + C.COLOURED_BORDER_WIDTH,
			C.COLOURED_BORDER_WIDTH, block_rect.height - C.COLOURED_BORDER_WIDTH))

	def draw_block_ornaments(self, cur_level: int, block_rect) -> None:
		"""
		Draw a series of rectangles with colors from the piece colors based on the current level.
		Each block contains little ornaments within itself. I have divided each block of each 
		tetromino in seven parts. Based on this distance measure i am drawing little rectangles within
		the block that make up the ornaments.

		Args:
			cur_level (int) : The current level of the game.
			block_rect: The rectangle representing the block.

		Returns:
			None
		"""

		tl = (block_rect.x, block_rect.y) # Top left.
		size = block_rect.width // 7 # Define new distance measure.

		# Draw all the ornaments.
		pg.draw.rect(self.surface, C.PIECE_COLOURS[cur_level%len(C.PIECE_COLOURS)][0], (tl[0], tl[1], size, size))
		pg.draw.rect(self.surface, C.PIECE_COLOURS[cur_level%len(C.PIECE_COLOURS)][0], (tl[0] + size, tl[1] + size, size, size))
		pg.draw.rect(self.surface, C.PIECE_COLOURS[cur_level%len(C.PIECE_COLOURS)][0], (tl[0] + 2*size, tl[1] + size, size, size))
		pg.draw.rect(self.surface, C.PIECE_COLOURS[cur_level%len(C.PIECE_COLOURS)][0], (tl[0] + size, tl[1] + 2*size, size, size))

	def draw_heart(self, display, board, heart_field: list, block_rect_width: int, block_rect_height: int, match_score: int) -> None:
		'''
		Draw a heart shape on the display to represent match scores.

		Args:
			display: The display surface to draw on.
			board: The game board.
			heart_field (list): The coordinates of the heart field.
			block_rect_width (int): The width of the block rectangle.
			block_rect_height (int): The height of the block rectangle.
			match_score (int): The current match score.

		Returns:
			None
		'''

		# Best of five, so you're looping until 3.
		for i in range(3):
			x = heart_field[0] + block_rect_width + 2.65*i*block_rect_width # Define upper left x-coordinate of the heart.
			y = heart_field[1] + 0.8*block_rect_height # Upper left y-coordinate.
			s = 1.5*block_rect_height/13 # Scaling factor. 1.5 times block rect and 13 because the heart has 13 pixels in the y-direction.

			# These coordinates will make up the heart when they are connected to each other.
			heart_coor_arr = [(x, y+2*s), (x+2*s, y), (x+5*s, y), (x+7*s, y+2*s), (x+7*s, y+3*s), (x+7*s, y+2*s), (x+9*s, y), (x+12*s, y),
			(x+14*s, y+2*s), (x+14*s, y+6*s), (x+7*s, y+13*s), (x, y+6*s), (x, y+2*s)]

			# Draw the grey shape of the heart.
			pg.draw.polygon(display, color=C.GREY, points=heart_coor_arr)

			# Fill in the heart with a red colour if a player has won a match.
			if i < match_score:
				pg.draw.polygon(display, color=C.RED, points=heart_coor_arr)

			# Draw 5 small white squares within the heart for aesthetical reasons.
			pg.draw.rect(display, color=C.WHITE, rect=(x+3*s, y+2*s, s, s))
			pg.draw.rect(display, color=C.WHITE, rect=(x+3*s, y+3*s, s, s))
			pg.draw.rect(display, color=C.WHITE, rect=(x+4*s, y+2*s, s, s))
			pg.draw.rect(display, color=C.WHITE, rect=(x+2*s, y+3*s, s, s))
			pg.draw.rect(display, color=C.WHITE, rect=(x+2*s, y+4*s, s, s))
		

	def draw_colored_pieces(self, tetromino, cur_level: int, block_rect, board_block=None) -> None:
		"""
		Draw colored pieces on the surface based on the type of tetromino and current level.

		Args:
			tetromino: The tetromino object.
			cur_level (int): The current level of the game.
			block_rect: The rectangle representing the block.
			board_block: Optional parameter indicating the type of block on the board.

		Returns:
			None
		"""

		# Draw different colours for different pieces and different levels.
		if board_block == None and tetromino.type in (C.BLOCKS.index(C.LONGBAR), C.BLOCKS.index(C.SQUARE), C.BLOCKS.index(C.T_BLOCK)) or board_block == 1:
			pg.draw.rect(self.surface, C.PIECE_COLOURS[cur_level%len(C.PIECE_COLOURS)][0], block_rect)
			self.draw_coloured_border(cur_level, block_rect)
		if board_block == None and tetromino.type in (C.BLOCKS.index(C.REVERSE_L_BLOCK), C.BLOCKS.index(C.REVERSE_SQUIGGLY)) or board_block == 2:
			pg.draw.rect(self.surface, C.PIECE_COLOURS[cur_level%len(C.PIECE_COLOURS)][1], block_rect)
			self.draw_block_ornaments(cur_level, block_rect)
		if board_block == None and tetromino.type in (C.BLOCKS.index(C.L_BLOCK), C.BLOCKS.index(C.SQUIGGLY)) or board_block == 3:
			pg.draw.rect(self.surface, C.PIECE_COLOURS[cur_level%len(C.PIECE_COLOURS)][2], block_rect)
			self.draw_block_ornaments(cur_level, block_rect)
		
		self.draw_black_border(block_rect)

	def draw_board(self, board, tetromino, cur_level: int, background_color) -> None:
		"""
		Draw the game board on the surface, including the blocks and the tetromino.

		Args:
			board: The game board.
			tetromino: The current tetromino object.
			cur_level (int): The current level of the game.
			background_color: The background color of the board.

		Returns:
			None
		"""

		# Draw the board.
		pg.draw.rect(self.surface, background_color, board.rect)

		# Divide the board into the dimensions specified in the constants and
		# parameters file. Default is a board of size 20x10 (with 2 invisible rows
		# at the top).
		block_rect = pg.Rect(0, 0, 
			board.rect.width // board.dimensions.width,
			board.rect.height // board.dimensions.height)

		# Draw pieces in the board. If in the board matrix a value 
		# is not equal to 0, it means a piece should be drawn here.
		for x, y in board:
			if y >= 2 and board.blocks[y][x] != 0:
				block_rect.x = board.rect.x + block_rect.width * x
				block_rect.y = board.rect.y + block_rect.height * y
				self.draw_colored_pieces(tetromino, cur_level, block_rect, board_block=board.blocks[y][x])

	def draw_tetromino(self, tetromino, position, block_rect, cur_level: int, block_rect_width=None, block_rect_height=None) -> None:
		"""
		Draw a tetromino on the surface at the specified position. This function
		is used for the tetromino's that are not located in the playfield, so for
		example, all the ones on the left of the screen that display how often each
		tetromino has occured in the current game.

		Args:
			tetromino: The tetromino object to be drawn.
			position: The position of the tetromino.
			block_rect: The rectangle representing a block.
			cur_level (int): The current level of the game.
			block_rect_width: Optional parameter for the width of the block rectangle.
			block_rect_height: Optional parameter for the height of the block rectangle.

		Returns:
			None
		"""

		# Change the size of the block rect if these values are given. This occurs for smaller screen resolutions are smaller board sizes.
		if block_rect_width != None and block_rect_height != None:
			for block in tetromino:
				block_rect.x = position.x + block.x * block_rect_width
				block_rect.y = position.y + block.y * block_rect_height
				self.draw_colored_pieces(tetromino, cur_level, pg.Rect(block_rect.x, block_rect.y, block_rect_width, block_rect_height))
		else:
			for block in tetromino:
				block_rect.x = position.x + block.x * block_rect.width
				block_rect.y = position.y + block.y * block_rect.height
				self.draw_colored_pieces(tetromino, cur_level, block_rect)

	def draw_preview_tetromino(self, tetromino, position, block_rect, cur_level: int, board_block=None) -> None:
		"""
		Draw a preview of a tetromino on the surface at the specified position.

		Args:
			tetromino: The tetromino object to be drawn.
			position: The position of the tetromino.
			block_rect: The rectangle representing a block.
			cur_level (int): The current level of the game.
			board_block: Optional parameter representing the type of block on the board.

		Returns:
			None
		"""

		# Create the distance measure that divides each block of each tetromino into 7 parts.
		bs = block_rect.width // 7

		# Loop through all the blocks of a tetromino.
		for block in tetromino:
			block_rect.x = position.x + block.x * block_rect.width
			block_rect.y = position.y + block.y * block_rect.height

			if board_block == None:
				pg.draw.rect(self.surface, C.PIECE_COLOURS[cur_level%len(C.PIECE_COLOURS)][1], block_rect)		
				pg.draw.rect(self.surface, C.BLACK, (block_rect.x + bs, block_rect.y + bs, block_rect.width - 2*bs, block_rect.height - 2*bs))
				self.draw_black_border(block_rect)

	def draw_rect(self, rect, background_color) -> None:
		"""
		Draw a rectangle on the surface with the specified background color.

		Args:
			rect: The rectangle object to be drawn.
			background_color: The color of the rectangle's background.

		Returns:
			None
		"""

		# Draw the rectangle object.
		pg.draw.rect(self.surface, background_color, rect)

	def draw_board_borders(self, board, block_rect, colour) -> None:
		"""
		Draw borders around the game board on the surface.

		Args:
			board: The game board object.
			block_rect: The rectangle representing a block.
			colour: The color of the board borders.

		Returns:
			None
		"""

		black = (0, 0, 0)
		d = int(C.BORDER_WIDTH / 2) # Define distance measure.

		# Define border corner coordinates.
		tl = (board.rect.x - d, board.rect.y - d + C.BOARD_INVIS_ROWS * block_rect.height) # Top left.
		tr = (board.rect.x + d + board.rect.width, board.rect.y - d + C.BOARD_INVIS_ROWS * block_rect.height) # Top right.
		bl = (board.rect.x - d, board.rect.y + board.rect.height + d) # Bottom left.
		br = (board.rect.x + d + board.rect.width, board.rect.y + board.rect.height + d) # Bottom right.

		# Draw the borders around the board.
		pg.draw.line(self.surface, colour, tl, tr, C.BORDER_WIDTH)
		pg.draw.line(self.surface, colour, tr, br, C.BORDER_WIDTH)
		pg.draw.line(self.surface, colour, br, bl, C.BORDER_WIDTH)
		pg.draw.line(self.surface, colour, bl, tl, C.BORDER_WIDTH)

	def draw_borders(self, block_rect, colour) -> None:
		"""
		Draw borders around a rectangle on the surface.

		Args:
			block_rect: The rectangle to draw borders around.
			colour: The color of the borders.

		Returns:
			None
		"""

		d = int(C.BORDER_WIDTH / 2) # Distance measure.

		# Define useful coordinates.
		tl = (block_rect.x - d, block_rect.y - d) # Top left.
		tr = (block_rect.x + block_rect.width + d, block_rect.y - d) # Top right.
		bl = (block_rect.x - d, block_rect.y + block_rect.height + d) # Bottom left.
		br = (block_rect.x + block_rect.width + d, block_rect.y + block_rect.height + d) # Bottom right.

		# Draw the borders.
		pg.draw.line(self.surface, colour, tl, tr, C.BORDER_WIDTH)
		pg.draw.line(self.surface, colour, tr, br, C.BORDER_WIDTH)
		pg.draw.line(self.surface, colour, br, bl, C.BORDER_WIDTH)
		pg.draw.line(self.surface, colour, bl, tl, C.BORDER_WIDTH)

	def draw_changing_text(self, text, pos, color=C.WHITE, background_color=C.BBC, other_fontsize = False, fontsize=0) -> None:
		"""
		Render and display changing text on the surface.

		Args:
			text: The text to be rendered and displayed.
			pos: The position and dimensions of the text area as a Rect object.
			color: The color of the text (default: C.WHITE).
			background_color: The background color of the text (default: C.BBC).
			other_fontsize: A flag indicating whether to use a different font size (default: False).
			fontsize: The font size to be used if other_fontsize is True (default: 0).

		Returns:
			None
		"""

		# Create a text object.
		text_obj = self.font.render(text, True, color, background_color)

		# If-statement that determines what to do if you're not using the default font size.
		if other_fontsize:
			other_font = pg.font.Font(C.FONT, fontsize)
			text_obj = other_font.render(text, True, color, background_color)
			#self.font = pg.font.Font(C.FONT, C.FONT_SIZE)
			#text_obj = self.font.render(text, True, color, background_color)

		# Draw the changing text.
		textRect = text_obj.get_rect()
		textRect.center = (pos.x + 0.5*pos.width, pos.y + 0.5*pos.height)
		self.display_surface.blit(text_obj, textRect)

	def draw_menu_text(self, text, xy, font, surface, button=False, color=C.WHITE, background_color=None, shadow=True, shadow_offset=(4, 4)) -> None:
		"""
		Render and display menu text on the surface.

		Args:
			text: The text to be rendered and displayed.
			xy: The top-left coordinates of the text.
			font: The font object to be used for rendering the text.
			surface: The surface on which the text will be displayed.
			button: A flag indicating whether the text represents a button (default: False).
			color: The color of the text (default: C.WHITE).
			background_color: The background color of the text (default: None).
			shadow: A flag indicating whether to display a shadow behind the text (default: True).
			shadow_offset: The offset of the shadow in pixels as a tuple (default: (4, 4)).

		Returns:
			button (Rect object) if button=True, otherwise None
		"""

		# Create text object and determine location.
		textobj = font.render(text, 1, color, background_color)
		textrect = textobj.get_rect()
		textrect.topleft = xy

		# If you want to include a shadow with the text.
		if shadow == True:
			textobj_shadow = font.render(text, 1, C.GREY, background_color)
			textrect_shadow = textobj.get_rect()
			textrect_shadow.topleft = (xy[0]+shadow_offset[0], xy[1]+shadow_offset[1])
			surface.blit(textobj_shadow, textrect_shadow)

		# Draw the text.
		surface.blit(textobj, textrect)

		# If the text should be clickable, add a button to the text.
		if button == True:
			button = pg.Rect(xy[0], xy[1], textrect[2], textrect[3])
			return button

	def draw_gridlines(self, board, block_rect, l, t, colour) -> None:
		"""
		Draw gridlines on the board.

		Args:
			board: The board object.
			block_rect: The rectangle representing a single block on the board.
			l: The left coordinate of the board.
			t: The top coordinate of the board.
			colour: The color of the gridlines.

		Returns:
			None
		"""

		# Horizontal lines.
		x = l; y = t # l = left, t = top.

		# Loop over the board width and draw vertical lines.
		while x < l + C.BOARD_WIDTH:
			if x > l + 1: pg.draw.line(self.surface, colour, (x, y), (x, y + C.BOARD_HEIGHT), C.GRIDLINES_WIDTH)
			x += block_rect.width

		x = l

		# Loop over the board height and draw horizontal lines.
		while y < t + C.BOARD_HEIGHT:
			if y > t + 2*block_rect.height: pg.draw.line(self.surface, colour, (x, y), (x + C.BOARD_WIDTH, y), C.GRIDLINES_WIDTH)
			y += block_rect.height

	def draw_line_clear_animation(self, board, block_rect, framerate, background_color, rows, timer) -> None:
		"""
		Draw the line clear animation on the board. This is an animation that
		occurs when the player has filled all values in a single row. When it is
		detected that for a single row all values are filled, the line clear animation 
		plays, and after the line is cleared, and the board is adjusted to the new
		state.

		Args:
			board: The board object.
			block_rect: The rectangle representing a single block on the board.
			framerate: The frame rate of the animation.
			background_color: The background color of the board.
			rows: The rows to be cleared.
			timer: The elapsed time of the animation.

		Returns:
			None
		"""

		# The line clear animation is divided up into 5 steps.
		# The length of the step is computed based on the framerate, and the line clear delay value.
		num_steps = 5
		step_size = C.compute_milliseconds(framerate, C.LINE_CLEAR_DELAY) / num_steps
		
		# Create a new variable x which is a step function based on the timer and step_size value.
		x = 1
		if timer > 1*step_size: x = 2
		if timer > 2*step_size: x = 3
		if timer > 3*step_size: x = 4
		if timer > 4*step_size: x = 5

		# Loop over all the rows that should be cleared (it could be multiple at the same time).
		for row in rows:
			# Draw the actual line clear animation.
			pg.draw.rect(self.surface, C.BBC, 
				(board.rect.x + (num_steps - x) * block_rect.width, 
				board.rect.y + row * block_rect.height,
				2*x * block_rect.width, block_rect.height))

	def draw_post_game_messages(self, m, locs) -> None:
		"""
		Draw the post-game messages on the screen.

		Args:
			m: A list of messages to be displayed.
			locs: A list of locations where each message should be displayed.

		Returns:
			None
		"""

		# Loop over all the different parts a post game message can consist of.
		for i in range(len(m)):
			# Draw the post game message.
			# The location of the message parts different if the number of parts
			# is greater than 2.
			if len(m) < 3: self.draw_changing_text(m[i], locs[i+1])
			else: self.draw_changing_text(m[i], locs[i])


	def game_over_messages(self, score: int, locs) -> None:
		"""
		Display game-over messages based on the player's score.

		Args:
			score (int): The player's score.
			locs: A list of locations where the messages should be displayed.

		Returns:
			None
		"""

		# For different score ranges, different messages are shown to the player when the game is over.
		if score >= 0 and score < 100: self.draw_post_game_messages(['COULD', 'HAVE', 'BEEN', 'WORSE'], locs)
		if score >= 100 and score < 1000: self.draw_post_game_messages(['ARE', 'YOU', 'EVEN', 'TRYING'], locs)
		if score >= 1000 and score < 5000: self.draw_post_game_messages(['MEDIOCRE'], locs)
		if score >= 5000 and score < 10000: self.draw_post_game_messages(['HAVE YOU', 'TRIED', 'DOING', 'YOUR BEST?'], locs)
		if score >= 10000 and score < 50000: self.draw_post_game_messages(['UNFOR-', 'TUNATELY', 'PEANUT', 'BUTTER'], locs)
		if score >= 50000 and score < 100000: self.draw_post_game_messages(['YOUR', 'MUM', 'MUST BE', 'PROUD'], locs)
		if score >= 100000 and score < 200000: self.draw_post_game_messages(['TASTY', 'BUSY'], locs)
		if score >= 200000 and score < 300000: self.draw_post_game_messages(['HELL', 'YEAH!'], locs)
		if score >= 1000000 and score < 1100000: self.draw_post_game_messages(['WELCOME', 'TO THE', 'MAXOUT', 'CLUB!'], locs)
		if score >= 1100000 and score < 1200000: self.draw_post_game_messages(["THAT'S A", '1.1', 'BABY!'], locs)

	def best_of_five_messages(self, score: int, locs: list, match_score: list, p1: bool) -> None:
		"""
		Display the match score in a best-of-five match.

		Args:
			score (int): The player's score in the current match.
			locs (list): A list of locations where the messages should be displayed.
			match_score(list): A list containing the match score for both players.
			p1 (bool): A boolean indicating if the player is player 1.

		Returns:
			None
		"""

		if p1: self.draw_post_game_messages([f'{match_score[0]}'], locs)
		else: self.draw_post_game_messages([f'{match_score[1]}'], locs)

		# The following is a work in progress. Eventually, the goal is to have custom messages for the
		# best of five game mode, that for example state that you're taking the lead if that is the case.

		'''
		if match_score == [1,0]: 
			if p1: self.draw_post_game_messages(['TAKING', 'THE LEAD', '', f'{match_score[0]}'], locs)
			else: self.draw_post_game_messages(['JUST THE', 'FIRST GAME', f'{match_score[1]}'], locs)
		if match_score == [0,1]: 
			if p1: self.draw_post_game_messages(['JUST THE', 'FIRST GAME', f'{match_score[0]}'], locs)
			else: self.draw_post_game_messages(['TAKING', 'THE LEAD', '', f'{match_score[1]}'], locs)
		if match_score == [1,1]: 
			if p1: self.draw_post_game_messages(['TIED', 'UP', f'{match_score[0]}'], locs)
			else: self.draw_post_game_messages(['TIED', 'UP', '', f'{match_score[1]}'], locs)
		if match_score == [2,1]: 
			if p1: self.draw_post_game_messages(['ONE WIN', 'TO GO', f'{match_score[0]}'], locs)
			else: self.draw_post_game_messages(['STILL', 'WINNABLE', '', f'{match_score[1]}'], locs)
		if match_score == [1,2]: 
			if p1: self.draw_post_game_messages(['STILL', 'WINNABLE', f'{match_score[0]}'], locs)
			else: self.draw_post_game_messages(['ONE WIN', 'TO GO', '', f'{match_score[1]}'], locs)
		if match_score == [2,2]: 
			if p1: self.draw_post_game_messages(['D-D-D-D-', 'DECIDER', f'{match_score[0]}'], locs)
			else: self.draw_post_game_messages(['D-D-D-D-', 'DECIDER', '', f'{match_score[1]}'], locs)
		if match_score == [3,2]: 
			if p1: self.draw_post_game_messages(['BEST', 'FIRST GAME', f'{match_score[0]}'], locs)
			else: self.draw_post_game_messages(['TAKING', 'THE LEAD', '', f'{match_score[1]}'], locs)
		if match_score == [2,3]: 
			if p1: self.draw_post_game_messages(['BEST', 'FIRST GAME', f'{match_score[0]}'], locs)
			else: self.draw_post_game_messages(['TAKING', 'THE LEAD', '', f'{match_score[1]}'], locs)
		'''
		
	def draw_start_game_animation(self, display, board, block_rect, color, background_color, timer) -> bool:
		"""
		Draw the animation for the start of the game.

		Args:
			display: The display surface to draw on.
			board: The game board.
			block_rect: The rectangle representing a single block.
			color: The color for the text.
			background_color: The background color for the text.
			timer: The timer for the animation.

		Returns:
			bool: False if the animation is complete, True otherwise.
		"""

		# Set up animation constants.
		ani_dur = 3e3 # Duration of the animation in milliseconds.
		s = ani_dur / 3 # Divide the animation up into 3 parts.
		fontsize = int(((timer*-1)%s)/9)+20 # Determine font size.

		# Set up the location.
		loc = pg.Rect(board.rect.x, board.rect.y + 0*block_rect.height, board.rect.width, board.rect.height)

		# Draw the animation.
		if timer < s: self.draw_changing_text('3', loc, C.WHITE, background_color, other_fontsize=True, fontsize=fontsize)
		if timer > s and timer < 2*s: self.draw_changing_text('2', loc, C.WHITE, background_color, other_fontsize=True, fontsize=fontsize)
		if timer > 2*s and timer < 3*s: self.draw_changing_text('1', loc, C.WHITE, background_color, other_fontsize=True, fontsize=fontsize)

		# End the animation when the timer has reached the same length as the animation duration.
		if timer > ani_dur:
			return False

	def draw_stats_button(self, display, stats_field, block_rect_width, block_rect_height) -> bool:
		"""
		Draw the stats button and handle user interaction.

		Args:
			display: The display surface to draw on.
			stats_field: The rectangle representing the stats field.
			block_rect_width: The width of a single block rectangle.
			block_rect_height: The height of a single block rectangle.

		Returns:
			bool: True if the stats button is clicked, False otherwise.
		"""

		# Set up the normal font.
		normal_font = pg.font.Font(C.FONT, int(0.75*C.FONT_SIZE))

		# Get current mouse position.
		mx, my = pg.mouse.get_pos()
		click = pg.mouse.get_pressed()[0]

		# Set up the botton.
		button_loc =  (stats_field[0] + (1/7.5)*stats_field[2], stats_field[1] + (2.65/8)*stats_field[3]) # Empirical ratios.
		button_stats = self.draw_menu_text('stats', button_loc, normal_font, display, True, shadow=False)

		# When the player clicks on the button. Return True if the player clicks on the button, otherwise False.
		if button_stats.collidepoint((mx, my)):
			self.draw_menu_text('stats', button_loc, normal_font, display, button=False, color=C.RED, shadow=False)
			if click:
				return True

		return False

	def draw_after_game_stats(self, display, board, block_rect, multiplayer=False) -> bool:
		"""
		Draw the after-game statistics screen and handle user interaction.

		Args:
			display: The display surface to draw on.
			board: The game board.
			block_rect: The rectangle representing a single block.
			multiplayer: A boolean indicating whether the game is multiplayer or not. Defaults to False.

		Returns:
			bool: True if the user stays on the after-game statistics screen, False if the user goes back to the main menu.
		"""

		# Distance measures and font.
		normal_font = pg.font.Font(C.FONT, C.FONT_SIZE)
		d1 = 100; d2 = 59; d3 = 20
		top_left = (d1, d1)

		# Make sure that you are using the global filename parameter.
		global filename

		# Load the images that were generated from the previously played game.
		try: 
			image = pg.image.load(f'after_game_stats/{filename}.png')
		except: 
			image = pg.image.load(f'after_game_stats/score.png')
		
		# Display the images.
		s = (display.get_height() - 2*d1)/image.get_rect().size[1]
		image = pg.transform.scale(image, (int(image.get_rect().size[0]*s), int(image.get_rect().size[1]*s)))
		display.blit(image, top_left)
		d4 = top_left[0] + image.get_rect().size[0] + d1

		# Draw fields and borders around the image.
		self.draw_borders(pg.Rect(top_left[0], top_left[1], image.get_rect().size[0], image.get_rect().size[1]), C.BLACK)
		self.draw_rect(pg.Rect(d4, top_left[1], 4*d1, image.get_rect().size[1]), C.BLACK)
		self.draw_borders(pg.Rect(d4, top_left[1], 4*d1, image.get_rect().size[1]), C.LIGHTGREY)

		# Get current mouse position.
		mx, my = pg.mouse.get_pos()
		click = pg.mouse.get_pressed()[0]

		# Button locations for all the images.
		score_button_loc = (d4 + d3, d1 + 0*d2)
		tetris_rate_button_loc = (d4 + d3, d1 + 1*d2)
		tetromino_distribution_button_loc = (d4 + d3, d1 + 2*d2)
		droughts_button_loc = (d4 + d3, d1 + 3*d2)
		sdtt_button_loc = (d4 + d3, d1 + 4*d2)
		score_difference_button_loc = (d4 + d3, d1 + 5*d2)
		back_button_loc = (d4 + d3, d1 + 14*d2)

		# Draw text and buttons for all the images.
		tetris_rate_button = self.draw_menu_text('Tetris rate', tetris_rate_button_loc, normal_font, display, True, shadow=False)
		score_button = self.draw_menu_text('Score', score_button_loc, normal_font, display, True, shadow=False)
		tetromino_distribution_button = self.draw_menu_text('Distribution', tetromino_distribution_button_loc, normal_font, display, True, shadow=False)
		droughts_button = self.draw_menu_text('Droughts', droughts_button_loc, normal_font, display, True, shadow=False)
		sdtt_button = self.draw_menu_text('Score dist', sdtt_button_loc, normal_font, display, True, shadow=False)
		if multiplayer: score_difference_button = self.draw_menu_text('Difference', score_difference_button_loc, normal_font, display, True, shadow=False)		
		back_button = self.draw_menu_text('Back', back_button_loc, normal_font, display, True, shadow=False)

		# Determine user interaction. If the user clicks on a certain button, the image corresponding
		# to the button should be shown.
		if score_button.collidepoint((mx, my)):
			self.draw_menu_text('Score', score_button_loc, normal_font, display, button=False, color=C.RED, shadow=False)
			if click:
				filename = 'score'
		if tetris_rate_button.collidepoint((mx, my)):
			self.draw_menu_text('Tetris rate', tetris_rate_button_loc, normal_font, display, button=False, color=C.RED, shadow=False)
			if click:
				filename = 'tetris_rate'
		if tetromino_distribution_button.collidepoint((mx, my)):
			self.draw_menu_text('Distribution', tetromino_distribution_button_loc, normal_font, display, button=False, color=C.RED, shadow=False)
			if click:
				filename = 'tetromino_distribution'
		if droughts_button.collidepoint((mx, my)):
			self.draw_menu_text('Droughts', droughts_button_loc, normal_font, display, button=False, color=C.RED, shadow=False)
			if click:
				filename = 'droughts'
		if sdtt_button.collidepoint((mx, my)):
			self.draw_menu_text('Score dist', sdtt_button_loc, normal_font, display, button=False, color=C.RED, shadow=False)
			if click:
				filename = 'sdtt_dist'
		if multiplayer:
			if score_difference_button.collidepoint((mx, my)):
				self.draw_menu_text('Difference', score_difference_button_loc, normal_font, display, button=False, color=C.RED, shadow=False)
				if click:
					filename = 'score_difference'
		if back_button.collidepoint((mx, my)):
			self.draw_menu_text('Back', back_button_loc, normal_font, display, button=False, color=C.RED, shadow=False)
			if click:
				filename = 'score'
				return False

		return True

	def draw_game_over_animation(self, display, board, block_rect, color, background_color, timer, score,
			other_game=None, mode=0, match_score=[0,0], p1=True) -> bool:
		"""
		Draw the game over animation screen and handle user interaction.

		Args:
			display: The display surface to draw on.
			board: The game board.
			block_rect: The rectangle representing a single block.
			color: The color of the game over animation.
			background_color: The background color of the game over animation.
			timer: The timer value for the animation.
			score: The final score achieved by the player.
			other_game: A boolean indicating whether there is another game to play or not. Defaults to None.
			mode: The game mode. Defaults to 0.
			match_score: The score of the match in multiplayer mode. Defaults to [0, 0].
			p1: A boolean indicating whether the current player is player 1 or not. Defaults to True.

		Returns:
			bool: True if the user wants to start a new game or continue, False if the user wants to quit.
		"""

		# Set up all the delay values in milliseconds.
		initial_delay = 1000
		score_delay = 1000
		step_size = 70
		yes_no_lin_shift = 2.9

		normal_font = pg.font.Font(C.FONT, C.FONT_SIZE)

		# Get current mouse position.
		mx, my = pg.mouse.get_pos()
		click = pg.mouse.get_pressed()[0]

		# Set up location values where the text will be drawn.
		loc_0 = pg.Rect(board.rect.x, board.rect.y + -7*block_rect.height, board.rect.width, board.rect.height)
		loc_1 = pg.Rect(board.rect.x, board.rect.y + -5*block_rect.height, board.rect.width, board.rect.height)

		loc_2 = pg.Rect(board.rect.x, board.rect.y + -2*block_rect.height, board.rect.width, board.rect.height)
		loc_3 = pg.Rect(board.rect.x, board.rect.y + 0*block_rect.height, board.rect.width, board.rect.height)
		loc_4 = pg.Rect(board.rect.x, board.rect.y + 2*block_rect.height, board.rect.width, board.rect.height)
		loc_5 = pg.Rect(board.rect.x, board.rect.y + 4*block_rect.height, board.rect.width, board.rect.height)
		locs = [loc_2, loc_3, loc_4, loc_5]

		loc_6 = pg.Rect(board.rect.x, board.rect.y + 7*block_rect.height, board.rect.width, board.rect.height)

		# Button locations.
		button_loc_1 = (board.rect.x - yes_no_lin_shift*block_rect.width, board.rect.y + 8*block_rect.height, board.rect.width, board.rect.height)
		button_loc_2 = (board.rect.x - (yes_no_lin_shift - 4)*block_rect.width, board.rect.y + 8*block_rect.height, board.rect.width, board.rect.height)
		button_loc_1 = (button_loc_1[0] + 0.5*button_loc_1[2], button_loc_1[1] + 0.5*button_loc_1[3])
		button_loc_2 = (button_loc_2[0] + 0.5*button_loc_2[2], button_loc_2[1] + 0.5*button_loc_2[3])

		# Row values which are dependent on the game over animation timer.
		# At different times, text will be drawn in different rows.
		row = min(int((timer-initial_delay)/step_size), C.BOARD_VIS_ROWS)

		# Draw the game over animation.
		if row >= 0 and row <= C.BOARD_VIS_ROWS:
			pg.draw.rect(self.surface, color,
				(board.rect.x, board.rect.y + board.rect.height - row*block_rect.height,
				board.rect.width, row*block_rect.height))

		if timer > initial_delay + step_size*C.BOARD_VIS_ROWS + score_delay:
			self.draw_changing_text('FINAL SCORE', loc_0, C.WHITE, background_color)
			self.draw_changing_text(f'{score}', loc_1, C.WHITE, background_color)
		if timer > initial_delay + step_size*C.BOARD_VIS_ROWS + score_delay*2:
			if mode == 1: self.best_of_five_messages(score, locs, match_score, p1)
			else: self.game_over_messages(score, locs)
		if timer > initial_delay + step_size*C.BOARD_VIS_ROWS + score_delay*3 and (other_game == True or other_game == None):
			if mode == 1 and (match_score[0] < 3 and match_score[1] < 3): self.draw_changing_text('NEXT GAME?', loc_6)
			else: self.draw_changing_text('RESTART?', loc_6)
			button_yes = self.draw_menu_text('Yes', button_loc_1, normal_font, display, True, shadow=False)
			button_no = self.draw_menu_text('No', button_loc_2, normal_font, display, True, shadow=False)

			# Actions that will be taken for each option.
			if button_yes.collidepoint((mx, my)):
				self.draw_menu_text('Yes', button_loc_1, normal_font, display, button=False, color=C.RED, shadow=False)
				if click:
					return False
			if button_no.collidepoint((mx, my)):
				self.draw_menu_text('No', button_loc_2, normal_font, display, button=False, color=C.RED, shadow=False)
				if click:
					return True

	def draw_pause_screen(self, board) -> None:
		"""
		Draw the pause screen on the specified game board.
		If the player presses pause (default: y-key), the pause screen should be drawn.

		Args:
			board: The game board to draw the pause screen on.

		Returns:
			None
		"""
		# Determine location for the word 'Pause'.
		loc = pg.Rect(board.rect.x, board.rect.y, board.rect.width, board.rect.height)

		# Draw 'Pause'.
		self.draw_rect(board, C.BBC)
		self.draw_changing_text('PAUSE', loc,
			C.WHITE, C.BBC)

	def __exit__(self, exc_type, exc_value, exc_trace) -> None:
		pg.display.update()