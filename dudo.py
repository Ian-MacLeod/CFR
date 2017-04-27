import cfr
import random

CHALLENGE_FAIL_VALUE = 1
CHALLENGE_SUCCESS_VALUE = -1
seen_histories = {}


def generate_dudo_state():
    states = [(i, j) for i in range(6) for j in range(6)]
    return random.choice(states)


class DudoHistory:
    def __init__(self, claims, active_player):
        self.claims = claims
        self.active_player = active_player
        self.actions = self.get_actions()
        self.next_histories = dict([(action, self.next_history(action))
                                    for action in self.actions])

    def _get_last_claim(self):
        for i in reversed(range(len(self.claims))):
            if self.claims[i]:
                break
        else:
            return -1
        return i

    def get_actions(self):
        if self.claims[-1]:
            return []
        last_claim = self._get_last_claim()
        return list(range(last_claim + 1, len(self.claims)))

    def next_history(self, action):
        last_claim = self._get_last_claim()
        if action <= last_claim:
            raise ValueError('New claim must be stronger than the previous one')
        new_claims = list(self.claims)
        new_claims[action] = True
        new_history = DudoHistory(new_claims, 1 - self.active_player)
        h = hash(new_history)
        if h not in seen_histories:
            seen_histories[h] = new_history
        return seen_histories[h]

    def __hash__(self):
        return hash(tuple(self.claims))

    def __eq__(self, other):
        return self.claims == other.claims

    def get_infoset(self, dice):
        return (str(dice[self.active_player]) + ' | ' +
                str(self.claims))

    def is_terminal_history(self):
        return self.claims[-1]

    def evaluate_terminal_history(self, dice):
        for i in reversed(range(len(self.claims) - 1)):
            if self.claims[i]:
                break
        else:
            return CHALLENGE_FAIL_VALUE
        claim_num = i // 6 + 1
        claim_rank = i % 6
        if dice.count(claim_rank) >= claim_num:
            return CHALLENGE_FAIL_VALUE
        else:
            return CHALLENGE_SUCCESS_VALUE


if __name__ == '__main__':
    root_history = DudoHistory(([False] * 13), 0)
    trainer = cfr.Trainer(root_history, generate_dudo_state)
    print(trainer.train(1000))
