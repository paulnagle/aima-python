"""
# A1_COMP9016_Nagle_JohnPaul_R00065426.py
#
# Name:         (John) Paul Nagle
# Student ID:   R00065426
# Class:        Knowledge Representation
# Assignment:   1
#
# The 2D world is comprised of a grid of blocks.
# There is one obstacle block that no agent can move to
# An agent gets charged some points (sum of x and y co-ordinates) for making a move.
# An agent gets penalised 50 points if it lands on the penalty block
# If the agent reaches the winning block it gets 100 points, wins the game and
# the game ends
# If the agent does not reach the winning block in the set number of moves, the game ends
# and the agent has lost the game.
#
# Here is an example map of the 2D world 
# (4 by 3 grid, obstacle at (1, 1), penalty at (3, 1) and winning block at (3, 0))
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


#  Agents:  Random Agent, picks the next move randomly (for comparison only)
#           Simple Reflex agent, always moves to the cheapest adjacent square.
#           Model based reflex agent, uses a model to predict the future.
#           Goal Based Agent, uses the history of precepts to determine the next move.


"""

import sys
import os
import random
import argparse
import time

# Parse command line arguments
parser = argparse.ArgumentParser(description='Grid World Environment Simulation')
parser.add_argument('-v', '--verbose', action='store_true',
                    help='Print detailed movement information')
parser.add_argument('-s', '--steps', type=int, required=True,
                    help='Number of steps to run the simulation (mandatory)')
parser.add_argument('-r', '--runs', type=int, required=True,
                    help='Number of times to run each agent (mandatory)')
args = parser.parse_args()

# Get the absolute path of the script's directory
script_dir = os.path.dirname(os.path.abspath(__file__))

# Get the parent directory (project root)
parent_dir = os.path.dirname(script_dir)

# Add the parent directory to sys.path
sys.path.append(parent_dir)

# Now you can import a module from the parent directory
from agents4e import Thing, XYEnvironment, Agent, Obstacle

# A global variable to keep track of whether the game is won or not
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

        # A list of positions of all obstacles in the environment
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
            if args.verbose:
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
        if args.verbose:
            print(f"✅ You  moved [{action:5}] from {initial_location} to {agent.location} successfully : Performance penalty: {agent.location[0] + agent.location[1]:4}  Performance Total: {agent.performance:4}")

        # Charge the agent some points to the agent for making a move
        agent.performance -= (agent.location[0] + agent.location[1])

        # Check if agent is at the winning destination
        positive_destinations = self.list_things_at(agent.location, PositiveDestination)
        if positive_destinations:
            agent.performance += 100
            if args.verbose:
                print("Agent reached winning destination! Performance increase 100.")
                print(f"🎉 Congratulations, you WON the game with a score of {agent.performance}!!")
                print("👏 Well done! You've successfully completed the game!")
            GAME_WON=True

        # Check if agent is at a penalty destination
        negative_destinations = self.list_things_at(agent.location, NegativeDestination)
        if negative_destinations:
            agent.performance -= 50
            if args.verbose:
                print(f"😭 You have reached the penalty destination!             : Performance penalty:   50  Performance Total: {agent.performance:4}")

    def is_done(self):
        """The environment is done if the agent has won the game or if no agents are alive."""
        global GAME_WON
        return GAME_WON or super().is_done()


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
def create_gridworld_environment(width, height):

    # Create the 2D grid world with the set width and height
    env = GridWorldEnvironment(width, height)

    # Set random positions for the obstacle, the penalty block and the winning block
    # Create a list to track occupied positions
    occupied_positions = []

    # Generate random position for obstacle
    obstacle_x = random.randint(0, width - 1)
    obstacle_y = random.randint(0, height - 1)
    occupied_positions.append((obstacle_x, obstacle_y))

    # Generate random position for positive destination (winning block)
    while True:
        pos_x = random.randint(0, width - 1)
        pos_y = random.randint(0, height - 1)
        if (pos_x, pos_y) not in occupied_positions:
            occupied_positions.append((pos_x, pos_y))
            break

    # Generate random position for negative destination (penalty block)
    while True:
        neg_x = random.randint(0, width - 1)
        neg_y = random.randint(0, height - 1)
        if (neg_x, neg_y) not in occupied_positions:
            occupied_positions.append((neg_x, neg_y))
            break

    # Add the obstacle, the penalty block and the winning block to the environment
    env.add_thing(Obstacle(), (obstacle_x, obstacle_y))
    env.add_thing(PositiveDestination(), (pos_x, pos_y))
    env.add_thing(NegativeDestination(), (neg_x, neg_y))

    if args.verbose:
        print(f"Obstacle location is {obstacle_x}, {obstacle_y}")
        print(f"Positive location is {pos_x}, {pos_y}")
        print(f"Negative location is {neg_x}, {neg_y}")

    return env, occupied_positions


def building_your_world(steps, runs):
    global GAME_WON

    # Generate and run the environment for {steps} steps with a list of agents
    agent_list = [RandomAgent().random_move, ReflexAgent().cheapest_move]
    
    for agent_program in agent_list:
        print("")
        print("********************************************************")
        print(f"* Agent: {agent_program.__name__:45} *")
        print("********************************************************")
        
        # Statistics for this agent across all runs
        total_performance = 0
        wins = 0
        
        # Run the agent the specified number of times
        for run in range(1, runs + 1):
            # Create a new environment for each run
            width, height = 10, 10
            env, occupied_positions = create_gridworld_environment(width, height)
            
            if args.verbose:
                print(f"\nRun {run} of {runs}")
            
            # Create a new agent
            agent = Agent(agent_program)
            
            # Generate random position for agent that doesn't overlap with other objects
            while True:
                random_position = (random.randint(0, width - 1), random.randint(0, height - 1))
                if random_position not in occupied_positions:
                    break
            
            # Add the agent to the environment
            env.add_thing(agent, random_position)
            if args.verbose:
                print(f"Starting position is {random_position}")
            
            # Run the simulation and measure time
            start_time = time.time()
            env.run(steps)
            end_time = time.time()
            elapsed_time = end_time - start_time
            
            # Update statistics
            total_performance += env.agents[0].performance
            if GAME_WON:
                wins += 1
                
            # Print results for this run
            print(f"AGENT:{agent_program.__name__}\tRUN:{run}/{runs}\tSTEPS:{steps}\tRESULT:{'WIN' if GAME_WON else 'LOST'}\tPERFORMANCE:{env.agents[0].performance:5}\t\tTIME:{elapsed_time:.4f}s")
            
            # Remove the agent from the environment
            env.delete_thing(agent)
            
            # Reset the global variable GAME_WON for the next run
            GAME_WON = False
        
        # Print summary statistics for this agent
        avg_performance = total_performance / runs
        win_rate = (wins / runs) * 100
        print(f"\nSummary for {agent_program.__name__}:")
        print(f"Average Performance: {avg_performance:.2f}")
        print(f"Win Rate: {win_rate:.2f}% ({wins}/{runs})")


def searching_your_world():
    pass


if __name__ == "__main__":
    # If not in verbose mode, print a message about the -v option
    if not args.verbose:
        print("Run with -v or --verbose to see detailed movement information")
    building_your_world(args.steps, args.runs)
    searching_your_world()
