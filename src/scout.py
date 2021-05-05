import numpy as np
from mesa import Agent

#########################################################################
"""
This file implements Scout Bee agents from the paper and our own modified
version of them with more realistic assumptions.  This may be implemented
as one class with a boolean flag (if things are very simple), two classes
or three classes where one class is a base class the others inherit from.
"""
#########################################################################

# Scout has 3 behaviors -- ##
#   - When there are at least 10 bees in scout's neighborhood
#       - Fly towards goal at vmax
#   - When there are less than 10 bees in scout's neighborhood
#       - reset to back (paper says scouts circle around, but
#       gives no explanation how).
#   - When near stopping point
#       - Disappear this will be implemented in the model
#############################

class Scout(Agent):
    """
    A Scout-Bee agent.  This agent is less common than Boid style agents
    and has different behaviors.  Instead of following the rules of the
    Boid style bees, it tries to move quickly through the swarm going the
    correct direction.  The rules (from the paper) are not as clear but
    I think I figured them out:
        - Scouts move towards the goal parallel to center of swarm.
            - In other words, scout does not move directly to goal but
            rather moves to some (x,y) where: 
            x=goal_x and y=goal_y + distance_from_center_y
            - Scouts always spawn pretty close to the center, prevents
            this from adding too much error
    When scouts get too far from the swarm they "go back around"
        - Looking at the animation in slow motion, it's clear
        the bees do not actually fly back, so I think they are
        teleporting to the back.
    
    """
    #TODO: these parameters will probably change
    def __init__(
        self,
        unique_id,
        scout_id, # used to determine when to leave
        model,
        pos,
        speed,
        velocity,
        vision,
        min_neighbors,
        goal
    ):
        super().__init__(unique_id, model)
        self.pos = np.array(pos)
        self.speed = speed
        self.velocity = velocity
        self.vision = vision # determines neighborhood
        self.min_neighbors = min_neighbors
        self.goal = goal
        self.leave_counter = scout_id
    
    # Scouts fly through on line parallel line from swarm center to goal.
    # This requires finding the swarm center.  In the paper they remove disconnected
    # Bees when doing this.  Here, we will just assume bees don't disconnect and remove
    # trials where they do.  We can keep track of how many trials we remove to get an idea
    # of how often disconnects take place.
    def get_center(self):
        points = self.model.space._agent_points
        return np.array([np.mean(points[:,0]), np.mean(points[:,1])])

    def get_furthest_uninformed_x(self):
        uninformed = np.array([a.pos for a in self.model.schedule._agents.values() if a.unique_id < self.model.population])
        return np.max(uninformed[:,0])

    def reset(self):
        # we want to restart along the same line.  To do this:
        # Find the minimum of all point x values
        # new_pos[x] = min_x
        # Find equation for line that reset point is travelling
        # on using point slope formula (i.e find m and b)
        # new_pos[y] = m * min_x + b
        # Add some randomness to x
        min_x = np.min(self.model.space._agent_points[:,0]) + self.random.random() * 2
        m = (self.pos[1] - self.goal[1]) / (self.pos[0] - self.goal[0])
        # (y = mx + b => y - mx = b)
        b = self.pos[1] - m * self.pos[0]
        new_y = m * min_x + b
        return np.array([min_x, new_y])

    def towards_goal(self):
        # Flying parallel through center requires finding unit vector from center to goal
        # Then modifying it to be the correct magnitude I don't think we need to know the position
        center = self.get_center()
        return self.speed * (self.goal - center) / np.linalg.norm(self.goal - center) 
        # return self.speed * np.array([1,0])
    # I think this does need to be called from here
    def disappear(self):
        self.model.schedule.remove(self)

    def step(self):
        # distance from goal where scouts disappear
        # distance is measured from swarm center
        close_to_goal = 75
        distance_from_goal = np.linalg.norm(self.goal - self.get_center())
        # When close to goal gradually remove bees
        if distance_from_goal < close_to_goal:
            if self.leave_counter == 0:
                self.disappear()
            else:
                self.leave_counter -= 1
        # When scout is in front go back
        elif len(self.model.space.get_neighbors(self.pos, self.vision * 1.5, False)) <= self.min_neighbors and self.pos[0] > self.get_furthest_uninformed_x():
            new_pos = self.reset()
            self.model.space.move_agent(self, new_pos)
        # In normal instances, move towards goal
        else:
            new_pos = self.pos + self.towards_goal()
            self.model.space.move_agent(self, new_pos)
            
