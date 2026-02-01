import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    user="diskuser",
    password="diskpass",
    database="disk_io_db"
)

cursor = conn.cursor()

cursor.execute("""
SELECT read_bytes, write_bytes, cpu_usage
FROM disk_metrics
ORDER BY timestamp DESC
LIMIT 50
""")

data = cursor.fetchall()
conn.close()
# STEP 3.2: Separate values into lists

read_values = []
write_values = []
cpu_values = []

for row in data:
    read_values.append(row[0])
    write_values.append(row[1])
    cpu_values.append(row[2])

print("Read values:", read_values[:5])
print("Write values:", write_values[:5])
print("CPU values:", cpu_values[:5])
# STEP 3.3: Moving Average Algorithm

avg_read = sum(read_values) / len(read_values)
avg_write = sum(write_values) / len(write_values)
avg_cpu = sum(cpu_values) / len(cpu_values)

print("\nAverage Read Bytes:", avg_read)
print("Average Write Bytes:", avg_write)
print("Average CPU Usage:", avg_cpu)
# STEP 3.4: Threshold Detection

READ_THRESHOLD = 50000000   # 50 MB
WRITE_THRESHOLD = 50000000

if avg_read > READ_THRESHOLD:
    print("High Disk Read Load Detected")
else:
    print("Disk Read Load Normal")

if avg_write > WRITE_THRESHOLD:
    print("High Disk Write Load Detected")
else:
    print("Disk Write Load Normal")
# STEP 3.5: Sliding Window Trend Analysis

mid = len(read_values) // 2

recent_avg = sum(read_values[:mid]) / mid
older_avg = sum(read_values[mid:]) / (len(read_values) - mid)

if recent_avg > older_avg:
    print("Disk Read Trend Increasing")
else:
    print("Disk Read Trend Stable/Decreasing")

