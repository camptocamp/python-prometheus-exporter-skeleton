import subprocess
import signal

from prometheus_client import start_http_server
from prometheus_client import Gauge, Counter


class Exporter:
    def __init__(self):

        # Start and configure prometheus exporter
        start_http_server(9351)

        self.temperature = Gauge('temperature', 'CPU temperature')
        self.temperature.set_function(self.temperatureCallback)

        self.signal = Counter('signals', 'signals received',
                              ['signal'])
        self.signalValues = {
            signal.SIGHUP: 'HUP',
            signal.SIGUSR1: 'USR1',
            signal.SIGUSR2: 'USR2',
        }

    def temperatureCallback(self):
        return self.cmd("sensors -u | grep -2 'Core 0' | "
                        "grep input |  awk '{print $2}'")

    def signalHandler(self, signalnum, _):
        self.signal.labels(self.signalValues[signalnum]).inc()

    def cmd(self, cmd):
        process = subprocess.run(cmd, capture_output=True, shell=True)
        return process.stdout.decode()
