#    This file is part of DEAP.
#
#    DEAP is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as
#    published by the Free Software Foundation, either version 3 of
#    the License, or (at your option) any later version.
#
#    DEAP is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public
#    License along with DEAP. If not, see <http://www.gnu.org/licenses/>.

from __future__ import division
import bisect
import math
import random

from itertools import chain
from operator import attrgetter, itemgetter
from collections import defaultdict

######################################
# Non-Dominated Sorting   (NSGA-II)  #
######################################

def selNSGA2(individuals, k, probabilitiesForObjectives):
    """Apply NSGA-II selection operator on the *individuals*. Usually, the
    size of *individuals* will be larger than *k* because any individual
    present in *individuals* will appear in the returned list at most once.
    Having the size of *individuals* equals to *k* will have no effect other
    than sorting the population according to their front rank. The
    list returned contains references to the input *individuals*. For more
    details on the NSGA-II operator see [Deb2002]_.
    
    :param individuals: A list of individuals to select from.
    :param k: The number of individuals to select.
    :param nd: Specify the non-dominated algorithm to use: 'standard' or 'log'.
    :returns: A list of selected individuals.
    
    .. [Deb2002] Deb, Pratab, Agarwal, and Meyarivan, "A fast elitist
       non-dominated sorting genetic algorithm for multi-objective
       optimization: NSGA-II", 2002.
    """
    pareto_fronts = sortNondominated(individuals, k, probabilitiesForObjectives)
    for front in pareto_fronts:
        assignCrowdingDist(front)

    chosen = list(chain(*pareto_fronts[:-1]))
    k = k - len(chosen)
    if k > 0:
        sorted_front = sorted(pareto_fronts[-1], key=attrgetter("fitness.crowding_dist"), reverse=True)
        chosen.extend(sorted_front[:k])

    return chosen

def stochasticallly_dominates(self, other, probabilitiesForObjectives, obj=slice(None)):
        """Return true if each objective of *self* is not strictly worse than
        the corresponding objective of *other* and at least one objective is
        strictly better.

        :param obj: Slice indicating on which objectives the domination is
                    tested. The default value is `slice(None)`, representing
                    every objectives.
        """
        #print("Does "+str(self)+" dominate "+ str(other) +"?")
        not_equal = False
        for self_wvalue, other_wvalue, p in zip(self.wvalues[obj], other.wvalues[obj], probabilitiesForObjectives[obj]):
            r = random.random()
            if (r<=p):
                if self_wvalue > other_wvalue:
                    not_equal = True
                elif self_wvalue < other_wvalue:
                    return False
        return not_equal

def sortNondominated(individuals, k, probabilitiesForObjectives, first_front_only=False):
    """Sort the first *k* *individuals* into different nondomination levels 
    using the "Fast Nondominated Sorting Approach" proposed by Deb et al.,
    see [Deb2002]_. This algorithm has a time complexity of :math:`O(MN^2)`, 
    where :math:`M` is the number of objectives and :math:`N` the number of 
    individuals.
    
    :param individuals: A list of individuals to select from.
    :param k: The number of individuals to select.
    :param first_front_only: If :obj:`True` sort only the first front and
                             exit.
    :returns: A list of Pareto fronts (lists), the first list includes 
              nondominated individuals.
    .. [Deb2002] Deb, Pratab, Agarwal, and Meyarivan, "A fast elitist
       non-dominated sorting genetic algorithm for multi-objective
       optimization: NSGA-II", 2002.
    """
    if k == 0:
        return []

    # Bucket individuals by their fitness
    map_fit_ind = defaultdict(list)
    for ind in individuals:
        map_fit_ind[ind.fitness].append(ind)
    fits = list(map_fit_ind.keys())
    
    current_front = []
    next_front = []
    dominating_fits = defaultdict(int)
    dominated_fits = defaultdict(list)
    levels = defaultdict(list)
    
    # Rank first Pareto front
    # dominating_fits = n(p) = Number of fitnesses, which dominate the fitness of individual p
    # dominated_fits = S(p) = List of fitnesses, which are dominated by the fitness of individual p
    for i, fit_i in enumerate(fits):
        for fit_j in fits[i+1:]:
            if stochasticallly_dominates(fit_i,fit_j,probabilitiesForObjectives):
            #if fit_i.dominates(fit_j):
                dominating_fits[fit_j] += 1
                dominated_fits[fit_i].append(fit_j)
            elif stochasticallly_dominates(fit_j,fit_i, probabilitiesForObjectives):
            #elif fit_j.dominates(fit_i):
                dominating_fits[fit_i] += 1
                dominated_fits[fit_j].append(fit_i)
        if dominating_fits[fit_i] == 0:
            current_front.append(fit_i)
        levels[dominating_fits[fit_i]].append(fit_i)

    fronts = []
    itemCounter = 0
    N = min(len(individuals), k)
    i = 0
    levelKeys = list(levels.keys())
    while (itemCounter < N) and (i < len(levelKeys)):
        fronts.append([])
        level = levelKeys[i]
        for fit_d in levels[level]:
            itemCounter += len(map_fit_ind[fit_d])
            fronts[-1].extend(map_fit_ind[fit_d])
        i += 1

    return fronts

def assignCrowdingDist(individuals):
    """Assign a crowding distance to each individual's fitness. The 
    crowding distance can be retrieve via the :attr:`crowding_dist` 
    attribute of each individual's fitness.
    """
    if len(individuals) == 0:
        return
    
    distances = [0.0] * len(individuals)
    crowd = [(ind.fitness.values, i) for i, ind in enumerate(individuals)]
    
    nobj = len(individuals[0].fitness.values)
    
    for i in range(nobj):
        crowd.sort(key=lambda element: element[0][i])
        distances[crowd[0][1]] = float("inf")
        distances[crowd[-1][1]] = float("inf")
        if crowd[-1][0][i] == crowd[0][0][i]:
            continue
        norm = nobj * float(crowd[-1][0][i] - crowd[0][0][i])
        for prev, cur, next in zip(crowd[:-2], crowd[1:-1], crowd[2:]):
            distances[cur[1]] += (next[0][i] - prev[0][i]) / norm

    for i, dist in enumerate(distances):
        individuals[i].fitness.crowding_dist = dist

def selTournamentDCD(individuals, k, probabilitiesForObjectives):
    #print("=============================\nselTournamentDCD\n=============================")
    """Tournament selection based on dominance (D) between two individuals, if
    the two individuals do not interdominate the selection is made
    based on crowding distance (CD). The *individuals* sequence length has to
    be a multiple of 4. Starting from the beginning of the selected
    individuals, two consecutive individuals will be different (assuming all
    individuals in the input list are unique). Each individual from the input
    list won't be selected more than twice.
    
    This selection requires the individuals to have a :attr:`crowding_dist`
    attribute, which can be set by the :func:`assignCrowdingDist` function.
    
    :param individuals: A list of individuals to select from.
    :param k: The number of individuals to select.
    :returns: A list of selected individuals.
    """
    def tourn(ind1, ind2):
        if stochasticallly_dominates(ind1.fitness,ind2.fitness, probabilitiesForObjectives):
        #if ind1.fitness.dominates(ind2.fitness):
            return ind1
        elif stochasticallly_dominates(ind2.fitness, ind1.fitness, probabilitiesForObjectives):
        #elif ind2.fitness.dominates(ind1.fitness):
            return ind2

        #print("Crowding distance")
        if ind1.fitness.crowding_dist < ind2.fitness.crowding_dist:
            return ind2
        elif ind1.fitness.crowding_dist > ind2.fitness.crowding_dist:
            return ind1

        #print("Random")
        if random.random() <= 0.5:
            return ind1
        return ind2

    individuals_1 = random.sample(individuals, len(individuals))
    individuals_2 = random.sample(individuals, len(individuals))

    chosen = []
    for i in range(0, k, 4):
        chosen.append(tourn(individuals_1[i],   individuals_1[i+1]))
        chosen.append(tourn(individuals_1[i+2], individuals_1[i+3]))
        chosen.append(tourn(individuals_2[i],   individuals_2[i+1]))
        chosen.append(tourn(individuals_2[i+2], individuals_2[i+3]))

    #print("=============================\n")
    return chosen
