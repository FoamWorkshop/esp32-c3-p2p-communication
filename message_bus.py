"""
Simple Message Bus abstraction using ESP-NOW for MicroPython.

Features implemented:
- HELLO broadcast on `send_hello()`; peers reply with HELLO unicast.
- Maintain `known_peers` set (MAC strings).
- Register handlers by message type; only modules with handler process messages.
- Handled messages get an `ACCEPTED` unicast reply to sender.
- Print/log network info after HELLO and log sent/received messages.

Note: This module is written to run on MicroPython ESP32 but includes
graceful fallbacks so it can be imported on a host for static analysis.
"""

from time import sleep
import sys
try:
    import network
    import espnow
except Exception as e:
    raise ImportError('This module requires the `network` and `espnow` modules available on ESP32 MicroPython: %s' % e)

from messages import (
    mac_bytes_to_str,
    mac_str_to_bytes,
    Message,
    Hello,
    Accepted,
    TYPE_HELLO,
)


class MessageBus:
    def __init__(self, iface=None):
        self.iface = iface
        self.esp = None
        self.esp_inited = False
        self.known_peers = set()
        self.handlers = {}
        self.own_mac = None

    def init_espnow(self):
        # STA interfejs dla ESP-NOW
        sta = network.WLAN(network.STA_IF)
        sta.active(True)
        sta.config(channel=6)

        # Inicjalizacja ESP-NOW na STA
        self.esp = espnow.ESPNow()
        self.esp.active(True)  # albo self.esp.active(True)
        
        # Pobieramy MAC STA, bo ESP-NOW korzysta z STA
        self.mac = sta.config('mac')
        self.own_mac = mac_bytes_to_str(self.mac)
        
        self.esp_inited = True

    def register_handler(self, message_type, handler_fn):
        """Register a handler callable for a message type.
        Handler receives a Message instance and should return truthy if handled.
        """
        self.handlers[message_type] = handler_fn

    def send_message(self, message, peer_mac=None):
        """Send `message` (Message instance).
        If `peer_mac` is None, send to all known peers (unicast to each).
        If `peer_mac` equals 'broadcast' or bytes b'\xff'*6, broadcast is used.
        """
        b = message.to_bytes()
        if peer_mac is None:
            # send to all known peers
            for peer in list(self.known_peers):
                try:
                    peer_bytes = mac_str_to_bytes(peer)
                    self._esp_send(peer_bytes, b)
                    print('SENT ->', message.type, 'to', peer)
                except Exception as e:
                    print('Send error to', peer, e)
        else:
            # send to specific peer
            if isinstance(peer_mac, str):
                peer_bytes = mac_str_to_bytes(peer_mac)
            else:
                peer_bytes = peer_mac
            self._esp_send(peer_bytes, b)
            print('SENT ->', message.type, 'to', mac_bytes_to_str(peer_bytes))

    def _esp_send(self, peer_bytes, payload_bytes):
        # some ESPNow implementations require adding a peer first
        try:
            # ensure espnow initialized; try to re-init if not
            if not self.esp_inited:
                try:
                    self.init_espnow()
                except Exception as e:
                    print('ESP send failed: ESPNow not initialized (%s)' % e)
                    return

            try:
                self.esp.add_peer(peer_bytes)
            except Exception:
                pass
            self.esp.send(peer_bytes, payload_bytes)
        except Exception as e:
            print('ESP send failed:', e)

    def send_hello(self):
        """Broadcast HELLO. Poll for a short period to collect replies and
        then print network info and known peers.
        """
        hello = Hello(sender=self.own_mac)
        # broadcast address
        bcast = b'\xff\xff\xff\xff\xff\xff'
        print('SENDING HELLO (broadcast) with MAC', self.own_mac)
        self._esp_send(bcast, hello.to_bytes())

        # poll for replies for a short time
        wait_ms = 20000
        interval_ms = 500
        waited = 0
        while waited < wait_ms:
            self.poll(timeout_ms=interval_ms)
            waited += interval_ms

        # log network info after collecting replies
        print('NETWORK INFO: own_mac=', self.own_mac)
        print('KNOWN PEERS (after replies):', list(self.known_peers))

    def _handle_incoming(self, peer, msg_bytes):
        peer_str = mac_bytes_to_str(peer)
        msg = Message.from_bytes(msg_bytes)
        if not msg:
            return
        print('RECEIVED <-', msg.type, 'from', peer_str)

        # Special handling for HELLO: add to known peers and reply with unicast HELLO
        if msg.type == TYPE_HELLO:
            if peer_str not in self.known_peers:
                self.known_peers.add(peer_str)
                print('Added peer', peer_str, 'to known_peers')
                # reply with our HELLO (unicast)
                reply = Hello(sender=self.own_mac)
                self.send_message(reply, peer_mac=peer)
            return

        # Default: dispatch to registered handler (if any)
        handler = self.handlers.get(msg.type)
        if handler:
            try:
                handled = handler(msg)
                if handled:
                    # send ACCEPTED back to sender
                    acc = Accepted(sender=self.own_mac, original_type=msg.type)
                    self.send_message(acc, peer_mac=peer)
                    print('Sent ACCEPTED for', msg.type, 'to', peer_str)
            except Exception as e:
                print('Handler error for', msg.type, e)
        else:
            # no handler -> ignore
            pass

    def poll(self, timeout_ms=100):
        """Poll for incoming espnow messages. Call regularly in main loop if no thread available."""
        if self.esp is None:
            return
        try:
            # espnow.recv returns (mac, msg) or None depending on port
            r = self.esp.recv(timeout_ms)
            if not r:
                return
            # Some ports return (mac, msg) while others return (mac, msg, timestamp)
            if len(r) >= 2:
                peer = r[0]
                msg = r[1]
                self._handle_incoming(peer, msg)
        except Exception as e:
            # non-fatal
            # print('Poll error', e)
            pass
