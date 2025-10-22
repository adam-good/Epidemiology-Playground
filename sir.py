import numpy as np
#from numpy.random import normal, uniform, poisson, geometric, choice
from numpy.random import choice
from distributions import Distribution, PoissonDist


class SIRStatus:
    """Enumerable type for representing a person's state in the simulation
    """
    SUSCEPTIBLE = 0
    INFECTED = 1
    RECOVERED = 2
    DEAD = 3

# TODO: lethality_rate/mortality_rate needs to e redefined
# TODO: if we're making this sim OO the distributions should just be types
class Disease:
    """Represents a Disease for the SIR Model
        
    Arguments:
        infection_rate {float} -- The probability of the disease being transferred in one interaction
        lethality_rate {float} -- The probability of an infected person will die on a given day of infection
        incubation_period_dist {Distribution} -- The statistical distribution of possible incubation periods
        illness_period_dist {Distribution} -- The statistical distribution of possible illness periods
    
    Keyword Arguments:
        name {string} -- The name of the disease (default: {None})
    """

    def __init__(self, infection_rate: float, mortality_rate: float,
                 incubation_period_dist: Distribution, illness_period_dist: Distribution,
                 name: str | None = None):
        self.infection_rate: float = infection_rate
        self.mortality_rate: float = mortality_rate
        self.incubation_period_dist: Distribution = incubation_period_dist
        self.illness_period_dist:  Distribution = illness_period_dist
        self.name: str | None = name

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
        period: float = distribution.sample()
        if period < 0: # TODO: This is hacky. Needs to be a better distribution
            period = 0
        return period

class Infection:
    """Couples disease to person when person gets sick and tracks disease progression
    """
    class InfectionState:
        """Enumerable type for representing a state in the infection
        """
        INCUBATION = 0
        ILLNESS = 1
        FINISHED = 2

    def __init__(self, person, disease):
        self.person: Person = person
        self.disease: Disease = disease
        self.incubation_period: int = PoissonDist(self.disease.get_incubation_period()).sample()
        self.illness_period: int = PoissonDist(self.disease.get_illness_period()).sample()

        # Solving for event success probability given cumulative probability of death over illness time (using geometric distribution)
        # https://math.stackexchange.com/questions/2161184/solving-for-the-cdf-of-the-geometric-probability-distribution
        self.daily_mortality: float = 1 - np.exp( np.log(1 - self.disease.mortality_rate) / self.illness_period )

        self.status: self.InfectionState = Infection.InfectionState.INCUBATION

    def advance_infection(self):
        """Advance the progress of the infection
        """
        if self.status == Infection.InfectionState.INCUBATION:
            self.incubation_period -= 1
            if self.incubation_period <= 0:
                self.status = Infection.InfectionState.ILLNESS

        elif self.status == Infection.InfectionState.ILLNESS:
            self.illness_period -= 1
            if self.illness_period <= 0:
                self.status = Infection.InfectionState.FINISHED

    def get_recovery_time(self):
        """Calculate Remaining Time Until Infection is Over (disregarding death)
        
        Returns:
            int -- The time until the infection will change to the FINISHED state
        """
        return self.incubation_period + self.illness_period

# TODO: Again, probability distributions can be abstracted
class Person:
    """Represents an individual person in the SIR model
    
    Arguments:
        interaction_dist: {float} -- Average social interactions per timestep
    """
    def __init__(self, avg_interactions: float):
        self.avg_interactions: float = avg_interactions
        if self.avg_interactions < 0: # TODO: This is hacky. Fix this by requiring a proper distribution
            self.avg_interactions = 0.0

        # TODO: Do we reall need the disease and infection seperately tied to person?
        # Infection could contain disease
        self.disease: Disease | None = None
        self.infection: Infection | None = None
        
        self.status: SIRStatus = SIRStatus.SUSCEPTIBLE

    # TODO: Abstract Distribution
    def update_interactions(self, avg_interactions: float):
        """Change the parameters of the interaction
        
        Arguments:
            interaction_dist: {float} -- Average social interactions per timestep
        """
        self.avg_interactions: float = avg_interactions

    def interact(self, person):
        """Simulates a "sneeze" where this person has the oppertunity to spread their disease to someone else, if infected
        
        Arguments:
            person {Person} -- The person who could recieve the disease
        """
        if self.is_infected() and person.is_susceptible():
            r: float = np.random.uniform()
            if r < self.disease.infection_rate:
                person.infect(self.disease)

    def infect(self, disease: Disease):
        """Infect this person with the given disease. This will change the person's state to INFECTED and calculate the time periods of this person's infection
        
        Arguments:
            disease {Disease} -- The disease that this person shall be infected with.
        """
        self.disease: Disease = disease
        self.status: SIRStatus = SIRStatus.INFECTED
        self.infection: Infection = Infection(self, disease)
        # TODO: Figure out what is happening here. I was smarter 5 years ago I guess
        self.survival_days: float = np.random.geometric(self.infection.daily_mortality) # NOTE: Man I was smarter back then. I don't remember this

    def advance_condition(self):
        """Advance the Person's condition in the simulation
        """
        if self.is_infected(): 
            self.infection.advance_infection()

            if self.infection.status == Infection.InfectionState.ILLNESS:
                self.survival_days -= 1
                if self.survival_days <= 0:
                    self.status = SIRStatus.DEAD
            elif self.infection.status == Infection.InfectionState.FINISHED:
                self.status = SIRStatus.RECOVERED
                self.infection = None

    # TODO: Refactor
    def is_susceptible(self):
        if self.status == SIRStatus.SUSCEPTIBLE:
            return True
        else:
            return False

    # TODO: Refactor
    def is_infected(self):
        if self.status == SIRStatus.INFECTED:
            return True
        else:
            return False

    # TODO: Refactor
    def is_ill(self):
        if self.status == SIRStatus.INFECTED and self.infection.status == Infection.InfectionState.ILLNESS:
            return True
        else:
            return False

# TODO: Abstract stat distributions here too
class Community:
    """A localized group of people

    Arguments:
        interaction_dist: {Distribution} -- The Distribution of average interactions per timestep of people in the community
        size {int} -- Number of people initially in the community
    """
    def __init__(self, interaction_dist: Distribution, size: int):
        self.interaction_dist: Distribution = interaction_dist
        self.size: int = size
        self.people: list[Person] = [Person(self.interaction_dist.sample()) for _ in range(self.size)]

    def init_infected(self, num: int, disease: Disease):
        """Initialize some number of people in the population to be infected
        
        Arguments:
            num {int} -- The number of people to infect
            disease {Disease} -- The disease to infect people with
        """
        infected = choice(self.people, size=num)
        for p in infected:
            p.infect(disease)

    # TODO: Should this be part of the commuity?
    def advance_time(self):
        """Advance the community state with respect to time
            (i.e. infections, recoveries, etc.)
        """
        sample = choice(self.people, size=self.size, replace=False)
        self.interact([p for p in sample if p.status != SIRStatus.DEAD])
        self.advance_conditions([p for p in sample if p.status == SIRStatus.INFECTED])

    def interact(self, sample: list[Person]):
        """Perform interactions among the people in the sample
        
        Arguments:
            sample {list} -- A list of people to interact with each other
        """
        for p in sample:
            n_interactions: int = poisson(p.avg_interactions)
            interactions = choice(
                a = [x for x in sample if x != p],
                size=n_interactions,
                replace=False
            )
            for i in interactions:
                p.interact(i)

    def advance_conditions(self, sample: list[Person]):
        """Advances the condition of each person in sample
        
        Arguments:
            sample {list[Person]} -- List of Persons
        """
        for p in sample:
            p.advance_condition()

    def print_counts(self):
        """Prints number of people currently in each state
        """
        susceptible: list[Person] = len([p for p in self.people if p.status == SIRStatus.SUSCEPTIBLE])
        infected: list[Person]= len([p for p in self.people if p.status == SIRStatus.INFECTED])
        recovered: list[Person] = len([p for p in self.people if p.status == SIRStatus.RECOVERED])
        dead: list[Person] = len([p for p in self.people if p.status == SIRStatus.DEAD])

        print(f'Susceptible  : {susceptible}')
        print(f'Infected     : {infected}')
        print(f'Recovered    : {recovered}')
        print(f'Dead         : {dead}')



