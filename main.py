"""
main.py - Message bus example

Simulate `EncoderValueChanged` messages every 1 second with a random
value 0-255 and register a handler that prints the value to console.
"""

from time import sleep
from message_bus import MessageBus
from messages import EncoderValueChanged, TYPE_ENCODER_VALUE_CHANGED

import random as _rand
import _thread



def _random_byte():
    try:
        return _rand.getrandbits(8)
    except Exception:
        # fallback to randint
        return _rand.randint(0, 255)


def main():
    bus = MessageBus()

    # initialize ESP-NOW
    bus.init_espnow()

    # register a handler that prints encoder values
    def encoder_handler(msg):
        try:
            v = msg.payload.get('value')
        except Exception:
            v = None
        print('EncoderValueChanged ->', v)
        # return False so MessageBus does not send an ACCEPTED ack
        return False

    bus.register_handler(TYPE_ENCODER_VALUE_CHANGED, encoder_handler)

    # send a HELLO message to announce our presence
    bus.send_hello()

    # Use a simple lock to protect access to the bus from multiple threads
    lock = _thread.allocate_lock()


    def _with_lock(fn, *a, **kw):
        if lock:
            try:
                lock.acquire()
                return fn(*a, **kw)
            finally:
                try:
                    lock.release()
                except Exception:
                    pass
        else:
            return fn(*a, **kw)

    # Polling thread: continuously call poll() to handle incoming messages
    def poll_loop():
        while True:
            try:
                _with_lock(bus.poll, 500)
            except Exception as e:
                print('Poll thread error:', e)
            # small sleep to yield
            sleep(0.01)

    # Sender thread: generate EncoderValueChanged every 1s and send
    def sender_loop():
        while True:
            val = _random_byte()
            msg = EncoderValueChanged(sender=bus.own_mac, value=val)
            try:
                _with_lock(bus.send_message, msg, None)
            except Exception as e:
                print('Sender thread error:', e)
            sleep(1)

    # Start threads
    try:
        _thread.start_new_thread(poll_loop, ())
        _thread.start_new_thread(sender_loop, ())
        # keep main alive
        while True:
            sleep(1)
    except Exception as e:
        print('Failed to start threads, falling back to single-threaded:', e)


if __name__ == '__main__':
    main()