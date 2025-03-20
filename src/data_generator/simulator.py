import json
import random
import time
import uuid
from datetime import datetime
import os
import sys

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

try:
    from azure.eventhub import EventHubProducerClient, EventData
    from azure.storage.blob import BlobServiceClient
    AZURE_AVAILABLE = True
except ImportError:
    print("Azure libraries not installed. Run: pip install azure-eventhub azure-storage-blob")
    print("For now, data will only be saved locally.")
    AZURE_AVAILABLE = False

from config.settings import (
    EVENTHUB_CONNECTION_STRING,
    EVENTHUB_NAME,
    SIMULATION_PATIENT_COUNT,
    SIMULATION_INTERVAL_SECONDS,
    ANOMALY_PROBABILITY,
    VITAL_RANGES
)

class PatientDataSimulator:
    """Simple simulator for generating patient vital sign data."""
    
    def __init__(self):
        self.patients = {}
        self.use_azure = False
        self.event_producer = None
        
        # Try to connect to Azure EventHub if we have credentials
        if AZURE_AVAILABLE and EVENTHUB_CONNECTION_STRING and EVENTHUB_NAME:
            try:
                self.event_producer = EventHubProducerClient.from_connection_string(
                    conn_str=EVENTHUB_CONNECTION_STRING,
                    eventhub_name=EVENTHUB_NAME
                )
                self.use_azure = True
                print("Connected to Azure EventHub!")
            except Exception as e:
                print(f"Could not connect to Azure EventHub: {e}")
                print("Will save data locally only.")
        else:
            if not AZURE_AVAILABLE:
                print("Azure libraries not available. Will save data locally only.")
            elif not EVENTHUB_CONNECTION_STRING:
                print("EventHub connection string not provided in environment variables.")
                print("Check your .env file. Will save data locally only.")
            elif not EVENTHUB_NAME:
                print("EventHub name not provided in environment variables.")
                print("Check your .env file. Will save data locally only.")
    
    def generate_patient_ids(self, count):
        """Generate unique patient IDs."""
        for _ in range(count):
            patient_id = str(uuid.uuid4())
            self.patients[patient_id] = {
                "heart_rate": random.uniform(70, 85),
                "temperature": random.uniform(36.5, 37.2),
                "blood_pressure_systolic": random.uniform(110, 120),
                "blood_pressure_diastolic": random.uniform(70, 80),
                "oxygen_saturation": random.uniform(95, 99),
                "respiratory_rate": random.uniform(14, 18)
            }
    
    def generate_vitals(self, patient_id):
        """Generate a new set of vital signs for a patient with some continuity."""
        prev_vitals = self.patients[patient_id]
        
        # Determine if this reading should have an anomaly
        contains_anomaly = random.random() < ANOMALY_PROBABILITY
        anomaly_vital = None
        
        # Generate new vitals with some continuity from previous readings
        new_vitals = {}
        
        # Heart rate: normally distributed around previous value
        new_vitals["heart_rate"] = max(40, min(150, prev_vitals["heart_rate"] + random.uniform(-5, 5)))
        
        # Temperature: normally distributed around previous value
        new_vitals["temperature"] = max(34, min(40, prev_vitals["temperature"] + random.uniform(-0.5, 0.5)))
        
        # Blood pressure: generate systolic and diastolic
        new_vitals["blood_pressure_systolic"] = max(80, min(180, prev_vitals["blood_pressure_systolic"] + random.uniform(-5, 5)))
        new_vitals["blood_pressure_diastolic"] = max(50, min(100, prev_vitals["blood_pressure_diastolic"] + random.uniform(-3, 3)))
        
        # Oxygen saturation: normally distributed around previous value
        new_vitals["oxygen_saturation"] = max(85, min(100, prev_vitals["oxygen_saturation"] + random.uniform(-2, 2)))
        
        # Respiratory rate: normally distributed around previous value
        new_vitals["respiratory_rate"] = max(8, min(30, prev_vitals["respiratory_rate"] + random.uniform(-1, 1)))
        
        # If we want an anomaly, pick a vital sign to make abnormal
        if contains_anomaly:
            anomaly_options = ["heart_rate", "temperature", "blood_pressure_systolic", "blood_pressure_diastolic", "oxygen_saturation", "respiratory_rate"]
            anomaly_vital = random.choice(anomaly_options)
            
            # Make the chosen vital sign abnormal
            if anomaly_vital == "heart_rate":
                # Either very low or very high heart rate
                new_vitals["heart_rate"] = random.choice([
                    random.uniform(30, 40),  # too low
                    random.uniform(130, 150)  # too high
                ])
            elif anomaly_vital == "temperature":
                # Either too low or too high temperature
                new_vitals["temperature"] = random.choice([
                    random.uniform(33, 35),  # too low
                    random.uniform(39, 41)   # too high
                ])
            elif anomaly_vital == "blood_pressure_systolic":
                # Abnormal systolic pressure
                new_vitals["blood_pressure_systolic"] = random.choice([
                    random.uniform(70, 80),   # too low
                    random.uniform(160, 200)  # too high
                ])
            elif anomaly_vital == "blood_pressure_diastolic":
                # Abnormal diastolic pressure
                new_vitals["blood_pressure_diastolic"] = random.choice([
                    random.uniform(40, 50),   # too low
                    random.uniform(95, 120)   # too high
                ])
            elif anomaly_vital == "oxygen_saturation":
                # Low oxygen levels
                new_vitals["oxygen_saturation"] = random.uniform(80, 90)
            elif anomaly_vital == "respiratory_rate":
                # Abnormal respiratory rate
                new_vitals["respiratory_rate"] = random.choice([
                    random.uniform(5, 9),     # too low
                    random.uniform(25, 35)    # too high
                ])
        
        # Update the stored vitals for continuity in next reading
        self.patients[patient_id] = new_vitals
        
        # Format blood pressure as a string (e.g., "120/80")
        bp_str = f"{int(new_vitals['blood_pressure_systolic'])}/{int(new_vitals['blood_pressure_diastolic'])}"
        
        # Create the patient data record
        record = {
            "patient_id": patient_id,
            "timestamp": datetime.now().isoformat(),
            "heart_rate": round(new_vitals["heart_rate"], 1),
            "temperature": round(new_vitals["temperature"], 1),
            "blood_pressure": bp_str,
            "oxygen_saturation": round(new_vitals["oxygen_saturation"], 1),
            "respiratory_rate": round(new_vitals["respiratory_rate"], 1),
            "contains_anomaly": contains_anomaly,
            "anomaly_vital": anomaly_vital
        }
        
        return record
    
    def send_to_eventhub(self, data_batch):
        """Send a batch of data to Azure Event Hub."""
        if not self.use_azure or not self.event_producer:
            return False
            
        try:
            # Create a batch of events
            event_data_batch = self.event_producer.create_batch()
            
            # Add messages to the batch
            for data in data_batch:
                event_data = EventData(json.dumps(data))
                event_data_batch.add(event_data)
            
            # Send the batch of events to the event hub
            self.event_producer.send_batch(event_data_batch)
            print(f"Sent {len(data_batch)} messages to EventHub")
            return True
        except Exception as e:
            print(f"Error sending to EventHub: {e}")
            return False
    
    def save_locally(self, data_batch):
        """Save data locally for testing."""
        with open("patient_data.jsonl", "a") as f:
            for data in data_batch:
                f.write(json.dumps(data) + "\n")
        print(f"Saved {len(data_batch)} records locally")
    
    def run_simulation(self):
        """Run the simulation continuously."""
        print(f"Starting simulation with {len(self.patients)} patients")
        print(f"Data will be generated every {SIMULATION_INTERVAL_SECONDS} seconds")
        
        try:
            while True:
                data_batch = []
                
                # Generate data for each patient
                for patient_id in self.patients:
                    patient_data = self.generate_vitals(patient_id)
                    data_batch.append(patient_data)
                
                # Send data to Azure if connected
                if self.use_azure:
                    self.send_to_eventhub(data_batch)
                
                # Always save locally as backup
                self.save_locally(data_batch)
                
                # Wait for the next interval
                time.sleep(SIMULATION_INTERVAL_SECONDS)
                
        except KeyboardInterrupt:
            print("Simulation stopped by user")
        finally:
            if self.use_azure and self.event_producer:
                self.event_producer.close()
            print("Simulation ended")
    
    def __del__(self):
        """Clean up resources when the object is destroyed."""
        if self.use_azure and self.event_producer:
            try:
                self.event_producer.close()
            except:
                pass

if __name__ == "__main__":
    # Create simulator
    simulator = PatientDataSimulator()
    
    # Generate patient IDs
    simulator.generate_patient_ids(SIMULATION_PATIENT_COUNT)
    
    # Run the simulation
    simulator.run_simulation() 