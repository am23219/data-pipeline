import os
import sys
import json
import time
import argparse
from datetime import datetime

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data_generator.simulator import PatientDataSimulator
from src.data_processing.spark_processor import PatientDataProcessor
from src.anomaly_detection.detector import SimpleAnomalyDetector, StatisticalAnomalyDetector
from src.alerting.alert_manager import PatientAlertManager

def simulate_data(duration=60, patient_count=5):
    """Run the patient data simulator for a specific duration."""
    print(f"Starting patient data simulation for {duration} seconds with {patient_count} patients")
    
    # Create simulator
    simulator = PatientDataSimulator()
    
    # Generate patient IDs
    simulator.generate_patient_ids(patient_count)
    
    # Run for specified duration
    start_time = time.time()
    try:
        while time.time() - start_time < duration:
            remaining = duration - (time.time() - start_time)
            print(f"Simulation running... {int(remaining)} seconds remaining")
            time.sleep(min(5, remaining))
    except KeyboardInterrupt:
        print("Simulation stopped by user")
    
    print("Simulation complete")

def process_patient_data(mode="batch", input_path="patient_data.jsonl"):
    """Process patient data using PySpark."""
    print(f"Processing patient data in {mode} mode")
    
    # Create processor
    processor = PatientDataProcessor()
    
    try:
        if mode == "stream":
            # Process streaming data
            processor.process_stream()
        else:
            # Process batch data
            df = processor.process_batch_data(input_path)
            
            # Convert to Python objects for further processing
            patients_data = []
            for row in df.collect():
                patients_data.append(row.asDict())
            
            # Return the processed data
            return patients_data
    except Exception as e:
        print(f"Error processing data: {e}")
    finally:
        # Stop Spark
        processor.stop()

def detect_anomalies(patient_data, detector_type="simple"):
    """Detect anomalies in patient data."""
    print(f"Detecting anomalies using {detector_type} detector")
    
    # Create detector
    if detector_type == "statistical":
        detector = StatisticalAnomalyDetector()
    else:
        detector = SimpleAnomalyDetector()
    
    # Process each patient record
    results = []
    for record in patient_data:
        # Detect anomalies
        if detector_type == "statistical":
            # Statistical detector needs history
            patient_id = record.get("patient_id")
            detector.add_to_history(patient_id, record)
            has_anomaly = detector.detect_anomalies(patient_id, record)
            
            if has_anomaly:
                results.append({
                    "patient_id": patient_id,
                    "timestamp": record.get("timestamp"),
                    "vitals": {
                        "heart_rate": record.get("heart_rate"),
                        "temperature": record.get("temperature"),
                        "blood_pressure": record.get("blood_pressure"),
                        "oxygen_saturation": record.get("oxygen_saturation"),
                        "respiratory_rate": record.get("respiratory_rate")
                    },
                    "anomalies": [{
                        "vital": "statistical_anomaly",
                        "value": "N/A",
                        "reason": "statistical outlier",
                        "severity": "medium"
                    }]
                })
        else:
            # Simple threshold-based detector
            anomalies = detector.check_vital_thresholds(record)
            
            if anomalies:
                results.append({
                    "patient_id": record.get("patient_id"),
                    "timestamp": record.get("timestamp"),
                    "vitals": {
                        "heart_rate": record.get("heart_rate"),
                        "temperature": record.get("temperature"),
                        "blood_pressure": record.get("blood_pressure"),
                        "oxygen_saturation": record.get("oxygen_saturation"),
                        "respiratory_rate": record.get("respiratory_rate")
                    },
                    "anomalies": anomalies
                })
    
    print(f"Found {len(results)} records with anomalies")
    return results

def generate_alerts(anomaly_results):
    """Generate alerts from anomaly detection results."""
    print("Generating alerts from anomaly results")
    
    # Create alert manager
    alert_manager = PatientAlertManager()
    
    # Process each result
    for result in anomaly_results:
        # Process the anomalies
        alert_manager.process_anomalies(
            result["patient_id"],
            result["timestamp"],
            result["vitals"],
            result["anomalies"]
        )
    
    # Export alerts to JSON
    alert_manager.export_alerts_to_json("patient_alerts.json")
    
    return alert_manager

def run_pipeline(mode="batch", duration=60, patient_count=5, detector_type="simple", input_path="patient_data.jsonl"):
    """Run the entire patient monitoring pipeline."""
    print(f"Starting patient monitoring pipeline in {mode} mode")
    
    if mode == "generate":
        # Just generate data
        simulate_data(duration, patient_count)
    
    elif mode == "stream":
        # Run in streaming mode
        process_patient_data(mode="stream")
    
    else:
        # Run in batch mode
        patient_data = process_patient_data(mode="batch", input_path=input_path)
        
        if patient_data:
            # Detect anomalies
            anomaly_results = detect_anomalies(patient_data, detector_type)
            
            # Generate alerts
            alert_manager = generate_alerts(anomaly_results)
            
            # Print summary
            print("\nPipeline complete!")
            print(f"Processed {len(patient_data)} patient records")
            print(f"Found {len(anomaly_results)} records with anomalies")
            
            # Count alerts by severity
            alerts_count = sum(len(alerts) for alerts in alert_manager.alert_history.values())
            print(f"Generated {alerts_count} alerts")

def main():
    """Main entry point with command line arguments."""
    parser = argparse.ArgumentParser(description="Patient Monitoring Pipeline")
    
    parser.add_argument("--mode", choices=["batch", "stream", "generate"], default="batch",
                      help="Mode to run the pipeline (batch, stream, or generate)")
    
    parser.add_argument("--duration", type=int, default=60,
                      help="Duration in seconds for data generation")
    
    parser.add_argument("--patients", type=int, default=5,
                      help="Number of patients to simulate")
    
    parser.add_argument("--detector", choices=["simple", "statistical"], default="simple",
                      help="Type of anomaly detector to use")
    
    parser.add_argument("--input", default="patient_data.jsonl",
                      help="Input file for batch processing")
    
    args = parser.parse_args()
    
    # Run the pipeline with the provided arguments
    run_pipeline(
        mode=args.mode,
        duration=args.duration,
        patient_count=args.patients,
        detector_type=args.detector,
        input_path=args.input
    )

if __name__ == "__main__":
    main() 