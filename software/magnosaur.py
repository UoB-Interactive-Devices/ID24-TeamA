import signal
import serial
import socket
import sys
import random
import keyboard
import numpy as np
import cv2
import matplotlib.pyplot as plt
# from mpl_toolkits.mplot3d import Axes3D
from projection import *
import time
import _thread
import asyncio

# Define server IP address and port
SERVER_ADDRESS = ("192.168.137.1", 8080)

BUFFER_SIZE = 4096  # Adjust buffer size as needed
TIMEOUT_SECONDS = 5  # Adjust timeout value as needed

# ser = serial.Serial(port="COM5", parity=serial.PARITY_EVEN, stopbits=serial.STOPBITS_ONE)
# ser.flush()

all_connections = []
current_connection = []
current_remove = []
nodes = []
    
#dict for sizes
box_sizes = {
    #first is the dimensions of the box, after that are local positions of each connector
    "b" : [5, 3, 2],
    "l" : [0, 2, 0],
    "n" : [0, 3, 0],
    "h" : [2, 1, 2]
    }

box_connections = {
    #first is the dimensions of the box, after that are local positions of each connector
    "b" : {
        "bottom" : {'1':[1, 0, 0], '2':[4, 0, 0], '3':[1, 0, 2], '4':[4, 0, 2]},
        "top" : {'1' :[1, 3, 1], '2':[3, 3, 1], '3':[5, 3, 1]},
        "front" : {'1':[5, 3, 1]},
        "back" : {'1':[0, 2, 1]}
        },
    "l" : {
        "top" : {'1':[0,2,0]},
        "bottom": {'1':[0, 0, 0]}
        },
    "n": {
        "top" : {'1':[0, 3, 0]},
        "bottom" : {'1':[0,0,0]}
        },
    "h" : {
        "back" : {'1':[0,1,1]},
        "bottom" : {'1':[0,0,1]}
        }
    }

# Function to detect request
def detector(request):
    try:
        if request.decode()[0] == 'x':
            print(request[1:].decode())
            return request.decode()
    except:
        pass

# Function to handle incoming HTTP requests
async def handle_request(client_sock):
    global all_connections
    global current_connection
    global current_remove
    global nodes
    repeat = False
    try:
        client_sock.settimeout(TIMEOUT_SECONDS)
        while True:
            request = await loop.sock_recv(client_sock, BUFFER_SIZE)
            print(request)
            if not request:
                break
            response = detector(request)
            print(response)
            split_response = response.split("/")
            print('split:', split_response)

            # Respond with a simple "OK" message            
            if response[1] == 'C':
                name = split_response[1]
                print("Connected to: " + name)
            elif response[1] == 'P':
                print('pressed')
                for x in current_connection:
                    if x[0] == split_response[1] and x[1] == split_response[2]:
                        repeat = True

                if repeat:
                    repeat = False
                else:
                    current_connection.append([split_response[1], split_response[2], split_response[3]])
                print(current_connection)
                print("length:", len(current_connection))

                    
                if len(current_connection) == 2:
                    print("thats enough connections!!!")
                    print('current:', current_connection)
                    #new_node = add_box(['l', 1, 'top.1'], ['l', 2, 'bottom.1'])
                    
                    #when two boxes are connected, add there objects both to all_connections
                    #print("Connecting " + str(current_connection))
                    
                    existing, new = find_existing_and_new(all_connections, current_connection)
                    print("existing:", existing)
                    print("new:", new)
                    all_connections.append(new[:2])
                    
                    print(all_connections, current_connection)
                    
                    add_box(existing, new)
                    current_connection = []

                    return

            elif response[1] == 'R':
                for x in current_remove:
                    if x[0] == split_response[1] and x[1] == split_response[2]:
                        repeat = True

                if repeat:
                    repeat = False
                else:
                    current_remove.append([split_response[1], split_response[2], split_response[3]])
                print(current_remove)
                print("remove queue length:", len(current_remove))
                
                if len(current_remove) == 2:
                    for i in reversed(range(len(all_connections))):
                        for j in range(len(current_remove)):
                            if all_connections[i][0] == split_response[1] and all_connections[i][1] ==  split_response[2]:
                                for node in nodes:
                                    if node.box_type == split_response[1] and node.box_id == split_response[2]:
                                        remove([node.box_type, node.box_id])
                                break
                current_remove = []
                return

            elif response[1] == 'H':
                await loop.sock_sendall(client_sock, b"badum")

    except socket.timeout:
        print("Connection timed out")
    except Exception as e:
        print("An error occurred:", e)
    finally:
        client_sock.close()

def add_box_grid(coord_1, coord_2, type):
    coord_1 = np.round(coord_1).astype(int)
    coord_2 = np.round(coord_2).astype(int)
    x1 = coord_1[0]
    y1 = coord_1[1]
    z1 = coord_1[2]

    x2 = coord_2[0]
    y2 = coord_2[1]
    z2 = coord_2[2]

    grid[x1][y1][z1] = 1
    grid[x2][y2][z2] = 1

    if type == 'h':
        countx=0
        county=0
        for x in range(min(x1, x2), max(x1, x2) + 1):
            countx += 1
            for y in range(min(y1, y2), max(y1, y2) + 1):
                county += 1
                for z in range(min(z1, z2), max(z1, z2) + 1):
                    if countx == 3 and county == 6:
                        grid[x][y][z] = 0
                    else:
                        grid[x][y][z] = 1
                    
    else:
        # Fill the rectangle
        for x in range(min(x1, x2), max(x1, x2) + 1):
            for y in range(min(y1, y2), max(y1, y2) + 1):
                for z in range(min(z1, z2), max(z1, z2) + 1):
                    grid[x][y][z] = 1
    update_projection(grid)
    
def remove(params):
    for node in nodes:
        if node.box_type == params[0] and node.box_id == params[1]:
            removeable = node

    coord_1 = removeable.location[0]
    coord_2 = removeable.location[1]


    coord_1 = np.round(coord_1).astype(int)
    coord_2 = np.round(coord_2).astype(int)
    x1 = coord_1[0]
    y1 = coord_1[1]
    z1 = coord_1[2]

    x2 = coord_2[0]
    y2 = coord_2[1]
    z2 = coord_2[2]

    grid[x1][y1][z1] = 0
    grid[x2][y2][z2] = 0

    for x in range(min(x1, x2), max(x1, x2) + 1):
        for y in range(min(y1, y2), max(y1, y2) + 1):
            for z in range(min(z1, z2), max(z1, z2) + 1):
                grid[x][y][z] = 0

    update_projection(grid)


def print_grid(grid):          
    # Print the grid to visualize the rectangle
    for y in range(20):
        print("y =", y)
        for x in range(20):
            print(" ".join(map(str, grid[x][y])))
        print()	

def visualize_grid(grid):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    for i in range(grid.shape[0]):
        for j in range(grid.shape[1]):
            for k in range(grid.shape[2]):
                if grid[i][j][k] == 1:
                    ax.bar3d(i, k, j, 1, 1, 1, color='b')

    ax.set_xlabel('X')
    ax.set_ylabel('Z')
    ax.set_zlabel('Y')
    ax.set_xlim(0, grid.shape[0])
    ax.set_ylim(0, grid.shape[2])
    ax.set_zlim(0, grid.shape[1])
    plt.show()

#0 for x, 1 for y, 2 for z
def find_opposite_coordinate(box, coord, axis):
    opposite_coord = coord.copy()
    opposite_coord[axis] = box[1][axis] if coord[axis] == box[0][axis] else box[0][axis]
    return opposite_coord

def rotate_point_around_axis(point, axis, angle):
    # Convert angle from degrees to radians
    angle = np.radians(angle)

    # Normalize the axis
    axis = axis / np.linalg.norm(axis)

    # Create the rotation matrix
    c = np.cos(angle)
    s = np.sin(angle)
    t = 1 - c
    x, y, z = axis
    rotation_matrix = np.array([[t*x*x + c,    t*x*y - z*s,  t*x*z + y*s],
                                [t*x*y + z*s,  t*y*y + c,    t*y*z - x*s],
                                [t*x*z - y*s,  t*y*z + x*s,  t*z*z + c]])

    # Apply the rotation
    rotated_point = np.dot(rotation_matrix, point)

    return np.round(rotated_point).astype(int)

#object for boxes, given when first connecting
class BoxNode:
    def __init__(self, box_type, box_id):
        self.box_type = box_type
        self.box_id = box_id
        self.size = box_sizes[box_type]
        self.location = np.array([[0, 0, 0], self.size])
        self.connections = box_connections[box_type]
        self.inStructure = False
        #where the orientation is the face that is facing down
        self.orientation = 'bottom'
    
    #where origin is the bottom right closest voxel, with the dinosaur facing right
    def update_connections(self, origin):
        for x in self.connections:
            connection = self.connections[x]
            for i in range(3):
                connection[i] = origin[i] + connection[i]
        return

    def translate(self, translation_vector):
        for i in range(len(self.location)):
             self.location[i] += translation_vector

    def rotate(self, axis, angle):
        rotation_matrix = self.rotation_matrix(axis, angle)
        self.location = np.dot(rotation_matrix, self.location.T).T

    def rotate_to_match(self, box2, face1, face2, new_con, existing_con):

        existing_con += box2.location[0]
        new_con += self.location[0]     

        if face1 == "top" and face2 == "bottom":
            translation = existing_con - new_con - [0, 1, 0]
            self.translate(translation)

        elif face1 == "bottom" and face2 == "top":
            translation = existing_con - new_con + [0, 1, 0]
            self.translate(translation)

        elif face1 == "top" and face2 == "top":
            new_con = find_opposite_coordinate(self.location, new_con, 1)
            translation = existing_con - new_con + [0, 1, 0]
            self.translate(translation)
            self.orientation = 'top'
            
        elif face1 == "bottom" and face2 == "bottom":
            new_con = find_opposite_coordinate(self.location, new_con, 1)
            translation = existing_con - new_con - [0, 1, 0]
            self.translate(translation)
            self.orientation = 'top'

        elif face1 == "front" and face2 == "back":
            translation = existing_con - new_con - [1, 0, 0]
            self.translate(translation)

        elif face1 == "back" and face2 == "front":
            translation = existing_con - new_con + [1, 0, 0]
            self.translate(translation)
        
        elif face1 == "front" and face2 == "front":
            new_con = find_opposite_coordinate(self.location, new_con, 0)
            translation = existing_con - new_con + [1, 0, 0]
            self.translate(translation)
            self.orientation = 'bottom_fbflip'
        
        elif face1 == "back" and face2 == "back":
            new_con = find_opposite_coordinate(self.location, new_con, 0)
            translation = existing_con - new_con - [1, 0, 0]
            self.translate(translation)
            self.orientation = 'bottom_fbflip'

        elif face1 == "back" and face2 == "top":
            self.rotate([0, 0, 1], 90)
            new_con = rotate_point_around_axis(new_con, [0, 0, 1], 90)
            translation = existing_con - new_con + [0, 1, 0]
            self.translate(translation)
            self.orientation = 'back'

        elif face1 == "back" and face2 == "bottom":
            self.rotate([0, 0, 1], -90)
            new_con = rotate_point_around_axis(new_con, [0, 0, 1], -90)
            translation = existing_con - new_con - [0, 1, 0]
            self.translate(translation)
            self.orientation = 'front'

        elif face1 == "front" and face2 == "top":
            new_con = find_opposite_coordinate(self.location, new_con, 0)
            self.rotate([0, 0, 1], 90)
            new_con = rotate_point_around_axis(new_con, [0, 0, 1], 90)
            translation = existing_con - new_con + [0, 1, 0]
            self.translate(translation)
            self.orientation = 'front'

        elif face1 == "front" and face2 == "bottom":
            new_con = find_opposite_coordinate(self.location, new_con, 0)
            self.rotate([0, 0, 1], -90)
            new_con = rotate_point_around_axis(new_con, [0, 0, 1], -90)
            translation = existing_con - new_con - [0, 1, 0]
            self.translate(translation)
            self.orientation = 'back'

        elif face1 == "top" and face2 == "front":
            self.rotate([0, 0, 1], 90)
            new_con = rotate_point_around_axis(new_con, [0, 0, 1], 90)
            translation = existing_con - new_con + [1, 0, 0]
            self.translate(translation)
            self.orientation = 'back'

        elif face1 == "top" and face2 == "back":
            new_con = find_opposite_coordinate(self.location, new_con, 1)
            self.rotate([0, 0, 1], 90)
            new_con = rotate_point_around_axis(new_con, [0, 0, 1], 90)
            translation = existing_con - new_con - [1, 0, 0]
            self.translate(translation)
            self.orientation = 'top'

        elif face1 == "bottom" and face2 == "front":
            new_con = find_opposite_coordinate(self.location, new_con, 1)
            self.rotate([0, 0, 1], 90)
            new_con = rotate_point_around_axis(new_con, [0, 0, 1], 90)
            translation = existing_con - new_con + [1, 0, 0]
            self.translate(translation)
            self.orientation = 'front'

        elif face1 == "bottom" and face2 == "back":
            self.rotate([0, 0, 1], 90)
            new_con = rotate_point_around_axis(new_con, [0, 0, 1], 90)
            translation = existing_con - new_con - [1, 0, 0]
            self.translate(translation)
            self.orientation = 'back'

        else:
            raise ValueError("Invalid faces provided")
        
        self.inStructure = True


    def rotation_matrix(self, axis, angle):

        angle = np.radians(angle)
        axis = np.asarray(axis)
        axis = axis / np.sqrt(np.dot(axis, axis))
        a = np.cos(angle / 2.0)
        b, c, d = -axis * np.sin(angle / 2.0)
        aa, bb, cc, dd = a * a, b * b, c * c, d * d
        bc, ad, ac, ab, bd, cd = b * c, a * d, a * c, a * b, b * d, c * d
        return np.array([[aa + bb - cc - dd, 2 * (bc + ad), 2 * (bd - ac)],
                         [2 * (bc - ad), aa + cc - bb - dd, 2 * (cd + ab)],
                         [2 * (bd + ac), 2 * (cd - ab), aa + dd - bb - cc]])



grid = np.zeros((24, 13, 12))

start_projection()

node_names = ["l", "b", "n", "h"]
node_no = [4, 1, 2, 1]

for i in range(len(node_names)):
    name = node_names[i]
    x = node_no[i]
    for j in range(x):
        nodes.append(BoxNode(name, str(j+1)))
        if name == 'l' and j+1 == 2:
            leg = nodes[len(nodes)-1]
            all_connections.append([leg.box_type, leg.box_id])

source = [7, 0, 1]
leg.location = np.array([[0, 0, 0], [0, 2, 0]])
leg.location += source
leg.inStructure = True
add_box_grid(leg.location[0], leg.location[1], 'l')

#visualize_grid(grid)

def find_existing_and_new(all_connections, connections):
    print(all_connections, connections)
    for new_node in connections:
        for existing_node in all_connections:
            if new_node[1] == existing_node[1] and new_node[0] == existing_node[0]:
                for c in connections:
                    if c[0] == existing_node[0] and c[1] == existing_node[1]:
                        print(c)
                        existing_id = c
                break
        else:
            continue
        break
    # Find the new ID
    for new_node in connections:
        if new_node[1] != existing_id[1] or new_node[0] != existing_id[0]:
            new_id = new_node
            break
    print('found existing')
    return existing_id, new_id

def find_slash(string):
    index = string.find('.')
    if index != -1:
        first_part = string[:index]
        second_part = string[index+1:]
        return first_part, second_part
    else:
        return None, None

def add_box(existing, new):
    print(existing, new)
    for node in nodes:
        if node.box_type == existing[0] and node.box_id == existing[1]:
            existing_node = node
        if node.box_type == new[0] and node.box_id == new[1]:
            new_node = node
    
    print(new_node.location, existing_node.location)

    #connection in format string "bottom.1" or "top.2"
    existing_con = find_slash(existing[2])
    new_con = find_slash(new[2])

    conn_point1 = box_connections[new_node.box_type]
    conn_point1 = conn_point1[new_con[0]]
    conn_point1 = conn_point1[new_con[1]]

    conn_point2 = box_connections[existing_node.box_type]
    conn_point2 = conn_point2[existing_con[0]]
    conn_point2 = conn_point2[existing_con[1]]
    
    if existing_node.orientation == 'bottom':
        existing_con = existing_con

    elif existing_node.orientation == 'bottom_fbflip':
        if new_con == 'front':
            new_con = 'back'
        elif new_con == 'back':
            new_con = 'front'

    elif existing_node.orientation == 'front':
        if existing_con == 'bottom':
            existing_con = 'back'
        elif existing_con == 'top':
            existing_con = 'front'
        elif existing_con == 'back':
            existing_con = 'top'
        elif existing_con == 'front':
            existing_con = 'bottom'

    elif existing_node.orientation == 'back':
        if existing_con == 'bottom':
            existing_con = 'front'
        elif existing_con == 'top':
            existing_con = 'back'
        elif existing_con == 'back':
            existing_con = 'bottom'
        elif existing_con == 'front':
            existing_con = 'top'
    
    elif existing_node.orientation == 'top':
        if existing_con == 'bottom':
            existing_con = 'top'
        elif existing_con == 'top':
            existing_con = 'bottom'
        elif existing_con == 'back':
            existing_con = 'back'
        elif existing_con == 'front':
            existing_con = 'front'
    
    if new_node.orientation == 'bottom':
        new_con = new_con
    
    elif new_node.orientation == 'bottom_fbflip':
        if new_con == 'front':
            new_con = 'back'
        elif new_con == 'back':
            new_con = 'front'

    elif new_node.orientation == 'front':
        if new_con == 'bottom':
            new_con = 'back'
        elif new_con == 'top':
            new_con = 'front'
        elif new_con == 'back':
            new_con = 'top'
        elif new_con == 'front':
            new_con = 'bottom'

    elif new_node.orientation == 'back':
        if new_con == 'bottom':
            new_con = 'front'
        elif new_con == 'top':
            new_con = 'back'
        elif new_con == 'back':
            new_con = 'bottom'
        elif new_con == 'front':
            new_con = 'top'
    
    elif new_node.orientation == 'top':
        if new_con == 'bottom':
            new_con = 'top'
        elif new_con == 'top':
            new_con = 'bottom'
        elif new_con == 'back':
            new_con = 'back'
        elif new_con == 'front':
            new_con = 'front'
        
    print(new_con[0], existing_con[0], conn_point1, conn_point2)
    new_node.rotate_to_match(existing_node, new_con[0], existing_con[0], conn_point1, conn_point2)
    add_box_grid(new_node.location[0], new_node.location[1], new_node.box_type)

def is_complete(connections):
    head_count = 0
    body_count = 0
    neck_count = 0
    leg_count = 0
    for connection in connections:
        if connection.box_type == 'l':
            leg_count += 1
        elif connection.box_type == 'n':
            neck_count += 1
        elif connection.box_type == 'b':
            body_count += 1
        elif connection.box_type == 'h':
            head_count += 1

    if leg_count == 4 and neck_count == 1 and body_count == 1 and head_count == 1:
        return 'steg'
    elif leg_count == 4 and neck_count == 2 and body_count == 1 and head_count == 1:
        return 'diplo'
    return 'nah'

# Main function
async def main():
    # #first array is information about an existing box, first coord is existingconnection, second coord is new
    # time.sleep(1)
    # new_node = add_box(['l', 1, 'top/1'], ['b', 1, 'bottom/1'])
    # time.sleep(1)
    # new_node = add_box(['b', 1, 'bottom/2'], ['l', 2, 'top/1'])
    # new_node = add_box(['b', 1, 'bottom/3'], ['l', 3, 'top/1'])
    # new_node = add_box(['b', 1, 'bottom/4'], ['l', 4, 'top/1'])

    # new_node = add_box(['b', 1, 'back/1'], ['n', 1, 'top/1'])
    # time.sleep(1)
    # new_node = add_box(['b', 1, 'front/1'], ['h', 1, 'back/1'])

    # time.sleep(1)
    # remove(['b', 1])

    # time.sleep(1)
    # remove(['n', 1])

    # time.sleep(1)
    # remove(['h', 1])

    # time.sleep(1)
    # remove(['l', 2])
    # remove(['l', 3])
    # remove(['l', 4])

    # Create a TCP/IP socket
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.bind(SERVER_ADDRESS)
    server_sock.listen()

    print("Server is listening on", SERVER_ADDRESS)
    while True:
        # dino = is_complete(all_connections)
        # if dino == 'steg':
        #     print("steg")
        # elif dino == 'diplo':
        #     print("diplo")
        client_sock, addr = await loop.sock_accept(server_sock)
        print("Connection from:", addr)
        asyncio.create_task(handle_request(client_sock))


# Create event loop and run the server
loop = asyncio.get_event_loop()
loop.run_until_complete(main())

#print_grid(grid)
#visualize_grid(grid)
# input()

#while True:

#     #s.write("data\r".encode())
#     mes = ser.read_until().strip()
#     request = mes.decode()
#     print(request)

#     #request comes as bytes, decodes into string
#     request_type = None
#     request_type = request[3]

#     if request[2] == 'x':
#         #find indexes of type and id within message
#         index = 0
#         indexes = []
#         while index < len(request):
#             index = request.find('_', index)
#             if index == -1:
#                 break
#             indexes.append(index)
#             index += 1

#         box_type = request[indexs[0]+1]
#         box_id = request[indexs[1]+1]
#         box_con = request[indexs[2]+1]
#         print(box_type, box_id, box_con, request_type)
        
#         #initial one side of connection
#         #temp_connection = [int(s) for s in request.split() if s.isdigit()]    

#         repeat = False
#         all_repeat = False
        
#         if request_type == 'P':

#             #if temp_connection != []:
#                 #add temp to current connection, makes sure that two boxes are connected to each other
#                 #print("working: " + str(temp_connection))

#             for x in current_connection:
#                 if x[0] == box_type and x[1] == box_id:
#                     repeat = True

#             if repeat:
#                 repeat = False
#             else:
#                 current_connection.append([box_type, box_id, box_con])
#             print(current_connection)
#             print("length:", len(current_connection))

                
#             if len(current_connection) == 2:
#                 print("thats enough connections!!!")
                
#                 #when two boxes are connected, add there objects both to all_connections
#                 #print("Connecting " + str(current_connection))
                
#                 existing, new = find_existing_and_new(all_connections, current_connection)
#                 print("existing:", existing_node)
#                 print("new:", existing_node)
#                 print(all_connections, current_connection)

#                 add_box(existing, new)
#                 current_connection = []


                
#         elif request_type == 'R':
#             #remove connections when disconnecting
#             print("Removing")

#             if len(current_connection) == 0 and temp_connection != []:
#                 remove_list_in_list(all_connections, temp_connection)  
#             elif temp_connection != []:
#                 current_connection.remove(temp_connection)
#             print("all connections: " + str(all_connections))
            
#         elif request_type == 'c':
#             #for initial connection to server, not when clients connect to each other
#             #add_box_grid([1, 2, 1], box_sizes["b"][0], 'bottom')
#             continue

    
