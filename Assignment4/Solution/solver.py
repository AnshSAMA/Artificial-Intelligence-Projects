from laser_tank import LaserTankMap, DotDict

import random
import time

"""
Template file for you to implement your solution to Assignment 4. You should implement your solution by filling in the
following method stubs:
    train_q_learning()
    train_sarsa()
    get_policy()
    
You may add to the __init__ method if required, and can add additional helper methods and classes if you wish.

To ensure your code is handled correctly by the autograder, you should avoid using any try-except blocks in your
implementation of the above methods (as this can interfere with our time-out handling).

COMP3702 2020 Assignment 4 Support Code
"""


class Solver:

    def __init__(self):
        """
        Initialise solver without a Q-value table.
        """
        MOVE_FORWARD = 'f'
        TURN_LEFT = 'l'
        TURN_RIGHT = 'r'
        SHOOT_LASER = 's'
        self.moves = [MOVE_FORWARD, TURN_LEFT, TURN_RIGHT, SHOOT_LASER]

        self.exploit_prob = 0.8
        
        #
        # TODO
        # You may add code here if you wish (e.g. define constants used by both methods).
        #
        # The allowed time for this method is 1 second.
        #

        self.q_values = None

    def train_q_learning(self, simulator):
        """
        Train the agent using Q-learning, building up a table of Q-values.
        :param simulator: A simulator for collecting episode data (LaserTankMap instance)
        """

        alpha = 0.05
        gamma = simulator.gamma

        time_limit = simulator.time_limit
        
        q_values = {}

        # Continue till time limit is reached
        start_time = time.time()
        elapsed_time = 0
        while elapsed_time < time_limit:
            current_time = time.time()
            elapsed_time = current_time - start_time

            #Run till the episode ends
            episode_finished = False
            while not episode_finished:

                """Get current state"""
                current_state = (simulator.player_x, simulator.player_y, simulator.player_heading)

                """Choose action"""
                if current_state in q_values:
                    # Epsilon Greedy
                    current_state_vals = q_values[current_state]
                    if random.random() > self.exploit_prob:
                        action = random.choice(self.moves) 
                    else:
                        action = max(current_state_vals, key = current_state_vals.get)
                else:
                    # Choose random action
                    action = random.choice(self.moves) #self.moves[random.randint(0,3)]
                    # Put this state in q_values
                    q_values[current_state] = {"f":0, "l":0, "r":0, "s":0}


                """Get previous value"""
                old_state_value = q_values[current_state][action]
                """Apply action"""
                reward = simulator.apply_move(action)
                """Get next state value"""
                next_state = (simulator.player_x, simulator.player_y, simulator.player_heading)
                next_state_vals = q_values.get(next_state)
                if next_state_vals  is not None:
                    next_state_value = max(next_state_vals.values())
                else:
                    next_state_value = 0

                new_state_value = old_state_value + alpha*(reward[0] + gamma*next_state_value - old_state_value)
                """Update episode finished or not"""
                episode_finished = reward[1]

                """Update table"""
                q_values[current_state][action] = new_state_value

            """Reset when episode finishes"""
            simulator.reset_to_start()

        # store the computed Q-values
        self.q_values = q_values
        

    def train_sarsa(self, simulator):
        """
        Train the agent using SARSA, building up a table of Q-values.
        :param simulator: A simulator for collecting episode data (LaserTankMap instance)
        """
        alpha = 0.05
        gamma = simulator.gamma

        time_limit = simulator.time_limit
        
        q_values = {}

        # Continue till time limit is reached
        start_time = time.time()
        elapsed_time = 0
        while elapsed_time < time_limit:
            current_time = time.time()
            elapsed_time = current_time - start_time

            action = random.choice(self.moves)

            #Run till the episode ends
            episode_finished = False
            while not episode_finished:

                previous_action = action

                """Get current state"""
                current_state = (simulator.player_x, simulator.player_y, simulator.player_heading)

                """Choose action"""
                if current_state not in q_values:
                    q_values[current_state] = {"f":0, "l":0, "r":0, "s":0}
                    # Epsilon Greedy
                    #current_state_vals = q_values[current_state]
                    #if random.random() > self.exploit_prob:
                        #action = random.choice(self.moves) 
                    #else:
                        #action = max(current_state_vals, key = current_state_vals.get)
                #else:
                    # Choose random action
                    #action = random.choice(self.moves) #self.moves[random.randint(0,3)]
                    # Put this state in q_values
                    #q_values[current_state] = {"f":0, "l":0, "r":0, "s":0}


                """Get previous value"""
                old_state_value = q_values[current_state][action]
                """Apply action"""
                reward = simulator.apply_move(action)
                """Get next state value"""
                next_state = (simulator.player_x, simulator.player_y, simulator.player_heading)
                next_state_vals = q_values.get(next_state)
                if next_state_vals  is not None:
                    if abs(max(next_state_vals.values())) == 0 or random.random() > self.exploit_prob:
                        action = random.choice(self.moves)
                    else:
                        action = max(next_state_vals, key = next_state_vals.get)
                    next_state_value = next_state_vals[action]
                else:
                    next_state_value = 0
                    action = random.choice(self.moves)

                new_state_value = old_state_value + alpha*(reward[0] + gamma*next_state_value - old_state_value)
                """Update episode finished or not"""
                episode_finished = reward[1]
                #if episode_finished:
                    #print("should")

                """Update table"""
                q_values[current_state][previous_action] = new_state_value

            """Reset when episode finishes"""
            #print("did")
            simulator.reset_to_start()

        # store the computed Q-values
        self.q_values = q_values
        

        
    def get_policy(self, state):
        """
        Get the policy for this state (i.e. the action that should be performed at this state).
        :param state: a LaserTankMap instance
        :return: pi(s) [an element of LaserTankMap.MOVES]
        """
        vals = self.q_values[(state.player_x, state.player_y, state.player_heading)]
        return max(vals, key = vals.get)

        #
        # TODO
        # Write code to return the optimal action to be performed at this state based on the stored Q-values.
        #
        # You can assume that either train_q_learning( ) or train_sarsa( ) has been called before this
        # method is called.
        #
        # When this method is called, you are allowed up to 1 second of compute time.
        #

        pass







