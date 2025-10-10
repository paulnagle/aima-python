"""
A1_COMP9016_Nagle_JohnPaul_R00065426.py

Name:         (John) Paul Nagle
Student ID:   R00065426
Class:        Knowledge Representation
Assignment:   1

"""
import sys
import os
import random
import argparse
import copy
import time

# Get the parent directory of the current directory
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Add the parent directory to sys.path
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Now you can import a module from the parent directory
from agents import Thing, XYEnvironment, Agent, Obstacle
from search import Problem, InstrumentedProblem 
from search import depth_limited_search, breadth_first_graph_search, depth_first_graph_search, uniform_cost_search, greedy_best_first_graph_search, astar_search, recursive_best_first_search

# Global to store current game result
GAME_WON=False

# Handy for calculating grid movements
direction_to_coords = {
    'up': (0, 1),
    'down': (0, -1),
    'left': (-1, 0),
    'right': (1, 0)
}

def verbose_message(message):
    """Log a message if verbose mode is enabled."""
    if args.verbose:
        print(message)

def generate_random_starting_positions(width, height):
    # Generate random positions for obstacle, winning destination, penalty destinations, and the agent.
    occupied_positions = []

    obstacle_x = random.randint(0, width - 1)
    obstacle_y = random.randint(0, height - 1)
    occupied_positions.append((obstacle_x, obstacle_y))

    while True:
        win_x = random.randint(0, width - 1)
        win_y = random.randint(0, height - 1)
        if (win_x, win_y) not in occupied_positions:
            occupied_positions.append((win_x, win_y))
            break

    # Place penalty blocks randomly based on the penalty_prob parameter
    penalty_positions = []
    for x in range(width):
        for y in range(height):
            pos = (x, y)
            if pos not in occupied_positions and random.random() < args.penalty_prob:
                penalty_positions.append(pos)
                occupied_positions.append(pos)

    while True:
        agent_x = random.randint(0, width - 1)
        agent_y = random.randint(0, height - 1)
        if (agent_x, agent_y) not in occupied_positions:
            occupied_positions.append((agent_x, agent_y))
            break

    verbose_message(f"Obstacle location is   ({obstacle_x}, {obstacle_y})")
    verbose_message(f"Winning location is    ({win_x}, {win_y})")
    verbose_message(f"Penalty locations are  {penalty_positions}")
    verbose_message(f"Agent location is      ({agent_x}, {agent_y})")
    verbose_message(f"Occupied positions are {occupied_positions}")

    return (obstacle_x, obstacle_y), (win_x, win_y), penalty_positions, (agent_x, agent_y), occupied_positions

# Env
class WinningDestination(Thing):
    """ A destination that awards 100 points and wins the game when an agent reaches it """
    pass

class PenaltyDestination(Thing):
    """ A destination that penalises 50 points when an agent reaches it """
    pass

class GridWorldEnvironment(XYEnvironment):
    """ This environment has a grid of rows and columns with obstacles and penalty blocks"""
    def __init__(self, width, height):
        super().__init__(width, height)
        self.width = width
        self.height = height
        
        # Generate random positions for obstacle, winning destination and penalty destinations
        obstacle_pos, winning_pos, penalty_positions, _, _ = generate_random_starting_positions(width, height)
        
        # Add things to the environment
        self.add_thing(Obstacle(), obstacle_pos)
        self.add_thing(WinningDestination(), winning_pos)
        
        # Add multiple penalty destinations
        for penalty_pos in penalty_positions:
            self.add_thing(PenaltyDestination(), penalty_pos)

    def percept(self, agent):
        # A list of available movements from the agent's current location and the associated cost
        x, y = agent.location
        obstacle_positions = []
        for thing in self.things:
            if isinstance(thing, Obstacle):
                # In XYEnvironment, all things get a location attribute when added
                loc = getattr(thing, 'location', None)
                if loc is not None:
                    obstacle_positions.append(loc)

        available_moves_with_costs = self.get_available_moves_with_costs(x, y, self.width, self.height, obstacle_positions)
        return available_moves_with_costs

    def get_available_moves_with_costs(self, x, y, width, height, obstacles=None):
        # Returns a list of tuples containing all possible moves and their associated costs
        if obstacles is None:
            obstacles = []

        available_moves = []

        if y < height -1 and ((x, y+1) not in obstacles) : 
            available_moves.append(('up', (x + (y+1))))

        if y > 0 and (x, y-1) not in obstacles:
            available_moves.append(('down', (x + (y-1))))

        if x < width-1 and (x+1, y) not in obstacles:
            available_moves.append(('right', ((x+1) + y)))

        if x > 0 and (x-1, y) not in obstacles: 
            available_moves.append(('left', ((x-1) + y)))

        # print(f"*********AVAILABLE MOVES FROM {x, y}: {available_moves}")
        return available_moves

    def execute_action(self, agent, action):
        initial_location = agent.location

        # Calculate obstacle positions
        obstacle_positions = []
        for thing in self.things:
            if isinstance(thing, Obstacle):
                # In XYEnvironment, all things get a location attribute when added
                loc = getattr(thing, 'location', None)
                if loc is not None:
                    obstacle_positions.append(loc)

        # Check if move is valid
        if not action:
            return
        if not self._is_valid_move(agent, action, obstacle_positions):
            verbose_message(f"❌ Tried to go [{action:5}] from {agent.location}, but cant go in that direction")
            return

        # Update agent location based on action using the direction_to_coords dictionary
        if action in direction_to_coords:
            dx, dy = direction_to_coords[action]
            agent.location = (agent.location[0] + dx, agent.location[1] + dy)

        verbose_message(f"✅ You  moved [{action:5}] from {initial_location} to {agent.location} successfully : Performance penalty: {agent.location[0] + agent.location[1]:4}  Performance Total: {agent.performance:4}")

        # Charge the agent for making a move (the cost is the sum of the x and y co-ordinates)
        agent.performance = agent.performance - (agent.location[0] + agent.location[1])

        # Check destinations and apply effects
        self._check_destinations(agent)

    def _is_valid_move(self, agent, action, obstacle_positions):
        available_moves = self.get_available_moves_with_costs(
            agent.location[0],
            agent.location[1],
            self.width,
            self.height,
            obstacle_positions
        )
        return any(action in tup[0] for tup in available_moves)

    def _check_destinations(self, agent):
        # Check if agent has landed on the winning or penalty squares
        global GAME_WON

        # Check for winning destination
        winning_destinations = self.list_things_at(agent.location, WinningDestination)
        if winning_destinations:
            agent.performance += 100
            verbose_message("Agent reached winning destination! Performance increase 100.")
            verbose_message(f"🎉 Congratulations, you WON the game with a score of {agent.performance}!!")
            verbose_message("👏 Well done! You've successfully completed the game!")
            GAME_WON = True

        # Check for penalty destination
        penalty_destination = self.list_things_at(agent.location, PenaltyDestination)
        if penalty_destination:
            agent.performance -= 50
            verbose_message(f"😭 You have reached a penalty destination!               : Performance penalty:   50  Performance Total: {agent.performance:4}")

    def is_done(self):
        """ The environment is done if the agent has won the game"""
        global GAME_WON
        return GAME_WON or super().is_done()

# Agents
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
        # returns the move with the lowest cost, based on the percepts available
        cheapest = min(percept, key=lambda x: x[1])
        return cheapest[0]

class TableDrivenAgent(Agent):
    # A table driven agent that uses a pre-calculated table to determine the action to take.
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
            (available_moves, ('up', 'right')): 'up',
            (available_moves, ('down', 'left')): 'left',
            (available_moves, ('down', 'right')): 'right',
            (available_moves, ('left', 'right')): 'left',
            (available_moves, ('up', 'down', 'left')): 'up',
            (available_moves, ('up', 'down', 'right')): 'up',
            (available_moves, ('up', 'left', 'right')): 'up',
            (available_moves, ('down', 'left', 'right')): 'left',
            (available_moves, ('up', 'down', 'left', 'right')): 'up',
        }

        preferred_move = self._get_preferred_move(agent_table, available_moves)
        return preferred_move

class GoalBasedAgent(Agent):
    # GOAL is self.location == goal_location
    def __init__(self, agent_pos, winning_pos, penalty_positions, obstacle_pos):
        # Maintain some state info for the agent
        self.location = agent_pos
        self.goal_location = winning_pos
        self.penalty_positions = penalty_positions
        self.obstacle_location = obstacle_pos
        super().__init__(self.goalbased_action)

    def goalbased_action(self, percept):
        # A goal based search, where the goal is the Winning position i.e. winning_pos
        # We will use the astar search to find the next move towards the goal
        global GAME_WON

        problem = GridSearchProblemWithHeuristic(
            initial=self.location,
            goal=self.goal_location,
            width=args.width,
            height=args.height,
            obstacles=[self.obstacle_location],
            penalty_location=self.penalty_positions[0] if self.penalty_positions else None
        )
        star_search_result = astar_search(problem)

        if star_search_result is None:
            return None
            
        if self.location == self.goal_location:
            GAME_WON = True
            
        return star_search_result.action

def compare_agents(EnvFactory, AgentFactories, numEnvs, steps):
    """See how well each of several agents do in n instances of an environment."""
    envs = [EnvFactory() for i in range(numEnvs)]
    results = [(agent, test_agent(agent, steps, copy.deepcopy(envs))) for agent in AgentFactories]
    return results

def test_agent(AgentFactory, steps, envs):
    """Return the stats of running an agent in each of the envs, for steps """
    def score(env):
        global GAME_WON
        run_stat = {}

        agent = AgentFactory()
        GAME_WON = False
        env.add_thing(agent)
        # Run the simulation and measure time
        start_time = time.time()
        env.run(steps)
        end_time = time.time()
        elapsed_time = end_time - start_time

        run_stat['agent'] = agent.__class__.__name__
        run_stat['time_taken'] = elapsed_time
        run_stat['performance'] = agent.performance
        run_stat['game_won'] = GAME_WON

        return run_stat

    agent_stats = []
    for env in envs:
        agent_stats.append(score(env))

    return agent_stats

def extract_locations_from_env(env):
    penalty_positions = []
    winning_pos = obstacle_pos = None
    occupied_positions = []
    for thing in env.things:
        loc = getattr(thing, 'location', None)
        occupied_positions.append(loc)
        if isinstance(thing, PenaltyDestination):
            penalty_positions.append(loc)
        elif isinstance(thing, WinningDestination):
            winning_pos = loc
        elif isinstance(thing, Obstacle):
            obstacle_pos = loc
    
    return penalty_positions, winning_pos, obstacle_pos, occupied_positions

def find_position_for_agent(env, occupied_positions):
    while True:
        x = random.randint(0, env.width - 1)
        y = random.randint(0, env.height - 1)
        pos = (x, y)
        if pos not in occupied_positions:
            break
    return pos


def building_your_world():
    """ This function is used to build the world for the agent to explore."""
    global GAME_WON

    # Define factories for the agents
    def random_agent_factory():
        agent = RandomAgent()
        return agent

    def reflex_agent_factory():
        agent = ReflexAgent()
        return agent

    def table_agent_factory():
        agent = TableDrivenAgent()
        return agent

    def goal_agent_factory():
        # Create a GridWorldEnvironment and extract positions from it
        env = GridWorldEnvironment(args.width, args.height)
        penalty_positions, winning_pos, obstacle_pos, occupied_positions = extract_locations_from_env(env)
        agent_pos = find_position_for_agent(env, occupied_positions)
        agent = GoalBasedAgent(agent_pos, winning_pos, penalty_positions, obstacle_pos)
        return agent

    # Define the environment factory
    def env_factory_gridworld():
        # Create a new GridWorldEnvironment with the specified width and height
        return GridWorldEnvironment(args.width, args.height)

    # List of agent factories for comparison 
    agent_factories = [
        random_agent_factory,
        reflex_agent_factory,
        table_agent_factory,
        goal_agent_factory
    ]

    def run_agent_comparison():
        # Run the comparison between the agents
        results = compare_agents(env_factory_gridworld, agent_factories, numEnvs=args.runs, steps=args.steps)

        agent_name = ''
        print(" AGENTS               | COST   | % GAMES WON  | AVG TIME ")
        print("---------------------------------------------------------")
        # Loop through the results and print each agent's name and average score
        for agent, stats in results:
            agent_name = stats[0]['agent'] if stats and len(stats) > 0 else "Unknown"
            verbose_message("Result:\t\tTime:\t\tPerformance:")
            total_games_won = total_games_lost = total_time_taken = total_performance = 0
            
            for agent_results in list(stats):
                if agent_results['game_won']:
                    total_games_won += 1
                else:
                    total_games_lost += 1
                total_time_taken += agent_results['time_taken']
                total_performance += agent_results['performance']
                verbose_message(
                    f"{'Win' if agent_results['game_won'] else 'Loss'}\t\t"
                    f"{agent_results['time_taken']:.5f} seconds\t\t"
                    f"{agent_results['performance']}"
                    )
            print(f"{agent_name:<22}|"
                  f"{-total_performance / len(stats):^8.2f}|"
                  f"{(total_games_won / (total_games_won + total_games_lost)):^14.1%}|"
                  f"{total_time_taken / len(stats):^11.6f}")
  
    run_agent_comparison()

# Search
class GridSearchProblem(Problem):
    def __init__(self, initial, goal, width, height, obstacles, penalty_location):
        super().__init__(initial, goal)
        self.width = width
        self.height = height
        self.obstacles = set(obstacles)
        self.penalty_location = penalty_location

    def actions(self, state):
        """Return valid directions from the current state."""
        x, y = state
        directions = []
        if y + 1 < self.height and (x, y + 1) not in self.obstacles:
            directions.append('up')
        if y > 0 and (x, y - 1) not in self.obstacles:
            directions.append('down')
        if x > 0 and (x - 1, y) not in self.obstacles:
            directions.append('left')
        if x + 1 < self.width and (x + 1, y) not in self.obstacles:
            directions.append('right')
        return directions

    def result(self, state, action):
        """Return the new state after applying the action."""
        x, y = state
        if action in direction_to_coords:
            dx, dy = direction_to_coords[action]
            return (x + dx, y + dy)
        else:
            raise ValueError(f"Unknown action: {action}")

    def goal_test(self, state):
        """Check if the current state is the goal."""
        return state == self.goal

    def path_cost(self, c, state1, action, state2):
        """Cost is the sum of x and y coordinates of the destination, plus 50 for a penalty
        position, and minus 100 for winning the game."""
        cost = c + (state2[0] + state2[1])

        # Apply 100 point bonus for reaching the goal (subtract from cost)
        if state2 == self.goal:
            cost -= 100

        # Apply 50 point penalty for landing on penalty square
        if state2 == self.penalty_location:
            cost += 50

        return cost

class GridSearchProblemWithHeuristic(GridSearchProblem):
    def __init__(self, initial, goal, width, height, obstacles, penalty_location):
        super().__init__(initial, goal, width, height, obstacles, penalty_location)

    def h(self, node):
        """Manhattan distance heuristic from current node to goal."""
        x1, y1 = node.state
        # Ensure goal is not None before unpacking
        if self.goal is None:
            return 0
        x2, y2 = self.goal
        return abs(x2 - x1) + abs(y2 - y1)

def run_search_experiment(algorithm_name, runs, search_type, use_heuristic=True):
    solution_stats = []
    solution_totals = {'path_cost': 0, 'goal_tests': 0, 'states': 0, 'succs': 0, 'time_taken': 0.0}
    
    for i in range(runs):
        # Create a GridWorldEnvironment and extract positions from it
        env = GridWorldEnvironment(args.width, args.height)
        penalty_positions, winning_pos, obstacle_pos, occupied_positions = extract_locations_from_env(env)
        agent_pos = find_position_for_agent(env, occupied_positions)
        # Create appropriate problem type based on whether or not we need a heuristic
        if use_heuristic:
            problem = GridSearchProblemWithHeuristic(
                initial=agent_pos,
                goal=winning_pos,
                width=args.width,
                height=args.height,
                obstacles=[obstacle_pos],
                penalty_location=penalty_positions[0] if penalty_positions else None
            )
        else:
            problem = GridSearchProblem(
                initial=agent_pos,
                goal=winning_pos,
                width=args.width,
                height=args.height,
                obstacles=[obstacle_pos],
                penalty_location=penalty_positions[0] if penalty_positions else None
            )
        
        run_stat = {}
        instrumented_problem = InstrumentedProblem(problem)
        
        # Call the appropriate search function
        solution = None
        start_time = time.time()
        try:
            if search_type == "astar":
                solution = astar_search(instrumented_problem, h=instrumented_problem.h)
            elif search_type == "dls":
                solution = depth_limited_search(instrumented_problem, limit=args.steps)
            elif search_type == "rbfs":
                solution = recursive_best_first_search(instrumented_problem, h=instrumented_problem.h)
            elif search_type == "greedy":
                solution = greedy_best_first_graph_search(instrumented_problem, f=instrumented_problem.h)
            elif search_type == "bfs":
                solution = breadth_first_graph_search(instrumented_problem)
            elif search_type == "dfs":
                solution = depth_first_graph_search(instrumented_problem)
            elif search_type == "ucs":
                solution = uniform_cost_search(instrumented_problem)
            end_time = time.time()
            elapsed_time = end_time - start_time
        except RecursionError as e:
            verbose_message(f"{algorithm_name} failed with: {e}")
            continue
        
        if solution is not None:
            run_stat['run_id'] = i
            run_stat['path_cost'] = solution.path_cost
            run_stat['goal_tests'] = instrumented_problem.goal_tests
            run_stat['states'] = instrumented_problem.states
            run_stat['succs'] = instrumented_problem.succs
            run_stat['time_taken'] = elapsed_time

            # Handle the case where solution might be 'cutoff' from depth_limited_search
            if solution != 'cutoff' and hasattr(solution, 'path_cost'):
                solution_totals['path_cost'] += solution.path_cost
            solution_totals['goal_tests'] += instrumented_problem.goal_tests
            solution_totals['states'] += instrumented_problem.states
            solution_totals['succs'] += instrumented_problem.succs
            solution_totals['time_taken'] += elapsed_time
            
            verbose_message(f" {algorithm_name} {run_stat}")
            solution_stats.append(run_stat)
        
        # Clean up
        del problem, instrumented_problem
        if solution is not None:
            del solution
    
    return solution_stats, solution_totals

def searching_your_world():
    # Uninformed searches
    # Breadth First Search
    _, solution_bfs_totals = run_search_experiment("BFS", args.runs, "bfs", use_heuristic=False)
    # Depth First Search 
    _, solution_dfs_totals = run_search_experiment("DFS", args.runs, "dfs", use_heuristic=False)
    # Uniform Cost Search
    _, solution_ucs_totals = run_search_experiment("UCS", args.runs, "ucs", use_heuristic=False)
    # Depth Limited Search
    _, solution_dls_totals = run_search_experiment("DLS", args.runs, "dls", use_heuristic=False)

    # Print results for uninformed searches
    print("")
    print(" UNINFORMED SEARCH   | COST   | GOAL TESTS | STATES | ACTIONS | AVG TIME")
    print("-------------------------------------------------------------------------")
    print(f"Breadth First Search | "
        f"{solution_bfs_totals['path_cost'] / args.runs:^7.2f}|"
        f"{solution_bfs_totals['goal_tests'] / args.runs:^12.2f}|"
        f"{solution_bfs_totals['states'] / args.runs:^8.2f}|"
        f"{solution_bfs_totals['succs'] / args.runs:^9.2f}|"
        f"{solution_bfs_totals['time_taken'] / args.runs:^11.6f}")
    print(f"Depth First Search   | "
        f"{solution_dfs_totals['path_cost'] / args.runs:^7.2f}|"
        f"{solution_dfs_totals['goal_tests'] / args.runs:^12.2f}|"
        f"{solution_dfs_totals['states'] / args.runs:^8.2f}|"
        f"{solution_dfs_totals['succs'] / args.runs:^9.2f}|"
        f"{solution_dfs_totals['time_taken'] / args.runs:^11.6f}")
    print(f"Uniform Cost Search  | "
        f"{solution_ucs_totals['path_cost'] / args.runs:^7.2f}|"
        f"{solution_ucs_totals['goal_tests'] / args.runs:^12.2f}|"
        f"{solution_ucs_totals['states'] / args.runs:^8.2f}|"
        f"{solution_ucs_totals['succs'] / args.runs:^9.2f}|"
        f"{solution_ucs_totals['time_taken'] / args.runs:^11.6f}")
    print(f"Depth Limited Search | "
          f"{solution_dls_totals['path_cost'] / args.runs:^7.2f}|"
          f"{solution_dls_totals['goal_tests'] / args.runs:^12.2f}|"
          f"{solution_dls_totals['states'] / args.runs:^8.2f}|"
          f"{solution_dls_totals['succs'] / args.runs:^9.2f}|"
          f"{solution_dls_totals['time_taken'] / args.runs:^11.6f}")


    # Informed searches
    # A* Search
    _, solution_astar_totals = run_search_experiment("A*", args.runs, "astar", use_heuristic=True)

    # Print results
    print("")
    print( " INFORMED SEARCH     | COST   | GOAL TESTS | STATES | ACTIONS | AVG TIME")
    print("-------------------------------------------------------------------------")
    print(f"A* Search            | "
          f"{solution_astar_totals['path_cost'] / args.runs:^7.2f}|"
          f"{solution_astar_totals['goal_tests'] / args.runs:^12.2f}|"
          f"{solution_astar_totals['states'] / args.runs:^8.2f}|"
          f"{solution_astar_totals['succs'] / args.runs:^9.2f}|"
          f"{solution_astar_totals['time_taken'] / args.runs:^11.6f}")

    # Recursive Best First Search
    try:
        _, solution_rbfs_totals = run_search_experiment("RBFS", 1, "rbfs", use_heuristic=True)
        print(f"Recurs Best 1st Srch | "
            f"{solution_rbfs_totals['path_cost']:^7.2f}|"
            f"{solution_rbfs_totals['goal_tests']:^12}|"
            f"{solution_rbfs_totals['states']:^8}|"
            f"{solution_rbfs_totals['succs']:^9}|"
            f"{solution_rbfs_totals['time_taken']:^11.6f}")
    except Exception as e:
        print(f"Recurs Best 1st Srch | {e}!")

    # Greedy Best First Search
    _, solution_greedy_totals = run_search_experiment("Greedy", 1, "greedy", use_heuristic=True)
    if solution_greedy_totals:
        print(f"Greedy Best 1st Srch | "
            f"{solution_greedy_totals['path_cost']:^7.2f}|"
            f"{solution_greedy_totals['goal_tests']:^12}|"
            f"{solution_greedy_totals['states']:^8}|"
            f"{solution_greedy_totals['succs']:^9}|"
            f"{solution_greedy_totals['time_taken']:^11.6f}")
    else:
        print("=> Greedy:  No solution found")

def print_args(args):
    print("\n*** Pass the -h parameter to see details on how to configure the parameters ***\n")
    print(" PARAMETER | STEPS   | RUNS   | WIDTH  | HEIGHT")
    print("-----------|---------|--------|--------|-------")
    print(f" VALUE     | {args.steps:^7} | {args.runs:^6} | {args.width:^6} | {args.height:^6}\n")

if __name__ == "__main__":
    # command line arguments
    parser = argparse.ArgumentParser(description='A1_COMP9016_Nagle_JohnPaul_R00065426')
    parser.add_argument('-v', '--verbose', action='store_true', help='Print detailed movement and agent information')
    parser.add_argument('-s', '--steps', type=int, nargs='?', const=1, default=40, help='Number of Agent steps per run to attempt to win the game (agent only) (DEFAULT: 40)')
    parser.add_argument('-r', '--runs', type=int, nargs='?', const=1, default=500, help='Number of times to run each Agent (agent only) (DEFAULT: 10)')
    parser.add_argument('-x', '--width', type=int, nargs='?', const=1, default=6, help='Width of the grid world (DEFAULT: 6)')
    parser.add_argument('-y', '--height', type=int, nargs='?', const=1, default=6, help='height of the grid world (DEFAULT: 6)')
    parser.add_argument('-p', '--penalty-prob', type=float, default=0.1, help='Probability of placing a penalty block at a position (DEFAULT: 0.1)')
    args = parser.parse_args()

    print_args(args)

    building_your_world()
    searching_your_world()
