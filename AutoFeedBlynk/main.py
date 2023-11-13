# Import required modules
import network
from machine import Pin
import BlynkLib
from servo import Servo
import time
import network
import usocket as socket
import config
def init_wifi():
    def change_wifi():
        # Create an access point (AP) for configuration
        ap = network.WLAN(network.AP_IF)
        ap.active(True)

        def serve_config_page():
            html = """<!DOCTYPE html>
            <html>
            <head>
                <title>ESP32 Wi-Fi Configuration</title>
            </head>
            <body>
                <h1>Configure Wi-Fi</h1>
                <form method="post" action="/connect">
                    <label for="ssid">SSID:</label>
                    <input type="text" id="ssid" name="ssid" required><br>
                    <label for="password">Password:</label>
                    <input type="password" id="password" name="password" required><br>
                    <input type="submit" value="Connect">
                </form>
            </body>
            </html>
            """
            client.send(html)

        # Start the AP and serve the configuration page
        ap.config(essid="ESP32_Config_2", password="12345678")
        ap.active(True)
        ap.ifconfig(('192.168.4.1', '255.255.255.0', '192.168.4.1', '192.168.4.1'))

        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(('0.0.0.0', 80))
        server.listen(5)

        while True:
            try:
                print("Waiting for connection...")
                client, addr = server.accept()
                print("Client connected from:", addr)

                request = client.recv(1024).decode('utf-8')
                if sta_if.isconnected():
                    break
                elif 'GET /' in request:
                    serve_config_page()
                elif 'POST /connect' in request:
                    print(request)
                    data = request.split('\r\n\r\n', 1)[1]
                    ssid, password = [line.split('=')[1] for line in data.split('&')]
                    # Connect to the specified Wi-Fi network
                    sta_if.connect(ssid, password)
                    if sta_if.isconnected():
                        with open('config.py', 'w') as file:
                            file.write(f'SSID="{ssid}"\n')
                            file.write(f'PASS="{password}"')
                        print(f"Connected to {ssid}...")
                        break
                    
                client.close()

            except Exception as e:
                print("Error:", str(e))
        server.close()

    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)

    try:
        sta_if.connect(config.SSID, config.PASS)
        time.sleep(1)
        print(f"Connected to {config.SSID}")
    except Exception as e:
        print(f"Cannot connect to {config.SSID}")
        change_wifi()

init_wifi()

# Connect to Blynk server
auth_token = "v0JetrHzS3vPh3HQK1vmsqiKjU1WmEYB"

blynk = BlynkLib.Blynk(auth_token)

# Define pin numbers
led_pin = 2

# Initialize LED pin
led = Pin(led_pin, Pin.OUT)

servo = Servo(13)
servo.move(45)

old_value = 0

# Define Blynk virtual pin handlers
@blynk.on("V0")
def v0_handler(value):
    if int(value[0]) == 1:
        led.value(1)
        servo.move(120)
        servo.move(45)
        time_tuple = time.localtime()
        st = "{:04}-{:02}-{:02} {:02}:{:02}:{:02}.{:03}".format(*time_tuple)
        blynk.virtual_write(1,st)	
    else:
        led.value(0)

# Start Blynk loop
while True:
    try:
        blynk.run()
    except Exception as e:
        init_wifi()
