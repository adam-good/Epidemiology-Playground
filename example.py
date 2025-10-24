from sir import Community, Disease, SIRStatus
import numpy as np
import matplotlib.pyplot as plt
from distributions import Distribution, NormalDist

np.random.seed(8675309)

if __name__ == "__main__":
    timesteps: int = 60
    healthcare_capacity: int = 200

    # TODO: Better naming
    c: Community = Community(
        interaction_dist=NormalDist(mean=5.0, stdev=1.0),
        size=500)
    d: Disease = Disease(
        infection_rate=0.054,
        case_fatality_rate=0.025,
        incubation_period=5.1,
        illness_period=5.0,
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
