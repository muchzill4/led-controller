# WiFi Configuration
WIFI_SSID = 'your_wifi_ssid'
WIFI_PASSWORD = 'your_wifi_password'

# MQTT Configuration
MQTT_BROKER = 'broker.hivemq.com'  # Public broker (or use your own)
MQTT_PORT = 1883
MQTT_CLIENT_ID = 'esp32_led_controller'
MQTT_USER = ''  # Leave empty if not required
MQTT_PASSWORD = ''  # Leave empty if not required
MQTT_TOPIC = b'esp32/led/control'
