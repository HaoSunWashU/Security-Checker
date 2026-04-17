import platform
import socket
import uuid
from datetime import datetime


def get_system_info() -> dict:
    hostname = socket.gethostname()

    try:
        ip = socket.gethostbyname(hostname)
    except Exception:
        ip = "N/A"

    mac_int = uuid.getnode()
    mac = ":".join(
        f"{(mac_int >> (5 - i) * 8) & 0xFF:02X}" for i in range(6)
    )

    return {
        "hostname": hostname,
        "os": f"{platform.system()} {platform.release()} {platform.version()}",
        "ip": ip,
        "mac": mac,
        "check_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "platform": platform.system(),
    }
