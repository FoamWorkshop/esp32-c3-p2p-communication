import network
import espnow
import time
import ubinascii

# A WLAN interface must be active to use ESP-NOW
sta = network.WLAN(network.STA_IF)
sta.active(True)
sta.config(channel=6)  # Use the same channel on both
sta.disconnect()

e = espnow.ESPNow()
e.active(True)

peer = b'\xec\xda\x3b\xbd\x64\x38' # ec:da:3b:bd:64:38

e.add_peer(peer) # Register the receiver as a peer

print("Sender active. Sending messages...")
i = 0
while True:
    i += 1
    msg = "Hello, world! #{}".format(i).encode() # Messages must be bytes
    e.send(peer, msg)
    print("Sent:", msg.decode())
    time.sleep(2)