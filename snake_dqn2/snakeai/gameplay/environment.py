
import time
import numpy as np
import pandas as pd
import pprint
from itertools import islice
from .entities import Point, Snake

class Environment(object):
    def __init__(self, config, verbose=1):
        """
        Create a new Snake RL environment.
        
        Args:
            config (dict): level configuration, typically found in JSON configs.  
            verbose (int): verbosity level:
                0 = do not write any debug information;
                1 = write a CSV file containing the statistics for every episode;
                2 = same as 1, but also write a full log file containing the state of each timestep.
        """
        self.snake = None
        self.fruit = None
        self.reward = config['reward']
        self.verbose = verbose
        self.debug_file = None
        self.stats_file = None
        self.max_step_limit = config.get('max_step_limit', 1000)
        self.size = config.get('size', 40)
        self.fov = config.get('fov', 9) // 2
        self.stats = EpisodeStatistics()
        self.is_game_over = False
        self.timestep_index = 0
        self.current_action = None

    def seed(self, value):
       np.random.seed(value)
    
    def newEpisode(self):
        self.snake = Snake(Point(np.random.randint(self.size), np.random.randint(self.size)))
        self.fruit = self.generateFruit()
        self.map = self.generateMap()
        self.stats.reset()

        result = TimestepResult(
            observation=self.getObservation(),
            reward=0,
            is_episode_end=self.is_game_over
        )

        self.record_timestep_stats(result)
        return result

    def record_timestep_stats(self, result):
        """ Record environment statistics according to the verbosity level. """
        timestamp = time.strftime('%Y%m%d-%H%M%S')

        # Write CSV header for the stats file.
        if self.verbose >= 1 and self.stats_file is None:
            self.stats_file = open(f'snake-env-{timestamp}.csv', 'w')
            stats_csv_header_line = self.stats.to_dataframe()[:0].to_csv(index=None)
            print(stats_csv_header_line, file=self.stats_file, end='', flush=True)

        # Create a blank debug log file.
        if self.verbose >= 2 and self.debug_file is None:
            self.debug_file = open(f'snake-env-{timestamp}.log', 'w')

        self.stats.record_timestep(self.current_action, result)
        self.stats.timesteps_survived = self.timestep_index

        if self.verbose >= 2:
            print(result, file=self.debug_file)

        # Log episode stats if the appropriate verbosity level is set.
        if result.is_episode_end:
            if self.verbose >= 1:
                stats_csv_line = self.stats.to_dataframe().to_csv(header=False, index=None)
                print(stats_csv_line, file=self.stats_file, end='', flush=True)
            if self.verbose >= 2:
                print(self.stats, file=self.debug_file)

    def generateFruit(self):
        pos = Point(np.random.randint(self.size), np.random.randint(self.size))
        while pos in self.snake.body:
            pos = Point(np.random.randint(self.size), np.random.randint(self.size))
        return pos

    def generateMap(self):
        field = np.zeros((self.size, self.size))
        for i in range(self.snake.length):
            field[self.snake.body[i]] = 1
        field[self.fruit] = 2
        return field

    def getObservation(self):
        return self.map[self.snake.head[0] - self.fov:self.snake.head[0] + self.fov + 1,
                        self.snake.head[1] - self.fov:self.snake.head[1] + self.fov + 1]

    def has_hit_wall(self):
        """ True if the snake has hit a wall, False otherwise. """
        return self.snake.head.x < 0 or self.snake.head.x >= 40 or self.snake.head.y < 0 or self.snake.head.y >= 40

    def has_hit_own_body(self):
        """ True if the snake has hit its own body, False otherwise. """
        return self.snake.head in islice(self.snake.body, 1, None)

    def is_alive(self):
        """ True if the snake is still alive, False otherwise. """
        return not self.has_hit_wall() and not self.has_hit_own_body()

    @property
    def shape(self):
        return self.map.shape

class TimestepResult(object):
    """ Represents the information provided to the agent after each timestep. """

    def __init__(self, observation, reward, is_episode_end):
        self.observation = observation
        self.reward = reward
        self.is_episode_end = is_episode_end

    def __str__(self):
        field_map = '\n'.join([
            ''.join(str(cell) for cell in row)
            for row in self.observation
        ])
        return f'{field_map}\nR = {self.reward}   end={self.is_episode_end}\n'

class EpisodeStatistics(object):
    """ Represents the summary of the agent's performance during the episode. """

    def __init__(self):
        self.reset()

    def reset(self):
        """ Forget all previous statistics and prepare for a new episode. """
        self.timesteps_survived = 0
        self.sum_episode_rewards = 0
        self.fruits_eaten = 0
        self.termination_reason = None
        self.action_counter = 0

    def record_timestep(self, action, result):
        """ Update the stats based on the current timestep results. """
        self.sum_episode_rewards += result.reward
        if action is not None:
            self.action_counter += 1

    def flatten(self):
        """ Format all episode statistics as a flat object. """
        flat_stats = {
            'timesteps_survived': self.timesteps_survived,
            'sum_episode_rewards': self.sum_episode_rewards,
            'mean_reward': self.sum_episode_rewards / self.timesteps_survived if self.timesteps_survived else None,
            'fruits_eaten': self.fruits_eaten,
            'termination_reason': self.termination_reason,
            'action_counter': self.action_counter
        }
        return flat_stats

    def to_dataframe(self):
        """ Convert the episode statistics to a Pandas data frame. """
        return pd.DataFrame([self.flatten()])

    def __str__(self):
        return pprint.pformat(self.flatten())