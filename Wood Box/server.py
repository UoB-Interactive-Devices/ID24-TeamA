import network
import socket
import time
import machine
import random
import numpy

grid = np.zeros((20, 20, 20))
[0, 0, 0] + box_sizes["l"][0]

#dict for sizes
box_sizes = {
    #first is the dimensions of the box, after that are local positions of each connector
    "b" : [[6, 4, 4], [2, 0, 1], [2, 0, 4], [5, 0, 1], [5, 0, 4]]
    "l" : [[1, 3, 1], [0, 0, 0], [1, 3, 1]]
    "n": [1, 6, 1],
    "h" : [3, 2, 2],
    "s" : [2, 1.7, 1]
    }

#object for boxes, given when first connecting
class BoxNode:
    def __init__(self, box_type, box_id):
            self.box_type = box_type
            self.box_id = box_id
            self.size = box_sizes[box_type]
            
            
def add_box_grid():
    
    
#remove sublist from list
def remove_list_in_list(nested_list, value):
    for sublist in nested_list:
        if value in sublist:
            print("Disconnecting " + str(sublist))
            nested_list.remove(sublist)
            break

#everything happens here
def ap_mode(ssid, password):
    ap = network.WLAN(network.AP_IF)
    ap.config(essid=ssid, password=password)
    ap.active(False)
    time.sleep(1)
    ap.active(True)
    
    while not ap.active():
        pass
    print('AP Mode Is Active, You can Now Connect')

    # Get the IP address of the AP
    ap_ip_address = ap.ifconfig()[0]
    print('IP Address To Connect to:', ap_ip_address)

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', 80))
    s.listen(5)
    
    all_connections = []
    current_connection = []
    temp_connection = 0
    
    boxes = []

    while True:
        #receive message from clients, each comes with type and id after _
        conn, addr = s.accept()
        print('Got a connection from %s' % str(addr))
        request = conn.recv(1024)
        print('Content = %s' % str(request))
        
        #request comes as bytes, decodes into string
        request_type = None
        request_type = str(request)[2]
        decoded_request = request.decode("utf-8")
        
        #find indexes of type and id within message
        index = 0
        indexs = []
        while index < len(decoded_request):
            index = decoded_request.find('_', index)
            if index == -1:
                break
            indexs.append(index)
            index += 1
        box_type = decoded_request[indexs[0]+1]
        box_id = decoded_request[indexs[1]+1]
        
        #initial one side of connection
        temp_connection = [int(s) for s in request.split() if s.isdigit()]    
        
        if request_type == 'p':
            if temp_connection != []:
                #add temp to current connection, makes sure that two boxes are connected to each other
                print("working: " + str(temp_connection))
                current_connection.append([temp_connection, box_type, box_id])
                print(str(current_connection))
                
            if len(current_connection) == 2:
                #when two boxes are connected, add there objects both to all_connections
                print("Connecting " + str(current_connection))
                for i in range(2):
                    for j in range(boxes):
                        if boxes[j].box_type == current_connections[i][1] and boxes[j].box_id == current_connections[i][2]:
                            all_connections.append(boxes[j])
                current_connection = []
                
        elif request_type == 'R':
            #remove connections when disconnecting
            print("removing")
            if len(current_connection) == 0 and temp_connection != []:
                remove_list_in_list(all_connections, temp_connection)  
            elif temp_connection != []:
                current_connection.remove(temp_connection)
            print("all connections: " + str(all_connections))
            
        elif request_type == 'c':
            #for initial connection to server, not when clients connect to each other
            boxes.append(BoxNode(box_type, int(box_id)))
           
        
        # Send the IP address to the client
        conn.send(ap_ip_address.encode())
        conn.close()
            

ap_mode('Angusosaur', '123456789')