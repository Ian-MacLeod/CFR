import random


def get_action_from_strategy(strategy):
    r = random.uniform(0, 1)
    cumulative_probability = 0
    for action, action_weight in strategy.items():
        cumulative_probability += action_weight
        if cumulative_probability >= r:
            return action


class OneTurnTrainer:
    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2

    def train(self, iterations):
        for i in range(iterations):
            p1_action = self.p1.get_action()
            p2_action = self.p2.get_action()
            self.p1.update_regrets(p1_action, p2_action)
            self.p2.update_regrets(p2_action, p1_action)

    def get_average_strategies(self):
        return {'p1': self.p1.get_average_strategy(),
                'p2': self.p2.get_average_strategy()}

    def __repr__(self):
        return '\n'.join(['CFR Trainer object',
                          'Player 1', str(self.p1),
                          '--------------------------',
                          'Player 2', str(self.p2)])


class Player:
    def __init__(self, game):
        self.game = game
        self.actions = game.get_possible_actions()
        self.regret_sum = dict([(action, 0) for action in self.actions])
        self.strategy_sum = dict([(action, 0) for action in self.actions])

    def get_action(self):
        strategy = {}
        normalizing_sum = 0
        for a in self.actions:
            strategy[a] = self.regret_sum[a] if self.regret_sum[a] > 0 else 0
            normalizing_sum += strategy[a]
        for a in self.actions:
            if normalizing_sum > 0:
                strategy[a] /= normalizing_sum
            else:
                strategy[a] = 1 / len(self.actions)
            self.strategy_sum[a] += strategy[a]
        return get_action_from_strategy(strategy)

    def update_regrets(self, my_action, opp_action):
        for a in self.actions:
            self.regret_sum[a] += (self.game.get_ev(a, opp_action)
                                   - self.game.get_ev(my_action, opp_action))

    def get_average_strategy(self):
        normalizing_sum = sum(self.strategy_sum.values())
        if normalizing_sum <= 0:
            return [1 / len(self.actions) for _ in range(len(self.actions))]
        return [(action, weight / normalizing_sum)
                for action, weight in self.strategy_sum.items()]

    def __repr__(self):
        return '\n'.join(['Player object for game:', str(self.game), 'Trained strategy:']
                         + [str(t) for t in self.get_average_strategy()])


class StrategyNode:
    def __init__(self, name, actions):
        self.name = name
        self.actions = actions
        self.regret_sum = [0] * len(actions)
        self.strategy_sum = [0] * len(actions)

    def get_strategy(self, realization_weight):
        strategy = [max(0, r) for r in self.regret_sum]
        normalizing_sum = sum(strategy)
        for i in range(len(self.actions)):
            if normalizing_sum > 0:
                strategy[i] /= normalizing_sum
            else:
                strategy[i] = 1 / len(self.actions)
            self.strategy_sum[i] += realization_weight * strategy[i]
        return zip(strategy, self.actions)

    def get_average_strategy(self):
        normalizing_sum = sum(self.strategy_sum)
        if normalizing_sum > 0:
            return [s / normalizing_sum for s in self.strategy_sum]
        else:
            return [1 / normalizing_sum for _ in self.strategy_sum]

    def __repr__(self):
        return str(self.name) + ': ' + str(self.get_average_strategy()) + '\n'


class Trainer:
    def __init__(self, root_history, state_gen):
        self.root_history = root_history
        self.state_gen = state_gen
        self.node_map = {}

    def train(self, iterations):
        util = 0
        for _ in range(iterations):
            self.state = self.state_gen()
            util += self.cfr(self.root_history, 1, 1)
        return 'Average game value: ' + str(util / iterations)

    def cfr(self, history, p0, p1):
        if history.is_terminal_history():
            return history.evaluate_terminal_history(self.state)

        infoset = history.get_infoset(self.state)
        if infoset not in self.node_map:
            self.node_map[infoset] = StrategyNode(infoset, history.actions)
        node = self.node_map[infoset]

        strategy = node.get_strategy(p0 if history.active_player == 0 else p1)
        util = []
        node_util = 0
        for weight, action in strategy:
            if history.active_player == 0:
                util.append(-self.cfr(history.next_histories[action], p0 * weight, p1))
            else:
                util.append(-self.cfr(history.next_histories[action], p0, p1 * weight))
            node_util += weight * util[-1]
        for i in range(len(util)):
            regret = util[i] - node_util
            node.regret_sum[i] += (p1 if history.active_player == 0 else p0) * regret

        return node_util
