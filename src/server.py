# See https://github.com/projectmesa/mesa/blob/main/examples/boid_flockers/boid_flockers/server.py
# This is being used as a starting point for our project
from mesa.visualization.ModularVisualization import ModularServer

from .boid import Boid
from .scout import Scout
from .model import BoidFlockers
from .SimpleContinuousModule import SimpleCanvas


def boid_draw(agent):
    portrayal = None
    if isinstance(agent, Boid):
        portrayal = {
            'Shape': 'circle',
            'r': 2,
            'Filled': 'true',
            'Color': 'Red'
        }
    elif isinstance(agent, Scout):
        portrayal = {
            'Shape': 'circle',
            'r': 4,
            'Filled': 'true',
            'Color': 'Blue'
        }

    return portrayal


boid_canvas = SimpleCanvas(boid_draw, 500, 500)
# just use defaults
# model_params = {
#     "population": 100,
#     "width": 100,
#     "height": 100,
#     "speed": 5,
#     "vision": 10,
#     "separation": 2,
# }

server = ModularServer(BoidFlockers, [boid_canvas], "Boids")