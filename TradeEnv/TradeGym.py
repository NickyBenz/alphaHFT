import math
import numpy as np
import gymnasium as gym
from gymnasium import spaces
from Simulator.Strategy import Strategy


class TradeEnv(gym.Env):
    metadata = {"render_modes": ["human"]}

    def __init__(self, strategy: Strategy, verbose=1200, render_mode=None):
        assert strategy is not None
        assert render_mode is None or render_mode in self.metadata["render_modes"]
        self.interval_pnl = np.zeros(300)
        self.trades = np.zeros(300)
        self.verbose = verbose
        self.strategy = strategy
        self.info = {}
        self.steps = 0
        self.prev_features = None
        self.prev_books = None
        self.next_book = None
        self.observation_space = spaces.Box(-10.0,
                                            10.0,
                                            shape=(120, 40),
                                            dtype=np.float32)

        self.action_space = spaces.MultiDiscrete([3, 3])

    def get_final_obs(self):
        features = np.zeros((121, 38))
        books = np.zeros((121, 2))

        if self.prev_features is None:
            for i in range(120):
                obs = self._get_obs()
                features[i, :] = obs['features']
                books[i, :] = obs['book'].values
        else:
            features[:-1, :] = self.prev_features[1:, :]
            books[:-1, :] = self.prev_books[1:, :]

        obs = self._get_obs()
        features[-1, :] = obs['features']
        books[-1, :] = obs['book'].values
        feature_differences = np.hstack((features[1:, :], np.diff(books, axis=0)))
        obs['features'] = feature_differences
        self.prev_features = features
        self.prev_books = books
        self.next_book = obs['book']
        return obs

    def _get_obs(self):
        obs = self.strategy.get_observation()
        info = self.strategy.get_info(obs.loc["bid_price"], obs.loc["ask_price"])
        trading_pnl = info["trading_pnl_pct"]
        inventory_pnl = info["inventory_pnl_pct"]
        book = obs[["bid_price", "ask_price"]]
        idx = obs.index.drop(["bid_price", "ask_price"])
        mid_price = 0.5 * (book.loc["bid_price"] + book.loc["ask_price"])
        avg_price_pct = (info["avg_price"] - mid_price) / mid_price * 1000.0
        feature_len = obs.loc[idx].values.shape[0]
        features = np.zeros(feature_len + 4)
        features[:-4] = obs.loc[idx].values
        features[-1] = inventory_pnl / 100.0
        features[-2] = trading_pnl / 100.0
        features[-3] = avg_price_pct
        features[-4] = info["leverage"] / 100.0
        return {"book": book, "features": features}

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.strategy.reset(0)
        self.steps = 0
        self.prev_features = None
        self.prev_books = None
        self.next_book = None
        self.interval_pnl[:] = 0
        self.trades[:] = 0
        observation = self.get_final_obs()
        self.info = self.strategy.get_info(observation['book'].loc['bid_price'],
                                           observation['book'].loc['ask_price'])
        return observation['features'], self.info

    def step(self, action):
        # take actions
        self.steps += 1
        buy_multiplier = action[0]  # 0 - dont change, 1 - re quote, 2 - cancel
        sell_multiplier = action[1]  # 0 - dont change, 1 - re quote, 2 - cancel
        buy_ticks = 1  # action[2] + 1
        sell_ticks = 1  # action[3] + 1
        book = self.next_book
        bid_price = book.loc['bid_price']
        ask_price = book.loc['ask_price']

        if self.steps % 10 != 1:

            if buy_multiplier == 1:
                buy_multiplier = 0

            if sell_multiplier == 1:
                sell_multiplier = 0

        done = not self.strategy.quote(buy_ticks, sell_ticks, buy_multiplier, sell_multiplier)

        self.info = self.strategy.get_info(bid_price, ask_price)

        pnl = self.info["trading_pnl_pct"]
        inventory_pnl = self.info["inventory_pnl_pct"]
        leverage = self.info["leverage"]
        trade_num = self.info["trade_count"]
        done = done or (pnl + inventory_pnl) < -10 or leverage > 15
        leverage_punish = 1 - math.pow(2, leverage)
        reward = pnl + inventory_pnl

        if self.steps <= 300:
            self.interval_pnl[self.steps-1] = reward
            self.trades[self.steps-1] = trade_num
        else:
            sum_reward = np.diff(self.interval_pnl).sum()
            self.interval_pnl[:-1] = self.interval_pnl[1:]
            self.interval_pnl[-1] = reward
            reward = sum_reward - 0.0005
            sum_trades = np.diff(self.trades).sum()
            self.trades[:-1] = self.trades[1:]
            self.trades[-1] = trade_num
            reward += min(0, sum_trades - 1) * 10.0

        if done:
            print("backtest done")
            reward = reward + leverage_punish * 0.01
            self.print_info(reward)
        else:
            reward += leverage_punish * 0.01

            if self.steps % self.verbose == 0:
                self.print_info(reward)

        obs = self.get_final_obs()
        return obs['features'], reward, done, False, self.info

    def print_info(self, reward):
        op = {k: round(v, 2) for k, v in self.info.items()}
        op["reward"] = round(reward, 6)
        del op['balance']
        del op["avg_price"]
        op["steps"] = self.steps
        print(op)

    def render(self):
        pass
        # print("rendering: ")
        # print(self.info)

    def close(self):
        pass
