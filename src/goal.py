import numpy as np
from mesa import Agent

# This agent does nothing and is not part of the schedule
# it only exists to display the goal point

class Goal(Agent):
    
    def __init__(self, pos=np.array([900,150])):
        self.pos = pos
    
    def step(self):
        pass 