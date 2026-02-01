from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import mysql.connector
import joblib

app = FastAPI()

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load trained ML model
model = joblib.load("../models/disk_io_model.pkl")


def get_db_data():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="diskuser",
            password="diskpass",
            database="disk_io_db",
            auth_plugin="mysql_native_password"
        )

        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT read_bytes, write_bytes, cpu_usage, memory_usage
            FROM disk_metrics
            ORDER BY timestamp DESC
            LIMIT 1
        """)

        row = cursor.fetchone()
        cursor.close()
        conn.close()

        return row

    except Exception as e:
        print("DB ERROR:", e)
        return None


@app.get("/")
def root():
    return {"message": "Disk I/O ML API is running"}


@app.get("/metrics")
def get_metrics():
    data = get_db_data()

    if data is None:
        return {"error": "Database connection failed"}

    # ML prediction using write_bytes, cpu_usage, memory_usage
    # Consistent with training: X = df[['write_bytes', 'cpu_usage', 'memory_usage']]
    features = [[
        float(data["write_bytes"]),
        float(data["cpu_usage"]),
        float(data["memory_usage"])
    ]]
    
    prediction = model.predict(features)

    # Convert predicted bytes → MB
    MB = 1024 * 1024
    predicted_mb = float(prediction[0]) / MB

    # ✅ Requirement: Ensure prediction output is non-negative and clipped at minimum 0
    predicted_mb = max(0.0, predicted_mb)

    # ✅ NEW REQUIRED STATUS RULES
    # < 1 MB → NORMAL
    # 1 MB – 10 MB → WARNING
    # > 10 MB → CRITICAL
    if predicted_mb < 1:
        status = "NORMAL"
    elif 1 <= predicted_mb <= 10:
        status = "WARNING"
    else:
        status = "CRITICAL"

    # ✅ DEBUG LOGGING (MANDATORY)
    print(f"DEBUG: Predicted MB: {predicted_mb:.2f}, Status: {status}")

    # ✅ Requirement: Clean JSON with numbers only
    return {
        "read_bytes": int(data["read_bytes"]),
        "write_bytes": int(data["write_bytes"]),
        "cpu_usage": float(data["cpu_usage"]),
        "memory_usage": float(data["memory_usage"]),
        "predicted_disk_load_mb": round(predicted_mb, 2),
        "status": status
    }


