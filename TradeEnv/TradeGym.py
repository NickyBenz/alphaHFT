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
        self.observation_space = spaces.Box(-10.0,
                                            10.0,
                                            shape=(38,),
                                            dtype=np.float32)

        self.action_space = spaces.Box(low=np.array([-100.0, 1]),
                                       high=np.array([100.0, 200.0]),
                                       dtype=np.float32)

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
        observation = self._get_obs()
        self.info = self.strategy.get_info(observation['book'].loc['bid_price'],
                                           observation['book'].loc['ask_price'])
        return observation['features'], self.info

    def step(self, action):
        # take actions
        self.steps += 1
        reserve_spread = action[0]
        tick_spread = action[1]
        obs = self._get_obs()
        bid_price = obs['book'].loc['bid_price']
        ask_price = obs['book'].loc['ask_price']
        mid_price = 0.5 * (bid_price + ask_price)
        reserve_price = mid_price + reserve_spread
        buy_price = reserve_price - tick_spread
        sell_price = reserve_price + tick_spread
        buy_ticks = max(int(round((bid_price - buy_price) / 0.5)), 1)
        sell_ticks = max(int(round((sell_price - ask_price) / 0.5)), 1)
        done = not self.strategy.quote(buy_ticks, sell_ticks,
                                       1, 1)

        self.info = self.strategy.get_info(bid_price, ask_price)

        pnl = self.info["trading_pnl_pct"]
        inventory_pnl = self.info["inventory_pnl_pct"]
        leverage = self.info["leverage"]
        trade_num = self.info["trade_count"]
        truncated = not (pnl + min(0, inventory_pnl) > -1 and leverage < 1)

        if done:
            print("backtest done")
            reward = pnl - abs(leverage) + min(inventory_pnl, 0)
            self.print_info(reward)
        elif truncated:
            print("backtest truncated")
            reward = pnl - abs(leverage) + min(inventory_pnl, 0)
            self.print_info(reward)
            done = True
        else:
            lev_change = self.prev_leverage - leverage
            inventory_pnl_change = inventory_pnl - self.prev_inventory_pnl
            leverage_punish = 1 - 3.0 / (3.0 - leverage)
            reward = lev_change + inventory_pnl_change + leverage_punish
            self.prev_leverage = leverage
            self.prev_inventory_pnl = inventory_pnl

            if trade_num >= self.prev_trades + 1:
                reward += (pnl - self.prev_pnl) * 10.0
                self.prev_trades = trade_num
                self.prev_pnl = pnl

            if self.steps % 300 == 0:
                self.print_info(reward)

        return obs['features'], reward, done, truncated, self.info

    def print_info(self, reward):
        balance = self.info["balance"]
        op = {k: round(v, 2) for k, v in self.info.items()}
        op["reward"] = round(reward, 2)
        op["balance"] = round(balance, 4)
        del op["avg_price"]
        op["steps"] = self.steps
        print(op)

    def render(self):
        pass
        # print("rendering: ")
        # print(self.info)

    def close(self):
        pass
