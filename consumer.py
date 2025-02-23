from kafka import KafkaConsumer
import json
import boto3
import os
import csv

# AWS S3 Configuration
AWS_ACCESS_KEY = ''  # Replace with your actual access key
AWS_SECRET_KEY = ''  # Replace with your actual secret key
S3_BUCKET_NAME = ''  #Replace with your bucket name

# Create an S3 session
session = boto3.Session(
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
)
s3 = session.client('s3')

# Define Kafka consumer
consumer = KafkaConsumer(
    'transactions',
    bootstrap_servers='localhost:9092',
    value_deserializer=lambda x: json.loads(x.decode('utf-8')),
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='fraud-trans-group'
)

print("Consuming messages from topic 'transactions'...")

batch_size = 1000  
batch = []  
counter = 1  

# Expected fields in CSV
expected_fields = ["Time"] + [f"V{i}" for i in range(1, 29)] + ["Amount", "Class"]

for message in consumer:
    try:
        data = message.value

        # Clean and Convert Data
        cleaned_data = {
            "Time": float(data.get("Time", 0.0)),  # Default to 0.0 if key not found
            **{f"V{i}": float(data.get(f"V{i}", 0.0)) for i in range(1, 29)},  # Default to 0.0 if key not found
            "Amount": float(data.get("Amount", 0.0)),  # Default to 0.0 if key not found
            "Class": int(data.get("Class", 0))  # Default to 0 if key not found
        }

        batch.append(cleaned_data)

        if len(batch) >= batch_size:
            filename = f"fraud_transaction_batch_{counter}.csv"
            filepath = os.path.join("/tmp", filename)

            with open(filepath, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=expected_fields)
                writer.writeheader()
                writer.writerows(batch)

            # Upload to S3
            s3.upload_file(filepath, S3_BUCKET_NAME, filename)
            print(f"Uploaded {filename} to S3 bucket {S3_BUCKET_NAME}")

            batch.clear()
            counter += 1
            
            # Optionally, remove the file after upload
            os.remove(filepath)

    except Exception as e:
        print(f"Skipping malformed row: {e}")
