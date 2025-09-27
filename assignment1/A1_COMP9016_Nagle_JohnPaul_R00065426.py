"""
# A1_COMP9016_Nagle_JohnPaul_R00065426.py
#
# Name:         (John) Paul Nagle
# Student ID:   R00065426
# Class:        Knowledge Representation
# Assignment:   1
#
# The 2D world is comprised of a 4 by 3 grid of blocks. 
# There is one obstacle block that no agent can move to at (1, 1)
# An agent gets charged some points (sum of x and y co-ordinates) for making a move.
# An agent gets penalised 50 points if it lands on the penalty block (3, 1)
# If the agent reaches the winning block (3, 0) it gets 100 points, wins the game and
# the game ends
# If the agent does not reach the winning block in the set number of moves, the game ends
# and the agent has lost the game.
#
# Here is a map of the 2D world
┌──────────┬──────────┬──────────┬──────────┐
│(0,0)     │(1,0)     │(2,0)     │(3,0)     │
│          │          │          │          │
│          │          │          │ WIN GAME │
┼──────────┼──────────┼──────────┼──────────┤
│(0,1)     │(1,1)     │(2,1)     │(3,1)     │
│          │          │          │          │
│          │ OBSTACLE │          │ PENALTY  │
┼──────────┼──────────┼──────────┼──────────┤
│(0,2)     │(1,2)     │(2,2)     │(3,2)     │
│          │          │          │          │
│          │          │          │          │
└──────────┴──────────┴──────────┴──────────┘


#  Agents:  Random Agent, picks the noxt move randomly
#           Reflex agent, always moves to the cheapest adjacent square.
#           Goal Based Agent, uses the history of precepts to determine the next move.


"""

import sys
import os
import random

# Get the parent dir of the current directory
parent_dir = os.path.dirname(os.getcwd())

# Add the parent directory to sys.path
sys.path.append(parent_dir)

# Now you can import a module from the parent directory
from agents4e import Thing, XYEnvironment, Agent, Obstacle


GAME_WON=False

# Define custom destination blocks
class PositiveDestination(Thing):
    """A destination that awards 100 points and wins the game when an agent reaches it"""
    pass


class NegativeDestination(Thing):
    """A destination that penalises 50 points when an agent reaches it"""
    pass


class GridWorldEnvironment(XYEnvironment):
    ''' This environment has a grid of rows and columns with obstacles '''

    def __init__(self, width, height):
        super().__init__()
        self.width = width
        self.height = height

    def get_agent_percepts(self, agent, env):
        """
        Returns the available moves for an agent in the given environment.
        """
        x, y = agent.location
        
        # Get positions of all obstacles in the environment
        obstacle_positions = [
                            (thing.location[0], thing.location[1])
                            for thing in env.things
                            if isinstance(thing, Obstacle)]
        
        return self.get_available_moves(x, y, env.width, env.height, obstacle_positions)

    def percept(self, agent):
        """ In this environment, a percept is a list of available movements from the agent's current location,
            based on the grid size and location of any obstacles in the environment, and the cost of moving to the
            new location.
            The movement directions could be 'up', 'down', 'left', or 'right'."""
        x, y = agent.location
        obstacle_positions = [(thing.location[0], thing.location[1])
                             for thing in self.things 
                             if isinstance(thing, Obstacle)]

        available_moves_with_costs = self.get_available_moves(x, y, self.width, self.height, obstacle_positions)
        return available_moves_with_costs

    def get_available_moves(self, x, y, width, height, obstacles=None):
        """
        Returns a list of available directions (up, down, left, right) that an agent can move
        based on its current position, grid boundaries and obstacles """

        if obstacles is None:
            obstacles = []

        available_moves = []

        # Check up (up is decreasing y)
        if y > 0 and (x, y-1) not in obstacles:
            available_moves.append(('up', (x + (y-1))))

        # Check down (down is increasing y)
        if y < height-1 and (x, y+1) not in obstacles:
            available_moves.append(('down', (x + (y+1))))

        # Check right (right is increasing x)
        if x < width-1 and (x+1, y) not in obstacles:
            available_moves.append(('right', ((x+1) + y)))

        # Check left (left is decreasing x)
        if x > 0 and (x-1, y) not in obstacles:
            available_moves.append(('left', ((x-1) + y)))

        # print(f"AVAILABLE MOVES FROM {x, y}: {available_moves}")
        return available_moves

    def execute_action(self, agent, action):
        global GAME_WON
        initial_location = agent.location

        # Calculate obstacle positions
        obstacle_positions = [(thing.location[0], thing.location[1])
                              for thing in self.things
                              if isinstance(thing, Obstacle)]

        # Get the list of moves available to the agent, and exit if the current move is invalid
        if not any(action in tup for tup in self.get_available_moves(agent.location[0],
                                                                 agent.location[1],
                                                             self.width,
                                                            self.height,
                                                         obstacle_positions)):

            print(f"❌ Tried to go [{action:5}] from {agent.location}, but cant go in that direction")
            return

        if action == 'up':
            agent.location = (agent.location[0], agent.location[1] - 1)  # Move up (decrease y)
        elif action == 'down':
            agent.location =  (agent.location[0], agent.location[1] + 1)  # Move down (increase y)
        elif action == 'left':
            agent.location =  (agent.location[0] - 1, agent.location[1])  # Move left (decrease x)
        elif action == 'right':
            agent.location =  (agent.location[0] + 1, agent.location[1])  # Move right (increase x)
        else:
            agent.location =  (agent.location[0], agent.location[1])
        print(f"✅ You  moved [{action:5}] from {initial_location} to {agent.location} successfully : Performance penalty: {agent.location[0] + agent.location[1]:4}  Performance Total: {agent.performance:4}")

        # Charge the agent some points to the agent for making a move
        agent.performance -= (agent.location[0] + agent.location[1])

        # Check if agent is at the winning destination
        positive_destinations = self.list_things_at(agent.location, PositiveDestination)
        if positive_destinations:
            agent.performance += 100
            print("Agent reached winning destination! Performance increase 100.")
            print(f"🎉 Congratulations, you WON the game with a score of {agent.performance}!!")
            GAME_WON=True

        # Check if agent is at a penalty destination
        negative_destinations = self.list_things_at(agent.location, NegativeDestination)
        if negative_destinations:
            agent.performance -= 50
            print(f"😭 You have reached the penalty destination!             : Performance penalty:   50  Performance Total: {agent.performance:4}")


class ReflexAgent(Agent):
    """A reflex agent that always moves to the cheapest adjacent square. 
       This agent doesnt care about the percept list. """

    def __init__(self):
        super().__init__(self.cheapest_move)

    def cheapest_move(self, percept):
        """
        Takes a percept (list of available moves with costs) and returns
        the direction with the lowest cost.

        Each move in percept is a tuple of (direction, cost)
        """
        if not percept:
            return None  # No moves available

        # Find the move with the minimum cost
        cheapest = min(percept, key=lambda x: x[1])

        # Return the direction of the cheapest move
        return cheapest[0]


class RandomAgent(Agent):
    """A simple agent program that moves randomly. The agent does receive a percept, but ignores it, as it is a random agent.
       The agent returns a random action """
    def __init__(self): 
        super().__init__(self.random_move)
    
    def random_move(self, percept):
        return random.choice(['down', 'left', 'up', 'right'])



# Create and set up the environment
def create_gridworld_environment(width, height, env_agent):

    # Create the 2D grid world with the set width and height
    env = GridWorldEnvironment(width, height)

    # Set the poitions of the obstacle, the penalty block and the winning block
    obstacle_x = 1
    obstacle_y = 1
    pos_x = 3
    pos_y = 0
    neg_x = 3
    neg_y = 1

    # Add the obstacle, the penalty block and the winning block to the environment
    env.add_thing(Obstacle(), (obstacle_x, obstacle_y))
    env.add_thing(PositiveDestination(), (pos_x, pos_y))
    env.add_thing(NegativeDestination(), (neg_x, neg_y))

    # Create and add the agent to the environment
    agent = Agent(env_agent)
    random_position = (random.randint(0, width - 1), random.randint(0, height - 1))
    env.add_thing(agent, random_position)

    print(f"Obstacle location is {obstacle_x}, {obstacle_y}")
    print(f"Positive location is {pos_x}, {pos_y}")
    print(f"Negative location is {neg_x}, {neg_y}")
    print(f"Starting position is {random_position}")

    return env


def main():
    global GAME_WON

    # Generate and run the environment for 20 steps with a list of agents
    agent_list =  [RandomAgent().random_move, ReflexAgent().cheapest_move]
    for agent in agent_list:
        print("********************************************************")
        print(f"* Agent: {agent.__name__:45} *")
        print("********************************************************")
        env = create_gridworld_environment(4, 3, agent)
        env.run(20)
        if not GAME_WON:
            print(f"😔 Winning location not found.. {agent.__name__} lost with a score of {env.agents[0].performance}")
            GAME_WON=False
        print("\n")


if __name__ == "__main__":
    main()
