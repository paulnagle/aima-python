import sys
import matplotlib.pyplot as plt
import random

sys.path.append('./aima-python')  # Ensure correct path to aima-python
print(sys.path)  # Check if aima-python is in sys.path

import agents4e as agents # Importing the agents module

# Import necessary classes from agents4e.py
from agents import (TrivialVacuumEnvironment, RandomVacuumAgent, TableDrivenVacuumAgent, ReflexVacuumAgent, ModelBasedVacuumAgent, compare_agents, TableDrivenAgentProgram, Environment, Agent, TraceAgent, VacuumEnvironment)

# """
# @author: Ruairi.OReilly
# """

"""A. The Farmer’s Dilemma"""

# 2) Specify a state diagram that realises the above solution (text, table, drawing - your choice).

"""
The states will be represented by the location of the farmer, chicken, feed, and fox. Let's denote:

A: Starting location (left side of the river).
B: Destination location (right side of the river).

The state can be represented as a tuple (Farmer, Chicken, Feed, Fox) where each element is either A (left bank) or B (right bank).

Initial state: (A, A, A, A) — all start at location A.
Goal state: (B, B, B, B) — all should safely reach location B.

The state transitions depend on the moves the farmer makes (either alone or carrying an item), and the constraints include:

- The farmer can only carry one thing at a time.
- The fox cannot be left with the chicken unless the farmer is present.
- The chicken cannot be left with the feed unless the farmer is present.

Table of Transitions:
Step	Far.	Chic.	Feed	Fox	Action
1	    A	    A	    A 	  A	Initial State
2	    B	    B	    A	    A	Farmer Moves chicken across
3	    A	    B	    A	    A	Farmer returns alone
4	    B	    B	    A	    B	Farmer Moves fox across
5	    A	    A	    A	    B	Farmer returns with chicken
6	    B	    A	    B	    B	Farmer Moves feed across
7	    A	    A	    B	    B	Farmer returns alone
8	    B	    B	    B	    B	Farmer Moves chicken across (Goal State)
"""

# 3) Derive the list of percepts that would be experienced by a farmer agent to include location, chicken, feed and fox.

"""
The percepts are the observations the farmer makes about the location of each of the objects (chicken, fox, feed) and the relative safety of leaving them together. The percepts will consist of:

- Farmer's current location.
- Location of the chicken.
- Location of the fox.
- Location of the feed.

Each percept will be a tuple representing these positions at any given state.

For example:
Initial state percept: (Farmer=A, Chicken=A, Fox=A, Feed=A)
After the first move: (Farmer=B, Chicken=B, Fox=A, Feed=A)
"""

# 4) Define the appropriate actions needed for solving the problem.

"""
The set of actions the farmer can Move is:
- Move(Chicken)
- Move(Fox)
- Move(Feed)
- ReturnAlone

Each action changes the state according to the movement of the farmer and any item he carries across the river.
"""

# 5) Generate the percept sequence necessary map the appropriate actions for the problem to be solved.

""" NOTE I AM ONLY CONSIDERING ONE SOLUTION PATH 
The percept sequence maps to the following actions:
    Percept: (A, A, A, A) → Action: Move(Chicken)
    Percept: (B, B, A, A) → Action: ReturnAlone
    Percept: (A, B, A, A) → Action: Move(Fox)
    Percept: (B, B, A, B) → Action: Move(Chicken)
    Percept: (A, A, A, B) → Action: Move(Feed)
    Percept: (B, A, B, B) → Action: ReturnAlone
    Percept: (A, A, B, B) → Action: Move(Chicken)
    Percept: (B, B, B, B) → Action: Goal State Reached
"""

#6) Implement a TableDrivenAgentProgram (see agents.py) that will solve this problem - note may require  customisation of a TableDrivenAgentProgram and associated environment.


# Define the problem states as tuples (Farmer, Chicken, Feed, Fox)
initial_state = ('A', 'A', 'A', 'A')
goal_state = ('B', 'B', 'B', 'B')

# Table of percepts -> actions
# Mapping percepts to actions
percept_action_table = {
    (('A', 'A', 'A', 'A'),): 'Move(Chicken)',
    (('A', 'A', 'A', 'A'), ('B', 'B', 'A', 'A')): 'ReturnAlone',
    (('A', 'A', 'A', 'A'), ('B', 'B', 'A', 'A'), ('A', 'B', 'A', 'A')): 'Move(Fox)',
    (('A', 'A', 'A', 'A'), ('B', 'B', 'A', 'A'), ('A', 'B', 'A', 'A'), ('B', 'B', 'A', 'B')): 'Move(Chicken)',
    (('A', 'A', 'A', 'A'), ('B', 'B', 'A', 'A'), ('A', 'B', 'A', 'A'), ('B', 'B', 'A', 'B'), ('A', 'A', 'A', 'B')): 'Move(Feed)',
    (('A', 'A', 'A', 'A'), ('B', 'B', 'A', 'A'), ('A', 'B', 'A', 'A'), ('B', 'B', 'A', 'B'), ('A', 'A', 'A', 'B'), ('B', 'A', 'B', 'B')): 'ReturnAlone',
    (('A', 'A', 'A', 'A'), ('B', 'B', 'A', 'A'), ('A', 'B', 'A', 'A'), ('B', 'B', 'A', 'B'), ('A', 'A', 'A', 'B'), ('B', 'A', 'B', 'B'), ('A', 'A', 'B', 'B')): 'Move(Chicken)',
    (('A', 'A', 'A', 'A'), ('B', 'B', 'A', 'A'), ('A', 'B', 'A', 'A'), ('B', 'B', 'A', 'B'), ('A', 'A', 'A', 'B'), ('B', 'A', 'B', 'B'), ('A', 'A', 'B', 'B'), ('B', 'B', 'B', 'B')): 'GoalReached'
}

# Implementing the Table-Driven Agent Program for the Farmer Problem
class FarmerRiverCrossingEnvironment(Environment):
    def __init__(self):
        super().__init__()
        self.state = initial_state
    
    def percept(self, agent):
        # Return the current state as the percept
        return self.state
    
    def execute_action(self, agent, action):
        # Perform the action and update the state accordingly
        if action == 'Move(Chicken)':
            # Move farmer and chicken across
            self.state = ('B' if self.state[0] == 'A' else 'A', 'B' if self.state[1] == 'A' else 'A', self.state[2], self.state[3])
        elif action == 'Move(Fox)':
            # Move farmer and fox across
            self.state = ('B' if self.state[0] == 'A' else 'A', self.state[1], self.state[2], 'B' if self.state[3] == 'A' else 'A')
        elif action == 'Move(Feed)':
            # Move farmer and feed across
            self.state = ('B' if self.state[0] == 'A' else 'A', self.state[1], 'B' if self.state[2] == 'A' else 'A', self.state[3])
        elif action == 'ReturnAlone':
            # Move only the farmer across
            self.state = ('B' if self.state[0] == 'A' else 'A', self.state[1], self.state[2], self.state[3])
        # Print the current state after action
        print(f"State after action {action}: {self.state}")
    
    def is_done(self):
        # Check if the goal state has been reached
        return self.state == goal_state


def run_farmers_dilemma():
  # Create the agent with the table-driven program
  farmer_agent = Agent(TableDrivenAgentProgram(percept_action_table))

  #USEFUL CODE TO SEE MORE INFO ON AGENT#
  # Wrap the farmer_agent in a TraceAgent to log percepts and actions
  traced_farmer_agent = TraceAgent(farmer_agent)

  # Create the environment and add the agent
  env = FarmerRiverCrossingEnvironment()
  env.add_thing(traced_farmer_agent)

  # Run the environment to solve the problem
  while not env.is_done():
      action = traced_farmer_agent.program(env.percept(traced_farmer_agent))
      env.execute_action(traced_farmer_agent, action)

  print("Problem Solved!")



""" B. Agent performance """

# Specify the PEAS for each (in a 5x5 table).
"""
| Agent                | Perf Measure                | Env             | Actuators  | Sensors         |
|----------------------|-----------------------------|-----------------|------------|-----------------|
| RandomVacuumAgent     | Dirt cleaned (+10), rnd (-1)| TrivialVacEnv   | Move, Suck | Loc, Dirt       |
| TableDrivenVacuumAgent| Dirt cleaned (+10), tbl (-1)| TrivialVacEnv   | Move, Suck | Loc, Dirt       |
| ReflexVacuumAgent     | Dirt cleaned (+10), rct (-1)| TrivialVacEnv   | Move, Suck | Loc, Dirt       |
| ModelBasedVacuumAgent | Dirt cleaned (+10), mem (-1)| TrivialVacEnv   | Move, Suck | Loc, Dirt, Mem  |

"""
# Perform a comparative analysis of the agents operating in a TrivialVacuumEnvironment.

# Define factories for the agents
def random_vacuum_agent_factory():
    agent = RandomVacuumAgent()
    agent.__name__ = "RandomVacuumAgent"  # Add a custom name to identify this agent
    print(f"Created agent: {agent.__name__}")
    return agent

def table_driven_vacuum_agent_factory():
    agent = TableDrivenVacuumAgent()
    agent.__name__ = "TableDrivenVacuumAgent"  # Add a custom name to identify this agent
    print(f"Created agent: {agent.__name__}")
    return agent

def reflex_vacuum_agent_factory():
    agent = ReflexVacuumAgent()
    agent.__name__ = "ReflexVacuumAgent"  # Add a custom name to identify this agent
    print(f"Created agent: {agent.__name__}")
    return agent

def model_based_vacuum_agent_factory():
    agent = ModelBasedVacuumAgent()
    agent.__name__ = "ModelBasedVacuumAgent"  # Add a custom name to identify this agent
    print(f"Created agent: {agent.__name__}")
    return agent


# Define the environment factory
def env_factory_trivial_vac():
    return TrivialVacuumEnvironment()

# Environment factory for the one-dimensional vacuum environment
def env_factory_1d(n_tiles=5):
    return OneDimensionalVacuumEnvironment(n_tiles=n_tiles)

# List of agent factories for comparison - part B
agent_factories = [
    random_vacuum_agent_factory,
    table_driven_vacuum_agent_factory,
    reflex_vacuum_agent_factory,
    model_based_vacuum_agent_factory
]

# List of agent factories for comparison
agent_factories_part_c = [
    random_vacuum_agent_factory,
    reflex_vacuum_agent_factory,
    model_based_vacuum_agent_factory
]

def run_agent_comparison():
  # Run the comparison between the agents
  results = compare_agents(env_factory_trivial_vac, agent_factories, n=10, steps=1000)

  # Loop through the results and print each agent's name and average score
  for agent, avg_score in results:
    print(f"Agent: {agent.__name__}, Average Score: {avg_score}")

# Detail the different characteristics of the agents and how that relates to their performance.
"""
| Agent                | Strengths                       | Weaknesses                          |
|----------------------|---------------------------------|-------------------------------------|
| RandomVacuumAgent     | Simple, no knowledge needed    | Random moves, inefficient, high step cost |
| TableDrivenVacuumAgent| Can work well with good table  | Inflexible, depends on predefined table |
| ReflexVacuumAgent     | Quick response, simple logic   | Redundant moves, no memory, inefficient in large env |
| ModelBasedVacuumAgent | Efficient, minimizes moves     | Overly complex for trivial env, step cost can be mitigated |

"""

#OK Lets run multiple iterations of the compare_agents against increasing no. step sizes (powers of 2, from 2^1 to 2^8) and plot the performance results against agent type.
def run_agent_comparison_visualise_results():
    
   # Line styles for different agents
    line_styles = ['-.', '--', ':', '-']

    # Step sizes (powers of 2: 2^1 to 2^8)
    step_sizes = [2**i for i in range(1, 9)]

    # Store results for each agent
    performance_results = {agent.__name__: [] for agent in agent_factories}

    # Run comparison for each step size
    for steps in step_sizes:
        results = compare_agents(TrivialVacuumEnvironment, agent_factories, n=10, steps=steps)
        for agent, avg_score in results:
            performance_results[agent.__name__].append(avg_score)
    # Plot results
    plt.figure(figsize=(10, 6))

    for agent, style in zip(performance_results, line_styles):
        plt.plot(step_sizes, performance_results[agent], label=agent, linestyle=style)

    # Plot formatting
    plt.title('Agent Performance Across Different Step Sizes (Powers of 2)')
    plt.xlabel('Step Size')
    plt.ylabel('Average Performance')
    plt.xscale('log', base=2)
    plt.grid(True)
    plt.legend(loc='lower left')
    plt.show()

# Define a one-dimensional vacuum environment
class OneDimensionalVacuumEnvironment(VacuumEnvironment):
    """A one-dimensional vacuum environment with n tiles."""
    
    def __init__(self, n_tiles=5):
        super().__init__()
        self.n_tiles = n_tiles
        self.status = {i: random.choice(['Clean', 'Dirty']) for i in range(n_tiles)}
    
    def percept(self, agent):
        """Return the agent's current location and the status of the tile."""
        return agent.location, self.status[agent.location]
    
    def execute_action(self, agent, action):
        """Execute the action of the agent: Move or Clean."""
        if action == 'Left' and agent.location > 0:
            agent.location -= 1
            agent.performance -= 1  # Moving costs
        elif action == 'Right' and agent.location < self.n_tiles - 1:
            agent.location += 1
            agent.performance -= 1
        elif action == 'Suck':
            if self.status[agent.location] == 'Dirty':
                self.status[agent.location] = 'Clean'
                agent.performance += 10  # Cleaning reward
    
    def is_done(self):
        """The environment is done if all tiles are clean."""
        return all(state == 'Clean' for state in self.status.values())

    def default_location(self, agent):
        """Ensure the agent starts within valid tile range."""
        return random.choice(range(self.n_tiles))

# List of agent factories for the one-dimensional vacuum environment
agent_factories_part_c = [random_vacuum_agent_factory, reflex_vacuum_agent_factory, model_based_vacuum_agent_factory]

# Define the environment factory for the one-dimensional environment
def env_factory_1d(n_tiles=5):
    return OneDimensionalVacuumEnvironment(n_tiles=n_tiles)

# Use compare_agents to test agents in the one-dimensional vacuum environment
def compare_agents_in_1D_env(n_tiles, steps):
    # Pass the factories, not instances
    results = compare_agents(lambda: env_factory_1d(n_tiles), agent_factories_part_c,  # Pass factories
    n=10, steps=steps)
    return results

# Test for different environment sizes and gather performance
def test_one_dimensional_vacuum_environment():
    n_tiles_list = [5, 10, 15, 20]
    steps = 1000

    # Initialize performance_results with the agent names as keys
    performance_results = {
        'RandomVacuumAgent': [],
        'ReflexVacuumAgent': [],
        'ModelBasedVacuumAgent': []
    }

    for n_tiles in n_tiles_list:
        results = compare_agents_in_1D_env(n_tiles, steps)
        for agent_name, performance in results:
            print(f"Agent class name during result processing: {agent_name}")

            # Check for agent_name in performance_results
            if agent_name in performance_results:
                performance_results[agent_name].append(performance)
            else:
                print(f"KeyError: {agent_name} not found in performance_results")
   
    # Plot the results
    plt.figure(figsize=(10, 6))
    for agent_name, performance in performance_results.items():
        plt.plot(n_tiles_list, performance, label=agent_name)

    plt.xlabel('Number of Tiles')
    plt.ylabel('Average Performance')
    plt.title('Agent Performance in One-Dimensional Vacuum Environment')
    plt.legend(loc='best')
    plt.show()


###

""" B. Goal-based Agent """

"""
Converting a Reflex Agent into a Goal-Based Agent:
- Define a Goal: The agent's goal is to clean the entire environment. It should know when it's done (when all tiles are clean).
- Percept History: The agent should keep track of the state of the environment (which tiles are clean/dirty) and where it has been.
- World Model: The agent needs a model of the environment (e.g., a 1-dimensional grid) to understand how its movements affect the world.
- Action Planning: Before deciding on an action, the agent should evaluate if that action will lead to progress towards the goal (cleaning the environment).


Goal: The goal is to clean all the dirty tiles in the environment.

Percept History and World Model: We'll keep track of the environment's state (clean or dirty) and the vacuum's position on the grid.

Planning Mechanism: The agent will decide its next action based on the goal of cleaning the entire room. It will try to visit every tile and clean if necessary

"""

# Goal-Based Vacuum Agent Program with Complete Tile Tracking
def GoalBasedVacuumAgentProgram(n_tiles):
    """A goal-based vacuum agent for a one-dimensional environment."""
    state = {i: 'Unknown' for i in range(n_tiles)}  # Initialize state for all tiles
    goal = 'Clean'  # Goal is to clean the entire environment
    
    def program(percept):
        location, status = percept  # Get the location and status (clean/dirty)
        state[location] = status  # Update the state of the current tile
        
        # Check if the environment is fully clean
        if all(tile_status == 'Clean' for tile_status in state.values()):
            print("Goal achieved: The entire environment is clean!")
            return 'NoOp'  # Stop acting
        
        # If the current tile is dirty, clean it, print the state, and return 'Suck'
        if status == 'Dirty':
            print(f"Current state: {state}")
            return 'Suck'
        
        # If the current tile is clean, move to the next unexplored or dirty tile, print the state, and return 'Left' or 'Right'
        if location > 0 and state[location - 1] != 'Clean':  # Check left
            print(f"Current state: {state}, Moving Left")
            return 'Left'
        elif location < len(state) - 1 and state[location + 1] != 'Clean':  # Check right
            print(f"Current state: {state}, Moving Left")
            return 'Right'
        else:
            # If both sides are clean or unknown, move randomly (since it's a 1D environment)
            print(f"Current state: {state}, Moving Randomly")
            return random.choice(['Left', 'Right'])
    
    return program

"""
World Model & Percept History: The agent maintains a state dictionary that tracks the status of each tile (whether it's clean or dirty). It updates the state with each percept it receives.

Goal: The agent's goal is to clean all the dirty tiles. Once all tiles are clean, the agent will stop working.

Action Planning: The agent evaluates whether the current tile is dirty. If it is, the agent cleans it. If the tile is already clean, the agent moves to the next tile that might be dirty, based on its percept history (state). The agent chooses to move left or right depending on which neighboring tile it thinks is still dirty.

Stopping Condition: Once all tiles are clean, the agent stops and does nothing (NoOp).

Improvements Over Reflex Agent:

- Memory: The agent now keeps track of where it has been and which tiles are clean or dirty.
- Goal: It has a defined goal: cleaning the entire environment. It knows when it has achieved this goal and stops acting.
- Simple Planning: The agent evaluates which action is more likely to help it achieve its goal (moving to dirty tiles).

"""


# Test the Goal-Based Agent in the 1D environment
def test_goal_based_agent():
    env = OneDimensionalVacuumEnvironment(n_tiles=5)  # Create a 5-tile environment
    agent = Agent(program=GoalBasedVacuumAgentProgram(env.n_tiles))  # Create the agent
    agent.location = env.default_location(agent)  # Place the agent in the environment
    
    # Run the environment until all tiles are clean
    while not env.is_done():
        percept = env.percept(agent)  # Get the agent's percept
        action = agent.program(percept)  # Get the action based on the goal-based program
        if action == 'NoOp':
            break  # Stop if NoOp is returned
        env.execute_action(agent, action)  # Execute the action in the environment
    
    print(f"Final performance: {agent.performance}")

# Run the test
test_goal_based_agent()

# run_farmers_dilemma()
# run_agent_comparison()
# run_agent_comparison_visualise_results()
# NOT WORKING - UNDER CONSTRUCTION --- Run the test
# test_one_dimensional_vacuum_environment()


