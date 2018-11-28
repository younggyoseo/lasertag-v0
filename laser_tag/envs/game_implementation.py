from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import random
import enum
import numpy as np
from copy import deepcopy

from pycolab import things as plab_things
from pycolab.prefab_parts import sprites as prefab_sprites
from pycolab import human_ui
from pycolab import ascii_art

LEVELS = [
    ['*********',
     '*P     P*',
     '*       *',
     '*  * *  *',
     '* ** ** *',
     '*  * *  *',
     '*       *',
     '*P     P*',
     '*********'],

     ['****************',
      '*P        * *P *',
      '* **   *       *',
      '* *  *       * *',
      '*        *     *',
      '* *            *',
      '* P  *     *   *',
      '*  *          P*',
      '****************'],

      ['**********************',
       '*P        * *P       *',
       '* **   *          P  *',
       '* *  *       *       *',
       '*        *          **',
       '* *               *  *',
       '* P  *      *        *',
       '*  *                P*',
       '*               *    *',
       '*     P              *',
       '*                    *',
       '*      *      P      *',
       '**                   *',
       '**********************'],
]

COLOURS = {'P': (0, 0, 0),        # Respawn
           '1': (999, 0, 0),      # Red Player
           '2': (0, 0, 999),      # Blue Player
           'R': (600, 200, 200),  # Direction of Red Player
           'B': (200, 200, 600),  # Direction of Blue Player
           'r': (700, 400, 400),  # Laser of Red Player
           'b': (400, 400, 700),  # Laser of Blue Player
           '*': (500, 500, 500),  # Impassable wall
           ' ': (0, 0, 0),        # Black background  
}

class Actions(enum.IntEnum):
    """Actions for agent movement."""
    FORWARD = 0
    BACKWARD = 1
    STEP_LEFT = 2
    STEP_RIGHT = 3
    TURN_LEFT = 4
    TURN_RIGHT = 5
    FORWARD_LEFT = 6
    FORWARD_RIGHT = 7
    BEAM = 8

    # This will not be used by agent
    STAY = 9


def random_level(level):
    my_level = deepcopy(level)
    indices = []
    for row, line in enumerate(my_level):
        for col, char in enumerate(line):
            if char == 'P':
                indices.append((row,col))

    num_spawns = len(indices)
    rand_indices = np.random.choice(num_spawns, 2, replace=False)

    new_chars = [' '] * num_spawns
    new_chars[rand_indices[0]] = '1'
    new_chars[rand_indices[1]] = '2'

    for idx, (row, col) in enumerate(indices):
        my_level[row] = my_level[row][:col] + new_chars[idx] + my_level[row][col+1:]

    return my_level

def make_game(size=0):
    """Build and returns a game of LaserTag."""
    return ascii_art.ascii_art_to_game(
        random_level(LEVELS[size]), what_lies_beneath=' ',
        sprites={
            '1': PlayerSprite,
            '2': PlayerSprite},
        drapes={
            'R': DirectionDrape,
            'B': DirectionDrape,
            'r': LaserDrape,
            'b': LaserDrape},
        update_schedule=[['1', '2'], ['R', 'B'], ['r', 'b']],
        z_order = ['R', 'B', 'r', 'b', '1', '2'])

class PlayerSprite(prefab_sprites.MazeWalker):
    
    def __init__(self, corner, position, character):
        if character == '1':
            impassable = '*2'
        else:
            impassable = '*1'
        super(PlayerSprite, self).__init__(
            corner, position, character, impassable=impassable, confined_to_board=True)
        self.directions = None

    def update(self, actions, board, layers, backdrop, things, the_plot):
        if actions is not None:
            p_actions = actions[self.character]
        else:
            p_actions = None
        if p_actions is None:                     # Initialization
            self._set_initial_direction(board, the_plot)
        elif p_actions == Actions.FORWARD:
            self._forward(board, the_plot)
        elif p_actions == Actions.BACKWARD:
            self._backward(board, the_plot)
        elif p_actions == Actions.STEP_LEFT:
            self._step_left(board, the_plot)
        elif p_actions == Actions.STEP_RIGHT:
            self._step_right(board, the_plot)
        elif p_actions == Actions.TURN_LEFT:
            self._turn_left(board, the_plot)
        elif p_actions == Actions.TURN_RIGHT:
            self._turn_right(board, the_plot)
        elif p_actions == Actions.FORWARD_LEFT:
            self._forward(board, the_plot)
            self._turn_left(board, the_plot)
        elif p_actions == Actions.FORWARD_RIGHT:
            self._forward(board, the_plot)
            self._turn_right(board, the_plot)
        else:  # STAY or BEAM 
            self._stay(board, the_plot)

    def _turn_left(self, board, the_plot):
        if self.directions == self._NORTH:
            chk = self._check_motion(board, self._WEST, is_turn=True)
            if not chk: self.directions = self._WEST
        elif self.directions == self._SOUTH:
            chk = self._check_motion(board, self._EAST, is_turn=True)
            if not chk: self.directions = self._EAST
        elif self.directions == self._WEST:
            chk = self._check_motion(board, self._SOUTH, is_turn=True)
            if not chk: self.directions = self._SOUTH
        elif self.directions == self._EAST:
            chk = self._check_motion(board, self._NORTH, is_turn=True)
            if not chk: self.directions = self._NORTH

    def _turn_right(self, board, the_plot):
        if self.directions == self._NORTH:
            chk = self._check_motion(board, self._EAST, is_turn=True)
            if not chk: self.directions = self._EAST
        elif self.directions == self._SOUTH:
            chk = self._check_motion(board, self._WEST, is_turn=True)
            if not chk: self.directions = self._WEST
        elif self.directions == self._WEST:
            chk = self._check_motion(board, self._NORTH, is_turn=True)
            if not chk: self.directions = self._NORTH
        elif self.directions == self._EAST:
            chk = self._check_motion(board, self._SOUTH, is_turn=True)
            if not chk: self.directions = self._SOUTH

    def _forward(self, board, the_plot):
        if self.directions == self._NORTH:
            self._move(board, the_plot, self._NORTH)
        elif self.directions == self._SOUTH:
            self._move(board, the_plot, self._SOUTH)
        elif self.directions == self._WEST:
            self._move(board, the_plot, self._WEST)
        elif self.directions == self._EAST:
            self._move(board, the_plot, self._EAST)
        else:
            assert False, "Direction is not set!"
    
    def _backward(self, board, the_plot):
        if self.directions == self._NORTH:
            self._move(board, the_plot, self._SOUTH)
        elif self.directions == self._SOUTH:
            self._move(board, the_plot, self._NORTH)
        elif self.directions == self._WEST:
            self._move(board, the_plot, self._EAST)
        elif self.directions == self._EAST:
            self._move(board, the_plot, self._WEST)
        else:
            assert False, "Direction is not set!"
    
    def _step_left(self, board, the_plot):
        if self.directions == self._NORTH:
            self._move(board, the_plot, self._WEST)
        elif self.directions == self._SOUTH:
            self._move(board, the_plot, self._EAST)
        elif self.directions == self._WEST:
            self._move(board, the_plot, self._SOUTH)
        elif self.directions == self._EAST:
            self._move(board, the_plot, self._NORTH)
        else:
            assert False, "Direction is not set!"

    def _step_right(self, board, the_plot):
        if self.directions == self._NORTH:
            self._move(board, the_plot, self._EAST)
        elif self.directions == self._SOUTH:
            self._move(board, the_plot, self._WEST)
        elif self.directions == self._WEST:
            self._move(board, the_plot, self._NORTH)
        elif self.directions == self._EAST:
            self._move(board, the_plot, self._SOUTH)
        else:
            assert False, "Direction is not set! at {}".format(self.directions)

    def _set_initial_direction(self, board, the_plot):
        north_check = self._check_motion(board, self._NORTH)
        south_check = self._check_motion(board, self._SOUTH)
        east_check = self._check_motion(board, self._EAST)
        west_check = self._check_motion(board, self._WEST)

        available_directions = []
        if not north_check:
            available_directions.append(self._NORTH)
        if not south_check:
            available_directions.append(self._SOUTH)
        if not east_check:
            available_directions.append(self._EAST)
        if not west_check:
            available_directions.append(self._WEST)
        
        if len(available_directions) == 0:
            assert False, "{}_{}_{}_{}".format(north_check, south_check, east_check, west_check)

        self.directions = random.sample(available_directions, 1)[0]
    
    def _check_motion(self, board, motion, is_turn=False):
        """Deterimine whether `motion` is legal for this `MazeWalker`.
        Computes whether the single-cell motion in `motion` would be legal for
        this `MazeWalker` to execute. Reasons it might not be legal include: a
        pattern of impassable characters is in the way, or for `MazeWalker`s
        confined to the game board, the edge of the game board may be blocking.
        Args:
        board: a 2-D numpy array with dtype `uint8` containing the completely
            rendered game board from the last board repaint (which usually means
            the last game iteration; see `Engine` docs for details).
        motion: A 2-tuple containing the motion as `(δrow, δcol)`.
        Returns:
        None if the motion is executed successfully; otherwise, a tuple (for
        diagonal motions) or a single-character ASCII string (for motions in
        "cardinal direction") describing the obstruction blocking the
        `MazeWalker`. See class docstring for details.
        """

        def at(coords):
            """Report character at egocentric `(row, col)` coordinates."""
            drow, dcol = coords
            new_row = self._virtual_row + drow
            new_col = self._virtual_col + dcol
            if not self._on_board(new_row, new_col): return self.EDGE
            return chr(board[new_row, new_col])

        def is_impassable(char, is_turn=False, step=1):
            """Return True if `char` is impassable to this `MazeWalker`.

               --------------------------------------------------------
               Modified: Look one step further to inverstigate whether
                         another agent is in the way.
               --------------------------------------------------------"""
            if step == 1:
                impassable = self._impassable
                if is_turn: impassable = impassable.difference({"B", "R"})
                return ((self._confined_to_board and (char is self.EDGE)) or
                        (char in impassable))
            else:
                return char in {'1', '2'}

        # Investigate all of the board positions that could keep this MazeWalker
        # from executing the desired motion. Math is hard, so we just hard-code
        # relative positions for each type of permissible motion.

        # Modified: For _NORTH, _EAST, _WEST, _SOUTH, We will see one step further

        if motion == self._STAY:
            return None  # Moving nowhere is always fine.
        elif motion == self._NORTHWEST:    # ↖
            neighbs = at(self._WEST), at(self._NORTHWEST), at(self._NORTH)
        elif motion == self._NORTH:        # ↑
            neighbs = at(self._NORTH), at(tuple(elem * 2 for elem in self._NORTH))
        elif motion == self._NORTHEAST:    # ↗
            neighbs = at(self._NORTH), at(self._NORTHEAST), at(self._EAST)
        elif motion == (self._EAST):       # →
            neighbs = at(self._EAST), at(tuple(elem * 2 for elem in self._EAST))
        elif motion == (self._SOUTHEAST):  # ↘
            neighbs = at(self._EAST), at(self._SOUTHEAST), at(self._SOUTH)
        elif motion == (self._SOUTH):      # ↓
            neighbs = at(self._SOUTH), at(tuple(elem * 2 for elem in self._SOUTH))
        elif motion == (self._SOUTHWEST):  # ↙
            neighbs = at(self._SOUTH), at(self._SOUTHWEST), at(self._WEST)
        elif motion == (self._WEST):       # ←
            neighbs = at(self._WEST), at(tuple(elem * 2 for elem in self._WEST))
        else:
            assert False, 'illegal motion {}'.format(motion)

        # Determine whether there are impassable obstacles in the neighbours. If
        # there are, return the full array of neighbours.
        if all(motion):  # If the motion is diagonal:
            if is_impassable(neighbs[1], is_turn): return neighbs
            if is_impassable(neighbs[0], is_turn) and is_impassable(neighbs[2], is_turn): return neighbs
        else:  # Otherwise, if the motion is "cardinal":
        ##############################################################
        # TODO(Aiden): Is there other way to elaborate these lines?  #
        ##############################################################
            if is_turn:
                # If this check is for turning, there is no need to check step 2
                if is_impassable(neighbs[0], is_turn): return neighbs
            else:         
                if is_impassable(neighbs[0], is_turn) or is_impassable(neighbs[1], step=2): return neighbs
        # There are no obstacles; we're free to proceed.
        return None

class DirectionDrape(plab_things.Drape):
    """Drape for Direction."""
    
    def __init__(self, curtain, character):
        super(DirectionDrape, self).__init__(curtain, character)
        if self.character == 'R':
            self.player = '1'
        elif self.character == 'B':
            self.player = '2'
        self.directions = None

    def update(self, actions, board, layers, backdrop, things, the_plot):
        ply_y, ply_x = things[self.player].position
        directions = things[self.player].directions
        dy, dx = directions[0], directions[1]

        cur_y, cur_x = ply_y + dy, ply_x + dx
        self.curtain.fill(False)
        if not layers['*'][cur_y, cur_x]:
            self.curtain[cur_y, cur_x] = True
        
        self.directions = directions

class LaserDrape(plab_things.Drape):
    """Drape for Laser."""

    def __init__(self, curtain, character):
        super(LaserDrape, self).__init__(curtain, character)
        if self.character == 'r':
            self.player = '1'
        elif self.character == 'b':
            self.player = '2'
        
        self.tagged = {'1': 0, '2': 0}
        self._lasers = []
        self._reward = np.array([0, 0])
    
    def update(self, actions, board, layers, backdrop, things, the_plot):
        if actions is None:
            return
        self._lasers.clear()
        self.curtain.fill(False)
        p_actions = actions[self.player]
        if p_actions != Actions.BEAM:
            return
        ply_y, ply_x = things[self.player].position
        directions = things[self.player].directions
        dy, dx = directions[0], directions[1]
        
        opponent = [player for player in ['1', '2'] if player != self.player][0]
        height, width = layers[self.player].shape
        for step in range(1, max(height, width)):
            cur_x = ply_x + dx * step
            cur_y = ply_y + dy * step
            if cur_x < 0 or cur_x >= width or cur_y < 0 or cur_y >= height:
                # Out of bounds, beam went nowhere
                break
            elif layers['*'][cur_y, cur_x]:
                # Hit an impassable wall
                break
            elif layers[opponent][cur_y, cur_x]:
                self.tagged[opponent] += 1
                if self.player == '1':
                    reward = np.array([1, 0])
                else:
                    reward = np.array([0, 1])
                the_plot.add_reward(reward)
                break
            else:
                self._lasers.append((cur_y, cur_x))
        
        self.curtain.fill(False)
        for laser in self.lasers:
            self.curtain[laser] = True
        
        if 2 in self.tagged.values():
            the_plot.terminate_episode()
        
    @property
    def lasers(self):
        """Returns locations of all lasers in the map."""
        return tuple(a for a in self._lasers if a is not None)


def main():
    # Build a game of LaserTag.
    game = make_game()
    
    # Make a CursesUi to play it with.
    ui = human_ui.CursesUi(
        # Multi-agent arguments don't have to be dicts---they can be just about
        # anything; numpy arrays, scalars, nests, whatever.
    keys_to_actions={
        'w': {'1': Actions.FORWARD, '2': Actions.STAY},
        's': {'1': Actions.BACKWARD, '2': Actions.STAY},
        'a': {'1': Actions.STEP_LEFT, '2': Actions.STAY},
        'd': {'1': Actions.STEP_RIGHT, '2': Actions.STAY},
        'q': {'1': Actions.TURN_LEFT, '2': Actions.STAY},
        'e': {'1': Actions.TURN_RIGHT, '2': Actions.STAY},
        'z': {'1': Actions.FORWARD_LEFT, '2': Actions.STAY},
        'c': {'1': Actions.FORWARD_RIGHT, '2': Actions.STAY},
        'x': {'1': Actions.BEAM, '2': Actions.STAY},
        't': {'1': Actions.STAY, '2': Actions.FORWARD},
        'g': {'1': Actions.STAY, '2': Actions.BACKWARD},
        'f': {'1': Actions.STAY, '2': Actions.STEP_LEFT},
        'h': {'1': Actions.STAY, '2': Actions.STEP_RIGHT},
        'r': {'1': Actions.STAY, '2': Actions.TURN_LEFT},
        'y': {'1': Actions.STAY, '2': Actions.TURN_RIGHT},
        'v': {'1': Actions.STAY, '2': Actions.FORWARD_LEFT},
        'n': {'1': Actions.STAY, '2': Actions.FORWARD_RIGHT},
        'b': {'1': Actions.STAY, '2': Actions.BEAM}
    },
    delay=33, colour_fg=COLOURS)

    ui.play(game)


if __name__ == '__main__':
    main()