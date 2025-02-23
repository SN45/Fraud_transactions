from kafka import KafkaProducer
import csv
import json
import time

# Create a Kafka producer
producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# Path to the CSV file
csv_file = "/Volumes/Ext_ssd/project/fraud_trans/creditcard.csv"

# Read the CSV file and send data to Kafka
with open(csv_file, 'r') as file:
    reader = csv.DictReader(file)
    for row in reader:
        producer.send('transactions', value=row)
        print(f"Sent message: {row}")  # Print the message being sent
        time.sleep(0.01)  # Simulate real-time streaming

print("Data streaming to Kafka topic 'transactions' started.")
producer.flush()  # Ensure all messages are sent
producer.close()  # Close the producer when done
