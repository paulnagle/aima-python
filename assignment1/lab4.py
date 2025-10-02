""" Paul Nagle R00065426 Knowledge Representation Lab 4 """
import sys
import os
import random

# Get the parent directory of the current directory
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Add the parent directory to sys.path
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Now you can import a module from the parent directory
from agents import Dirt, XYEnvironment, Agent
from search import Problem, breadth_first_graph_search


class RandomVacuumAgent(Agent):
    def __init__(self):
        super().__init__(self.random_program)

    def random_program(self, percept):
        return random.choice(['Suck', 'Down', 'Left', 'Up', 'Right'])


class RandomDirtVacuumEnvironment(XYEnvironment):
    def __init__(self, width, height):
        super().__init__(width, height)
        self.width = width
        self.height = height
        self.dirt_positions = []

    def populate_with_dirt(self):
        dirt_probability = 0.8
        for x in range(0, self.width):
            for y in range(0, self.height):
                if random.random() < dirt_probability:
                    self.add_thing(Dirt(), (x, y), True)
                    self.dirt_positions.append((x, y))


class VacuumProblem(Problem):
    def __init__(self, initial_state, width, height):
        super().__init__(initial_state)
        self.width = width
        self.height = height
        self.state = initial_state

    def actions(self, state):
        possible_actions = ['Suck']

        x, y = state[0]
        if y > 0:
            possible_actions.append('Down')
        if y < self.height - 1:
            possible_actions.append('Up')
        if x > 0:
            possible_actions.append('Left')
        if x < self.width - 1:
            possible_actions.append('Right')
        return possible_actions

    def result(self, state, action):
        x, y = state[0]
        position = (x, y)
        if action == 'Up':
            state[0] = (x, y + 1)
        elif action == 'Down':
            state[0] = (x, y - 1)
        elif action == 'Left':
            state[0] = (x - 1, y)
        elif action == 'Right':
            state[0] = (x + 1, y)
        elif action == 'Suck':
            if position in state[1]:
                state[1].remove((x, y))
        else:
            raise ValueError(f"Unknown action: {action}")
        return state

    def goal_test(self, state):
        if not state[1]:
            return True
        else:
            return False

    def path_cost(self, c, state1, action, state2):
        if action in ['Up', 'Down', 'Left', 'Right']:
            return 1
        if action in ['Suck']:
            return 100


def get_initial_state_from_env(agent_position, env):
    return (agent_position, env.dirt_positions)


if __name__ == "__main__":
    print("Hello")
    width = height = 8
    agent_position = (0, 0)
    env = RandomDirtVacuumEnvironment(width, height)
    env.populate_with_dirt()
    agent = RandomVacuumAgent()
    env.add_thing(agent, agent_position)
    initial_state = get_initial_state_from_env(agent_position, env)
    my_problem = VacuumProblem(initial_state, width, height)
    solution_bfgs = breadth_first_graph_search(my_problem)
    print(solution_bfgs)
