# OTA:file:main.py
# OTA:reboot:true
from machine import Pin

import uasyncio as asyncio
from mqtt_handler import MqttHandler


BASE_TOPIC = 'esp32/otatest'

led = Pin(2, Pin.OUT)
version = 1
led_sleep_secs = 1

mqtt = MqttHandler(BASE_TOPIC)


async def main():
    while True:
        try:
            print("Starting main()...")
            await mqtt.client.connect()
            print("Connected...")
            await asyncio.sleep(2)  # Give broker time
            await mqtt.online()
            print("Online...")
            print("Trying to publish version...")
            await mqtt.client.publish(mqtt.version_topic, str(version), retain=True)
            print("Published version...")
            while True:
                led.on()
                await asyncio.sleep(led_sleep_secs)
                led.off()
                await asyncio.sleep(led_sleep_secs)
        except Exception as e:
            print(f"Problem in main loop: {e}")


try:
    loop = asyncio.get_event_loop()
    loop.create_task(main())
    loop.run_forever()
except Exception as e:
    print(f"Problem launching: {e}")
finally:
    mqtt.client.close()
    asyncio.stop()
