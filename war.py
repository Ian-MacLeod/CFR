import cfr


class WarGame:
    def __init__(self, troops, battlefields):
        self.troops = troops
        self.battlefields = battlefields

    def get_possible_actions(self):
        def gpa(troops, battlefields):
            if battlefields == 0:
                if troops == 0:
                    yield []
                return
            for i in range(troops + 1):
                for rest in gpa(troops - i, battlefields - 1):
                    rest.append(i)
                    yield rest
        return [tuple(a) for a in gpa(self.troops, self.battlefields)]

    def get_ev(self, my_action, opp_action):
        result = 0
        for my_troops, opp_troops in zip(my_action, opp_action):
            if my_troops > opp_troops:
                result += 1
            elif opp_troops > my_troops:
                result -= 1
        return result

    def __repr__(self):
        return ('WarGame(troops=' + str(self.troops) +
                ', battlefields=' + str(self.battlefields) + ')')


if __name__ == '__main__':
    war = WarGame(5, 3)
    p1 = cfr.Player(war)
    p2 = cfr.Player(war)
    trainer = cfr.OneTurnTrainer(p1, p2)
    trainer.train(100000)
    print(trainer)
