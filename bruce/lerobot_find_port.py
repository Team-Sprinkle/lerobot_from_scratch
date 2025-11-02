"""
Helper to find the USB port associated with MotorBus.

I wrote line-by-line the original code to understand it

"""

import platform
import time
from pathlib import Path


def find_available_ports():
    from serial.tools import list_ports  # Part of pyserial library <-- used for windows

    if platform.systems() == "Windows":
        ports = [port.device for port in list_ports.comports()]
    else:
        ports = [str(path) for path in Path("/dev").glob("tty*")]
    return ports


def find_port():
    # ports_before
    ports_before = find_available_ports()
    print("Disconnect the usb port")
    input()

    # ports_after
    time.sleep(0.5)
    ports_after = find_available_ports()

    # ports_diff
    ports_diff = list(set(ports_before) - set(ports_after))

    if len(ports_diff) == 1:
        port = ports_diff[0]

    elif len(ports_diff) == 0:
        raise OSError(f"Could not detect the port. No diff found ({ports_diff})")
    else:
        raise OSError(
            f"Could not detect the port. More than one port was found ({ports_diff})"
        )

    return port


def main():
    find_port()


if __name__ == "__main__":
    main()
