#-*- coding:utf-8 -*-
'''
    elo.py

    elo algorithm suggests using k = 16 for master, 32 for amateurs
    (k is the maximum rating change that can be yielded by a match)
'''

k = 24 # for intermediates
class Elo(object):
    def update(self, winner, losers):
        winner.score += sum(
            self.standard_elo(winner, loser, winner_delta=True)
                for loser in losers)
        winner.wins += 1

    @staticmethod
    def standard_elo(winner, loser, winner_delta=False):
        # elo rating algorithm
        rd1 = max(min(loser.score - winner.score, 400), -400)
        rd2 = max(min(winner.score - loser.score, 400), -400)

        e1 = 1./(1 + 10**(rd1/400.))
        e2 = 1./(1 + 10**(rd2/400.))

        s1, s2 = 1, 0

        loser.score += k*(s2 - e2)
        if winner_delta is False:
            winner.score += k*(s1 - e1)
        else:
            return k*(s1 - e1)
