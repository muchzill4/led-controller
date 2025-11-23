from machine import Pin
import network
import time
from umqtt.simple import MQTTClient
import neopixel
import socket
import config

# Predefined color palette
COLORS = {
    'red': (255, 0, 0),
    'green': (0, 255, 0),
    'blue': (0, 0, 255),
    'white': (255, 255, 255),
    'warm_white': (255, 147, 41),
    'yellow': (255, 255, 0),
    'cyan': (0, 255, 255),
    'magenta': (255, 0, 255),
    'orange': (255, 165, 0),
    'purple': (128, 0, 128),
    'pink': (255, 192, 203),
    'lime': (50, 205, 50),
    'off': (0, 0, 0)
}

class LEDController:
    def __init__(self, pin, num_leds):
        self.strip = neopixel.NeoPixel(Pin(pin), num_leds)
        self.num_leds = num_leds
        self.brightness = 100
        self.color = COLORS['white']
        self.is_on = False

    def apply_brightness(self, color, brightness):
        """Apply brightness percentage to RGB color"""
        r, g, b = color
        factor = brightness / 100.0
        return (int(r * factor), int(g * factor), int(b * factor))

    def update_strip(self):
        """Update all LEDs in the strip with current state"""
        if self.is_on:
            rgb = self.apply_brightness(self.color, self.brightness)
        else:
            rgb = (0, 0, 0)

        for i in range(self.num_leds):
            self.strip[i] = rgb
        self.strip.write()

    def turn_on(self):
        """Turn on LEDs"""
        self.is_on = True
        self.update_strip()

    def turn_off(self):
        """Turn off LEDs"""
        self.is_on = False
        self.update_strip()

    def set_brightness(self, value):
        """Set brightness (0-100)"""
        if 0 <= value <= 100:
            self.brightness = value
            if self.is_on:
                self.update_strip()
            return True
        return False

    def set_color(self, color):
        """Set color (RGB tuple)"""
        self.color = color
        self.is_on = True
        self.update_strip()

    def set_color_by_name(self, name):
        """Set color by predefined name"""
        if name in COLORS:
            self.set_color(COLORS[name])
            return True
        return False

    def get_state(self):
        """Get current state as string"""
        return f"Color: {self.color}, Brightness: {self.brightness}%, On: {self.is_on}"

# WiFi connection
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    if not wlan.isconnected():
        print('Connecting to WiFi...')
        wlan.connect(config.WIFI_SSID, config.WIFI_PASSWORD)

        timeout = 0
        while not wlan.isconnected() and timeout < 30:
            time.sleep(1)
            timeout += 1
            print('.', end='')

        if not wlan.isconnected():
            print('\nFailed to connect to WiFi')
            return False

    print('\nWiFi connected!')
    print('Network config:', wlan.ifconfig())
    return True

# Create MQTT callback for LED controller
def create_mqtt_callback(led_controller):
    """Factory function to create MQTT callback with LED controller instance"""
    def mqtt_callback(topic, msg):
        print(f'Received: {msg}')

        try:
            message = msg.decode('utf-8').strip()
            command = message.lower()

            # Simple on/off commands
            if command == 'on':
                led_controller.turn_on()
                print(f'LEDs turned ON - {led_controller.get_state()}')

            elif command == 'off':
                led_controller.turn_off()
                print('LEDs turned OFF')

            # Brightness control: brightness:50
            elif command.startswith('brightness:'):
                value = int(command.split(':')[1])
                if led_controller.set_brightness(value):
                    print(f'Brightness set to {led_controller.brightness}%')
                else:
                    print('Brightness must be 0-100')

            # Predefined color: color:red
            elif command.startswith('color:'):
                color_name = command.split(':')[1]
                if led_controller.set_color_by_name(color_name):
                    print(f'Color set to {color_name}: {led_controller.color}')
                else:
                    print(f'Unknown color: {color_name}')
                    print(f'Available: {", ".join(COLORS.keys())}')

            # Custom RGB: rgb:255,128,0
            elif command.startswith('rgb:'):
                rgb_str = command.split(':')[1]
                r, g, b = map(int, rgb_str.split(','))
                if all(0 <= x <= 255 for x in [r, g, b]):
                    led_controller.set_color((r, g, b))
                    print(f'Custom color set: RGB{led_controller.color}')
                else:
                    print('RGB values must be 0-255')

            # List available colors
            elif command == 'list' or command == 'colors':
                print('Available colors:')
                for name, rgb in COLORS.items():
                    print(f'  {name}: RGB{rgb}')

            # Get current state
            elif command == 'state' or command == 'status':
                print(led_controller.get_state())

            else:
                print(f'Unknown command: {message}')
                print('Commands: on, off, brightness:0-100, color:name, rgb:r,g,b, list, state')

        except Exception as e:
            print(f'Error processing message: {e}')

    return mqtt_callback

# Connect to MQTT broker
def connect_mqtt(callback):
    """Connect to MQTT broker with provided callback"""
    try:
        client = MQTTClient(
            client_id=config.MQTT_CLIENT_ID,
            server=config.MQTT_BROKER,
            port=config.MQTT_PORT,
            user=config.MQTT_USER,
            password=config.MQTT_PASSWORD
        )

        client.set_callback(callback)
        client.connect()
        client.subscribe(config.MQTT_TOPIC)

        print(f'Connected to MQTT broker at {config.MQTT_BROKER}')
        print(f'Subscribed to topic: {config.MQTT_TOPIC}')

        return client
    except Exception as e:
        print(f'Failed to connect to MQTT broker: {e}')
        return None

# Web server functions
def get_basic_html():
    """Return basic HTML page for testing web server"""
    html = """<!DOCTYPE html>
<html>
<head>
    <title>ESP32 LED Controller</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
</head>
<body>
    <h1>ESP32 LED Controller</h1>
    <p>Web server is running!</p>
    <p>LED control interface coming soon...</p>
</body>
</html>"""
    return html

def start_web_server(port=80):
    """Start HTTP server on specified port"""
    try:
        addr = socket.getaddrinfo('0.0.0.0', port)[0][-1]
        s = socket.socket()
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(addr)
        s.listen(1)
        s.setblocking(False)
        print(f'Web server started on port {port}')
        return s
    except Exception as e:
        print(f'Failed to start web server: {e}')
        return None

def handle_web_request(server_socket):
    """Handle incoming web requests (non-blocking)"""
    try:
        conn, addr = server_socket.accept()
        conn.setblocking(False)
        try:
            request = conn.recv(1024).decode('utf-8')

            # Simple GET request handling
            if request.startswith('GET'):
                html = get_basic_html()
                response = f'HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nConnection: close\r\n\r\n{html}'
                conn.send(response.encode('utf-8'))

            conn.close()
        except:
            conn.close()
    except OSError:
        # No connection available (non-blocking)
        pass
    except Exception as e:
        print(f'Error handling web request: {e}')

# Main program
def main():
    print('Starting ESP32 WS2812 LED Controller')
    print('=' * 40)

    # Initialize LED controller
    led_controller = LEDController(config.LED_PIN, config.NUM_LEDS)
    print(f'Initialized {config.NUM_LEDS} LEDs on pin {config.LED_PIN}')

    # Connect to WiFi
    if not connect_wifi():
        print('Cannot proceed without WiFi connection')
        return

    # Create MQTT callback with LED controller
    callback = create_mqtt_callback(led_controller)

    # Connect to MQTT broker
    client = connect_mqtt(callback)
    if not client:
        print('Cannot proceed without MQTT connection')
        return

    # Start web server
    web_server = start_web_server()
    if not web_server:
        print('Warning: Web server failed to start')

    print('System ready!')
    print(f'MQTT Topic: {config.MQTT_TOPIC}')
    print('MQTT Commands: on, off, brightness:0-100, color:name, rgb:r,g,b, list')
    if web_server:
        print('Web interface: http://<ESP32_IP>/')
    print('=' * 40)

    # Main loop
    try:
        while True:
            client.check_msg()
            if web_server:
                handle_web_request(web_server)
            time.sleep(0.01)
    except KeyboardInterrupt:
        print('\nShutting down...')
        led_controller.turn_off()
        client.disconnect()
        if web_server:
            web_server.close()
        print('Disconnected from MQTT broker')
    except Exception as e:
        print(f'Error in main loop: {e}')
        try:
            led_controller.turn_off()
            client.disconnect()
            if web_server:
                web_server.close()
        except:
            pass

if __name__ == '__main__':
    main()
