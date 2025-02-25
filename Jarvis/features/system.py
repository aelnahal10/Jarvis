import psutil

def convert_size(size_bytes):
    """Converts bytes into a human-readable format (KB, MB, GB, etc.)."""
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB")
    i = int(psutil.virtual_memory().total.bit_length() / 10)  # Log base 1024
    p = 1024 ** i
    s = round(size_bytes / p, 2)
    return f"{s} {size_name[i]}"

def system_stats():
    """Fetches CPU usage, RAM status, and battery percentage."""
    cpu_usage = psutil.cpu_percent()
    memory_in_use = convert_size(psutil.virtual_memory().used)
    total_memory = convert_size(psutil.virtual_memory().total)
    battery = psutil.sensors_battery()

    battery_status = f"{battery.percent}%" if battery else "Battery status not available."

    return f"CPU usage is {cpu_usage}%, RAM usage is {memory_in_use} out of {total_memory}, and battery is at {battery_status}."
