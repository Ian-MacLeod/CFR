import cfr


class RPSGame:
    NUM_ACTIONS = 3

    def get_possible_actions(self):
        return (0, 1, 2)

    def get_ev(self, action, opp_action):
        if action == opp_action:
            return 0
        elif action == (opp_action + 1) % self.NUM_ACTIONS:
            return 1
        elif action == (opp_action - 1) % self.NUM_ACTIONS:
            return -1

    def __repr__(self):
        return "RPSGame object"


if __name__ == '__main__':
    rps = RPSGame()
    p1 = cfr.Player(rps)
    p2 = cfr.Player(rps)
    trainer = cfr.OneTurnTrainer(p1, p2)
    trainer.train(100000)
    print(trainer)
