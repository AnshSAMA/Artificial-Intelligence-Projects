import sys


from problem_spec import ProblemSpec
from robot_config import write_robot_config_list_to_file
from robot_config import make_robot_config_from_ee1
from robot_config import make_robot_config_from_ee2
from angle import Angle
from tester import test_config_equality

import random

import math

import copy

from tester import test_obstacle_collision
from tester import test_self_collision
from tester import test_environment_bounds
from tester import test_angle_constraints



"""
Template file for you to implement your solution to Assignment 2. Contains a class you can use to represent graph nodes,
and a method for finding a path in a graph made up of GraphNode objects.

COMP3702 2020 Assignment 2 Support Code
"""


class GraphNode:
    """
    Class representing a node in the state graph. You should create an instance of this class each time you generate
    a sample.
    """

    def __init__(self, spec, config):
        """
        Create a new graph node object for the given config.

        Neighbors should be added by appending to self.neighbors after creating each new GraphNode.

        :param spec: ProblemSpec object
        :param config: the RobotConfig object to be stored in this node
        """
        self.spec = spec
        self.config = config
        self.neighbors = []

    def __eq__(self, other):
        return test_config_equality(self.config, other.config, self.spec)

    def __hash__(self):
        return hash(tuple(self.config.points))

    def get_successors(self):
        return self.neighbors

    @staticmethod
    def add_connection(n1, n2):
        """
        Creates a neighbor connection between the 2 given GraphNode objects.

        :param n1: a GraphNode object
        :param n2: a GraphNode object
        """
        n1.neighbors.append(n2)
        n2.neighbors.append(n1)


def find_graph_path(spec, init_node):
    """
    This method performs a breadth first search of the state graph and return a list of configs which form a path
    through the state graph between the initial and the goal. Note that this path will not satisfy the primitive step
    requirement - you will need to interpolate between the configs in the returned list.

    You may use this method in your solver if you wish, or can implement your own graph search algorithm to improve
    performance.

    :param spec: ProblemSpec object
    :param init_node: GraphNode object for the initial configuration
    :return: List of configs forming a path through the graph from initial to goal
    """
    # search the graph
    init_container = [init_node]

    # here, each key is a graph node, each value is the list of configs visited on the path to the graph node
    init_visited = {init_node: [init_node.config]}

    while len(init_container) > 0:
        current = init_container.pop(0)

        if test_config_equality(current.config, spec.goal, spec):
            # found path to goal
            return init_visited[current]

        successors = current.get_successors()
        for suc in successors:
            if suc not in init_visited:
                init_container.append(suc)
                init_visited[suc] = init_visited[current] + [suc.config]

    return None

# No obstacle and self collision + lies in workspace
# Returns True for pass
def individual_config_collision_checking(spec, config):
    # Obstacle Collision - true for pass, false for fail
    # Self Collision - return true for pass, false for fail
    # Environment Bound - return true for pass, false for fail
    # Angle Constraints - true for pass, false for fail
    return test_obstacle_collision(config, spec, spec.obstacles) and test_self_collision(config, spec) and test_environment_bounds(config) and test_angle_constraints(config, spec)

# Generate a random RobotConfig based on arm grappled
def generate_sample(spec):
    arm = spec.initial
    min_lengths = spec.min_lengths
    max_lengths = spec.max_lengths
    #print(min_lengths)
    #print(max_lengths)
    angles  = []
    lengths = []
    for i in range(len(arm.lengths)):
        if i == 0:
            angles.append(Angle(math.radians(random.randint(-180, 180))))
        else:
            angles.append(Angle(math.radians(random.randint(-165, 165))))
        lengths.append(random.uniform(min_lengths[i], max_lengths[i]))
    #print(angles)
    #print(lengths)
    #print(arm.points[0][0])
    #print(arm.points[0][1])
    #print(arm.points[1])
    sample = make_robot_config_from_ee1(arm.points[0][0], arm.points[0][1], angles, lengths, True)
    while(not individual_config_collision_checking(spec, sample)):
        sample = generate_sample(spec)
    return sample
    #sample_list = [sample]
    #write_robot_config_list_to_file('new_output.txt', sample_list)
    #print(len(arm.lengths))

def interpolate_path(config_1, config_2, spec):
    path = []
    path.append(config_1)
    # Make copy of config_1
    new_config = make_robot_config_from_ee1(config_1.points[0][0], config_1.points[0][1], config_1.ee1_angles, config_1.lengths, True)
    
    # Number of Segments and Angles to iterate over
    no_of_angles = len(config_1.ee1_angles)

    list_delta = []
    list_length_delta = []
    # Add Delta i.e. InitConfig.angle - FinalConfig.angle
    for theta_angle in range(no_of_angles):
        list_delta.append((config_1.ee1_angles[theta_angle].in_radians() - config_2.ee1_angles[theta_angle].in_radians()))
        list_length_delta.append((config_1.lengths[theta_angle] - config_2.lengths[theta_angle]))

    max_delta = 0
    for delta in list_delta:
        if abs(delta) > max_delta:
            max_delta = abs(delta)
    max_length_delta = 0
    for delta in list_length_delta:
        if abs(delta) > max_length_delta:
            max_length_delta = abs(delta)
    no_of_steps = max_delta/0.001
    no_of_steps_length = max_length_delta/0.001
    
    while(True):
        
# TO DO - MANUAL COPY INSTEAD OF DEEP COPY

        # Deepcopy previous angles and lengths and change them on this config
        new_angles = copy.deepcopy(new_config.ee1_angles)
        new_lengths = copy.deepcopy(new_config.lengths)
        
        for angle_no in range(no_of_angles):
            # Increase Angles
            if (abs(new_config.ee1_angles[angle_no].in_radians() - config_2.ee1_angles[angle_no].in_radians()) >= 0.001):
                increment_val = -(list_delta[angle_no]/no_of_steps)
                new_angles[angle_no] = Angle(new_config.ee1_angles[angle_no].in_radians() + increment_val)
                
            # Increase Lengths
            if (abs(new_config.lengths[angle_no] - config_2.lengths[angle_no]) >= 0.001):
                increment_val = -(list_length_delta[angle_no]/no_of_steps_length)
                new_lengths[angle_no] = new_config.lengths[angle_no] + increment_val
                
        new_config = make_robot_config_from_ee1(new_config.points[0][0], new_config.points[0][1], new_angles, new_lengths, True)
        #for angles in new_angles:
            #print(angles.in_degrees())
        #for angle_no in range(no_of_angles):
            #print(new_config.ee1_angles[angle_no], end = "")
            #print(" ", end="")
        #print("")
        if individual_config_collision_checking(spec, new_config) == False:
            #print("Fuck")
            #exit()
            return None
        path.append(new_config)
        
        if check_last_step_interpolation(new_config, config_2):
            break
    path.append(config_2)
    return path

def check_last_step_interpolation(config, final_config):
    for angle_no in range(len(config.ee1_angles)):    
        if abs(config.ee1_angles[angle_no].in_radians() - final_config.ee1_angles[angle_no].in_radians()) >= 0.001 or abs(config.lengths[angle_no] - final_config.lengths[angle_no]) >= 0.001:
            return False
    return True
        
def create_bridge_config(spec):
    grapple_points = spec.grapple_points
    arm = spec.initial
    min_lengths = spec.min_lengths
    max_lengths = spec.max_lengths
    #print(min_lengths)
    #print(max_lengths)
    angles  = []
    lengths = []
    for i in range(len(arm.lengths)):
        if i == 0:
            angles.append(Angle(math.radians(random.randint(-180, 180))))
        else:
            angles.append(Angle(math.radians(random.randint(-165, 165))))
        lengths.append(random.uniform(min_lengths[i], max_lengths[i]))
    
    #angles.append(Angle)
    #print(angles)
    #print(lengths)
    #print(arm.points[0][0])
    #print(arm.points[0][1])
    #print(arm.points[1])
    sample = make_robot_config_from_ee1(arm.points[0][0], arm.points[0][1], angles, lengths, True)
    #for points in sample.points:
        #print(points)
    sample_points = sample.points[-2]
    #print("--------------")
    #print(sample_points)
    delta_y = grapple_points[1][1] - sample_points[1]
    delta_x = grapple_points[1][0] - sample_points[0]
    new_angle = delta_y/delta_x
    last_angle = Angle.tan(new_angle)
    sum_angles = 0
    for angle in range(len(angles) - 1):
        if angle == 0:
            sum_angles = angles[angle].in_degrees() 
        else:
            sum_angles = 180 + angles[angle].in_degrees() 
    second_last_angle = 360 - sum_angles - last_angle
    angles[-1] = Angle(math.radians(360 + second_last_angle))
    lengths[-1] = math.sqrt(delta_x**2 + delta_y**2)

    bridge_2_config = make_robot_config_from_ee1(arm.points[0][0], arm.points[0][1], angles, lengths, True, False)
    while(not individual_config_collision_checking(spec, bridge_2_config)):
        bridge_2_config = create_bridge_config(spec)
    return bridge_2_config
    

def main(arglist):
#def main():
    input_file = arglist[0]
    output_file = arglist[1]
    #input_file = 'testcases/3g2_m1.txt'
    #output_file = 'new_output.txt'

    spec = ProblemSpec(input_file)
    init_node = GraphNode(spec, spec.initial)
    goal_node = GraphNode(spec, spec.goal)

    # Keep track of all samples generated
    nodes_in_graph = []
    nodes_in_graph.append(init_node)
    nodes_in_graph.append(goal_node)


    #bridge = []
    #new_bridge = create_bridge_config(spec)
    #bridge.append(new_bridge)
    #bridge.append(new_bridge)
    #bridge.append(new_bridge)
    #bridge.append(new_bridge)
    #bridge.append(new_bridge)
    #bridge.append(new_bridge)
    #bridge.append(new_bridge)
    #bridge.append(new_bridge)
    #bridge.append(new_bridge)
    #write_robot_config_list_to_file(output_file, bridge)
    #exit()


    search_remaining = True
    #connections_added = 0
    while search_remaining:
        # Generate X new Samples
        for i in range(10):
            sample = generate_sample(spec)
            sample_node = GraphNode(spec, sample)
            # Connect sample to all samples if d < 0.2 and interpolated_path != None
            for node in nodes_in_graph:
                distance_bw_nodes = abs(sample.points[-1][1] - node.config.points[-1][1]) + abs(sample.points[-1][0] - node.config.points[-1][0])
                #print(distance_bw_nodes)
                if distance_bw_nodes < 0.2:
                    # Lazy Check
                    mid_angles = []
                    mid_angles.extend(node.config.ee1_angles)
                    for angle in range(len(sample.ee1_angles)):
                        mid_angles[angle] = (mid_angles[angle].in_degrees() + sample.ee1_angles[angle].in_degrees())/2

                    mid_lengths = []
                    mid_lengths.extend(node.config.lengths)
                    for length in range(len(sample.lengths)):
                        mid_lengths[length] = ( mid_lengths[length] + sample.lengths[length])/2
                    mid_new_config = make_robot_config_from_ee1(sample.points[0][0], sample.points[0][1], mid_angles, mid_lengths, True)
                    if individual_config_collision_checking(spec, mid_new_config) == False:# False shouldn't work
                        GraphNode.add_connection(node, sample_node)
                        #connections_added = connections_added + 1
                    # Full Check
                    #interpolated_path = interpolate_path(node.config, sample_node.config, spec)
                    #if interpolated_path != None:
                        #GraphNode.add_connection(node, sample_node)
                        #connections_added = connections_added + 1
            nodes_in_graph.append(sample_node)
        #print(connections_added)

        # Search Graph
        path_found = find_graph_path(spec, init_node)
        if path_found != None:
            final_path = []
            searched_paths = 0
            for path_no in range(len(path_found) - 1):
                path_yay = interpolate_path(path_found[path_no], path_found[path_no +1], spec)
                if path_yay == None:
                    print("Some Error")
                    for node in nodes_in_graph:
                        if node == GraphNode(spec, path_found[path_no]):
                            first_node = node
                        elif node == GraphNode(spec, path_found[path_no + 1]):
                            second_node = node
                    first_node.neighbors.remove(second_node)
                    second_node.neighbors.remove(first_node)

                    break
                else:
                    print("yay")
                    final_path.extend(path_yay)
                    # Break when goal reached
                    searched_paths += 1
                    #search_completed = False
            if searched_paths == len(path_found) - 1:
                write_robot_config_list_to_file(output_file, final_path)
                search_remaining = False
        else:
            print("no path found")
            

    

    #GraphNode.add_connection(init_node, goal_node)

    

    #interpolate_path(spec.initial, spec.goal)

    steps = []

    #
    #
    # Code for your main method can go here.
    #
    # Your code should find a sequence of RobotConfig objects such that all configurations are collision free, the
    # distance between 2 successive configurations is less than 1 primitive step, the first configuration is the initial
    # state and the last configuration is the goal state.
    #
    #


    

    #if len(arglist) > 1:
        #write_robot_config_list_to_file(output_file, steps)

    #
    # You may uncomment this line to launch visualiser once a solution has been found. This may be useful for debugging.
    # *** Make sure this line is commented out when you submit to Gradescope ***
    #
    #v = Visualiser(spec, steps)


# Current Problems
# Connected nodes not having None interpolated_path
# Mid Point Checking

# To Do
# Midpoint instead of interpolation

if __name__ == '__main__':
    main(sys.argv[1:])
    #main()
