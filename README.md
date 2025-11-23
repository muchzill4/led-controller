# ESP32 WS2812 LED Controller with MQTT

Control WS2812 LED strips (NeoPixels) on an ESP32 board using MicroPython, WiFi, and MQTT.

## Features

- WiFi connectivity
- MQTT communication for remote control
- Modern web interface with real-time status
- Full RGB color control with predefined color palette
- Brightness control (0-100%)
- Support for WS2812/WS2812B LED strips
- Custom RGB color setting via color picker
- Clean class-based architecture
- Error handling and connection management
- Responsive UI with animations and gradients

## Hardware Requirements

- **ESP32 development board**
  - [ESP32-DevKitC on Amazon](https://www.amazon.com/s?k=ESP32+development+board)
  - [Adafruit ESP32 Feather](https://www.adafruit.com/product/3405)
  - [SparkFun ESP32 Thing](https://www.sparkfun.com/products/13907)

- **WS2812/WS2812B LED strip**
  - [Adafruit NeoPixel Strip](https://www.adafruit.com/category/168)
  - [BTF-LIGHTING WS2812B on Amazon](https://www.amazon.com/s?k=WS2812B+LED+strip)
  - [AliExpress WS2812B](https://www.aliexpress.com/wholesale?SearchText=ws2812b+led+strip)

- **5V power supply** (for LED strip)
  - [5V 10A Power Supply on Amazon](https://www.amazon.com/s?k=5V+power+supply+LED)
  - [Adafruit 5V 4A Supply](https://www.adafruit.com/product/1466)
  - Note: Calculate ~60mA per LED at full white brightness

- **USB cable** for programming (usually Micro-USB or USB-C depending on board)

- **Optional: Level shifter** (3.3V to 5V) for data line
  - [Adafruit 4-channel I2C-safe Bi-directional Logic Level Converter](https://www.adafruit.com/product/757)
  - [SparkFun Logic Level Converter](https://www.sparkfun.com/products/12009)

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

### 3. Configure WiFi, MQTT, and LED Strip

Edit `config.py` and update:

**WiFi Configuration:**
- `WIFI_SSID`: Your WiFi network name
- `WIFI_PASSWORD`: Your WiFi password

**MQTT Configuration:**
- `MQTT_BROKER`: Your MQTT broker address
- `MQTT_PORT`: MQTT broker port (default: 1883)
- `MQTT_CLIENT_ID`: Unique client ID
- `MQTT_USER`: MQTT username (if required)
- `MQTT_PASSWORD`: MQTT password (if required)
- `MQTT_TOPIC`: Topic to subscribe to

**LED Strip Configuration:**
- `LED_PIN`: GPIO pin connected to LED strip data line (default: 5)
- `NUM_LEDS`: Number of LEDs in your strip (default: 30)

### 4. Upload Files to ESP32

Upload both `main.py` and `config.py` to the ESP32 using ampy, rshell, or Thonny IDE:

Using ampy:
```bash
ampy --port /dev/ttyUSB0 put config.py
ampy --port /dev/ttyUSB0 put main.py
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

### Control the LED Strip

Publish messages to the configured MQTT topic to control the LED strip.

#### Available Commands

**Basic Control:**
- `on` - Turn LEDs on with current color/brightness
- `off` - Turn LEDs off
- `state` or `status` - Get current state

**Brightness Control:**
- `brightness:50` - Set brightness to 50% (0-100)

**Predefined Colors:**
- `color:red` - Set color to red
- `color:green` - Set color to green
- `color:blue` - Set color to blue
- `color:white` - Set color to white
- `color:warm_white` - Set color to warm white
- `color:yellow` - Set color to yellow
- `color:cyan` - Set color to cyan
- `color:magenta` - Set color to magenta
- `color:orange` - Set color to orange
- `color:purple` - Set color to purple
- `color:pink` - Set color to pink
- `color:lime` - Set color to lime

**Custom RGB Colors:**
- `rgb:255,0,0` - Set custom RGB color (red in this example)
- `rgb:128,0,255` - Purple
- `rgb:255,165,0` - Orange

**List Colors:**
- `list` or `colors` - List all available predefined colors

#### Example using mosquitto_pub:
```bash
# Turn on LEDs
mosquitto_pub -h broker.hivemq.com -t esp32/led/control -m "on"

# Set color to red
mosquitto_pub -h broker.hivemq.com -t esp32/led/control -m "color:red"

# Set brightness to 30%
mosquitto_pub -h broker.hivemq.com -t esp32/led/control -m "brightness:30"

# Set custom RGB color
mosquitto_pub -h broker.hivemq.com -t esp32/led/control -m "rgb:255,128,0"

# Turn off
mosquitto_pub -h broker.hivemq.com -t esp32/led/control -m "off"

# List available colors
mosquitto_pub -h broker.hivemq.com -t esp32/led/control -m "list"
```

#### Example using Python paho-mqtt:
```python
import paho.mqtt.client as mqtt

client = mqtt.Client()
client.connect("broker.hivemq.com", 1883, 60)

# Set color and brightness
client.publish("esp32/led/control", "color:blue")
client.publish("esp32/led/control", "brightness:50")

# Custom RGB
client.publish("esp32/led/control", "rgb:255,100,50")

client.disconnect()
```

### Using the Web Interface

Once the ESP32 is running, you can control the LEDs through a web browser:

1. Find your ESP32's IP address from the serial console output
2. Open your browser and navigate to `http://<ESP32_IP>/`
3. Use the web interface to:
   - Turn LEDs on/off with big colorful buttons
   - Adjust brightness with a slider
   - Pick custom colors using the color picker
   - Select from predefined color palette
   - View real-time status (LED state, color, brightness, network info)

The web interface updates automatically and works on mobile devices too!

## Troubleshooting

**WiFi connection fails:**
- Check SSID and password in config.py
- Ensure ESP32 is in range of WiFi network
- Check if WiFi network is 2.4GHz (ESP32 doesn't support 5GHz)

**MQTT connection fails:**
- Verify MQTT broker address and port
- Check if broker requires authentication
- Test broker connectivity from another device

**LEDs don't respond:**
- Check LED pin configuration in config.py
- Verify LED strip is properly powered (5V)
- Check data line connection
- Ensure MQTT topic matches between publisher and subscriber
- Check NUM_LEDS matches your actual strip length

**LEDs show wrong colors:**
- Check power supply voltage (should be 5V)
- Verify data line connection is solid
- Try adding a level shifter if using 3.3V data line directly
- Reduce brightness if power supply is insufficient

**LEDs flicker or are unstable:**
- Check power supply capacity (WS2812 LEDs can draw up to 60mA each at full white)
- Use adequate wire gauge for power connections
- Add capacitor (1000µF) across power supply
- Keep data wire short and away from power wires

## Circuit Diagram

### WS2812 LED Strip Connection

```
ESP32                    WS2812 LED Strip
-----                    ----------------
GPIO 5 (or configured) -> DIN (Data In)
GND ---------------------> GND

5V Power Supply
---------------
5V ----------------------> 5V/VCC
GND ---------------------> GND (common with ESP32)
```

**Important Notes:**
- WS2812 strips require 5V power supply
- Data line can work with 3.3V from ESP32 (some strips may need level shifter)
- Connect ESP32 GND and power supply GND together
- For strips longer than 10 LEDs, power both ends of the strip
- Add 300-500Ω resistor in series with data line for protection (optional)
- Add 1000µF capacitor across power supply (optional but recommended)

## License

MIT License
