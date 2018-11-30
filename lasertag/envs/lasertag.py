import gym
import numpy as np

from gym import error, spaces, utils
from gym.utils import seeding
from lasertag.envs.game_implementation import make_game, COLOURS

# MACRO
NORTH = (-1, 0)
SOUTH = (1, 0)
EAST = (0, 1)
WEST = (0, -1)
FORWARD_VIEW = 17
BACKWARD_VIEW = 2
WEST_VIEW = 10
EAST_VIEW = 10

class LaserTag(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self):
        row = WEST_VIEW + EAST_VIEW + 1
        col = BACKWARD_VIEW + FORWARD_VIEW + 1

        self.action_space = spaces.Discrete(10)
        self.observation_space = spaces.Box(low=0, high=255, shape=(row, col, 3), dtype=np.uint8)

        self._obs = None
        self.viewer = None
    
    def step(self, action):
        (obs, _), reward, _ = self.game.play(action)
        done = self.game.game_over
        if reward is None:
            reward = np.array([0, 0])
        info = None

        # Save for rendering before converting obs to player's partial obs
        self._obs = self._obs_to_rgb(obs)

        partial_obs = (self.make_observation(obs, 1), self.make_observation(obs, 2))
        rgb_obs = (self._obs_to_rgb(partial_obs[0]), self._obs_to_rgb(partial_obs[1]))
        return rgb_obs, reward, done, info
    
    def seed(self, seed=None):
        np.random.seed(seed)
    
    def reset(self):
        self.game = make_game()
        (obs, _), _, _ = self.game.its_showtime()

        # Save for rendering before converting obs to player's partial obs
        self._obs = self._obs_to_rgb(obs)

        partial_obs = (self.make_observation(obs, 1), self.make_observation(obs, 2))
        rgb_obs = (self._obs_to_rgb(partial_obs[0]), self._obs_to_rgb(partial_obs[1]))
        return rgb_obs
    
    def render(self, mode='human', close=False):
        img = self._obs
        if mode == 'rgb_array':
            return img
        elif mode == 'human':
            from gym.envs.classic_control import rendering
            if self.viewer is None:
                self.viewer = rendering.SimpleImageViewer()
            img = self._repeat_upsample(img, 64, 64)
            self.viewer.imshow(img)
            if close:
                self.viewer.close()
            return self.viewer.isopen
    
    def close(self):
        if self.viewer is not None:
            self.viewer.close()
            self.viewer = None

    def make_observation(self, obs, player):
        """
        Convert raw observation to player's partial view observation.
        Rotate observation to make obs' EAST direction == player's direction
        """
        rotated_obs = self._rotate_obs(obs, player)
        padded_obs = self._pad_obs(rotated_obs)
        partial_obs = self._partial_obs(padded_obs, player)
        return partial_obs

    def _find_player(self, obs, player):
        player_ascii = ord('{}'.format(player))
        player_arr = (obs == player_ascii)
        if np.sum(player_arr) == 0:
            # TODO(Aiden): The only moment when player disappears is that they overlapped.
            #              How this moment could be avoided?
            player_ascii = ord('2' if player == 1 else '1')
            player_arr = (obs == player_ascii)
            assert np.sum(player_arr) == 1, "Error Here"

        player_index = np.where(player_arr)
        player_index = (player_index[0].item(), player_index[1].item())

        return player_index
    
    def _find_direction(self, obs, player):
        direction_chr = "R" if player == 1 else 'B'

        # TODO(Aiden): This is dirty hack to receive direction information
        #              directly from drape. This is not recommended.
        #              Is there any other way to improve?
        direction = self.game.things[direction_chr].directions
        return direction

    def _rotate_obs(self, obs, player):
        """
        Rotates observation in order to make NORTH meets player's direction
        """
        direction = self._find_direction(obs, player)
        if direction == NORTH:       # Rotate 270(-90)
            rot = -1
        elif direction == SOUTH:     # Rotate 90
            rot = 1
        elif direction == EAST:      # Rotate 0
            rot = 0
        elif direction == WEST:      # Rotate 180
            rot = 2
        else:
            assert False, "Direction Error. Direction is {}\nObs is {}".format(direction, obs)
        return np.rot90(obs, k=rot)

    def _pad_obs(self, obs):
        """
        Add padding to observation.
        Padding's value is set as '*', impassable wall in game.
        --------------------------------
        West : 10, East : 10      (10,10)
        Backward: 2, Forward: 17  (2, 17)
        """
        impassable_ascii = ord('*')

        new_obs = np.pad(array=obs,
                         pad_width=((WEST_VIEW, EAST_VIEW),
                                    (BACKWARD_VIEW, FORWARD_VIEW)),
                         mode='constant', constant_values=(impassable_ascii))
        return new_obs
    
    def _partial_obs(self, obs, player):
        """
        Crop observation with player's partial view.
        """
        player_index = self._find_player(obs, player)
        y, x = player_index

        y_start = y - WEST_VIEW
        y_end   = y + EAST_VIEW + 1
        x_start = x - BACKWARD_VIEW
        x_end   = x + FORWARD_VIEW + 1

        partial_obs = obs[y_start: y_end, x_start: x_end] # (y, x, rgb)
        return partial_obs

    def _colour_to_rgb(self, c):
        """
        Convert pycolab's COLOURS(0~999) to RGB(0~255)
        """
        c = tuple(int(element * 255 / 999) for element in c)
        return c
    
    def _obs_to_rgb(self, obs):
        """
        Convert observation with ascii code to observation with RGB channel
        """
        colours = {key: self._colour_to_rgb(value) for key, value in COLOURS.items()}
        new_obs = np.array(
            [[colours[chr(ascii_code)] for ascii_code in row] for row in obs], dtype=np.uint8
        )
        return new_obs

    def _repeat_upsample(self, rgb_array, k=1, l=1, err=[]):
        """
        This code is borrowed from https://github.com/openai/gym/issues/550

        Necessary for rendering. The size of map for LaserTag is very small.
        We should upsample image for rendering.
        """
        # repeat kinda crashes if k/l are zero
        if k <= 0 or l <= 0: 
            if not err: 
                print("Number of repeats must be larger than 0, k: {}, l: {}, returning default array!".format(k, l))
                err.append('logged')
            return rgb_array

        # repeat the pixels k times along the y axis and l times along the x axis
        # if the input image is of shape (m,n,3), the output image will be of shape (k*m, l*n, 3)
        return np.repeat(np.repeat(rgb_array, k, axis=0), l, axis=1)


class LaserTag_small2(LaserTag):
    metadata = {'render.modes': ['human']}
    def __init__(self):
        super(LaserTag_small2, self).__init__()
    
    def reset(self):
        self.game = make_game(size=0)
        (obs, _), _, _ = self.game.its_showtime()

        # Save for rendering before converting obs to player's partial obs
        self._obs = self._obs_to_rgb(obs)

        partial_obs = (self.make_observation(obs, 1), self.make_observation(obs, 2))
        rgb_obs = (self._obs_to_rgb(partial_obs[0]), self._obs_to_rgb(partial_obs[1]))
        return rgb_obs

class LaserTag_small3(LaserTag):
    metadata = {'render.modes': ['human']}
    def __init__(self):
        super(LaserTag_small3, self).__init__()
    
    def reset(self):
        self.game = make_game(size=1)
        (obs, _), _, _ = self.game.its_showtime()

        # Save for rendering before converting obs to player's partial obs
        self._obs = self._obs_to_rgb(obs)

        partial_obs = (self.make_observation(obs, 1), self.make_observation(obs, 2))
        rgb_obs = (self._obs_to_rgb(partial_obs[0]), self._obs_to_rgb(partial_obs[1]))
        return rgb_obs

class LaserTag_small4(LaserTag):
    metadata = {'render.modes': ['human']}
    def __init__(self):
        super(LaserTag_small4, self).__init__()
    
    def reset(self):
        self.game = make_game(size=2)
        (obs, _), _, _ = self.game.its_showtime()

        # Save for rendering before converting obs to player's partial obs
        self._obs = self._obs_to_rgb(obs)

        partial_obs = (self.make_observation(obs, 1), self.make_observation(obs, 2))
        rgb_obs = (self._obs_to_rgb(partial_obs[0]), self._obs_to_rgb(partial_obs[1]))
        return rgb_obs