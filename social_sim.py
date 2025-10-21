import numpy as np
from numpy.random import normal, uniform, poisson, geometric, choice

class Person:
    class Interaction:
        def __init__(self, p1, p2):
            self.person1 = p1
            self.person2  = p2

    def __init__(self, avg_interactions):
        self.avg_interactions = avg_interactions
#        self.todays_interactions = self.get_daily_interactions()

    def update_daily_interactions(self):
        self.todays_interactions = self.get_daily_interactions()

    def get_daily_interactions(self):
        return poisson(self.avg_interactions)

    def interact(self, person):
        return Person.Interaction(self, person)

class Community:
    def __init__(self, size, avg_interactions, stdev_interactions):
        self.people = [Person(normal(avg_interactions, stdev_interactions)) for _ in size]

    def get_interactions(self):
        for p in self.people:
            p.update_daily_interactions()

        shuffle = choice(self.people, size=len(self.people), replace=False)
        for p in shuffle:
            num_inters = p.todays_interactions
            inters = 
