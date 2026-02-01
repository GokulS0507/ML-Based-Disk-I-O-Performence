import joblib
import mysql.connector
import pandas as pd

# Load saved model
model = joblib.load("../models/disk_io_model.pkl")
print("Model loaded")

# Fetch latest data
conn = mysql.connector.connect(
    host="localhost",
    user="diskuser",
    password="diskpass",
    database="disk_io_db"
)

query = """
SELECT write_bytes, cpu_usage, memory_usage
FROM disk_metrics
ORDER BY timestamp DESC
LIMIT 1
"""

df = pd.read_sql(query, conn)
conn.close()

# Predict
prediction = model.predict(df)

print("Predicted Future Disk Read Bytes:", int(prediction[0]))

# Interpret prediction into system status

GB = 1024 * 1024 * 1024
predicted_gb = prediction[0] / GB

if predicted_gb < 0.5:
    status = "NORMAL"
elif predicted_gb < 1:
    status = "WARNING"
else:
    status = "CRITICAL"

print(f"Predicted Disk Read Load: {predicted_gb:.2f} GB")
print(f"System Status: {status}")

