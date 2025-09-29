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
# (width 4 by depth 3 grid, obstacle at (1, 1), penalty at (3, 1) and winning block at (3, 0))
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


#  Agents:  Random Agent, picks the next move randomly
#           Simple Reflex agent, always moves to the cheapest adjacent square.
#           Model based reflex agent, uses an internal model to predict the what the best move will be.

"""

import sys
import os
import random
import argparse
import time

# Get the absolute path of the script's directory
script_dir = os.path.dirname(os.path.abspath(__file__))

# Get the parent directory (project root)
parent_dir = os.path.dirname(script_dir)

# Add the parent directory to sys.path
sys.path.append(parent_dir)

# Now you can import a module from the parent directory
from agents4e import Thing, XYEnvironment, Agent, Obstacle


# Define a global utility dictionary mapping directions to coordinate changes
direction_to_coords = {
    'up': (0, -1),
    'down': (0, 1),
    'left': (-1, 0),
    'right': (1, 0)
}


# A global variable to keep track of whether the game is won or not
GAME_WON=False


# A global function to display a message based on the verbose command line parameter being True
def log_message(message):
    """Log a message if verbose mode is enabled."""
    if args.verbose:
        print(message)


class PositiveDestination(Thing):
    """ A destination that awards 100 points and wins the game when an agent reaches it """
    pass


class NegativeDestination(Thing):
    """ A destination that penalises 50 points when an agent reaches it """
    pass


class GridWorldEnvironment(XYEnvironment):
    """ This environment has a grid of rows and columns with obstacles """
    def __init__(self, width, depth):
        super().__init__()
        self.width = width
        self.depth = depth

    def percept(self, agent):
        """ In this environment, a percept is a list of available movements from the agent's current location,
            based on the grid size and location of any obstacles in the environment, and the cost of moving to the
            new location.
            The movement directions could be 'up', 'down', 'left', or 'right'. """
        x, y = agent.location
        obstacle_positions = []
        for thing in self.things:
            if isinstance(thing, Obstacle):
                # Safely get location if it exists
                if hasattr(thing, 'location') and thing.location is not None:
                    obstacle_positions.append(thing.location)

        available_moves_with_costs = self.get_available_moves_with_costs(x, y, self.width, self.depth, obstacle_positions)
        return available_moves_with_costs

    def get_available_moves_with_costs(self, x, y, width, depth, obstacles=None):
        """ Returns a list of available directions (up, down, left, right) that an agent can move
            based on its current position, grid boundaries and obstacles """

        if obstacles is None:
            obstacles = []

        available_moves = []

        # Check up (up is decreasing y)
        if y > 0 and (x, y-1) not in obstacles:
            available_moves.append(('up', (x + (y-1))))

        # Check down (down is increasing y)
        if y < depth-1 and (x, y+1) not in obstacles:
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
        obstacle_positions = []
        for thing in self.things:
            if isinstance(thing, Obstacle):
                # Safely get location if it exists
                if hasattr(thing, 'location') and thing.location is not None:
                    obstacle_positions.append(thing.location)

        # Check if move is valid
        if not self._is_valid_move(agent, action, obstacle_positions):
            log_message(f"❌ Tried to go [{action:5}] from {agent.location}, but cant go in that direction")
            return

        # Update agent location based on action using the direction_to_coords dictionary
        if action in direction_to_coords:
            dx, dy = direction_to_coords[action]
            agent.location = (agent.location[0] + dx, agent.location[1] + dy)

        log_message(f"✅ You  moved [{action:5}] from {initial_location} to {agent.location} successfully : Performance penalty: {agent.location[0] + agent.location[1]:4}  Performance Total: {agent.performance:4}")

        # Charge the agent for making a move (the cost is the sum of the x and y co-ordinates)
        agent.performance -= (agent.location[0] + agent.location[1])

        # Check destinations and apply effects
        self._check_destinations(agent)

    def _is_valid_move(self, agent, action, obstacle_positions):
        """Check if the action is valid for the agent's current position."""
        available_moves = self.get_available_moves_with_costs(
            agent.location[0],
            agent.location[1],
            self.width,
            self.depth,
            obstacle_positions
        )
        return any(action in tup for tup in available_moves)

    def _check_destinations(self, agent):
        """Check if agent is at special destinations and apply effects."""
        global GAME_WON

        # Check for positive destination (winning)
        positive_destinations = self.list_things_at(agent.location, PositiveDestination)
        if positive_destinations:
            agent.performance += 100
            log_message("Agent reached winning destination! Performance increase 100.")
            log_message(f"🎉 Congratulations, you WON the game with a score of {agent.performance}!!")
            log_message("👏 Well done! You've successfully completed the game!")
            GAME_WON = True

        # Check for negative destination (penalty)
        negative_destinations = self.list_things_at(agent.location, NegativeDestination)
        if negative_destinations:
            agent.performance -= 50
            log_message(f"😭 You have reached the penalty destination!             : Performance penalty:   50  Performance Total: {agent.performance:4}")

    def is_done(self):
        """ The environment is done if the agent has won the game or if no agents are alive. """
        global GAME_WON
        return GAME_WON or super().is_done()


class RandomAgent(Agent):
    """ A simple agent program that moves randomly. The agent does receive a percept, 
        but ignores it, as it is a random agent. The agent returns a random action """
    def __init__(self):
        super().__init__(self.random_move)

    def random_move(self, percept):
        """ This function takes a percept and returns a random move """
        return random.choice(['down', 'left', 'up', 'right'])


class ReflexAgent(Agent):
    """ A reflex agent that always moves to the cheapest adjacent square. 
        This agent doesnt care about the percept list. """

    def __init__(self):
        super().__init__(self.cheapest_move)

    def cheapest_move(self, percept):
        """ Takes a percept (list of available moves with costs) and returns
            the direction with the lowest cost. Each move in percept is a tuple 
            of (direction, cost) """
        if not percept:
            return None  # No moves available

        # Find the move with the minimum cost
        cheapest = min(percept, key=lambda x: x[1])

        # Return the direction of the cheapest move
        return cheapest[0]


class ModelBasedReflexAgent(Agent):
    """A model-based reflex agent that uses an internal model of the environment to make decisions.
       The internal model is built up as the agent moves around the environment"""

    def __init__(self):
        # Initialize the agent with the model-based reflex program
        super().__init__(self.model_based_reflex_agent)

        # Initialize the model
        self.model = {
            'width': None,                        # Will be inferred from percepts
            'depth': None,                        # Will be inferred from percepts
            'obstacles': set(),                   # Known obstacle positions
            'negative_dest': None,                # Penalty block position (if known)
            'visited': set(),                     # Positions the agent has visited
            'last_performance': 0,                # Last known performance value
            'last_position': None,                # Last position of the agent
            'move_history': [],                   # History of moves to avoid loops
        }

        # Initialize state and action
        self.state = None
        self.action = None
    
    def model_based_reflex_agent(self, percept):
        """The model-based reflex agent program."""
        # Initialize state if first call
        if self.state is None:
            # Make sure we have a location before initializing state
            if hasattr(self, 'location') and self.location is not None:
                self.state = {'location': self.location, 'performance': 0}
                # Add initial location to visited positions
                self.model['visited'].add(self.location)
                self.model['last_position'] = self.location
                self.model['last_performance'] = 0

        # Update the state based on percept and model
        if self.state is not None:
            self.state = self.update_state(self.state, self.action, percept)

            # Apply rules to determine the action
            self.action = self.apply_rules(percept)

            # Record this move in history to detect loops
            if self.action is not None:
                self.model['move_history'].append(self.action)
                # Keep only the last 10 moves in history
                if len(self.model['move_history']) > 10:
                    self.model['move_history'] = self.model['move_history'][-10:]

            return self.action

        # If state is not initialized yet, default to a random move
        if percept:
            return random.choice([move[0] for move in percept])
        return None

    def update_state(self, state, action, percept):
        """Update the state based on percept and model."""
        # Update the model with the current location
        if action is not None:
            # Save the last position and performance
            self.model['last_position'] = state['location']
            self.model['last_performance'] = state['performance']

            # Update current location based on the action taken using direction_to_coords
            x, y = state['location']
            if action in direction_to_coords:
                dx, dy = direction_to_coords[action]
                state['location'] = (x + dx, y + dy)

            # Update performance in state
            state['performance'] = self.performance

            # Check for significant performance changes
            perf_change = state['performance'] - self.model['last_performance']

            # If performance decreased by more than the move cost, might be a penalty block
            expected_cost = state['location'][0] + state['location'][1]
            if perf_change < -expected_cost - 10:  # Significant penalty (more than just move cost)
                self.model['negative_dest'] = state['location']

        # Add current location to visited positions
        self.model['visited'].add(state['location'])

        # Try to infer grid dimensions and obstacles from percepts
        if percept:
            # Infer possible moves from current position
            possible_directions = [move[0] for move in percept]
            x, y = state['location']

            # If we can't move up, we might be at the top edge or there's an obstacle
            if 'up' not in possible_directions and y > 0:
                self.model['obstacles'].add((x, y-1))

            # If we can't move down, we might be at the bottom edge or there's an obstacle
            if 'down' not in possible_directions:
                # Infer depth if we can't move down
                if self.model['depth'] is None or y + 1 > self.model['depth']:
                    self.model['depth'] = y + 1
                else:
                    self.model['obstacles'].add((x, y+1))

            # If we can't move left, we might be at the left edge or there's an obstacle
            if 'left' not in possible_directions and x > 0:
                self.model['obstacles'].add((x-1, y))

            # If we can't move right, we might be at the right edge or there's an obstacle
            if 'right' not in possible_directions:
                # Infer width if we can't move right
                if self.model['width'] is None or x + 1 > self.model['width']:
                    self.model['width'] = x + 1
                else:
                    self.model['obstacles'].add((x+1, y))

        return state

    def apply_rules(self, percept):
        """Apply rules to determine the action."""
        if not percept:
            return None

        # Rule 1: If we know where the penalty block is, avoid it
        if self.model['negative_dest'] is not None and self.state is not None:
            # Filter out moves that would lead to the penalty block
            neg_pos = self.model['negative_dest']

            # Make sure neg_pos is a valid tuple
            if isinstance(neg_pos, tuple) and len(neg_pos) == 2:
                neg_x, neg_y = neg_pos
                x, y = self.state['location']

                safe_moves = []
                for move in percept:
                    direction = move[0]
                    # Calculate new position using direction_to_coords
                    if direction in direction_to_coords:
                        dx, dy = direction_to_coords[direction]
                        new_pos = (x + dx, y + dy)

                        if new_pos != (neg_x, neg_y):
                            safe_moves.append(move)

                if safe_moves:
                    # Continue with the remaining rules using only safe moves
                    percept = safe_moves

        # Rule 2: Avoid getting stuck in loops
        if len(self.model['move_history']) >= 4:
            # Check for simple loops like up-down-up-down or left-right-left-right
            last_moves = self.model['move_history'][-4:]
            if (last_moves[0] == last_moves[2] and last_moves[1] == last_moves[3] and self.opposite_direction(last_moves[0]) == last_moves[1]):
                # We're in a loop, try to break out by choosing a different move
                loop_moves = {last_moves[0], last_moves[1]}
                non_loop_moves = [move for move in percept if move[0] not in loop_moves]
                if non_loop_moves:
                    # Choose the cheapest non-loop move
                    return min(non_loop_moves, key=lambda x: x[1])[0]

        # Rule 3 Prefer moves to unvisited positions
        if self.state is not None:
            unvisited_moves = []
            for move in percept:
                direction = move[0]
                x, y = self.state['location']

                # Calculate new position using direction_to_coords
                if direction in direction_to_coords:
                    dx, dy = direction_to_coords[direction]
                    new_pos = (x + dx, y + dy)

                    # Check if the new position is unvisited
                    if new_pos not in self.model['visited']:
                        unvisited_moves.append(move)

            if unvisited_moves:
                # Choose the cheapest unvisited move
                return min(unvisited_moves, key=lambda x: x[1])[0]

        # Rule 4: Choose the move with the lowest cost
        return min(percept, key=lambda x: x[1])[0]

    def opposite_direction(self, direction):
        """Return the opposite direction."""
        opposites = {
            'up': 'down',
            'down': 'up',
            'left': 'right',
            'right': 'left'
        }
        return opposites.get(direction)


# Create and set up the environment
def create_gridworld_environment(width, depth):
    """ Create a 2D grid world environment with the specified width and depth.
        The environment is represented as a 2D list of cells, where each cell can be either
        a wall, a negative destination (penalty block), or a positive destination (winning block)."""
    # Create the 2D grid world with the set width and depth
    env = GridWorldEnvironment(width, depth)

    # Set random positions for the obstacle, the penalty block and the winning block
    # Create a list to track occupied positions
    occupied_positions = []

    # Generate random position for obstacle
    obstacle_x = random.randint(0, width - 1)
    obstacle_y = random.randint(0, depth - 1)
    occupied_positions.append((obstacle_x, obstacle_y))

    # Generate random position for positive destination (winning block)
    while True:
        pos_x = random.randint(0, width - 1)
        pos_y = random.randint(0, depth - 1)
        if (pos_x, pos_y) not in occupied_positions:
            occupied_positions.append((pos_x, pos_y))
            break

    # Generate random position for negative destination (penalty block)
    while True:
        neg_x = random.randint(0, width - 1)
        neg_y = random.randint(0, depth - 1)
        if (neg_x, neg_y) not in occupied_positions:
            occupied_positions.append((neg_x, neg_y))
            break

    # Add the obstacle, the penalty block and the winning block to the environment
    env.add_thing(Obstacle(), (obstacle_x, obstacle_y))
    env.add_thing(PositiveDestination(), (pos_x, pos_y))
    env.add_thing(NegativeDestination(), (neg_x, neg_y))

    log_message(f"Obstacle location is {obstacle_x}, {obstacle_y}")
    log_message(f"Positive location is {pos_x}, {pos_y}")
    log_message(f"Negative location is {neg_x}, {neg_y}")

    return env, occupied_positions


def building_your_world():
    """ This function is used to build the world for the agent to explore."""
    global GAME_WON

    # Generate and run the environment for {steps} steps with a list of agents
    agent_list = [RandomAgent().random_move, ReflexAgent().cheapest_move, ModelBasedReflexAgent().model_based_reflex_agent]

    for agent_program in agent_list:
        log_message("")
        log_message("********************************************************")
        log_message(f"* Agent: {agent_program.__name__:45} *")
        log_message("********************************************************")

        # Statistics for this agent across all runs
        agent_stats = {
            'total_performance': 0,
            'wins': 0
        }

        # Create a new environment for the set of runs per agent type
        env, occupied_positions = create_gridworld_environment(args.width, args.depth)

        # Run the agent the specified number of times
        for run in range(1, args.runs + 1):
            log_message(f"\nRun {run} of {args.runs}")

            # Create a new agent
            agent = Agent(agent_program)

            # Generate random position for agent that doesn't overlap with other objects
            while True:
                random_position = (random.randint(0, args.width - 1), random.randint(0, args.depth - 1))
                if random_position not in occupied_positions:
                    break

            # Add the agent to the environment
            env.add_thing(agent, random_position)
            log_message(f"Starting position is {random_position}")

            # Run the simulation and measure time
            start_time = time.time()
            env.run(args.steps)
            end_time = time.time()
            elapsed_time = end_time - start_time

            # Update statistics using the dictionary
            agent_stats['total_performance'] += agent.performance  # Store performance before deletion
            if GAME_WON:
                agent_stats['wins'] += 1

            # Print results for this run
            log_message(f"AGENT:{agent_program.__name__}\tRUN:{run}/{args.runs}\tSTEPS:{args.steps}\tRESULT:{'WIN' if GAME_WON else 'LOSE'}\tPERFORMANCE:{agent.performance:5}\t\tTIME:{elapsed_time:.4f}s")

            # Remove the agent from the environment if it's still in the environment
            if agent in env.things:
                env.delete_thing(agent)

            # Reset the global variable GAME_WON for the next run
            GAME_WON = False

        # Print summary statistics for this agent
        avg_performance = agent_stats['total_performance'] / args.runs
        win_rate = (agent_stats['wins'] / args.runs) * 100
        print(f"\nSummary for [{agent_program.__name__:30}]: Average Performance: {avg_performance:.2f} Win Rate: {win_rate:.2f}% ({agent_stats['wins']}/{args.runs})")


def searching_your_world():
    pass


if __name__ == "__main__":

    # Parse command line arguments
    parser = argparse.ArgumentParser(description='A1_COMP9016_Nagle_JohnPaul_R00065426')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Print detailed movement and agent information')
    parser.add_argument('-s', '--steps', type=int, required=True,
                        help='Number of steps per run to attempt to win the game (mandatory)')
    parser.add_argument('-r', '--runs', type=int, required=True,
                        help='Number of times to run each agent (mandatory)')
    parser.add_argument('-w', '--width', type=int, required=True,
                        help='Width of the grid world (mandatory)')
    parser.add_argument('-d', '--depth', type=int, required=True,
                        help='depth of the grid world (mandatory)')
    args = parser.parse_args()

    building_your_world()
    searching_your_world()
