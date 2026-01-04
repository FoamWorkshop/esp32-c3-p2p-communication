from time import sleep
from message_bus import MessageBus
from messages import EncoderValueChanged, TYPE_ENCODER_VALUE_CHANGED

import _thread


def main():
    bus = MessageBus()

    # initialize ESP-NOW
    bus.init_espnow()

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


    # Start threads
    try:
        _thread.start_new_thread(poll_loop, ())
        # keep main alive
        while True:
            sleep(1)
    except Exception as e:
        print('Failed to start threads, falling back to single-threaded:', e)


if __name__ == '__main__':
    main()