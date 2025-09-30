"""
A1_COMP9016_Nagle_JohnPaul_R00065426.py

Name:         (John) Paul Nagle
Student ID:   R00065426
Class:        Knowledge Representation
Assignment:   1

The 2D world is comprised of a grid of blocks.
There is one obstacle block that no agent can move to.
An agent gets penalised points (sum of x and y co-ordinates) for making each move.
An agent gets penalised 50 points if it lands on the penalty block
If the agent reaches the winning block it gets 100 points, wins the game and the game ends.
If the agent does not reach the winning block in the set number of moves, the game ends and the agent has lost the game.

Here is an example map of the 2D world
Obstacle location is   (1, 1)
Positive location is   (4, 3)
Negative location is   (0, 4)
Agent location is      (6, 2)

    0 1 2 3 4 5 6 7
  +-----------------+
0 | . . . . . . . . |
1 | . O . . . . . . |
2 | . . . . . . A . |
3 | . . . . P . . . |
4 | N . . . . . . . |
5 | . . . . . . . . |
6 | . . . . . . . . |
7 | . . . . . . . . |
  +-----------------+

AGENTS:
 - Random Agent, picks the next move randomly
 - Simple Reflex agent, always moves to the cheapest adjacent square.
 - Table based agent, uses a table to decide the next move

UNINFORMED SEARCHES:
 - Breadth First Search
 - Depth First Search
 - Uniform Cost Search

INFORMED SEARCHES:
- Greedy Best First Search
- A* Search i.e. Best First Graph Search
- Recursive Best First Search

"""
import sys
import os
import random
import argparse
import time

# Get the parent directory of the current directory
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Add the parent directory to sys.path
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Now you can import a module from the parent directory
from agents4e import Thing, XYEnvironment, Agent, Obstacle
from search import Node, Problem, breadth_first_graph_search, depth_first_graph_search, uniform_cost_search, greedy_best_first_graph_search, astar_search, recursive_best_first_search
from utils4e import PriorityQueue, memoize

GAME_WON=False

direction_to_coords = {
    'up': (0, -1),
    'down': (0, 1),
    'left': (-1, 0),
    'right': (1, 0)
}

def log_message(message):
    """Log a message if verbose mode is enabled."""
    if args.verbose:
        print(message)

# Based on https://stackoverflow.com/questions/61626953/python-printing-an-ascii-cartesian-coordinate-grid-from-a-2d-array-of-position
def draw_grid(agent, obstacle, positive, negative):
    # Just for reference, draw the grid with the agent, obstacles, winning and penalty squares marked
    print("\nA = Agent, P = Winning Square, N = Penalty Square, O = Obstacle\n")
    rows = args.width
    cols = args.depth
    content = [["."]*cols for _ in range(rows)]

    grid = [
        (obstacle[0], obstacle[1], "O"),
        (agent[0], agent[1], "A"),
        (positive[0], positive[1], "P"),
        (negative[0], negative[1], "N")]
    for (x, y, c) in grid: content[y][x] = c

    # build frame
    width       = len(str(max(rows, cols)-1))
    contentLine = "# | values |"

    dashes      = "-".join("-"*width for _ in range(cols))
    frameLine   = contentLine.replace("values", dashes)
    frameLine   = frameLine.replace("#", " "*width)
    frameLine   = frameLine.replace("| ", "+-").replace(" |", "-+")

    # x-axis numbers (at the top)
    numLine = contentLine.replace("|", " ")
    numLine = numLine.replace("#", " "*width)
    colNums = " ".join(f"{i:<{width}d}" for i in range(cols))
    numLine = numLine.replace("values", colNums)
    print(numLine)

    # print grid
    print(frameLine)
    for i, row in enumerate(content):
        values = " ".join(f"{v:{width}s}" for v in row)
        line   = contentLine.replace("values", values)
        line   = line.replace("#", f"{i:{width}d}")
        print(line)
    print(frameLine)

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
        # A list of available movements from the agent's current location and the associated cost
        x, y = agent.location
        obstacle_positions = []
        for thing in self.things:
            if isinstance(thing, Obstacle):
                if hasattr(thing, 'location') and thing.location is not None:
                    obstacle_positions.append(thing.location)

        available_moves_with_costs = self.get_available_moves_with_costs(x, y, self.width, self.depth, obstacle_positions)
        return available_moves_with_costs

    def get_available_moves_with_costs(self, x, y, width, depth, obstacles=None):
        # Returns a list of tuples containing all  possible moves and their associated costs
        if obstacles is None:
            obstacles = []

        available_moves = []

        if y > 0 and (x, y-1) not in obstacles:  # UP is ok
            available_moves.append(('up', (x + (y-1))))

        if y < depth-1 and (x, y+1) not in obstacles:  # DOWN is ok
            available_moves.append(('down', (x + (y+1))))

        if x < width-1 and (x+1, y) not in obstacles:  # RIGHT is ok
            available_moves.append(('right', ((x+1) + y)))

        if x > 0 and (x-1, y) not in obstacles:  # LEFT is ok
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
        available_moves = self.get_available_moves_with_costs(
            agent.location[0],
            agent.location[1],
            self.width,
            self.depth,
            obstacle_positions
        )
        return any(action in tup for tup in available_moves)

    def _check_destinations(self, agent):
        # Check if agent has landed on the winning or penalyty squares
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
    # A simple agent program that moves randomly.
    def __init__(self):
        super().__init__(self.random_move)

    def random_move(self, percept):
        return random.choice(['down', 'left', 'up', 'right'])

class ReflexAgent(Agent):
    # A reflex agent that always moves to the cheapest adjacent square
    def __init__(self):
        super().__init__(self.cheapest_move)

    def cheapest_move(self, percept):
        # returns the move with the lowest cost
        cheapest = min(percept, key=lambda x: x[1])
        return cheapest[0]

class TableDrivenAgent(Agent):
    # A table driven agent that uses a pre-calculated table to determine the best action to take.
    def __init__(self):
        super().__init__(self.table_action)

    def _get_preferred_move(self, table, available_moves):
        for (_, move_list), direction in table.items():
            if set(move_list) == set(available_moves):
                return direction

    def table_action(self, percept):
        available_moves_list = []
        for allowed_movement in percept:
            available_moves_list.append(allowed_movement[0])

        available_moves = tuple(available_moves_list)

        agent_table = {
            (available_moves, ('up',)): 'up',
            (available_moves, ('down',)): 'down',
            (available_moves, ('right',)): 'right',
            (available_moves, ('left',)): 'left',
            (available_moves, ('up', 'down')): 'up',
            (available_moves, ('up', 'left')): 'up',
            (available_moves, ('up', 'right')): 'right',
            (available_moves, ('down', 'left')): 'down',
            (available_moves, ('down', 'right')): 'right',
            (available_moves, ('left', 'right')): 'left',
            (available_moves, ('up', 'down', 'left')): 'up',
            (available_moves, ('up', 'down', 'right')): 'up',
            (available_moves, ('up', 'left', 'right')): 'right',
            (available_moves, ('down', 'left', 'right')): 'left',
            (available_moves, ('up', 'down', 'left', 'right')): 'up',
        }

        return self._get_preferred_move(agent_table, available_moves)

def generate_random_starting_positions(width, depth):
    # Generate random positions for obstacle, positive destination, negative destination, and the agent.
    occupied_positions = []

    obstacle_x = random.randint(0, width - 1)
    obstacle_y = random.randint(0, depth - 1)
    occupied_positions.append((obstacle_x, obstacle_y))

    while True:
        pos_x = random.randint(0, width - 1)
        pos_y = random.randint(0, depth - 1)
        if (pos_x, pos_y) not in occupied_positions:
            occupied_positions.append((pos_x, pos_y))
            break

    while True:
        neg_x = random.randint(0, width - 1)
        neg_y = random.randint(0, depth - 1)
        if (neg_x, neg_y) not in occupied_positions:
            occupied_positions.append((neg_x, neg_y))
            break

    agent_position = None
    while True:
        agent_x = random.randint(0, width - 1)
        agent_y = random.randint(0, depth - 1)
        if (agent_x, agent_y) not in occupied_positions:
            occupied_positions.append((agent_x, agent_y))
            break

    log_message(f"Obstacle location is   ({obstacle_x}, {obstacle_y})")
    log_message(f"Positive location is   ({pos_x}, {pos_y})")
    log_message(f"Negative location is   ({neg_x}, {neg_y})")
    log_message(f"Agent location is      ({agent_x}, {agent_y})")
    log_message(f"Occupied positions are [{occupied_positions}]")

    return (obstacle_x, obstacle_y), (pos_x, pos_y), (neg_x, neg_y), (agent_x, agent_y), occupied_positions

# Create and set up the environment
def create_gridworld_environment(width, depth, obstacle_pos, positive_pos, negative_pos):
    # Create the 2D grid world with the set width and depth, and Things located at the specified positions
    env = GridWorldEnvironment(width, depth)
    env.add_thing(Obstacle(), obstacle_pos)
    env.add_thing(PositiveDestination(), positive_pos)
    env.add_thing(NegativeDestination(), negative_pos)

    return env

# Search
class GridSearchProblem(Problem):
    def __init__(self, initial, goal, width, depth, obstacles):
        super().__init__(initial, goal)
        self.width = width
        self.depth = depth
        self.obstacles = set(obstacles)

    def actions(self, state):
        """Return valid directions from the current state."""
        x, y = state
        directions = []
        if y > 0 and (x, y - 1) not in self.obstacles:
            directions.append('up')
        if y < self.depth - 1 and (x, y + 1) not in self.obstacles:
            directions.append('down')
        if x > 0 and (x - 1, y) not in self.obstacles:
            directions.append('left')
        if x < self.width - 1 and (x + 1, y) not in self.obstacles:
            directions.append('right')
        return directions

    def result(self, state, action):
        """Return the new state after applying the action."""
        x, y = state
        if action == 'up':
            return (x, y - 1)
        elif action == 'down':
            return (x, y + 1)
        elif action == 'left':
            return (x - 1, y)
        elif action == 'right':
            return (x + 1, y)
        else:
            raise ValueError(f"Unknown action: {action}")

    def goal_test(self, state):
        """Check if the current state is the goal."""
        return state == self.goal

    def path_cost(self, c, state1, action, state2):
        """Cost is the sum of x and y coordinates of the destination."""
        return c + state2[0] + state2[1]

class GridSearchProblemWithHeuristic(GridSearchProblem):
    def h(self, node):
        """Manhattan distance heuristic from current node to goal."""
        x1, y1 = node.state
        x2, y2 = self.goal
        return abs(x2 - x1) + abs(y2 - y1)

def building_your_world(obstacle_pos, positive_pos, negative_pos, agent_pos):
    """ This function is used to build the world for the agent to explore."""
    global GAME_WON

    agent_list = [RandomAgent().random_move, ReflexAgent().cheapest_move, TableDrivenAgent().table_action]

    print("\nAGENT RESULTS")
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
        env = create_gridworld_environment(args.width, args.depth, obstacle_pos, positive_pos, negative_pos)

        # Run the agent the specified number of times
        for run in range(1, args.runs + 1):
            log_message(f"\nRun {run} of {args.runs}")

            # Add an agent to the environment
            agent = Agent(agent_program)
            env.add_thing(agent, agent_pos)
            log_message(f"Starting position is {agent_pos}")

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
        print(f"=> {agent_program.__name__:20}:  Performance: {avg_performance:.2f} Win Rate: {win_rate:.2f}% ({agent_stats['wins']}/{args.runs})")
        # print(f"\nSummary for [{agent_program.__name__:30}]: Average Performance: {avg_performance:.2f} Win Rate: {win_rate:.2f}% ({agent_stats['wins']}/{args.runs})")

def searching_your_world(obstacle_pos, positive_pos, negative_pos, agent_pos):
    problem = GridSearchProblem(
        initial=agent_pos,
        goal=positive_pos,
        width=args.width,
        depth=args.depth,
        obstacles=[obstacle_pos, negative_pos]
    )

    solution_bfs = breadth_first_graph_search(problem)
    solution_dfs = depth_first_graph_search(problem)
    solution_ucs = uniform_cost_search(problem)

    print("\nUNINFORMED SEARCH RESULTS")
    print(f"=> Breadth First Search:     Cost: {solution_bfs.path_cost:5} solution {solution_bfs.solution()}  ")
    print(f"=> Depth First Search  :     Cost: {solution_dfs.path_cost:5} solution {solution_dfs.solution()}  ")
    print(f"=> Uniform Cost Search :     Cost: {solution_ucs.path_cost:5} solution {solution_ucs.solution()}  ")

    problemInformed = GridSearchProblemWithHeuristic(
        initial=agent_pos,
        goal=positive_pos,
        width=args.width,
        depth=args.depth,
        obstacles=[obstacle_pos, negative_pos]
    )

    print("\nINFORMED SEARCH RESULTS")

    solution_astar = astar_search(problemInformed, h=problemInformed.h)
    print(f"=> A*:      Cost: {solution_astar.path_cost:5} Solution: {solution_astar.solution()}")

    solution_rbfs = recursive_best_first_search(problemInformed, h=problemInformed.h)
    print(f"=> RBFS:    Cost: {solution_rbfs.path_cost:5} Solution: {solution_rbfs.solution()}")

    solution_greedy = greedy_best_first_graph_search(problemInformed, f=problemInformed.h)
    if solution_greedy:
        print(f"=> Greedy:  Cost: {solution_greedy.path_cost:5} Solution: {solution_greedy.solution()}")
    else:
        print("=> Greedy:  No solution found")

if __name__ == "__main__":

    print("\nFYI: Pass the -h parameter to see details on how to configure the run")
    # command line arguments
    parser = argparse.ArgumentParser(description='A1_COMP9016_Nagle_JohnPaul_R00065426')
    parser.add_argument('-v', '--verbose', action='store_true', help='Print detailed movement and agent information')
    parser.add_argument('-s', '--steps', type=int, nargs='?', const=1, default=25, help='Number of Agent steps per run to attempt to win the game (agent only)')
    parser.add_argument('-r', '--runs', type=int, nargs='?', const=1, default=25, help='Number of times to run each Agent (agent only)')
    parser.add_argument('-w', '--width', type=int, nargs='?', const=1, default=10, help='Width of the grid world')
    parser.add_argument('-d', '--depth', type=int, nargs='?', const=1, default=10, help='depth of the grid world')
    args = parser.parse_args()

    # Generate random positions for obstacle, positive destination, and negative destination as well as an initial position for the agent
    obstacle_pos, positive_pos, negative_pos, agent_pos, occupied_positions = generate_random_starting_positions(args.width, args.depth)

    draw_grid(agent_pos, obstacle_pos, positive_pos, negative_pos)

    building_your_world(obstacle_pos, positive_pos, negative_pos, agent_pos)
    searching_your_world(obstacle_pos, positive_pos, negative_pos, agent_pos)
