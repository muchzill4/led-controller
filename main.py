from machine import Pin
import network
import time
from umqtt.simple import MQTTClient
import config

# LED GPIO pin (change as needed)
LED_PIN = 2  # Built-in LED on most ESP32 boards

# Initialize LED
led = Pin(LED_PIN, Pin.OUT)

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

# MQTT message callback
def mqtt_callback(topic, msg):
    print(f'Received message on topic {topic}: {msg}')

    try:
        message = msg.decode('utf-8').lower()

        if message == 'on':
            led.value(1)
            print('LED turned ON')
        elif message == 'off':
            led.value(0)
            print('LED turned OFF')
        elif message == 'toggle':
            led.value(not led.value())
            print(f'LED toggled to {"ON" if led.value() else "OFF"}')
        else:
            print(f'Unknown command: {message}')
    except Exception as e:
        print(f'Error processing message: {e}')

# Connect to MQTT broker
def connect_mqtt():
    try:
        client = MQTTClient(
            client_id=config.MQTT_CLIENT_ID,
            server=config.MQTT_BROKER,
            port=config.MQTT_PORT,
            user=config.MQTT_USER,
            password=config.MQTT_PASSWORD
        )

        client.set_callback(mqtt_callback)
        client.connect()
        client.subscribe(config.MQTT_TOPIC)

        print(f'Connected to MQTT broker at {config.MQTT_BROKER}')
        print(f'Subscribed to topic: {config.MQTT_TOPIC}')

        return client
    except Exception as e:
        print(f'Failed to connect to MQTT broker: {e}')
        return None

# Main program
def main():
    print('Starting ESP32 LED Controller')
    print('=' * 40)

    # Connect to WiFi
    if not connect_wifi():
        print('Cannot proceed without WiFi connection')
        return

    # Connect to MQTT broker
    client = connect_mqtt()
    if not client:
        print('Cannot proceed without MQTT connection')
        return

    print('System ready!')
    print(f'Send "on", "off", or "toggle" to topic: {config.MQTT_TOPIC}')
    print('=' * 40)

    # Main loop
    try:
        while True:
            client.check_msg()  # Check for new messages
            time.sleep(0.1)
    except KeyboardInterrupt:
        print('\nShutting down...')
        client.disconnect()
        print('Disconnected from MQTT broker')
    except Exception as e:
        print(f'Error in main loop: {e}')
        try:
            client.disconnect()
        except:
            pass

if __name__ == '__main__':
    main()
