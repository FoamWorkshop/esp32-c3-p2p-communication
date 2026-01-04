from time import sleep
from message_bus import MessageBus
from messages import PotensiometerValueChanged
from machine import ADC, Pin

import _thread


def pot_loop(bus, with_lock):
    """Top-level potentiometer reading thread.
    Reads two ADCs on GPIO0 and GPIO1 and sends PotensiometerValueChanged
    messages via the provided `with_lock` wrapper.
    """

    adc_pins = [0, 1]
    adcs = [None, None]
    if ADC is not None and Pin is not None:
            adcs[0] = ADC(Pin(adc_pins[0]))
            adcs[1] = ADC(Pin(adc_pins[1]))
            print('Initialized ADCs on pins', adc_pins)

    prev = [None, None]
    # moving-average buffers and short hysteresis to avoid spikes
    buffers = [[], []]
    stable_counts = [0, 0]
    WINDOW_SIZE = 8
    CONSECUTIVE_REQUIRED = 3

    while True:
        try:
            for i in (0, 1):
                adc = adcs[i]
                if adc is None:
                    continue
                val = adc.read_u16()

                # update moving-average buffer
                buf = buffers[i]
                buf.append(val)
                if len(buf) > WINDOW_SIZE:
                    buf.pop(0)

                avg = sum(buf) // len(buf)

                # normalize avg from 0..65535 to 0..30 (integer)
                norm = int((avg * 30 + 32767) // 65535)
                if norm < 0:
                    norm = 0
                elif norm > 30:
                    norm = 30

                last = prev[i]

                if last is None:
                    # always send the first stable reading
                    changed = True
                else:
                    # require the normalized value to change for several
                    # consecutive readings to avoid transient spikes
                    if abs(norm - last) >= 1:
                        stable_counts[i] += 1
                    else:
                        stable_counts[i] = 0

                    changed = stable_counts[i] >= CONSECUTIVE_REQUIRED

                if changed:
                    prev[i] = int(norm)
                    
                    print('Pot', i, 'changed to', prev[i])

                    msg = PotensiometerValueChanged(index=i, value=prev[i])
                    try:
                        with_lock(bus.send_message, msg)
                    except Exception as e:
                        print('Failed to send pot message', e)
        except Exception as e:
            print('Pot thread error:', e)


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
                _with_lock(bus.poll, 100)
            except Exception as e:
                print('Poll thread error:', e)


    # Start threads
    try:
        _thread.start_new_thread(poll_loop, ())
        _thread.start_new_thread(pot_loop, (bus, _with_lock))
        # keep main alive
        while True:
            sleep(1)
    except Exception as e:
        print('Failed to start threads, falling back to single-threaded:', e)


if __name__ == '__main__':
    main()