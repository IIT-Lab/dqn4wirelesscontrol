from collections import deque
from numpy import max, abs, exp
from numpy.random import rand, randint, multinomial
import pandas as pd
import matplotlib.pyplot as plt


class SimpleMaze:
    def __init__(self):
        self.actions = ['left', 'right', 'up', 'down']
        self.dims = (4, 5)
        self.goal_state = (2, 2)
        self.state = None
        self.reset()

    def observe(self):
        return self.state

    def interact(self, action):
        next_state, reward = self.transition_(self.state, action)
        self.state = next_state
        return next_state, reward

    def transition_(self, current_state, action):
        if current_state == self.goal_state:
            return current_state, 0
        elif action == 'left':
            next_state = current_state if current_state[1] == 0 else (current_state[0], current_state[1]-1)
        elif action == 'up':
            next_state = current_state if current_state[0] == 0 else (current_state[0]-1, current_state[1])
        elif action == 'right':
            next_state = current_state if current_state[1] == (self.dims[1]-1) else (current_state[0], current_state[1]+1)
        elif action == 'down':
            next_state = current_state if current_state[0] == (self.dims[0]-1) else (current_state[0]+1, current_state[1])
        else:
            print 'I don\'t understand this action, I\'ll stay.'
            next_state = current_state
        reward = 100 if next_state == self.goal_state else 0
        return next_state, reward

    def reset(self):
        next_state = self.goal_state
        while next_state == self.goal_state:
            next_state = (randint(0, self.dims[0]), randint(0, self.dims[1]))
        self.state = next_state

    def finished(self):
        return self.state == self.goal_state


class QAgent(object):
    def __init__(self, actions, alpha=1.0, gamma=0.5, epsilon=0.0, explore_strategy='fixed_epsilon', init_state=None):
        # static attributes
        self.ACTIONS = actions
        self.ALPHA = alpha  # learning rate
        self.GAMMA = gamma  # discount factor
        self.EPSILON = epsilon  # exploration probability
        self.DEFAULT_QVAL = 0  # default initial value for Q table entries
        self.EXPLORE = explore_strategy
        # dynamic attributes
        self.current_state = init_state
        self.current_action = None
        self.q_table = {}

    def act(self):
        if self.EXPLORE == 'fixed_epsilon':
            if rand() < self.EPSILON:  # random exploration with "epsilon" prob.
                idx_action = randint(0, len(self.ACTIONS))
            else:  # select the best action with "1-epsilon" prob., break tie randomly
                q_vals = self.lookup_table_(self.current_state)
                max_qval = max(q_vals)
                idx_best_actions = [i for i in range(len(q_vals)) if q_vals[i] == max_qval]
                idx_action = idx_best_actions[randint(0, len(idx_best_actions))]
        elif self.EXPLORE == 'soft_probability':
                q_vals = self.lookup_table_(self.current_state)
                exp_q_vals = exp(q_vals)
                idx_action = multinomial(1, exp_q_vals/sum(exp_q_vals)).nonzero()[0][0]
        else:
            raise ValueError('Unknown keyword for exploration strategy!')
        self.current_action = self.ACTIONS[idx_action]
        return self.current_action

    def lookup_table_(self, state):
        # return q values of all actions at given state
        return [self.q_table[(state, a)] if (state, a) in self.q_table else self.DEFAULT_QVAL for a in self.ACTIONS]

    def reinforce(self, new_state, reward):
        update_result = self.update_table_(new_state, reward)
        self.current_state = new_state
        return update_result

    def update_table_(self, new_state, reward):
        current_state = self.current_state
        current_action = self.current_action
        best_qval = max(self.lookup_table_(new_state))
        delta_q = reward + self.GAMMA * best_qval
        self.q_table[(current_state, current_action)] = self.ALPHA * delta_q + (1 - self.ALPHA) * self.q_table[(current_state, current_action)] if (current_state, current_action) in self.q_table else self.DEFAULT_QVAL
        return None

    def reset(self, init_state=None, foget_table=False):
        self.current_state = init_state
        self.current_action = None
        if foget_table:
            self.q_table = {}


if __name__ == "__main__":
    maze = SimpleMaze()
    agent = QAgent(actions=maze.actions, alpha=0.5, gamma=0.5, explore_strategy='fixed_epsilon', epsilon=0.2)
    # logging
    path = deque()  # path in this episode
    episode_reward_rates = []
    num_episodes = 0
    cum_reward = 0
    cum_steps = 0

    # repeatedly run episodes
    while True:
        maze.reset()
        new_state = maze.observe()
        agent.reset(init_state=new_state)

        path.clear()
        path.append(new_state)
        episode_reward = 0
        episode_steps = 0

        # interact and reinforce repeatedly
        while not maze.finished():
            action = agent.act()
            new_state, reward = maze.interact(action)
            agent.reinforce(new_state=new_state, reward=reward)

            path.append(new_state)
            episode_reward += reward
            episode_steps += 1

        cum_steps += episode_steps
        cum_reward += episode_reward
        num_episodes += 1
        episode_reward_rates.append(episode_reward / episode_steps)
        if num_episodes % 100 == 0:
            print num_episodes, len(agent.q_table), 1.0 * cum_reward / cum_steps, path
    win = 50
    # s = pd.rolling_mean(pd.Series([0]*win+episode_reward_rates), window=win, min_periods=1)
    # s.plot()
    # plt.show()
