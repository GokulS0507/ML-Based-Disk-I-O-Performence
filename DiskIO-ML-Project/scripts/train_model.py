from sklearn.model_selection import train_test_split
import mysql.connector
import pandas as pd
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt


conn = mysql.connector.connect(
    host="localhost",
    user="diskuser",
    password="diskpass",
    database="disk_io_db"
)

query = """
SELECT read_bytes, write_bytes, cpu_usage, memory_usage
FROM disk_metrics
ORDER BY timestamp ASC
LIMIT 500
"""

df = pd.read_sql(query, conn)
conn.close()

print(df.head())
# STEP-ML-5.1: Data Cleaning

print("\nBefore cleaning:")
print(df.isnull().sum())

df.dropna(inplace=True)

print("\nAfter cleaning:")
print(df.isnull().sum())
# STEP-ML-5.2: Feature and Target Separation

X = df[['write_bytes', 'cpu_usage', 'memory_usage']]
y = df['read_bytes']

print("\nFeatures (X) sample:")
print(X.head())

print("\nTarget (y) sample:")
print(y.head())

X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42
)

print("\nTraining set size:", X_train.shape)
print("Testing set size:", X_test.shape)

model = LinearRegression()
model.fit(X_train, y_train)

print("\n✅ Model trained successfully")

# STEP-ML-8.1: Predict using test data

y_pred = model.predict(X_test)

print("\nSample predictions:")
for i in range(5):
    print(f"Actual: {y_test.iloc[i]}  |  Predicted: {int(y_pred[i])}")
from sklearn.metrics import mean_absolute_error

mae = mean_absolute_error(y_test, y_pred)
print("\n📊 Mean Absolute Error (MAE):", mae)

# STEP-ML-9.1: Predict future disk read load

latest_row = df.iloc[-1]

sample_input = [[
    latest_row['write_bytes'],
    latest_row['cpu_usage'],
    latest_row['memory_usage']
]]

future_read_prediction = model.predict(sample_input)

print("\n🔮 Predicted Future Disk Read Bytes:", int(future_read_prediction[0]))
# STEP-ML-9.2: Interpret prediction

CRITICAL_THRESHOLD = 50000000  # 50 MB

if future_read_prediction[0] > CRITICAL_THRESHOLD:
    print("🚨 Status: CRITICAL – Disk overload likely")
else:
    print("✅ Status: NORMAL – Disk usage stable")


# STEP-5.1: Visualization – Actual vs Predicted

plt.figure()
plt.plot(y_test.values[:50], label="Actual Read Bytes")
plt.plot(y_pred[:50], label="Predicted Read Bytes")

plt.xlabel("Sample Index")
plt.ylabel("Disk Read Bytes")
plt.title("Actual vs Predicted Disk Read Performance")
plt.legend()
plt.show()
# Error (Residual) Visualization
errors = y_test.values - y_pred

import matplotlib.pyplot as plt
plt.figure()
plt.plot(errors[:50])
plt.axhline(y=0)
plt.xlabel("Sample Index")
plt.ylabel("Prediction Error (Bytes)")
plt.title("Prediction Error (Actual - Predicted)")
plt.show()

import joblib
import os

# Create models folder if not exists
os.makedirs("../models", exist_ok=True)

# Save the trained model
joblib.dump(model, "../models/disk_io_model.pkl")

print("💾 Model saved as disk_io_model.pkl")
