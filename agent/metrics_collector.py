"""
Coleta de métricas de hardware do computador (CPU, RAM, disco, rede).

Requer: pip install psutil
"""
import time
import psutil


class MetricsCollector:
    def __init__(self):
        self._last_net = psutil.net_io_counters()
        self._last_net_time = time.time()

    def collect(self) -> dict:
        cpu_percent = psutil.cpu_percent(interval=0.5)
        ram_percent = psutil.virtual_memory().percent
        disk_percent = psutil.disk_usage("C:\\" if _is_windows() else "/").percent

        net_sent_kbps, net_recv_kbps = self._net_throughput()

        return {
            "cpu_percent": round(cpu_percent, 1),
            "ram_percent": round(ram_percent, 1),
            "disk_percent": round(disk_percent, 1),
            "net_sent_kbps": net_sent_kbps,
            "net_recv_kbps": net_recv_kbps,
        }

    def _net_throughput(self):
        now = psutil.net_io_counters()
        now_time = time.time()
        elapsed = max(now_time - self._last_net_time, 0.001)

        sent_kbps = ((now.bytes_sent - self._last_net.bytes_sent) / 1024) / elapsed
        recv_kbps = ((now.bytes_recv - self._last_net.bytes_recv) / 1024) / elapsed

        self._last_net = now
        self._last_net_time = now_time

        return round(sent_kbps, 1), round(recv_kbps, 1)


def _is_windows() -> bool:
    import platform
    return platform.system() == "Windows"
