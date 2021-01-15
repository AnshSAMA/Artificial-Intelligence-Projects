#!/usr/bin/python
import sys
from laser_tank import LaserTankMap
#from queue import PriorityQueue
import copy
import queue

"""
Template file for you to implement your solution to Assignment 1.

COMP3702 2020 Assignment 1 Support Code
"""


#
#
# Code for any classes or functions you need can go here.
#
#

# Goal Coordinates
goal_coord_x = 0
goal_coord_y = 0

# Heuristic Function
def heuristic_func(player_coord_x, player_coord_y):
    return abs(player_coord_x - goal_coord_x) + abs(player_coord_y - goal_coord_y)

    
# State Representation
class PlayerTank:

    def __init__(self, grid, cost, coord_x, coord_y, action_taken, path, x_size, y_size, player_heading):
        self.grid = grid
        self.cost = cost
        self.action_taken = action_taken
        self.path = path
        self.coord_x = coord_x
        self.coord_y = coord_y
        self.x_size = x_size
        self.y_size = y_size
        self.player_heading = player_heading
        self.id = (coord_x, coord_y, self.player_heading)

    def get_total_cost(self):
        return self.cost + heuristic_func(self.coord_x, self.coord_y)
        
    def action_move(self, action):
        new_grid = [row[:] for row in self.grid]
        new_player = LaserTankMap(self.x_size, self.y_size, new_grid, self.coord_x, self.coord_y, self.player_heading)
        # Move Forward
        if action == 'W':
            result = new_player.apply_move('f')
            path_to_take = 'f'

        # Turn Clockwise
        elif action == 'D':
            result = new_player.apply_move('r')
            path_to_take = 'r'

        # Turn Counter-Clockwise 
        elif action == 'A':
            result = new_player.apply_move('l')
            path_to_take = 'l'

        # Shoot Laser
        elif action == 'S':
            result = new_player.apply_move('s')
            path_to_take = 's'
        else:
            print("No/Worng Action Input")

        if result == 0:
            new_state = PlayerTank(new_player.grid_data, self.cost + 1, new_player.player_x, new_player.player_y, action, self.path + [path_to_take], self.x_size, self.y_size, new_player.player_heading)
        elif result == 1:
            new_state = 0
        elif result == 2:
            new_state = 0
        return new_state

    def goal_reached(self):
        new_grid = [row[:] for row in self.grid]
        new_player = LaserTankMap(self.x_size, self.y_size, new_grid, self.coord_x, self.coord_y, self.player_heading)
        if new_player.is_finished():
            return True
        return False

    def __eq__(self, other):
        if other == 0:
            return False
        return self.coord_x == other.coord_x and self.coord_y == other.coord_y and self.player_heading == other.player_heading and self.grid == other.grid
    
    def __lt__(self, other):
        #return self.cost < other.cost
        return self.get_total_cost() < other.get_total_cost()
        

def write_output_file(filename, actions):
    """
    Write a list of actions to an output file. You should use this method to write your output file.
    :param filename: name of output file
    :param actions: list of actions where is action is in LaserTankMap.MOVES
    """
    f = open(filename, 'w')
    for i in range(len(actions)):
        f.write(str(actions[i]))
        if i < len(actions) - 1:
            f.write(',')
    f.write('\n')
    f.close()

def main(arglist):
    input_file = arglist[0]
    output_file = arglist[1]

    # Read the input testcase file
    game_map = LaserTankMap.process_input_file(input_file)

    # Extract goal 
    for coord_x in range(game_map.x_size):
        for coord_y in range(game_map.y_size):
            if game_map.grid_data[coord_y][coord_x] == 'F':
                global goal_coord_x
                global goal_coord_y
                goal_coord_x = coord_x
                goal_coord_y = coord_y
        

    actions = []

    actionset = ['W', 'D', 'A', 'S']

    # Initialise Starting State
    start_state = PlayerTank(game_map.grid_data, 0, game_map.player_x, game_map.player_y, 'W', [], game_map.x_size, game_map.y_size, game_map.player_heading)

    #Start the Fringe/Frontier
    fringe = queue.PriorityQueue()
    fringe.put(start_state)

    #Keep track of all states explored
    hash_explored = {start_state.id: [start_state]}
    
    while not fringe.empty():
        current = fringe.get()

        # When goal is reached
        if current.goal_reached():
            actions = current.path
            break
        
        for action in actionset:
            neighbor = current.action_move(action)

            # Proceed if no collision or game over.
            # Add to visited and fringe if not previously
            if neighbor != 0:
                if (neighbor.id not in hash_explored):
                    hash_explored[neighbor.id] = [neighbor]
                    fringe.put(neighbor)
                elif (neighbor not in hash_explored[neighbor.id]):
                    hash_explored[neighbor.id].append(neighbor)
                    fringe.put(neighbor)

    # Write the solution to the output file
    write_output_file(output_file, actions)


if __name__ == '__main__':
    main(sys.argv[1:])

