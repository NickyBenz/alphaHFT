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
        self.strategy = strategy
        self.info = {}
        self.steps = 0
        self.observation_space = spaces.Box(-10.0,
                                            10.0,
                                            shape=(38,),
                                            dtype=np.float32)

        self.action_space = spaces.MultiDiscrete([2,  # quote buy cancel (y/n)
                                                  2,  # quote sell cancel (y/n)
                                                  2,  # buy spread (ticks)
                                                  2,  # sell spread (ticks)
                                                  2,  # buy amount multiplier
                                                  2])  # sell amount multiplier

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
        observation = self._get_obs()
        self.info = self.strategy.get_info(observation['book'].loc['bid_price'],
                                           observation['book'].loc['ask_price'])
        return observation['features'], self.info

    def step(self, action):
        # take actions
        self.steps += 1
        quote_buy_cancel = action[0] > 0
        quote_sell_cancel = action[1] > 0
        buy_ticks = action[2] + 2
        sell_ticks = action[3] + 2
        buy_amount = action[4]
        sell_amount = action[5]

        done = not self.strategy.quote(quote_buy_cancel, quote_sell_cancel,
                                       buy_ticks, sell_ticks,
                                       buy_amount, sell_amount)

        obs = self._get_obs()
        self.info = self.strategy.get_info(obs['book'].loc['bid_price'],
                                           obs['book'].loc['ask_price'])

        pnl = self.info["trading_pnl_pct"]
        leverage = self.info["leverage"]
        trade_num = self.info["trade_count"]
        truncated = not (pnl > -5 and leverage < 25)
        inventory_pnl = self.info["inventory_pnl_pct"]

        if done:
            print("backtest done")
            reward = pnl - abs(leverage) + min(inventory_pnl, 0)

            if reward == 0:
                reward = -10

            self.print_info(reward)

        elif truncated:
            print("backtest truncated")
            reward = pnl - abs(leverage) + min(inventory_pnl, 0)
            self.print_info(reward)
            done = True
        else:
            if trade_num > self.prev_trades:
                reward = pnl - self.prev_pnl - abs(leverage) + min(inventory_pnl, 0)
                self.prev_trades = trade_num
                self.prev_pnl = pnl
            else:
                reward = -abs(leverage) + min(inventory_pnl, 0)

            if self.steps % 1200 == 0:
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
