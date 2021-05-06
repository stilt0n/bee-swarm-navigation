# See https://github.com/projectmesa/mesa/blob/main/examples/boid_flockers/boid_flockers/boid.py
# This is being used as a starting point for our project

import numpy as np

from mesa import Agent

# TODO: Make these into model parameters instead of constants
MAX_ACCEL = 0.3
VMAX = 1.55
ALPHA = 0.75
WEIGHT_RANDOM = 0 # paper turned this off in experiments
INERTIA = 0.8 # the paper apparently sets this to 0.8

class Boid(Agent):
    """
    A Boid-style flocker agent.
    The agent follows three behaviors to flock:
        - Cohesion: steering towards neighboring agents.
        - Separation: avoiding getting too close to any other agent.
        - Alignment: try to fly in the same direction as the neighbors.
    Boids have a vision that defines the radius in which they look for their
    neighbors to flock with. Their speed (a scalar) and velocity (a vector)
    define their movement. Separation is their desired minimum distance from
    any other Boid.
    """

    def __init__(
        self,
        unique_id,
        model,
        pos,
        speed,
        velocity,
        vision,
        separation,
        cohere=0.3,
        separate=0.3,
        match=0.3,
    ):
        """
        Create a new Boid flocker agent.
        Args:
            unique_id: Unique agent identifyer.
            pos: Starting position
            speed: Distance to move per step.
            heading: numpy vector for the Boid's direction of movement.
            vision: Radius to look around for nearby Boids.
            separation: Minimum distance to maintain from other Boids.
            cohere: the relative importance of matching neighbors' positions
            separate: the relative importance of avoiding close neighbors
            match: the relative importance of matching neighbors' headings
        """
        super().__init__(unique_id, model)
        self.pos = np.array(pos)
        self.speed = speed
        self.velocity = velocity
        self.vision = vision
        self.separation = separation
        self.cohere_factor = cohere
        self.separate_factor = separate
        self.match_factor = match

    def cohere(self, neighbors):
        """
        Return the vector toward the center of mass of the local neighbors.
        """
        cohere = np.zeros(2)
        if neighbors:
            for neighbor in neighbors:
                # Get heading finds the heading angle between two points
                # i.e. given point A and B, find the direction you would
                # need to travel from A to get to B.
                cohere += self.model.space.get_heading(self.pos, neighbor.pos)
            cohere /= len(neighbors)
            cohere /= self.vision
        return cohere

    # This corresponds to "Avoid" in the paper
    def separate(self, neighbors):
        """
        Return a vector away from any neighbors closer than separation dist.
        """
        me = self.pos
        them = [n.pos for n in neighbors if self.model.space.get_distance(me, n.pos) < self.separation]
        separation_vector = np.zeros(2)
        
        if len(them) > 0:
            for other in them:
                # get_heading(a,b) always subtracts a - b.  In the paper they
                # do a sum and basically flip this (i.e. get_heading(b,a)).
                delta = self.model.space.get_heading(other, me)
                separation_vector += delta * (self.separation / np.linalg.norm(delta) - 1)
            separation_vector /= len(them)
            separation_vector /= self.separation
            separation_vector = separation_vector / np.linalg.norm(separation_vector) ** ALPHA
        return separation_vector

    def random(self):
        # This doesn't behave exactly like the paper but it seems
        # like a pretty reasonable / similar alternative.  I don't
        # know of a built in function that does what they did and I'm
        # not sure how to create my own.  The idea is that random never
        # contributes more than 1.
        beta = np.random.exponential(.5)
        while(beta > 1):
            beta = np.random.exponential(.5)
        r = np.random.uniform(low=-1.0, high=1.0, size=2)
        r = r / np.linalg.norm(r)
        return beta * r

    # This corresponds to "Align" in the paper
    def match_heading(self, neighbors):
        """
        Return a vector of the neighbors' average heading.
        """
        match_vector = np.zeros(2)
        if neighbors:
            # scale influence by height.  Bees pay more attention to bees above them
            for neighbor in neighbors:
                scaling_factor = 1.5 if neighbor.pos[1] > self.pos[1] else 0.5
                match_vector += neighbor.velocity * scaling_factor
            match_vector /= len(neighbors)
            match_vector /= VMAX
        return match_vector

    def step(self):
        """
        Get the Boid's neighbors, compute the new vector, and move accordingly.
        """
        # The paper does not do the align behavior for the first few steps
        neighbors = self.model.space.get_neighbors(self.pos, self.vision, False)
        v_new = (
            self.cohere(neighbors) * self.cohere_factor
            + self.separate(neighbors) * self.separate_factor
            + (self.match_heading(neighbors) * self.match_factor if self.model.schedule.steps > 4 else 0)
            + self.random() * WEIGHT_RANDOM
        )
        if np.linalg.norm(v_new) > MAX_ACCEL:
            v_new = MAX_ACCEL * v_new / np.linalg.norm(v_new)
        self.velocity = self.velocity * INERTIA + v_new
        # speed will always be 1 here, which is the default value
        # it may be more clear if it's just removed in the future
        new_pos = self.pos + self.velocity * self.speed
        self.model.space.move_agent(self, new_pos)