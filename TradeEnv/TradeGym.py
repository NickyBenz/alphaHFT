import numpy as np
import gymnasium as gym
from gymnasium import spaces
from Simulator.Strategy import Strategy


class TradeEnv(gym.Env):
    metadata = {"render_modes": ["human"]}

    def __init__(self, strategy: Strategy, render_mode=None):
        assert strategy is not None
        assert render_mode is None or render_mode in self.metadata["render_modes"]

        self.strategy = strategy
        self.info = {}

        self.observation_space = spaces.Dict(
            {
                "book": spaces.Box(low=0,
                                   high=100000000,
                                   shape=(2,),
                                   dtype=np.float32),
                "features": spaces.Box(-10.0,
                                       10.0,
                                       shape=(30,),
                                       dtype=np.float32)
            }
        )

        self.action_space = spaces.MultiDiscrete([1,  # quote buy (y/n)
                                                  1,  # quote sell (y/n)
                                                  40,  # buy spread (ticks)
                                                  40,  # sell spread (ticks)
                                                  10,  # buy amount multiplier
                                                  10])  # sell amount multiplier

    def _get_obs(self):
        obs = self.strategy.get_observation()
        book = obs[["bid_price", "ask_price"]].values
        obs.index = obs.index.drop(["bid_price", "ask_price"])
        return {"book": book, "features": obs.values}

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        start_idx = np.random.randint(low=0, high=10000)
        self.strategy.reset(start_idx)
        observation = self._get_obs()
        self.info = self.strategy.get_info()
        return observation, self.info

    def step(self, action):
        # take actions
        quote_buy = action[0] > 0
        quote_sell = action[1] > 0
        buy_ticks = action[2]
        sell_ticks = action[3]
        buy_amount = action[4]
        sell_amount = action[5]

        done = self.strategy.quote(quote_buy, quote_sell, buy_ticks, sell_ticks, buy_amount, sell_amount)
        self.info = self.strategy.get_info()
        obs = self.strategy.get_observation()

        reward = self.info["pnlPct"]
        leverage = self.info["leverage"]
        truncated = not (reward > -0.02 and leverage < 0.8)

        if done:
            print("backtest done")
            print(self.info)
            reward *= 10.0

        elif truncated:
            print("backtest truncated")
            print(self.info)
            if leverage > 0.8:
                reward = -100
            else:
                reward = -1

        return obs, reward, done, truncated, self.info

    def render(self):
        if self.render_mode == "human":
            if self.strategy.order_id % 20 == 0:
                print(self.info)

    def close(self):
        pass
