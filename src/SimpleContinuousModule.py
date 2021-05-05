# See https://github.com/projectmesa/mesa/blob/main/examples/boid_flockers/boid_flockers/SimpleContinuousModule.py
# This example is being used a starting point for our project
from mesa.visualization.ModularVisualization import VisualizationElement
from .goal import Goal

class SimpleCanvas(VisualizationElement):
    local_includes = ["src/simple_continuous_canvas.js"]
    portrayal_method = None
    canvas_height = 400
    canvas_width = 1000

    def __init__(self, portrayal_method, canvas_height=500, canvas_width=500, goal=Goal()):
        """
        Instantiate a new SimpleCanvas
        """
        self.portrayal_method = portrayal_method
        self.canvas_height = canvas_height
        self.canvas_width = canvas_width
        self.goal = goal
        new_element = "new Simple_Continuous_Module({}, {})".format(
            self.canvas_width, self.canvas_height
        )
        self.js_code = "elements.push(" + new_element + ");"

    def render(self, model):
        space_state = []
        agents = model.schedule.agents
        agents.append(self.goal)
        for obj in agents:
            portrayal = self.portrayal_method(obj)
            x, y = obj.pos
            x = (self.canvas_width / self.canvas_height) * (x - model.space.x_min) / (model.space.x_max - model.space.x_min)
            y = (self.canvas_height / self.canvas_width) * (y - model.space.y_min) / (model.space.y_max - model.space.y_min)
            portrayal["x"] = x
            portrayal["y"] = y
            space_state.append(portrayal)
        # mark goal on canvas
        # goal_portrayal = self.portrayal_method(self.goal)
        # x, y = self.goal.pos
        # x = (self.canvas_width / self.canvas_height) * (x - model.space.x_min) / (model.space.x_max - model.space.x_min)
        # y = (self.canvas_height / self.canvas_width) * (x - model.space.y_min) / (model.space.y_max - model.space.y_min)
        # goal_portrayal['x'] = x
        # goal_portrayal['y'] = y
        # space_state.append(goal_portrayal)
        return space_state