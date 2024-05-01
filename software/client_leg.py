import time
import network
import machine
import usocket as socket
#from picozero import Button

pico_name = 'l/2'

led = machine.Pin("LED", machine.Pin.OUT)
led.on()

wifi = network.WLAN(network.STA_IF)

# Define the pin number where the button is connected
button_pin = machine.Pin(0, machine.Pin.IN, machine.Pin.PULL_UP)
button_pin2 = machine.Pin(4, machine.Pin.IN, machine.Pin.PULL_UP)

last_state = 0
last_state2 = 0


# Define server IP address and port
SERVER_ADDRESS = ("192.168.137.1", 8080)
retry_limit = 8

heartbeat_timeout = 10 # In seconds
heartbeat_counter = heartbeat_timeout * 100
start_time = time.time() 
        
def send_interaction(interaction, face, retry_limit=8):
    global start_time
    try:
        # Create a TCP/IP socket
        client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_sock.settimeout(3)
        client_sock.connect(SERVER_ADDRESS)
        # Send a simple HTTP GET request
        client_sock.sendall(b"" + interaction + "/"
                            + pico_name + "/" + face)
        # Wait for the server response (optional)
        response = client_sock.recv(1024)
        print("Received server response:", response)
        client_sock.close()
        start_time = time.time()
        return True  # Interaction successful
    except OSError as e:
        print("Error sending interaction:", e)
        if interaction == "xHEARTBEAT" or retry_limit <= 0:
            machine.reset()
        else:
            print("Retrying...")
            return send_interaction(interaction, face, retry_limit - 1)
    except Exception as e:
        print("An unexpected error occurred:", e)
        return False  # Interaction failed

def connect_to_internet(ssid, password):
    # Just making our internet connection
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    
    while True:
        # Wait for connect or fail
        max_wait = 20
        while max_wait > 0:
            if wlan.isconnected():
                return wlan.ifconfig()[0]
            max_wait -= 1
            print('Waiting for connection...')
            time.sleep(0.25)
            led.off()
            time.sleep(0.25)
            led.on()
        # Handle connection error
        raise RuntimeError('Network connection failed')

# Connect to the internet
try:
    ap_ip_address = connect_to_internet('Angusosaur', '123456789')
    print('Connected to Wi-Fi:', ap_ip_address)
except Exception as e:
    print("Failed to connect to Wi-Fi:", e)
    machine.reset()

while True:
    # Read the state of the button
    button_state = button_pin.value()
    button_state2 = button_pin2.value()
            
    # Check if the button is pressed (since it's connected to ground, it's LOW when pressed)
    if button_state == 0:
        # Create a socket and make a HTTP request
        if last_state == 0:
            send_interaction("xPRESS", 'top.1')
            print("PRESS")
            last_state = 1
    else:
        if last_state == 1:
            send_interaction("xRELEASE", 'top.1')
            print("RELEASE")
        last_state = 0
        
    # Check if the button is pressed (since it's connected to ground, it's LOW when pressed)
    if button_state2 == 0:
        # Create a socket and make a HTTP request
        if last_state2 == 0:
            send_interaction("xPRESS", 'bottom.1')
            print("PRESS")
            last_state2 = 1
    else:
        if last_state2 == 1:
            send_interaction("xRELEASE", 'bottom.1')
            print("RELEASE")
        last_state2 = 0
        
        
    if time.time() - start_time >= heartbeat_timeout:
        print("Babum")
        send_interaction("xHEARTBEAT", 'h')
        
    #heartbeat_counter -= 1
    #if heartbeat_counter <= 0:
    #    heartbeat_counter = heartbeat_timeout * 100
    #    send_heartbeat()
            
    time.sleep(0.01)    # wait
