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
    ''' This environment has a grid of rows and columns with obstacles '''

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
                            if isinstance(thing, Obstacle)]
        
        return self.get_available_moves(x, y, env.width, env.height, obstacle_positions)



    def percept(self, agent):
        """Override the percept method to include available moves"""
        # Add available moves to percepts
        x, y = agent.location
        obstacle_positions = [(thing.location[0], thing.location[1]) 
                             for thing in self.things 
                             if isinstance(thing, Obstacle)]
        
        available_moves = self.get_available_moves(x, y, self.width, self.height, obstacle_positions)
        
        # Return both standard percepts and available moves
        return (available_moves)


    def get_available_moves(self, x, y, width, height, obstacles=None):
        """
        Returns a list of available directions (north, south, east, west) that an agent can move
        based on its current position and grid boundaries. """

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
        print(f"Executing action {action}")
        print(f"Before action Location is {agent.location}")

        # Calculate obstacle positions 
        obstacle_positions = [(thing.location[0], thing.location[1])
                            for thing in self.things 
                            if isinstance(thing, Obstacle)]
        if action not in self.get_available_moves(agent.location[0],
                                              agent.location[1],
                                              self.width,
                                              self.height,
                                              obstacle_positions):
            print("❌ Cant go that direction!")
            return

        if action == 'north':
            agent.location = (agent.location[0], agent.location[1] - 1)  # Move up (decrease y)
        elif action == 'south':
            agent.location =  (agent.location[0], agent.location[1] + 1)  # Move down (increase y)
        elif action == 'east':
            agent.location =  (agent.location[0] + 1, agent.location[1])  # Move right (increase x)
        elif action == 'west':
            agent.location =  (agent.location[0] - 1, agent.location[1])  # Move left (decrease x)
        else:
            agent.location =  (agent.location[0], agent.location[1]) 

        print(f"After action Location is {agent.location}")

        # Check if agent is at a positive destination
        positive_destinations = self.list_things_at(agent.location, PositiveDestination)
        if positive_destinations:
            agent.performance += 1
            print(f"🎉 Agent reached positive destination! Score +1. Total: {agent.performance}")
            
        # Check if agent is at a negative destination
        negative_destinations = self.list_things_at(agent.location, NegativeDestination)
        if negative_destinations:
            agent.performance -= 1
            print(f"😭 Agent reached negative destination! Score -1. Total: {agent.performance}")


def random_agent_program(percept):
    """A simple agent program that moves randomly"""
    return random.choice(['south', 'east', 'north', 'west'])

# Create and set up the environment
def create_gridworld_environment(width, height):
    env = GridWorldEnvironment(width, height)

    # Generate some random locations for the obstacle, the positive block and the negative block
    obstacle_x = random.randint(0, width-1)
    obstacle_y = random.randint(0, height-1)

    while True:
        pos_x = random.randint(0, width -1)
        pos_y = random.randint(0, height - 1)
        if (pos_x, pos_y) != (obstacle_x, obstacle_y):
            break

    while True:
        neg_x = random.randint(0, width -1)
        neg_y = random.randint(0, height - 1)
        if (neg_x, neg_y) != (obstacle_x, obstacle_y) and (neg_x, neg_y) != (pos_x, pos_y):
            break

    print(f"Obstacle location is {obstacle_x}, {obstacle_y}")
    print(f"Positive location is {pos_x}, {pos_y}")
    print(f"Negative location is {neg_x}, {neg_y}")

    env.add_thing(Obstacle(), (obstacle_x, obstacle_y))
    env.add_thing(PositiveDestination(), (pos_x, pos_y))
    env.add_thing(NegativeDestination(), (neg_x, neg_y))
    
    # Create and add an agent with a direction
    agent = Agent(random_agent_program)
    env.add_thing(agent, (0, 0))
    
    return env


def main():

    # Generate
    env = create_gridworld_environment(4, 3)
    env.run(20)
    print(f"********** FINAL SCORE {env.agents[0].performance} ********")

if __name__ == "__main__":
    main()
