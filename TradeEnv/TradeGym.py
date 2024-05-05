import math
import numpy as np
import gymnasium as gym
from gymnasium import spaces
from Simulator.Strategy import Strategy


class TradeEnv(gym.Env):
    metadata = {"render_modes": ["human"]}

    def __init__(self, strategy: Strategy, render_mode=None):
        assert strategy is not None
        assert render_mode is None or render_mode in self.metadata["render_modes"]
        self.prev_pnl = 0
        self.prev_trades = 0
        self.prev_leverage = 0
        self.prev_inventory_pnl = 0
        self.strategy = strategy
        self.info = {}
        self.steps = 0
        self.prev_features = None
        self.observation_space = spaces.Box(-10.0,
                                            10.0,
                                            shape=(60, 38),
                                            dtype=np.float32)

        self.action_space = spaces.MultiDiscrete([3, 3])

    def get_final_obs(self):
        features = np.zeros((60, 38))
        if self.prev_features is None:
            for i in range(59):
                obs = self._get_obs()
                features[i, :] = obs['features']
        else:
            features[:-1, :] = self.prev_features[1:, :]

        obs = self._get_obs()
        features[-1, :] = obs['features']
        obs['features'] = features
        self.prev_features = features
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
        features[-1] = inventory_pnl
        features[-2] = trading_pnl
        features[-3] = avg_price_pct
        features[-4] = info["leverage"] / 10.0
        return {"book": book, "features": features}

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.strategy.reset(0)
        self.steps = 0
        self.prev_pnl = 0
        self.prev_trades = 0
        self.prev_leverage = 0
        self.prev_inventory_pnl = 0
        self.prev_features = None

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
        obs = self.get_final_obs()
        bid_price = obs['book'].loc['bid_price']
        ask_price = obs['book'].loc['ask_price']
        done = not self.strategy.quote(buy_ticks, sell_ticks, buy_multiplier, sell_multiplier)

        self.info = self.strategy.get_info(bid_price, ask_price)

        pnl = self.info["trading_pnl_pct"]
        inventory_pnl = self.info["inventory_pnl_pct"]
        leverage = self.info["leverage"]
        trade_num = self.info["trade_count"]
        truncated = not (pnl + min(0, inventory_pnl) > -10 and leverage < 50)

        leverage_punish = 1 - math.pow(2, leverage)
        trade_intensity = trade_num / self.steps
        reward = min(trade_intensity - 0.01, 0) if self.steps > 300 else 0

        if done:
            print("backtest done")
            reward += 10 * (pnl + inventory_pnl) - leverage_punish * 0.05
            if trade_num / self.steps < 0.005:
                reward -= 1
            self.print_info(reward)
        elif truncated:
            print("backtest truncated")
            reward -= 100
            self.print_info(reward)
            done = True
        else:
            reward += min(0, inventory_pnl) + leverage_punish * 0.05
            self.prev_leverage = leverage
            self.prev_inventory_pnl = inventory_pnl

            if trade_num > self.prev_trades + 4:
                reward += pnl - self.prev_pnl
                self.prev_trades = trade_num
                self.prev_pnl = pnl

            if self.steps % 10800 == 0:
                self.print_info(reward)

        return obs['features'], reward, done, truncated, self.info

    def print_info(self, reward):
        op = {k: round(v, 2) for k, v in self.info.items()}
        op["reward"] = round(reward, 2)
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
