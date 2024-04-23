import time
import network
import machine
import socket
#from picozero import Button

pico_name = 'l_1'

def send(message):
    ai = socket.getaddrinfo("192.168.4.1", 80) # Address of Web Server
    addr = ai[0][-1]
    
    s = socket.socket() # Open socket
    s.connect(addr)
    s.send(b""+message+"_"+pico_name)
    ss=str(s.recv(1024)) # Store reply
    s.close()

def connect_to_internet(ssid, password):
    # Pass in string arguments for ssid and password
    
    # Just making our internet connection
    wlan = network.WLAN(network.STA_IF)
    wlan.active(False)
    time.sleep(3)
    wlan.active(True)
    wlan.connect(ssid, password)
    
    # Wait for connect or fail
    max_wait = 10
    while max_wait > 0:
      if wlan.status() < 0 or wlan.status() >= 3:
        break
      max_wait -= 1
      print('waiting for connection...')
      time.sleep(1)
    # Handle connection error
    if wlan.status() != 3:
        #machine.reset()
        raise RuntimeError('Network connection failed')
    else:
        print('Connected')
        # Get and return the IP address
        ip_address = wlan.ifconfig()[0]
        print('IP Address:', ip_address)
        send("connect")
        return ip_address
      
ap_ip_address = connect_to_internet('Angusosaur', '123456789')

    
# Define the pin number where the button is connected
button_pin = machine.Pin(0, machine.Pin.IN, machine.Pin.PULL_UP)
last_state = 0


while True:
    
    # Read the state of the button
    button_state = button_pin.value()
    
    ai = socket.getaddrinfo("192.168.4.1", 80) # Address of Web Server
    addr = ai[0][-1]
            
    # Check if the button is pressed (since it's connected to ground, it's LOW when pressed)
    if button_state == 0:

        # Create a socket and make a HTTP request
        if last_state == 0:
            send("PRESS")
            last_state = 1
    else:
        if last_state == 1:
            send("RECEIVE")
        last_state = 0
            
    
           

    time.sleep(0.05)    # wait
