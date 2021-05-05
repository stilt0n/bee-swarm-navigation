# See https://github.com/projectmesa/mesa/blob/main/examples/boid_flockers/boid_flockers/model.py
# This is being used as a starting point for our project

"""
Flockers
=============================================================
A Mesa implementation of Craig Reynolds's Boids flocker model.
Uses numpy arrays to represent vectors.
"""

import numpy as np

from mesa import Model
from mesa.space import ContinuousSpace
from mesa.time import RandomActivation

from .boid import Boid
from .scout import Scout

# This is bad practice and should be parameters but it'll have to do
GOAL_X = 900 # in paper this will go out to 4000, but I'm doing some smaller runs first
GOAL_Y = 150 # in paper I think this is 200 -- This will probably eventually be some fraction of n/2 (maybe n/4?)
SCOUT_START_X = 75 # scout start area is from (0, SCOUT_START_X) scouts will be evenly spaced + noise
U_START_CENTER = np.array([150,150]) # in paper this is [200,200,200] and uninformed bees are placed in a cube with side lengths n/3
# n/3 is to prevent bees from starting starting disconnected.  I will do n/2 here instead.  I think n/3 has a lot to do with the
# dimension choice here.

# weights for cohere, avoid, align, random and max_accel
# are all set to 0.3 (this is what they are set to in the paper)
# alpha of 0.75 is used for the avoid rule
# w=0.8, v_max = 1.55, vision=30 d_min=15
# All scouts fly at velocity v_max (this maybe can be adjusted
# to allow for a different stopping condition, because the math
# behind the original model works by having the scouts leave the
# swarm when it's time to stop, but I think they don't do this).

class BoidFlockers(Model):
    """
    Flocker model class. Handles agent creation, placement and scheduling.
    """

    def __init__(
        self,
        population=100,
        scout_population=10,
        width=1000,
        height=400,
        speed=3,
        vision=30,
        separation=15,
        cohere=0.3,
        separate=0.3,
        match=0.3,
        goal=np.array([900,150]),
        vmax=1.55,
        min_scout_neighbors=10
    ):
        """
        Create a new Flockers model.
        Args:
            population: Number of Boids
            width, height: Size of the space.
            speed: How fast should the Boids move. -- speed scales the algorithm's velocities
            vision: How far around should each Boid look for its neighbors
            separation: What's the minimum distance each Boid will attempt to
                    keep from any other
            cohere, separate, match: factors for the relative importance of
                    the three drives.
        """
        self.population = population
        self.scout_population=scout_population
        self.goal = goal
        self.vision = vision
        self.speed = speed
        self.separation = separation
        self.vmax = vmax
        self.min_scout_neighbors = min_scout_neighbors
        self.schedule = RandomActivation(self)
        self.space = ContinuousSpace(width, height, False)
        self.factors = dict(cohere=cohere, separate=separate, match=match)
        self.make_agents()
        self.running = True

    def make_agents(self):
        """
        Create self.population agents, with random positions and starting headings.
        """
        scout_interval = SCOUT_START_X / self.scout_population
        # don't want to calculate this in a loop
        # scouts seem to be spaced in intervals along one axis in the paper rather
        # than completely randomly.  It could be they are random and then released
        # one at a time also, but I haven't been able to find anywhere that this is
        # mentioned.
        scout_intervals = np.array([scout_interval * i for i in range(self.scout_population)])
        # add noise to intervals
        scout_intervals += np.random.rand(self.scout_population) * scout_interval / 2
        n = self.population
        for i in range(n):
            # Uninformed bees are constrained to start near U_START_CENTER
            # The paper uses (CENTER - n/3, CENTER + n/3) for the range but
            # for 2-dimensions I am using n/2 instead.
            x = U_START_CENTER[0] - n/2 + self.random.random() * n
            y = U_START_CENTER[1] - n/2 + self.random.random() * n
            pos = np.array((x, y))
            # Uninformed bees start with no velocity
            velocity = np.zeros(2)
            # They are still called boids because I didn't want to find and replace
            # every instance of the word boid.
            boid = Boid(
                i,
                self,
                pos,
                self.speed,
                velocity,
                self.vision,
                self.separation,
                **self.factors
            )
            # This stuff adds the agents to the simulation
            self.space.place_agent(boid, pos)
            self.schedule.add(boid)
        for i in range(n, n + self.scout_population):
            # Scouts always start BEHIND uninformed bees
            # The paper isn't super clear on everything the scouts do
            # but in their animation they appear to join the simulation 1 by 1
            # to approximate this, we are lining the scouts up over an interval
            # but then adding randomness so it's not perfectly lined up
            # Scout height should be close to the center, but with variation.  This
            # wasn't that clear in the paper either, but it should be less variation
            # than for the entire swarm since the scouts actually only fly parallel to
            # the correct position.  The reason they should lead okay doing this is
            # because the correct position is the expected value of scout directions
            scout_id = i - n
            x = scout_intervals[scout_id]
            y = U_START_CENTER[1] - n/4 + self.random.random() * n/2
            pos = np.array((x,y))
            # This will be max_speed * unit_vector_in_goal_direction
            # scouts are always going max speed or "circling back"
            # the paper does not explain how circling back works but my best
            # guess from looking at the simulation in slow motion is that scouts
            # teleport to the back somehow.  There don't appear to be scouts moving
            # around or away from the goal at any point.
            velocity = np.array([self.vmax, 0])
            scout = Scout(
                i,
                scout_id, # keeps track of when to leave
                self,
                pos,
                self.speed * self.vmax, # scouts always move at max speed
                velocity,
                self.vision,
                self.min_scout_neighbors, # when a scout has fewer neighbors the circle back
                self.goal
            )
            self.space.place_agent(scout, pos)
            self.schedule.add(scout)
    def step(self):
        self.schedule.step()