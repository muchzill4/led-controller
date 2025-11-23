# ESP32 LED Controller with MQTT

Control LEDs on an ESP32 board using MicroPython, WiFi, and MQTT.

## Features

- WiFi connectivity
- MQTT communication
- LED control via MQTT messages (on/off/toggle)
- Error handling and connection management

## Hardware Requirements

- ESP32 development board
- LED (or use built-in LED)
- USB cable for programming

## Software Requirements

- MicroPython firmware for ESP32
- MQTT broker (public or private)

## Installation

### 1. Flash MicroPython to ESP32

Download MicroPython firmware from [micropython.org](https://micropython.org/download/ESP32_GENERIC/)

Flash using esptool:
```bash
esptool.py --chip esp32 --port /dev/ttyUSB0 erase_flash
esptool.py --chip esp32 --port /dev/ttyUSB0 write_flash -z 0x1000 esp32-*.bin
```

### 2. Install umqtt library

Connect to the ESP32 via serial terminal and run:
```python
import upip
upip.install('umqtt.simple')
```

Or manually download and upload the umqtt library to the ESP32.

### 3. Configure WiFi and MQTT

Edit `config.py` and update:
- `WIFI_SSID`: Your WiFi network name
- `WIFI_PASSWORD`: Your WiFi password
- `MQTT_BROKER`: Your MQTT broker address
- `MQTT_PORT`: MQTT broker port (default: 1883)
- `MQTT_CLIENT_ID`: Unique client ID
- `MQTT_USER`: MQTT username (if required)
- `MQTT_PASSWORD`: MQTT password (if required)
- `MQTT_TOPIC`: Topic to subscribe to

### 4. Upload Files to ESP32

Upload both `main.py` and `config.py` to the ESP32 using ampy, rshell, or Thonny IDE:

Using ampy:
```bash
ampy --port /dev/ttyUSB0 put config.py
ampy --port /dev/ttyUSB0 put main.py
```

### 5. Customize LED Pin

By default, the program uses GPIO pin 2 (built-in LED on most ESP32 boards).

To change the LED pin, edit line 8 in `main.py`:
```python
LED_PIN = 2  # Change to your LED pin number
```

## Usage

### Start the Program

Reset the ESP32 or run:
```python
import main
```

The program will:
1. Connect to WiFi
2. Connect to the MQTT broker
3. Subscribe to the configured topic
4. Wait for messages

### Control the LED

Publish messages to the configured MQTT topic:

- `on` - Turn LED on
- `off` - Turn LED off
- `toggle` - Toggle LED state

#### Example using mosquitto_pub:
```bash
mosquitto_pub -h broker.hivemq.com -t esp32/led/control -m "on"
mosquitto_pub -h broker.hivemq.com -t esp32/led/control -m "off"
mosquitto_pub -h broker.hivemq.com -t esp32/led/control -m "toggle"
```

#### Example using Python paho-mqtt:
```python
import paho.mqtt.client as mqtt

client = mqtt.Client()
client.connect("broker.hivemq.com", 1883, 60)
client.publish("esp32/led/control", "on")
client.disconnect()
```

## Troubleshooting

**WiFi connection fails:**
- Check SSID and password in config.py
- Ensure ESP32 is in range of WiFi network
- Check if WiFi network is 2.4GHz (ESP32 doesn't support 5GHz)

**MQTT connection fails:**
- Verify MQTT broker address and port
- Check if broker requires authentication
- Test broker connectivity from another device

**LED doesn't respond:**
- Check LED pin configuration
- Verify LED is connected correctly
- Check MQTT topic matches between publisher and subscriber

## Circuit Diagram

```
ESP32 GPIO Pin -> LED (+) -> Resistor (220Ω) -> GND
```

For built-in LED, no external circuit is needed.

## License

MIT License
