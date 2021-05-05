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
        height=300,
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
                    the three drives."""
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
        for i in range(self.population):
            # Bees in model start with no velocity
            # Modify this to constrain where the regular bees can start
            # They will start centered around (150,150)
            n = self.population
            x = 50 + self.random.random() * 200
            y = 50 + self.random.random() * 200
            pos = np.array((x, y))
            # starting at 0 for some reason breaks the simulation
            # the error messages are extremely confusing here because
            # they involve stuff that shouldn't even use the velocity
            velocity = np.zeros(2)
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
            self.space.place_agent(boid, pos)
            self.schedule.add(boid)
        for i in range(self.population, self.population + self.scout_population):
            # Modify this to constrain where scout bees can start
            # Scouts should start BEHIND regular bees
            # Scouts start between x=(0,30) and y=(120, 180)
            x = 30 * self.random.random()
            y = 120 + self.random.random() * 60
            pos = np.array((x,y))
            # This will be max_speed * unit_vector_in_goal_direction
            # scouts are always going max speed or "circling back"
            # the paper does not explain how circling back works and it's not
            # clear from the pictures either so I guess we'll need to create our
            # own rule here.
            # For now goal can be the bottom right corned and the start point
            # can be generally around the top right corner.  I don't think
            # either should be exactly at the edge of the simulation.
            # we should just keep speed at 1, for these simulations but I'm still including it
            # velocity = self.vmax * self.speed * (self.goal - pos) / np.linalg.norm(self.goal - pos)
            velocity = np.array([self.vmax, 0])
            scout = Scout(
                i,
                i - self.population, # keeps track of when to leave
                self,
                pos,
                self.speed * self.vmax, # scouts always move at max speed
                velocity,
                self.vision,
                self.min_scout_neighbors,
                self.goal
            )
            self.space.place_agent(scout, pos)
            self.schedule.add(scout)
    def step(self):
        self.schedule.step()