import csv
from queue import Queue
import time
import pandas as pd

def read_entry_v1(file_name):
    """ 
    read_entry takes as input the file of the name as a csv file. It returns a dictionary of type (robot, directions)
    
    """
   
    instructions = {}  # dictionary of type: (robot, direction)
    
    with open(file_name, 'r') as file:
        reader = csv.reader(file) # possivel alteração para qualquer tipo de ficheiro? 
        for line in reader:
            robot = line[0] 
            directions = line[1]
            
            if robot in instructions:
                instructions[robot] += directions  # concatenate the total steps of each robot in his directions 
            else:
                instructions[robot] = directions
    
    return instructions


def read_entry_v2(file_name):
    read = pd.read_csv(file_name, header=None, names=["robot", "directions"])
    instructions = read.groupby('robot')['directions'].apply(''.join).to_dict()
    return instructions



def find_dimension(instructions):
    """ 
    find_dimension  takes as input the dictionary previously created by read_entry. 
    It returns: 
        - width and height of the labirinth; 
        - start_point and end_point of the labirinth
    """
    
    coordinates = {'U': (0, -1), 'D': (0, 1), 'R': (1, 0), 'L': (-1, 0)}  # this dictionary is the correspondence
                                                                          # between the directions present in the file and 
                                                                          # coordinates that each robot does in the maze
    # Initialize the limits of the maze: 
    min_x, max_x = 0, 0
    min_y, max_y = 0, 0
    
    # For each robot, we will substitute his directions to the steps in the maze (accordingly to coordinates):  
    for robot, directions in instructions.items():
        x, y = 0, 0 
        for direction in directions:
            if direction in coordinates:
                nx, ny = coordinates[direction]  # we will atualize x and y accordingly to the commands: 
                x += nx
                y += ny
                # Atualize the limits of the maze 
                max_x = max(max_x, x)
                max_y = max(max_y, y)
                min_x = min(min_x, x)
                min_y = min(min_y, y)
    
    # Calculation of the width and height of the maze: 
    width = max_x - min_x + 1  # width will be the difference between the maximum and the minimum of x 
    height = max_y - min_y + 1  # height will be the difference between the maximum and the minimum of y
    
    # Calculation of the start and the end of the maze:
    start_point = [abs(min_x), abs(min_y)]  # the start point will be the one with the less value of x and the less value of y 
    end_point = [abs(max_x), abs(max_y)]  # the end point will be the one with the bigger value of x and the bigger value of y 
    # Output variables: 
    return width, height, start_point, end_point

def define_maze(instructions, width, height, start_point):
    """ 
    define_maze takes the as input the dictionary previously created by read_entry, and the width, height and start_point
    previously found by find_dimension. 
    It creates a matrix that represents the maze. 
    It prints the maze and the steps of the robot in the Command Window. 
    - The spaces available by '.'; 
    - The spaces that cannot be stepped by '*'; 
    - The start by 'e'; 
    - The space with water by 'w'
    - The end by 's'
    """
    matrix = [['*' for _ in range(width)] for _ in range(height)]  # This is the matrix that will represent the maze. 
                                                                   # Initially, it wil be full of *
                                                                   
    coordinates = {'U': (0, -1), 'D': (0, 1), 'R': (1, 0), 'L': (-1, 0)}  # this dictionary is the correspondence
                                                                          # between the directions present in the file and 
                                                                     # coordinates that each robot does in the maze
                                                                     
    # Initialize the search, we will begin in the start_point found in find_dimension: 
    X, Y = start_point  
    x, y = X, Y  
    
    # 
    has_run = False
    has_run_ = False
    
    # For each robot, we will take its directions and transform them in steps in the maze:
    for robot, directions in instructions.items():
        x, y = X, Y  # Reinitialize the startpoint for each robot
        
        for direction in directions:
            if direction in coordinates:  # If the command is in coordinates (U,D,L or R), it is valid and the robot moves
                nx, ny = coordinates[direction]
                x += nx
                y += ny
                if 0 <= x < width and 0 <= y < height:  # Verify if each coordinate is between the limits of the maze
                    matrix[y][x] = '.'  # Represents the robot's movements in the maze
            
            elif direction == '?' and not has_run:  # If the command is '?' it represents the water
                x_w, y_w = x, y  # x_w and y_w are the coordinates of the water cell
                has_run = True # means we have reach the water target 
            
            elif direction == '!' and not has_run_:  # If the command is '!' it represents the end
                x_s, y_s = x, y  # x_s and y_s are the coordinates of the end point
                has_run_ = True # means we have reach the end target
    
    # Define the key points in the maze: 
    matrix[Y][X] = 'e' # the start 
    matrix[y_w][x_w] = 'w' # water
    matrix[y_s][x_s] = 's' # the end 
    
    
    return matrix,(x_w,y_w)

def solve(maze, width, height, start_point, water=None,state=0):
    """ 
    solve takes the matrix found in define_lab, and also the width, the height and the start_point that were found in find_dimension. 
    It returns for each maze the shortest path from the start to the end, passing through the water. 
    """
    print('state ',state)
    visited = set()  # This will be used to save the positions that the robot passes through
    
    X, Y = start_point  # the coordinates of the start_point
    

    
    end = 'w' if state==1 else 's'  # the first target will be the water cell, and then the end point. 
    
    if state==0: #Firstly, it is True, so we find the shortest path between the start point and the end
       
        path_to_w = solve(maze, width, height, start_point, state=1) # We call recursevily, to found the path to water       
        # Then we calculate the rest (the path between water and the end point)
        path_to_s = solve(maze, width, height, water,state=2)
        
        # Returns the path as a string: 
        return path_to_w + path_to_s

    # Possible directions to the search: 
    dx = [-1, 1, 0, 0]
    dy = [0, 0, -1, 1]
    directions = ['l', 'r', 'u', 'd']


    q=Queue()
    q.put((X,Y,[]))

    
    visited.add((X, Y))  # The starting point is added to the visited list
    
    while not q.empty():
        # We will be removing the coordinates from the queues: 

        x,y,path=q.get()
        #if state==1: print(''.join(path))
        
        if maze[y][x] == end:  # If we reach the water ('w') or the end ('s') 
            
            return path  # Returns the path as a string

        # Explore the 4 directions possible: 
        for i in range(4):
            xx = x + dx[i]
            yy = y + dy[i]

            if xx < 0 or yy < 0 or yy >= height or xx >= width:  # Validation of the position in the maze 
                continue            
            if maze[yy][xx] == '*': # or if it is a wall
                continue           
            if (xx, yy) in visited:   # Validation if the position was already visited,
                continue 

            q.put((xx,yy,path + [directions[i]]))
            visited.add((xx, yy))  # Then we marked that position as visited 
    
    return []  # If the path is not found, it returns as empty

def robot(instructions, width, height, start_point,maze,shortest_path):
    """
    robot takes as input the dictionay instructions created by read_entry, and the width, height and
    start_point created by find_dimension .It will return a robot that does the the shortest path
    """
    # Definition of the maze: 
    #maze = define_maze(instructions, width, height, start_point)
    
    # Shortest path determined by method solve
    #shortest_path = solve(maze, width, height, start_point)
    
    # As the function solve returns a list with the directions of the shortest path, we convert it to a string
    shortest_path_str = ''.join(shortest_path)  
    
    last_robot = [] # as seen as the maze1.result, we wanted to return the last robot that does the shortest path


    # Compare each direction of each robot, to the shortest_path_str
    for robot, directions in instructions.items():
        
        filtered_directions = ''.join([d for d in directions if d in "UDLR"]) # we just want to store directions, not characteres
        if filtered_directions == shortest_path_str.upper():  
            last_robot.append(robot) # If they are the same, meand that the robot took the fastest way. 
    if last_robot==[]: return 0     
    return " ".join(last_robot)
def write_output(output_file, dimensions, maze, shortest_path, robots):
    """
    Escreve os resultados no ficheiro de saída.
    """
    with open(output_file, 'w') as f:
        f.write(f"{dimensions[0]} {dimensions[1]}\n")
        for row in maze:
            f.write(''.join(row) + '\n')
        f.write(shortest_path + '\n')
        f.write(str(robots))






    
    
# test
t1=time.time()
inpp='maze3.txt'
file_name = f'C:\\Users\\marga\\Documents\\BIOMEDDD\\3 ano\\EDA\\projeto\\test-data\\{inpp}'
t2=time.time()
#i = read_entry_v1(file_name)  # Lê o arquivo de entrada
ii=read_entry_v2(file_name)
t3=time.time()
w, h, e, s = find_dimension(ii)  # Calcula as dimensões do labirinto
t4=time.time()
maze, water= define_maze(ii, w, h, e)  # Cria o labirinto
t5=time.time()
# This will print the maze: 
for row in maze:
    print("".join(row))
    
path=solve(maze, w, h, e,water)
t6=time.time()
ours =''.join(path)
robot= robot(ii, w, h, e,maze,path)

print(str(robot))
t7=time.time()

print(ours)  # This will print the directions of the shortest path
#print((solve(maze, w, h, e)))
t9=time.time()


output_file = 'maze3_output.txt'

write_output(output_file, (w, h), maze, ours, robot)

print(f"Saída escrita no ficheiro {output_file}")

t10=time.time()
print('file',str(t2-t1))
print('read',str(t3-t2))
print('find',str(t4-t3))
print('define',str(t5-t4))
print('solve',str(t6-t5))
print('robot',str(t7-t6))
print('all',str(t7-t1))
print('out',str(t10-t9))
#m3='rddddrruuuurrrrddrruurrrrddrruurrrrddrrddrrrrrruuuurrddrruurrrrrrddrruurrddddrrrrrruuuurrrrrrrrrrrrddrruurrddrruurrrrrrrrrrrrrrddllddrrrrrrrruulllluurrrrrrrrrrrrrrddrruurru'
#m2='rrrrrrrddllddddllddrrrruuuurrrruulluurrllddrrddddllddrrddr'
#m1='rddr'
#out='ddrrddrruuuurlddddr'
#if ours!=m1:
 #   print('BURRA')
#else:
 #   print('lalala')