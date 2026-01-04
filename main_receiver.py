import network
import espnow
import ubinascii

# A WLAN interface must be active
sta = network.WLAN(network.STA_IF)
sta.active(True)
sta.config(channel=6)  # Use the same channel on both
sta.disconnect() # Not strictly necessary, but good practice for ESP8266

e = espnow.ESPNow()
e.active(True)

print(ubinascii.hexlify(sta.config('mac'), ':').decode())

print("Receiver active. Waiting for messages...")

while True:
    # Wait for a message (returns mac, message)
    host, msg = e.recv()
    if host:
        print("Received from {0}: {1}", ubinascii.hexlify(host).decode(), msg.decode())