import ota
import uasyncio as asyncio
from mqtt_local import config
from mqtt_as import MQTTClient


class MqttHandler:
    def __init__(self, base_topic):
        self.base_topic = base_topic
        self.version_topic = f'{base_topic}/version'
        self.ota_topic = f'{base_topic}/ota'
        self.available_topic = f'{base_topic}/availability'

        config['subs_cb'] = self.handle_incoming_message
        config['connect_coro'] = self.conn_han
        config['wifi_coro'] = self.wifi_han
        config['will'] = [self.available_topic, 'offline', True, 0]

        MQTTClient.DEBUG = False
        self.client = MQTTClient(config)

    def handle_incoming_message(self, topic, msg, retained):
        msg_string = str(msg, 'UTF-8')
        print(f'{topic}: {msg_string}')
        if topic == self.ota_topic:
            ota.process_ota_msg(msg)

    async def wifi_han(self, state):
        print('Wifi is ', 'up' if state else 'down')
        await asyncio.sleep(1)

    # If you connect with clean_session True, must re-subscribe (MQTT spec 3.1.2.4)
    async def conn_han(self, client):
        await client.subscribe(self.ota_topic, 0)
        await self.online()

    async def online(self):
        await self.client.publish(self.available_topic, 'online', retain=True, qos=0)
