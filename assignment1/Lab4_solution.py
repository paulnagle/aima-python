# Import necessary modules and ensure the correct path to aima-python
import sys
sys.path.append('./aima-python')  # Adjust the path to where aima-python is located

import random
from agents import Agent, XYEnvironment, Dirt
from search import Problem, breadth_first_graph_search

# Step 1: Define the RandomVacuumAgent
# This agent will be placed in the environment but is not directly used in the search-based solution.
class RandomVacuumAgent(Agent):
    """An agent that randomly selects an action at each step."""

    def __init__(self):
        super().__init__()
        self.program = self.random_program  # Attach the agent's program

    def random_program(self, percept):
        """The agent's program that returns a random action."""
        return random.choice(['Suck', 'Left', 'Right', 'Up', 'Down'])

# Step 2: Define the RandomDirtVacuumEnvironment
# This environment simulates a grid where dirt is placed at random locations.
class RandomDirtVacuumEnvironment(XYEnvironment):
    """Environment where dirt is randomly placed on a grid."""

    def __init__(self, width=5, height=5, dirt_prob=0.2):
        super().__init__(width, height)
        self.dirt_prob = dirt_prob
        self.populate_with_dirt()  # Populate the environment with dirt

    def populate_with_dirt(self):
        """Randomly place dirt in the environment based on dirt_prob."""
        for x in range(self.width):
            for y in range(self.height):
                if random.random() < self.dirt_prob:
                    self.add_thing(Dirt(), (x, y))

# Step 3: Define the VacuumProblem for search
# Convert the vacuum environment into a search problem.
class VacuumProblem(Problem):
    """Search problem representation of the vacuum environment."""

    def __init__(self, initial_state, width, height):
        """
        initial_state: ((x, y), dirt_locations)
        width, height: dimensions of the grid
        """
        print("Initial state:", initial_state)
        self.width = width
        self.height = height
        super().__init__(initial_state)

    def actions(self, state):
        """Return the possible actions from the current state."""
        print("Current state:", state)
        (x, y), dirt_locations = state  # Unpack the agent's position and dirt locations
        actions = []

        # Check boundaries and add possible movement actions
        if x > 0:
            actions.append('Left')
        if x < self.width - 1:
            actions.append('Right')
        if y > 0:
            actions.append('Up')
        if y < self.height - 1:
            actions.append('Down')

        # 'Suck' action to clean dirt at the current position
        actions.append('Suck')
        return actions

    def result(self, state, action):
        """Return the new state after performing the given action."""
        (x, y), dirt_locations = state  # Unpack the current state
        dirt_locations = set(dirt_locations)  # Convert to set for easy manipulation

        # Define the result of each possible action
        if action == 'Left':
            return ((x - 1, y), tuple(dirt_locations))
        elif action == 'Right':
            return ((x + 1, y), tuple(dirt_locations))
        elif action == 'Up':
            return ((x, y - 1), tuple(dirt_locations))
        elif action == 'Down':
            return ((x, y + 1), tuple(dirt_locations))
        elif action == 'Suck':
            # Remove dirt at the current position if present
            if (x, y) in dirt_locations:
                dirt_locations.remove((x, y))
            return ((x, y), tuple(dirt_locations))

    def goal_test(self, state):
        """Check if all dirt has been cleaned."""
        _, dirt_locations = state
        return len(dirt_locations) == 0

    def step_cost(self, state, action, result):
        """Define the cost of each action."""
        if action == 'Suck':
            return -100  # Negative cost to represent a reward for cleaning
        else:
            return 1  # Positive cost for movement

# Step 4: Automatically Generate the Initial State from the Environment
def get_initial_state_from_env(env):
    """Extract the agent's position and dirt locations from the environment."""
    agent_location = None
    dirt_locations = set()

    # Iterate over all things in the environment
    for thing in env.things:
        if isinstance(thing, Dirt):
            dirt_locations.add(thing.location)
        elif isinstance(thing, Agent):
            agent_location = thing.location

    return (agent_location, tuple(dirt_locations))  # Return as a tuple for hashability

# Step 5: Solve the Problem Using Search Algorithms
if __name__ == '__main__':
    # Create an instance of the agent
    agent = RandomVacuumAgent()

    # Initialize the environment and add the agent
    env = RandomDirtVacuumEnvironment(width=5, height=5, dirt_prob=0.3)
    env.add_thing(agent, (0, 0))  # Place the agent at position (0, 0)

    # Generate the initial state from the environment
    initial_state = get_initial_state_from_env(env)
    print("Initial state:", initial_state)  # For debugging

    # Define the vacuum problem for the search
    vacuum_problem = VacuumProblem(initial_state, env.width, env.height)

    # Use breadth-first search to find a solution
    solution_node = breadth_first_graph_search(vacuum_problem)

    # Output the results
    if solution_node:
        print("Solution found!")
        print("Solution steps:", solution_node.solution())
        print("Path to solution:", [node.state for node in solution_node.path()])
        print("Total cost:", solution_node.path_cost)
    else:
        print("No solution found.")
