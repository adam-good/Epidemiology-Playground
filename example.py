from sir import Community, Disease, SIRStatus
import numpy as np
import matplotlib.pyplot as plt

np.random.seed(8675309)

if __name__ == "__main__":
    timesteps: int = 60
    healthcare_capacity: int = 200

    # Population Parameters
    mean_interactions: float = 5.0
    stdev_interactions:float = 1.0
    pop_size: int = 500

    # Disease Parameters
    infection_rate: float = 0.054
    mortality_rate: float = 0.025
    avg_incubation_period: float = 5.1
    stddev_incubation_period: float = 2.13
    avg_illness_period: float = 5.0
    stddev_illness_period: float = 1.0

    # TODO: Better naming
    c: Community = Community(
        avg_ineractions=mean_interactions,
        stdev_interactions=stdev_interactions,
        size=pop_size)
    d: Disease = Disease(
        infection_rate=infection_rate,
        mortality_rate=mortality_rate,
        incubation_period_dist=(avg_incubation_period, stddev_incubation_period),
        illness_period_dist=(avg_illness_period, stddev_illness_period),
        name="Uh Oh Me No Feel Good")
    c.init_infected(1, d)

    susceptible = np.zeros(timesteps)
    infected = np.zeros(timesteps)
    recovered = np.zeros(timesteps)
    timeline = range(timesteps)

    for i in range(timesteps):
        susceptible[i] = len([p for p in c.people if p.status == SIRStatus.SUSCEPTIBLE])
        infected[i] = len([p for p in c.people if p.status == SIRStatus.INFECTED])
        recovered[i] = len([p for p in c.people if p.status == SIRStatus.RECOVERED])

        print(f"Iteration {i}")
        c.print_counts()
        c.advance_time()

    plt.plot(timeline, susceptible, label='susceptible')
    plt.plot(timeline, infected, label='infected')
    plt.plot(timeline, recovered, label='recovered')
    plt.plot(timeline, [healthcare_capacity for _ in timeline], linestyle='-.', label='healthcare capacity')
    plt.legend()
    plt.title(f"SIR Model of '{d.name}' Disease")
    plt.savefig("output/sir.png")
