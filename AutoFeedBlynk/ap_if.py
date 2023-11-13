import network
import usocket as socket

# Set your default SSID and password
default_ssid = "YourDefaultSSID"
default_password = "YourDefaultPassword"

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
        if 'GET /' in request:
            serve_config_page()
        elif 'POST /connect' in request:
            print(request)
            data = request.split('\r\n\r\n', 1)[1]
            ssid, password = [line.split('=')[1] for line in data.split('&')]
            # Connect to the specified Wi-Fi network
            sta = network.WLAN(network.STA_IF)
            sta.active(True)
            sta.connect(ssid, password)
            if sta.isconnected():
                print(f"Connected to {ssid}...")
                break
            

        client.close()

    except Exception as e:
        print("Error:", str(e))
server.close()