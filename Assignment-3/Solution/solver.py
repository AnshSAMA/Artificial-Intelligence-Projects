from laser_tank import LaserTankMap, DotDict
import time
import copy

"""
Template file for you to implement your solution to Assignment 3. You should implement your solution by filling in the
following method stubs:
    run_value_iteration()
    run_policy_iteration()
    get_offline_value()
    get_offline_policy()
    get_mcts_policy()
    
You may add to the __init__ method if required, and can add additional helper methods and classes if you wish.

To ensure your code is handled correctly by the autograder, you should avoid using any try-except blocks in your
implementation of the above methods (as this can interfere with our time-out handling).

COMP3702 2020 Assignment 3 Support Code
"""


class Solver:

    def __init__(self, game_map):
        self.game_map = game_map
        self.success_prob = game_map.t_success_prob
        self.error_prob = (game_map.t_error_prob)/5
        
        self.up = 0
        self.down = 1
        self.left = 2
        self.right = 3
        self.directions = [0, 1, 2, 3]

        self.move_cost = game_map.move_cost
        self.collision_cost = game_map.collision_cost
        self.game_over_cost = game_map.game_over_cost
        self.goal_reward = game_map.goal_reward

        self.gamma = game_map.gamma
        self.epsilon = game_map.epsilon
        self.time_limit = game_map.time_limit

        forward_reward_next_state = {}
        action = "f"
        for y in range(self.game_map.y_size):
            for x in range(self.game_map.x_size):
                if self.game_map.cell_is_blocked(y,x) or self.game_map.cell_is_game_over(y,x):
                    continue
                coords = (x,y)    
                for direction in self.directions:
                    new_game_map = self.game_map.make_clone()
                    new_game_map.player_x = x
                    new_game_map.player_y = y
                    new_game_map.player_heading = direction
                    # Forward
                    forward_game_map = new_game_map.make_clone()
                    forward_expected_reward = forward_game_map.apply_move(action, 44)
                    forward_next_state = (forward_game_map.player_x, forward_game_map.player_y)
                    forward_reward_next_state[(coords,direction,"f")] = (forward_expected_reward, forward_next_state)
                    # Left
                    forward_game_map = new_game_map.make_clone()
                    forward_expected_reward = forward_game_map.apply_move(action, 2)
                    forward_next_state = (forward_game_map.player_x, forward_game_map.player_y)
                    forward_reward_next_state[(coords,direction,"l")] = (forward_expected_reward, forward_next_state)
                    # Right
                    forward_game_map = new_game_map.make_clone()
                    forward_expected_reward = forward_game_map.apply_move(action, 52)
                    forward_next_state = (forward_game_map.player_x, forward_game_map.player_y)
                    forward_reward_next_state[(coords,direction,"r")] = (forward_expected_reward, forward_next_state)
                    # Forward-Left
                    forward_game_map = new_game_map.make_clone()
                    forward_expected_reward = forward_game_map.apply_move(action, 54)
                    forward_next_state = (forward_game_map.player_x, forward_game_map.player_y)
                    forward_reward_next_state[(coords,direction,"fl")] = (forward_expected_reward, forward_next_state)
                    # Forward-Right
                    forward_game_map = new_game_map.make_clone()
                    forward_expected_reward = forward_game_map.apply_move(action, 62)
                    forward_next_state = (forward_game_map.player_x, forward_game_map.player_y)
                    forward_reward_next_state[(coords,direction,"fr")] = (forward_expected_reward, forward_next_state)


        self.forward_reward_next_state = forward_reward_next_state
        
        self.values = None
        self.policy = None

    def run_value_iteration(self):
        """
        Build a value table and a policy table using value iteration, and store inside self.values and self.policy.
        """

        actions = ['f', 'l', 'r', 's']

        
        values = [[[0 for _ in LaserTankMap.DIRECTIONS]
                   for __ in range(0, self.game_map.y_size)]
                  for ___ in range(0, self.game_map.x_size)]
        policy = [[[-1 for _ in LaserTankMap.DIRECTIONS]
                   for __ in range(0, self.game_map.y_size)]
                  for ___ in range(0, self.game_map.x_size)]

        self.values = copy.deepcopy(values)
        self.policy = copy.deepcopy(policy)
        y_size = self.game_map.y_size
        x_size = self.game_map.x_size
        start_time = time.time()
        elapsed_time = 0
        iterations = 0
        while elapsed_time < self.time_limit:
            
            current_time = time.time()
            elapsed_time = current_time - start_time

            all_deltas = list()
                        
            # Value Iteration
            for y in range(self.game_map.y_size):
                for x in range(self.game_map.x_size):
                    coords = (x,y)
                    deltas = list()
                    if self.game_map.cell_is_blocked(y,x) or self.game_map.cell_is_game_over(y,x):
                        # Skip. No need to count cost here
                        continue
                    
                    for direction in self.directions:
                        action_values = list()
                        
                        for action in actions:
                            # Copy The Game Map
                            new_game_map = self.game_map.make_clone()
                            # Change player position to current state
                            # Now, can find future values using apply_move()
                            new_game_map.player_x = x
                            new_game_map.player_y = y
                            new_game_map.player_heading = direction

                            if action == 'f':
                                # Reward
                                forward_expected_reward = 0
                                next_state_val = 0

                                # Move Forward
                                prob = self.success_prob
                                forward_expected_reward += prob*((self.forward_reward_next_state[(coords,direction,"f")])[0])
                                next_state = (self.forward_reward_next_state[(coords,direction,"f")])[1]
                                next_state_val += prob*self.values[next_state[0]][next_state[1]][direction]
                                
                                # Move Left
                                prob = self.error_prob
                                forward_expected_reward += prob*((self.forward_reward_next_state[(coords,direction,"l")])[0])
                                next_state = (self.forward_reward_next_state[(coords,direction,"l")])[1]
                                next_state_val += prob*self.values[next_state[0]][next_state[1]][direction]
                                
                                # Move Right
                                prob = self.error_prob
                                forward_expected_reward += prob*((self.forward_reward_next_state[(coords,direction,"r")])[0])
                                next_state = (self.forward_reward_next_state[(coords,direction,"r")])[1]
                                next_state_val += prob*self.values[next_state[0]][next_state[1]][direction]

                                # Move Forward-Left
                                prob = self.error_prob
                                forward_expected_reward += prob*((self.forward_reward_next_state[(coords,direction,"fl")])[0])
                                next_state = (self.forward_reward_next_state[(coords,direction,"fl")])[1]
                                next_state_val += prob*self.values[next_state[0]][next_state[1]][direction]

                                # Move Forward-Right
                                prob = self.error_prob
                                forward_expected_reward += prob*((self.forward_reward_next_state[(coords,direction,"fr")])[0])
                                next_state = (self.forward_reward_next_state[(coords,direction,"fr")])[1]
                                next_state_val += prob*self.values[next_state[0]][next_state[1]][direction]

                                # Move Same
                                prob = self.error_prob
                                forward_expected_reward += prob*self.move_cost
                                next_state_val += prob*self.values[x][y][direction]

                                total = forward_expected_reward + self.gamma*next_state_val
                                #print("Reward Forward", total)
                                action_values.append(total)
                                
                            else:
                                reward = new_game_map.apply_move(action)
                                future_val = (self.gamma)*(self.values[new_game_map.player_x][new_game_map.player_y][new_game_map.player_heading])
                                total = reward + future_val
                                action_values.append(total)
                        
                        # Setup Correct Values
                        max_val = -9999
                        max_index = 0
                        j = 0
                        for val in action_values:
                            if val > max_val:
                                max_val = val
                                max_index = j
                            j += 1

                        old_val = values[x][y][direction]
                        new_val = max_val
                        delta = abs((new_val - old_val))
                        deltas.append(delta)
                        
                        values[x][y][direction] = max_val
                        policy[x][y][direction] = actions[max_index]
                    
                    all_deltas.append(max(deltas))
                    
            iterations += 1
            # store the computed values and policy
            self.values = copy.deepcopy(values)
            self.policy = copy.deepcopy(policy)

            if max(all_deltas) < self.epsilon:
                break

    def run_policy_iteration(self):
        """
        Build a value table and a policy table using policy iteration, and store inside self.values and self.policy.
        """
        values = [[[0 for _ in LaserTankMap.DIRECTIONS]
                   for __ in range(0, self.game_map.y_size)]
                  for ___ in range(0, self.game_map.x_size)]
        policy = [[[-1 for _ in LaserTankMap.DIRECTIONS]
                   for __ in range(0, self.game_map.y_size)]
                  for ___ in range(0, self.game_map.x_size)]

        self.values = copy.deepcopy(values)
        early_policy = copy.deepcopy(self.policy)        
        actions = ['f', 'l', 'r', 's']        
        
        # Setup Initial Policy
        for y in range(self.game_map.y_size):
            for x in range(self.game_map.x_size):
                if self.game_map.cell_is_blocked(y,x) or self.game_map.cell_is_game_over(y,x):
                    continue
                for direction in self.directions:
                    policy[x][y][direction] = "f"
        
        # PI
        iterations = 0
        l = 0
              
        start_time = time.time()
        elapsed_time = 0
        while elapsed_time < self.time_limit:
            current_time = time.time()
            elapsed_time = current_time - start_time
            
            
            
            # Setup Initial Values 
            for y in range(self.game_map.y_size):
                for x in range(self.game_map.x_size):
                    if self.game_map.cell_is_blocked(y,x) or self.game_map.cell_is_game_over(y,x):
                        continue
                    coords = (x,y)
                    for direction in self.directions:
                        action = policy[x][y][direction]
                        if action != -1:
                            # Copy The Game Map
                            new_game_map = self.game_map.make_clone()
                            # Change player position to current state
                            # Now, can find future values using apply_move()
                            new_game_map.player_x = x
                            new_game_map.player_y = y
                            new_game_map.player_heading = direction

                            if action == "f":
                                # Reward
                                forward_expected_reward = 0
                                next_state_val = 0

                                # Move Forward
                                prob = self.success_prob
                                forward_expected_reward += prob*((self.forward_reward_next_state[(coords,direction,"f")])[0])
                                next_state = (self.forward_reward_next_state[(coords,direction,"f")])[1]
                                next_state_val += prob*self.values[next_state[0]][next_state[1]][direction]
                                    
                                # Move Left
                                prob = self.error_prob
                                forward_expected_reward += prob*((self.forward_reward_next_state[(coords,direction,"l")])[0])
                                next_state = (self.forward_reward_next_state[(coords,direction,"l")])[1]
                                next_state_val += prob*self.values[next_state[0]][next_state[1]][direction]
                                    
                                # Move Right
                                prob = self.error_prob
                                forward_expected_reward += prob*((self.forward_reward_next_state[(coords,direction,"r")])[0])
                                next_state = (self.forward_reward_next_state[(coords,direction,"r")])[1]
                                next_state_val += prob*self.values[next_state[0]][next_state[1]][direction]

                                # Move Forward-Left
                                prob = self.error_prob
                                forward_expected_reward += prob*((self.forward_reward_next_state[(coords,direction,"fl")])[0])
                                next_state = (self.forward_reward_next_state[(coords,direction,"fl")])[1]
                                next_state_val += prob*self.values[next_state[0]][next_state[1]][direction]

                                # Move Forward-Right
                                prob = self.error_prob
                                forward_expected_reward += prob*((self.forward_reward_next_state[(coords,direction,"fr")])[0])
                                next_state = (self.forward_reward_next_state[(coords,direction,"fr")])[1]
                                next_state_val += prob*self.values[next_state[0]][next_state[1]][direction]

                                # Move Same
                                prob = self.error_prob
                                forward_expected_reward += prob*self.move_cost
                                next_state_val += prob*self.values[x][y][direction]
                                
                                total = forward_expected_reward + self.gamma*next_state_val
                                values[x][y][direction] = total
                                
                            else:
                                reward = new_game_map.apply_move(action)
                                future_val = (self.gamma)*(self.values[new_game_map.player_x][new_game_map.player_y][new_game_map.player_heading])
                                
                                total = reward + future_val
                                values[x][y][direction] = total

            # Update Policy
            for y in range(self.game_map.y_size):
                for x in range(self.game_map.x_size):
                    coords = (x,y)
                    if self.game_map.cell_is_blocked(y,x) or self.game_map.cell_is_game_over(y,x):
                        # Skip. No need to count cost here
                        continue
                    
                    for direction in self.directions:
                        action_values = list()
                        for action in actions:
                            # Copy The Game Map
                            new_game_map = self.game_map.make_clone()
                            # Change player position to current state
                            # Now, can find future values using apply_move()
                            new_game_map.player_x = x
                            new_game_map.player_y = y
                            new_game_map.player_heading = direction

                            if action == 'f':
                                # Reward
                                forward_expected_reward = 0
                                next_state_val = 0

                                # Move Forward
                                prob = self.success_prob
                                forward_expected_reward += prob*((self.forward_reward_next_state[(coords,direction,"f")])[0])
                                next_state = (self.forward_reward_next_state[(coords,direction,"f")])[1]
                                next_state_val += prob*values[next_state[0]][next_state[1]][direction]
                                
                                # Move Left
                                prob = self.error_prob
                                forward_expected_reward += prob*((self.forward_reward_next_state[(coords,direction,"l")])[0])
                                next_state = (self.forward_reward_next_state[(coords,direction,"l")])[1]
                                next_state_val += prob*values[next_state[0]][next_state[1]][direction]
                                
                                # Move Right
                                prob = self.error_prob
                                forward_expected_reward += prob*((self.forward_reward_next_state[(coords,direction,"r")])[0])
                                next_state = (self.forward_reward_next_state[(coords,direction,"r")])[1]
                                next_state_val += prob*values[next_state[0]][next_state[1]][direction]

                                # Move Forward-Left
                                prob = self.error_prob
                                forward_expected_reward += prob*((self.forward_reward_next_state[(coords,direction,"fl")])[0])
                                next_state = (self.forward_reward_next_state[(coords,direction,"fl")])[1]
                                next_state_val += prob*values[next_state[0]][next_state[1]][direction]

                                # Move Forward-Right
                                prob = self.error_prob
                                forward_expected_reward += prob*((self.forward_reward_next_state[(coords,direction,"fr")])[0])
                                next_state = (self.forward_reward_next_state[(coords,direction,"fr")])[1]
                                next_state_val += prob*values[next_state[0]][next_state[1]][direction]

                                # Move Same
                                prob = self.error_prob
                                forward_expected_reward += prob*self.move_cost
                                next_state_val += prob*values[x][y][direction]

                                total = forward_expected_reward + self.gamma*next_state_val
                                #print("Reward Forward", total)
                                action_values.append(total)
                                
                            else:
                                reward = new_game_map.apply_move(action)
                                future_val = (self.gamma)*(values[new_game_map.player_x][new_game_map.player_y][new_game_map.player_heading])
                                total = reward + future_val
                                action_values.append(total)
                                
                        max_val = -999
                        max_index = 0
                        j = 0
                        for val in action_values:
                            if val > max_val:
                                max_val = val
                                max_index = j
                            j += 1
                        policy[x][y][direction] = actions[max_index]

            iterations += 1
            
                
            if policy == self.policy:
                l += 1
                if l > 5:
                    l = 0
                    early_policy = copy.deepcopy(policy)
                    
                if early_policy == policy:
                    break
                    
            self.values = copy.deepcopy(values)
            self.policy = copy.deepcopy(policy)

        self.values = values
        self.policy = policy

    def get_offline_value(self, state):
        """
        Get the value of this state.
        :param state: a LaserTankMap instance
        :return: V(s) [a floating point number]
        """
        return self.values[state.player_x][state.player_y][state.player_heading]


    def get_offline_policy(self, state):
        """
        Get the policy for this state (i.e. the action that should be performed at this state).
        :param state: a LaserTankMap instance
        :return: pi(s) [an element of LaserTankMap.MOVES]
        """
        return self.policy[state.player_x][state.player_y][state.player_heading]

    def get_mcts_policy(self, state):
        """
        Choose an action to be performed using online MCTS.
        :param state: a LaserTankMap instance
        :return: pi(s) [an element of LaserTankMap.MOVES]
        """
        pass
    







