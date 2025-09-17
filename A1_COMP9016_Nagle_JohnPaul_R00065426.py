import sys
import os

# Get the parent dir of the current directory
parent_dir = os.path.dirname(os.getcwd())

# Add the parent directory to sys.path
sys.path.append(parent_dir)

# Now you can import a module from the parent directory
from agents import *


# Define custom destination blocks
class PositiveDestination(Thing):
    """A destination that awards 1 point when an agent reaches it"""
    pass

class NegativeDestination(Thing):
    """A destination that penalizes 1 point when an agent reaches it"""
    pass


class GridWorldEnvironment(Environment):
    # This environment has a grid of rows and columns with obstacles randomly dispersed
    # 

    def __init__(self, width=4, height=3):
        super().__init__()
        self.width = width
        self.height = height


    def get_agent_percepts(self, agent, env):
        """
        Returns the available moves for an agent in the given environment.
        
        Parameters:
        - agent: The agent object
        - env: The XYEnvironment object
        
        Returns:
        - List of available directions
        """
        x, y = agent.location
        
        # Get positions of all obstacles in the environment
        obstacle_positions = [(thing.location[0], thing.location[1]) 
                            for thing in env.things 
                            if isinstance(thing, Obstacle) and hasattr(thing, 'location')]
        
        return self.get_available_moves(x, y, env.width, env.height, obstacle_positions)



    def percept(self, agent):
        """Override the percept method to include available moves"""
        # Get standard percepts from parent class
        standard_percepts = super().percept(agent)
        
        # Add available moves to percepts
        x, y = agent.location
        obstacle_positions = [(thing.location[0], thing.location[1]) 
                             for thing in self.things 
                             if isinstance(thing, Obstacle)]
        
        available_moves = self.get_available_moves(x, y, self.width, self.height, obstacle_positions)
        
        # Return both standard percepts and available moves
        return (standard_percepts, available_moves)


    def get_available_moves(self, x, y, width, height, obstacles=None):
        """
        Returns a list of available directions (north, south, east, west) that an agent can move
        based on its current position and grid boundaries.
        
        Parameters:
        - x, y: Current coordinates of the agent
        - width, height: Dimensions of the grid
        - obstacles: Optional list of (x,y) tuples representing obstacle positions
        
        Returns:
        - List of available directions as strings ('north', 'south', 'east', 'west')
        """
        if obstacles is None:
            obstacles = []
            
        available_moves = []
        
        # Check North (up, decreasing y)
        if y > 0 and (x, y-1) not in obstacles:
            available_moves.append('north')
            
        # Check South (down, increasing y)
        if y < height-1 and (x, y+1) not in obstacles:
            available_moves.append('south')
            
        # Check East (right, increasing x)
        if x < width-1 and (x+1, y) not in obstacles:
            available_moves.append('east')
            
        # Check West (left, decreasing x)
        if x > 0 and (x-1, y) not in obstacles:
            available_moves.append('west')
            
        return available_moves



    def execute_action(self, agent, action):
        # First execute the standard action
        super().execute_action(agent, action)
        
        # Check if agent is at a positive destination
        positive_destinations = self.list_things_at(agent.location, PositiveDestination)
        if positive_destinations:
            agent.performance += 1
            print(f"Agent reached positive destination! Score +1. Total: {agent.performance}")
            
        # Check if agent is at a negative destination
        negative_destinations = self.list_things_at(agent.location, NegativeDestination)
        if negative_destinations:
            agent.performance -= 1
            print(f"Agent reached negative destination! Score -1. Total: {agent.performance}")


def simple_agent_program(percept):
    """A simple agent program that moves randomly"""
    return random.choice(['Forward', 'TurnRight', 'TurnLeft'])

# Create and set up the environment
def create_custom_environment():
    # Create environment with width 4 and height 3
    env = GridWorldEnvironment(4, 3)
    
    env.add_thing(Obstacle(), (2, 3))
    env.add_thing(PositiveDestination(), (4, 1))
    env.add_thing(NegativeDestination(), (3, 1))
    
    # Create and add an agent with a direction
    agent = Agent(simple_agent_program)
    agent.direction = Direction("right")  # Give the agent a direction
    env.add_thing(agent, (0, 0))
    
    return env


def main():

    env = create_custom_environment()
    env.run(20)

if __name__ == "__main__":
    main()
