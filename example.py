from sir import Community, Disease, NormalDistDTO, SIR_Status
import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt

np.random.seed(8675309)

if __name__ == "__main__":
    timesteps = 60
    healthcare_capacity = 200

    # Population Parameters
    mean_interactions = 5
    stdev_interactions = 1
    pop_size=500

    # Disease Parameters
    infection_rate = 0.054
    mortality_rate = 0.025
    avg_incubation_period = 5.1
    stddev_incubation_period = 2.13
    avg_illness_period = 5
    stddev_illness_period = 1

    c = Community(
        avg_ineractions=mean_interactions,
        stdev_interactions=stdev_interactions,
        size=pop_size)
    d = Disease(
        infection_rate=infection_rate,
        mortality_rate=mortality_rate,
        incubation_period_dist=NormalDistDTO(avg_incubation_period, stddev_incubation_period),
        illness_period_dist=NormalDistDTO(avg_illness_period, stddev_illness_period),
        name="Uh Oh Me No Feel Good")
    c.init_infected(1, d)

    susceptible = np.zeros(timesteps)
    infected = np.zeros(timesteps)
    recovered = np.zeros(timesteps)
    timeline = range(timesteps)

    for i in range(timesteps):
#        if i == 20:
#            for p in c.people:
#                p.update_interactions(avg_inter=1.85, stdev_inter=0.5)
                # p.update_interaction(avg_inter=3, stdev_inter=0.75)

        susceptible[i] = len([p for p in c.people if p.status == SIR_Status.SUSCEPTIBLE])
        infected[i] = len([p for p in c.people if p.status == SIR_Status.INFECTED])
        recovered[i] = len([p for p in c.people if p.status == SIR_Status.RECOVERED])

        print(f"Iteration {i}")
        c.print_counts()
        c.iterate()

    fn = lambda x,a,b,c: a / (1 + np.exp( -b * (x-c) ))
    popt, pcov = curve_fit(fn, timeline, infected+recovered, p0=[pop_size, 1, 1])
    fit = fn(timeline, *popt)
    print(popt)


    plt.plot(timeline, susceptible, label='susceptible')
    plt.plot(timeline, infected, label='infected')
    plt.plot(timeline, recovered, label='recovered')
    plt.plot(timeline, [healthcare_capacity for _ in timeline], linestyle='-.', label='healthcare capacity')
    plt.legend()
    plt.title(f"SIR Model of '{d.name}' Disease")
    plt.savefig("output/sir.png")

    plt.clf()

    plt.plot(timeline, infected+recovered, label='infected')
    plt.plot(timeline, fit, label='fit')
    plt.legend()
    plt.title("SIR Infected Growth / Exponential Growth")
    plt.savefig('output/exp.png')