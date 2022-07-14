import rp2
import re
import network
import ubinascii
import machine
import urequests as requests
import time
from secret import secret
import socket

# Set country to avoid possible errors
rp2.country('GB')

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
# If you need to disable powersaving mode
# wlan.config(pm = 0xa11140)

# See the MAC address in the wireless chip OTP
mac = ubinascii.hexlify(network.WLAN().config('mac'),':').decode()
print('mac = ' + mac)


# Other things to query
# print(wlan.config('channel'))
# print(wlan.config('essid'))
# print(wlan.config('txpower'))

# Load login data from different file for safety reasons
ssid = secret['ssid']
pw = secret['pw']

wlan.connect(ssid, pw)

# Wait for connection with 10 second timeout
timeout = 10
while timeout > 0:
    if wlan.status() < 0 or wlan.status() >= 3:
        break
    timeout -= 1
    print('Waiting for connection...')
    time.sleep(1)

def sanitise_request(raw_request):
    raw_request = str(raw_request)
    print(raw_request)
    start_request = raw_request.find('GET') + 3
    end_request   = raw_request.find('HTTP')
    return raw_request[start_request: end_request]

# Define blinking function for onboard LED to indicate error codes    
def blink_onboard_led(num_blinks):
    led = machine.Pin('LED', machine.Pin.OUT)
    for i in range(num_blinks):
        led.on()
        time.sleep(.2)
        led.off()
        time.sleep(.2)
        
def led_function(arg):
    if "on" in arg:
        set_onboard_led(1)
    elif 'off'in arg:
        set_onboard_led(0)
        
        
def temp_function():
    return str(get_temperature())
        
def set_onboard_led(state):
    led = machine.Pin('LED', machine.Pin.OUT)
    if state:
        led.on()
        time.sleep(.2)
        led.off()
        time.sleep(.2)
        led.on()
    else:
        led.off()
        time.sleep(0.2)
        led.on()
        time.sleep(0.2)
        led.off()



wlan_status = wlan.status()
blink_onboard_led(wlan_status)

if wlan_status != 3:
    raise RuntimeError('Wi-Fi connection failed')
else:
    print('Connected')
    status = wlan.ifconfig()
    print('ip = ' + status[0])


# HTTP server with socket
addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
s = socket.socket()
time.sleep(1)
print(addr)

s.bind(addr)

s.listen(1)

def get_file(file_file):
    print('reading {file_file}'.format(file_file=file_file))
    temp = get_temperature()
    with open(file_file, 'r') as file:
        html = file.read()
    return html

def get_temperature():
    sensor_temp = machine.ADC(4)
    conversion_factor = 3.3 / (65535)
    reading = sensor_temp.read_u16() * conversion_factor
    temperature = 27 - (reading - 0.707)/0.001721
    return temperature


print('Listening on', addr)
led = machine.Pin('LED', machine.Pin.OUT)

# Listen for connections
def main():
    while True:
        try:
            cl, addr = s.accept()
            print('Client connected from', addr)
            r = cl.recv(1024)
            url = sanitise_request(r[0:30])
            if '?' in url: 
               url, arg = url.split('?')
               print('args: {}'.format(arg))
            else:
               print('no arguments') 
               arg=''
               
            if 'led' in arg:
                led_function(arg)

            if url.strip() in ['/','index.html']:
               response = get_file('index.html')
               cl.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
               cl.send(response)
            elif url.strip() in ['/graph_frontend.py']:
               response = get_file('/graph_frontend.py')
               cl.send('HTTP/1.0 200 OK\r\nContent-type: text/plain\r\n\r\n')
               cl.send(response) 
            elif url.strip() in ['/temp','/temperature']:
               cl.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
               cl.send(temp_function())
            else:
               print(url)
               cl.send('HTTP/1.0 404 NOT FOUND\r\nContent-type: text/html\r\n\r\n')
               cl.send('"{url}" 404 Not found'.format(url=url))
            cl.close()
        
        except OSError as e:
            cl.close()
            print('Connection closed')
            machine.reset()

print(__name__)
if __name__ == "__main__":
    main()
