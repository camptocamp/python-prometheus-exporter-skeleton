import signal
import time

from exporter.exporter import Exporter

def main():
    exporter = Exporter()
    signal.signal(signal.SIGHUP, exporter.signalHandler)
    signal.signal(signal.SIGUSR1, exporter.signalHandler)
    signal.signal(signal.SIGUSR2, exporter.signalHandler)
    while True:
        time.sleep(1)

if __name__ == '__main__':
    main()
