#-*- coding:utf-8 -*-
'''
    elo.py

    defines the class Elo
    * use _match_algo_strict for Modified Elo Rating Algorithm
    * use _match_algo_elo for Standard Elo Rating Algorithm

    elo algorithm suggests using k = 16 for master, 32 for amateurs
'''
k = 24 # for intermediates
class Elo(object):
    matches = 0 # total matches - static variable
    t = 0 # times since last match - static variable
    def __init__(self):
        self.last_match = 0 # last match - instance variable

    def match(self, p1, p2):
        Elo.t = Elo.matches-self.last_match # time (matches) since last match was played
        ret = self.modified_elo(p1,p2)
        Elo.matches += 1 # update total number of matches played
        self.last_match = Elo.matches # update last match
        return ret

    # elo algorithm with activity dynamics feature
    # (to avoid parking the bus approach)
    @staticmethod
    def modified_elo(winner, loser):
        r1 = max(min(loser.score - winner.score, 400), -400)
        r2 = max(min(winner.score - loser.score, 400), -400)
        rdf = 1. / pow(1 + Elo.t, 0.5) # rating deviation factor
        e1 = 1. / (1 + 10**(rdf*r1 / 400))
        e2 = 1. / (1 + 10**(rdf*r2 / 400))
        s1, s2 = 1, 0

        winner.score += k*(s1-e1)
        loser.score += k*(s2-e2)

        winner.wins += 1
        winner.matches += 1
        loser.matches += 1
        return winner, loser

    # elo algorithm standard implementation
    @staticmethod
    def standard_elo(winner, loser):
        r1 = max(min(loser.score - winner.score, 400), -400)
        r2 = max(min(winner.score - loser.score, 400), -400)
        e1 = 1. / (1 + 10**(r1 / 400))
        e2 = 1. / (1 + 10**(r2 / 400))
        s1, s2 = 1, 0

        winner.score += k*(s1-e1)
        loser.score += k*(s2-e2)
        winner.wins +=1
        winner.matches +=1
        loser.matches +=1
        return winner, loser