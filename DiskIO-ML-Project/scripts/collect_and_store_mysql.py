import psutil
import mysql.connector
import time
from datetime import datetime

# Connect to MySQL
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="diskuser",
        password="diskpass",
        database="disk_io_db",
        auth_plugin="mysql_native_password"
    )

print("Starting disk metrics collection...")

# Get initial disk counters
prev_disk = psutil.disk_io_counters()

while True:
    time.sleep(1)  # interval for delta calculation

    # Get current metrics
    disk = psutil.disk_io_counters()
    cpu = psutil.cpu_percent()
    memory = psutil.virtual_memory().percent

    # ✅ Calculate DELTA (difference) per interval
    # This prevents Read Bytes from showing cumulative totals or 0 incorrectly
    read_diff = max(0, disk.read_bytes - prev_disk.read_bytes)
    write_diff = max(0, disk.write_bytes - prev_disk.write_bytes)
    read_time_diff = max(0, disk.read_time - prev_disk.read_time)
    write_time_diff = max(0, disk.write_time - prev_disk.write_time)

    # Update reference for next iteration
    prev_disk = disk

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        sql = """
        INSERT INTO disk_metrics (
            timestamp, read_bytes, write_bytes,
            read_time, write_time, cpu_usage, memory_usage
        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        """

        values = (
            datetime.now(),
            read_diff,
            write_diff,
            read_time_diff,
            write_time_diff,
            cpu,
            memory
        )

        cursor.execute(sql, values)
        conn.commit()
        cursor.close()
        conn.close()

        print(f"[{datetime.now().strftime('%H:%M:%S')}] Saved: Read={read_diff}B, Write={write_diff}B, CPU={cpu}%")

    except Exception as e:
        print("DB ERROR:", e)

