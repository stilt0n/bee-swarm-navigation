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
        width=100,
        height=100,
        speed=1,
        vision=30,
        separation=15,
        cohere=0.3,
        separate=0.3,
        match=0.3
    ):
        """
        Create a new Flockers model.
        Args:
            population: Number of Boids
            width, height: Size of the space.
            speed: How fast should the Boids move.
            vision: How far around should each Boid look for its neighbors
            separation: What's the minimum distance each Boid will attempt to
                    keep from any other
            cohere, separate, match: factors for the relative importance of
                    the three drives."""
        self.population = population
        self.vision = vision
        self.speed = speed
        self.separation = separation
        self.schedule = RandomActivation(self)
        self.space = ContinuousSpace(width, height, True)
        self.factors = dict(cohere=cohere, separate=separate, match=match)
        self.make_agents()
        self.running = True

    def make_agents(self):
        """
        Create self.population agents, with random positions and starting headings.
        """
        for i in range(self.population):
            x = self.random.random() * self.space.x_max
            y = self.random.random() * self.space.y_max
            pos = np.array((x, y))
            velocity = np.random.random(2) * 2 - 1
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

    def step(self):
        self.schedule.step()