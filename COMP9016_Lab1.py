# COMP9016 Lab 1 
# NAME: (John) Paul Nagle
# STUDENT NUMBER: R00065426@mymtu.ie

# NB: I had a lot of issues with earlier versions of python (i.e. anything below 3.10) on my macbook, so I an using python 3.12 here
# I think this is the only way I could started, and f strings are the only pre-python 3.6 feature that I am using
# I get nearly all of the pytests passing with python 3.12, so I think my env is OK
# i.e. 2 failed, 417 passed


# IV. Theoretical exercise

# 1) Show that the simple vacuum-cleaner agent function
# described in Figure 3 is indeed rational under the
# assumptions listed below.

    #  @~ = roomba (i.e. agent)
    #  ::: = dirt

    # +----------------+----------------+
    # |  A             |  B             |
    # |     @~         |                |
    # |                |                |
    # |   ::::         |       :::      |
    # +----------------+----------------+


    # "A rational agent is one that does the right thing."
    # "For each possible precept sequence, a rational agent should
    #  select an action expected to maximize its performance measure, 
    #  given the evidence provided by the percept sequence,
    #  and whatever built-in knowledge the agent has." 
    # [Artificial Intelligence, A Modern Approach, Russell and Norvig, 4th Edition]

    # So, in our example, the agent will be able to percive it's location i.e. A, and it will be 
    # able to percive the dirt state i.e. dirty.
    # It will be able to select the correct action, i.e. suck. 
    # At that stage, it will have incurred a penalty of 1 point, as the tile had dirt. 
    # The action function will generate a reward of 1 point, so we can say that 
    # the agent is maximising it's performance measure.
    # At this stage the agent will again be able to percive it's location (left), and 
    # the clean/dirty state of the tile.
    # It will be able to generate an action function (i.e. Right) based on it's percept history. 
    # So, the percept history at this stage will be

    # [A, Dirty]                  -> Suck
    # [A, Clean]                  -> Right

    # Now, in tile B (which is dirty) it receives a penalty point, as it percieves correctly that the 
    # tile B is dirty. It generates an action function i.e.Suck. It receives a point. The 
    # percept history is now

    # [A, Dirty]                  -> Suck
    # [A, Clean]                  -> Right
    # [B, Dirty]                  -> Suck
    # [B, Clean]                  -> Left

    # From this point on, the agent will move from left to right, perceiving a clean tile each time. and 
    # being rewarded with one point for each clean tile perception

    # In conclusion, we can say that this agent is rational.

# 2) Describe a rational agent function for the case in
# which each movement costs one point. Does the
# corresponding agent program require internal state?

    # In the scenario in which each movement costs one point, we cannot say that the previous agent would
    # be rational.
    # This is beacause the agent will not be maximimising it's performance measure by carrying out the
    # agent functions that it has been provided. There would be a conflict between the agents designed
    # functions of Left or Right when the agent has percieved that it is on a clean tile, and a rational
    # agents goal of maximising its performance measure. To move would cost it one point, and to land on 
    # a clean tile would award it one point. The agent would behave irrationally by oscillating between
    # tiles for no net reward.

    # To make such an agent rational, we could change the performance measure to award say 2 points 
    # for detecting a clean tile. Or we could change the environment to randonly generate dirt. In that case
    # performance measure would be capable increasing over the time steps, so the agent would be behaving
    # rationally by oscillitating between tiles.

    # Introducing an internal state to the agent, of say remembering how long it had been since it last saw
    # the random dirt generated could be a way to optimise the agent's performance measure. If it somehow
    # deduces, based on it's memory of the environment that is stored in the agents internal state, that 
    # dirt is onb average generated every 10 time steps, then we could introduce logic that tells that 
    # agent to wait for 10 time steps before it moves. This might, on average, improve the performance
    # reward, and might increase the rationality of the agent.


# 3) Discuss possible agent designs for the cases in which
# clean squares can become dirty and the geography
# of the environment is unknown. Does it make sense
# for the agent to learn from its experience in these
# cases? If so, what should it learn? If not, why not?

    # Where clean squares can become dirty and where the geography of the env is unknown means that we need to 
    # introduce an element of environment detection to the agent. This would allow the agent to learn from its
    # actions, and to build up an internal map maybe of the environment. Assuming the agent has some more actions 
    # available to it regarding movements i.e. Left Right, Up, Down
    # The agent could build up an internal table of tiles, and the directions of travel available to/from that tile
    # 
    # +----------------+----------------+----------------+----------------+
    # |  A             |  B             |  C             |  D             |
    # |     @~         |                |                |                |
    # |                |                |                |                |
    # |   ::::         |       :::      |                |                |
    # +----------------+----------------+----------------+----------------+
    # |  E             |  F             |  
    # |                |                | 
    # |                |                |
    # |                |                |
    # +----------------+----------------+

    # Tile  UP  DOWN    LEFT    RIGHT
    # A     N   Y       N       Y               
    # B     N   Y       Y       Y
    # C     N   N       Y       Y
    # D     N   N       Y       N
    # E     Y   N       N       Y
    # F     Y   N       Y       N

    # It might get more complicated here, as the agent might also keep track of how many times each tile has been 
    # visited, and use that information to decide which tiles to visit next. It would need to be able to generate
    # directions to the destination tile. Tiles visited along the way would alter count of the tile vists, and 
    # might change the next optimal tile to visit etc

    # The agent might also keep track of how often and where dirt is appearing, and we miught be able to add logic
    # to wait for some time-steps before moving. It might turn out that there is one area where dirt appears more 
    # often (less randomly), so we might might want to give that tile more weight when deciding what the next tile 
    # visit is.

    # Depending on how much control the roomba have over it's motors, we might be able to train the roomba to move
    # diagonally, and add more actions like UP-LEFT or DOWN-RIGHT thus allowing more tile traversal per time-step 
    # and optimising the rewards. (This goes against the assumption that we have a set number of actions available to us)
    


################################################################################
# My niave code implementation of the agent, and an environment to run it in.
################################################################################

from typing import List
import random


class Percept:
    """ A basic percept class that stores the agent's location, whether the
       current tile is dirty, and the action taken by the agent. """
    def __init__(self, location, dirty, action=None):
        self.location = location
        self.dirty = dirty
        self.action = action
    
    def __str__(self):
        return f"Location: {self.location}, Dirty: {self.dirty}"

class Tile:
    """ A basic tile class that stores the tile's name and whether it is dirty. """
    def __init__(self, name, dirt=False): 
        self.name = name
        self.dirt = dirt
    
    def __str__(self):
        return f"Tile {self.name} ({'dirty' if self.dirt else 'clean'})"

class Agent:
    """ An agent class that stores the agent's performance, percept history, and current location. """
    def __init__(self):
        self.performance = 0
        self.percept_history: List[Percept] = []
        self.location = None

    def set_performance_award(self, performance):
        """ Set the performance award for the agent """
        self.performance += performance
    
    def action(self, percept):
        """ Perform an action based on a perception """
        # FIrst, store the percept in history
        self.percept_history.append(percept)
        
        if percept.dirty:
            return "Suck"
        if percept.location in ("A", "C"): # Obviously, these hard coded values wont scale
            return "Right"
        if percept.location in ("B", "D"): # Obviously, these hard coded values wont scale
            return "Left"

        return False

class Environment:
    """ An environment to run an agent in """
    def __init__(self, tiles, agent, penalise_movement):
        self.tiles = tiles
        self.agent = agent
        self.penalise_movement = penalise_movement
        self.set_random_agent_location()
    
    def set_random_agent_location(self):
        """Set the agent's location to a random tile"""
        # Choose a random tile from the available tiles
        random_tile = random.choice(self.tiles)
        self.agent.location = random_tile.name

    def percept(self, agent):
        """ Return what the agent percieves at this stage """
        for tile in self.tiles:
            if tile.name == agent.location:
                return Percept(location=agent.location, dirty=tile.dirt)
        
        # If agent's location is not found, return a default percept
        return Percept(location=None, dirty=False)
    
    def execute_action(self, agent, action):
        """ The agent executes the action """
        if action == "Suck":
            for tile in self.tiles:
                if tile.name == agent.location and tile.dirt:
                    tile.dirt = False
                    agent.set_performance_award(1)
        elif action == "Left":
            if agent.location == self.tiles[1].name: # Obviously, these hard coded values wont scale
                agent.location = self.tiles[0].name  # Obviously, these hard coded values wont scale
            if self.penalise_movement:
                agent.set_performance_award(-1)
        elif action == "Right":
            if agent.location == self.tiles[0].name: # Obviously, these hard coded values wont scale
                agent.location = self.tiles[1].name  # Obviously, these hard coded values wont scale
            if self.penalise_movement:
                agent.set_performance_award(-1)
    
    
    def step(self):
        """  Run a step in the environment  """
        actions = []

        # Get the percept for the agent
        percept = self.percept(self.agent)
        
        # Get the action from the agent
        action = self.agent.action(percept)
        actions.append((self.agent, action, percept))
            
        # Execute all actions
        for agent, action, _ in actions:
            self.execute_action(agent, action)
        
        return actions
    
    def run(self, steps):
        """  Run the environment for the specified number of steps  """
        for step_num in range(steps):
            print("=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-")
            self.print_state(f"STEP {step_num + 1}")
            actions = self.step()
            for agent, action, percept in actions:
                print(f"Agent perceives [{percept}] and takes action  [{action}]")
                print(f"Performance score is now {agent.performance}")
                
    
    def print_state(self, message):
        """  Print the current state of the environment  """
        print(f"==> {message}")
        for tile in self.tiles:
            agent_here = (self.agent.location == tile.name)
            print(f"Tile {tile.name}: {'dirty' if tile.dirt else 'clean'}{' (agent here)' if agent_here else ''}")



def main():
    # Create tiles A and B
    tile_a = Tile("A", dirt=True)
    tile_b = Tile("B", dirt=True)
    
    # Create an environment with an agent, tiles A and B, and no penalisation for movmenet
    agent_1 = Agent()
    env_1 = Environment([tile_a, tile_b], agent_1, penalise_movement=False)
    
    env_1.print_state("INITIAL STATE ENV_1")
    
    # Run the environment!
    env_1.run(11)

    env_1.print_state("FINAL STATE ENV_1")
    
    # # Print the agent's percept history
    # print("\nAgent's percept history:")
    # for i, percept in enumerate(agent.percept_history):
    #     print(f"{i+1}: {percept}")

    print("\n\n")
    print("*****************************************************")
    print("\n\n")


# 2) Describe a rational agent function for the case in which each movement costs one point.

    # Create new tiles C and D for the new env
    tile_c = Tile("C", dirt=True)
    tile_d = Tile("D", dirt=True)
   
    # Create an environment with tiles A and B, and no penalisation for movmenet
    agent_2 = Agent()
    env_2 = Environment([tile_c, tile_d], agent_2, penalise_movement=True)
    
    env_2.print_state("INITIAL STATE ENV_2")
    
    # Run the environment!
    env_2.run(1000)

    env_2.print_state("FINAL STATE ENV_2")


if __name__ == "__main__":
    main()
