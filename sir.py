import numpy as np
from numpy.random import normal, uniform, poisson, geometric, choice


class SIR_Status:
    """Enumerable type for representing a person's state in the simulation
    """
    SUSCEPTIBLE = 0
    INFECTED = 1
    RECOVERED = 2
    DEAD = 3

class Disease:
    """Represents a Disease for the SIR Model
        
    Arguments:
        infection_rate {float} -- The probability of the disease being transferred in one interaction
        lethality_rate {float} -- The probability of an infected person will die on a given day of infection
        incubation_period_dist {tuple(float, float)} -- The mean and standard deviation of the Normal Distribution of which the incubation period is sampled
        illness_period_dist {tuple(float, float)} -- The mean and standard deviation of the Normal Distribution of which the illness period is sampled
    
    Keyword Arguments:
        name {string} -- The name of the disease (default: {None})
    """

    def __init__(self, infection_rate, mortality_rate, incubation_period_dist, illness_period_dist, name=None):
        self.infection_rate = infection_rate
        self.mortality_rate = mortality_rate
        self.incubation_period_dist = incubation_period_dist

        self.illness_period_dist = illness_period_dist
        self.name = name

    def get_incubation_period(self):
        """Sample's the incubation period distribution
        
        Returns:
            float -- An average incubation period
        """
        return self._get_period(self.incubation_period_dist)

    def get_illness_period(self):
        """Sample's the illness period distribution
        
        Returns:
            float -- An average illness period
        """
        return self._get_period(self.illness_period_dist)

    def _get_period(self, distribution):
        mean, stdev = distribution
        period = normal(mean, stdev)
        if period < 0: period = 0
        return period

class Infection:
    """Couples disease to person when person gets sick and tracks disease progression
    """
    class Infection_State:
        """Enumerable type for representing a state in the infection
        """
        INCUBATION = 0
        ILLNESS = 1
        FINISHED = 2

    def __init__(self, person, disease):
        self.person = person
        self.disease = disease
        self.incubation_period = poisson(self.disease.get_incubation_period())
        self.illness_period = poisson(self.disease.get_illness_period()) + 1 # shift one so we can't be sick for 0 days. It's a cheap hack, I know...probably messes up the math!

        # Solving for event success probability given cumulative probability of death over illness time (using geometric distribution)
        # https://math.stackexchange.com/questions/2161184/solving-for-the-cdf-of-the-geometric-probability-distribution
        self.daily_mortality = 1 - np.exp( np.log(1 - self.disease.mortality_rate) / self.illness_period )

        self.status = Infection.Infection_State.INCUBATION

    def advance_infection(self):
        """Advance the progress of the infection
        """
        if self.status == Infection.Infection_State.INCUBATION:
            self.incubation_period -= 1
            if self.incubation_period <= 0:
                self.status = Infection.Infection_State.ILLNESS

        elif self.status == Infection.Infection_State.ILLNESS:
            self.illness_period -= 1
            if self.illness_period <= 0:
                self.status = Infection.Infection_State.FINISHED

    def get_recovery_time(self):
        """Calculate Remaining Time Until Infection is Over (disregarding death)
        
        Returns:
            int -- The time until the infection will change to the FINISHED state
        """
        return self.incubation_period + self.illness_period

class Person:
    """Represents an individual person in the SIR model
    
    Arguments:
        avg_inter {float} -- Average interactions this person has per day
        stdev_inter {float} -- Standard deviation of interactions this person has per day
    """
    def __init__(self, avg_inter, stdev_inter):
        self.avg_interactions = normal(loc=avg_inter, scale=stdev_inter)
        if self.avg_interactions < 0: self.avg_interactions = 0
        self.disease = None
        self.infection = None
        self.status = SIR_Status.SUSCEPTIBLE

    def update_interactions(self, avg_inter, stdev_inter):
        """Change the parameters of the interaction
        
        Arguments:
            avg_inter {float} -- Average interactions this person will have per day
            stdev_inter {float} -- Standard deviation of interactions this person has per day
        """
        self.avg_interactions = normal(avg_inter, stdev_inter)

    def interact(self, person):
        """Simulates a "sneeze" where this person has the oppertunity to spread their disease to someone else, if infected
        
        Arguments:
            person {Person} -- The person who could recieve the disease
        """
        if self.is_infected() and person.is_susceptible():
            r = uniform()
            if r < self.disease.infection_rate:
                person.infect(self.disease)

    def infect(self, disease):
        """Infect this person with the given disease. This will change the person's state to INFECTED and calculate the time periods of this person's infection
        
        Arguments:
            disease {Disease} -- The disease that this person shall be infected with.
        """
        self.disease = disease
        self.status = SIR_Status.INFECTED
        self.infection = Infection(self, disease)
        self.survival_days = geometric(self.infection.daily_mortality)

    def advance_condition(self):
        """Advance the Person's condition in the simulation
        """
        if self.is_infected(): 
            self.infection.advance_infection()

            if self.infection.status == Infection.Infection_State.ILLNESS:
                self.survival_days -= 1
                if self.survival_days <= 0:
                    self.status = SIR_Status.DEAD
            elif self.infection.status == Infection.Infection_State.FINISHED:
                self.status = SIR_Status.RECOVERED
                self.infection = None

    def is_susceptible(self):
        if self.status == SIR_Status.SUSCEPTIBLE:
            return True
        else:
            return False

    def is_infected(self):
        if self.status == SIR_Status.INFECTED:
            return True
        else:
            return False

    def is_ill(self):
        if self.status == SIR_Status.INFECTED and self.infection.status == Infection.Infection_State.ILLNESS:
            return True
        else:
            return False

class Community:
    """A localized group of people

    Arguments:
        avg_ineractions {float} -- Average number of infectious interactions per person per day
        stdev_interactions {float} -- Standard deviation of infectious interactions per person per day
        size {int} -- Number of people initially in the community
    """
    def __init__(self, avg_ineractions, stdev_interactions, size):
        self.avg_ineractions = avg_ineractions
        self.stdev_interactions = stdev_interactions
        self.size = size

        self.people = [Person(self.avg_ineractions, self.stdev_interactions) for _ in range(self.size)]

    def init_infected(self, num, disease):
        """Initialize some number of people in the population to be infected
        
        Arguments:
            num {int} -- The number of people to infect
            disease {Disease} -- The disease to infect people with
        """
        infected = choice(self.people, size=num)
        for p in infected:
            p.infect(disease)

    def advance_time(self):
        """Advance the community state with respect to time
            (i.e. infections, recoveries, etc.)
        """
        sample = choice(self.people, size=self.size, replace=False)
        self.interact([p for p in sample if p.status != SIR_Status.DEAD])
        self.advance_conditions([p for p in sample if p.status == SIR_Status.INFECTED])

    def interact(self, sample):
        """Perform interactions among the people in the sample
        
        Arguments:
            sample {list} -- A list of people to interact with each other
        """
        for p in sample:
            n_interactions = poisson(p.avg_interactions)
            interactions = choice(
                a = [x for x in sample if x != p],
                size=n_interactions,
                replace=False
            )
            for i in interactions:
                p.interact(i)

    def advance_conditions(self, sample):
        """Advances the condition of each person in sample
        
        Arguments:
            sample {list[Person]} -- List of Persons
        """
        for p in sample:
            p.advance_condition()

    def print_counts(self):
        """Prints number of people currently in each state
        """
        susceptible = len([p for p in self.people if p.status == SIR_Status.SUSCEPTIBLE])
        infected = len([p for p in self.people if p.status == SIR_Status.INFECTED])
        recovered = len([p for p in self.people if p.status == SIR_Status.RECOVERED])
        dead = len([p for p in self.people if p.status == SIR_Status.DEAD])

        print(f'Susceptible  : {susceptible}')
        print(f'Infected     : {infected}')
        print(f'Recovered    : {recovered}')
        print(f'Dead         : {dead}')



