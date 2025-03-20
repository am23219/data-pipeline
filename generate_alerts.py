#!/usr/bin/env python3
"""
Quick script to test alert generation on detected anomalies.
"""
import json
import sys
sys.path.append('.')
from src.anomaly_detection.detector import SimpleAnomalyDetector
from src.alerting.alert_manager import PatientAlertManager

# Create the detector and alert manager
detector = SimpleAnomalyDetector()
alert_manager = PatientAlertManager()

# Process each data point
total_records = 0
anomalies_found = 0
alerts_generated = 0

print("Processing patient data and generating alerts...")
with open('patient_data.jsonl', 'r') as f:
    for line in f:
        total_records += 1
        data = json.loads(line)
        
        # Detect anomalies
        anomalies = detector.check_vital_thresholds(data)
        
        if anomalies:
            anomalies_found += 1
            
            # Generate alerts
            alert_manager.process_anomalies(
                data["patient_id"],
                data["timestamp"],
                {
                    "heart_rate": data["heart_rate"],
                    "temperature": data["temperature"],
                    "blood_pressure": data["blood_pressure"],
                    "oxygen_saturation": data["oxygen_saturation"],
                    "respiratory_rate": data["respiratory_rate"]
                },
                anomalies
            )

# Count alerts
total_alerts = sum(len(alerts) for patient_id, alerts in alert_manager.alert_history.items())

# Display summary
print(f"\nProcessed {total_records} records")
print(f"Found {anomalies_found} data points with anomalies")
print(f"Generated {total_alerts} alerts for {len(alert_manager.alert_history)} patients")

# Define level mapping for comparison
level_map = {
    "CRITICAL": 3,
    "HIGH": 2,
    "MEDIUM": 1,
    "LOW": 0
}

# Show sample alerts for each patient
print("\nSample alerts by patient:")

for patient_id, alerts in alert_manager.alert_history.items():
    # Get highest level alert
    highest_alert = None
    highest_level = 0
    
    for alert in alerts:
        if level_map[alert["level"]] > highest_level:
            highest_level = level_map[alert["level"]]
            highest_alert = alert
    
    short_id = patient_id.split('-')[-1]
    print(f"\nPatient {short_id} - {len(alerts)} alerts:")
    if highest_alert:
        print(f"  Highest level: {highest_alert['level']} (at {highest_alert['timestamp']})")
        # Display vital signs from the highest alert
        if "description" in highest_alert:
            print(f"  Issues: {highest_alert['description']}")
        
        # Count most common anomalies
        anomaly_counts = {}
        for alert in alerts:
            if "vitals" in alert:
                for vital, is_anomaly in alert["vitals"].items():
                    if is_anomaly and vital != "contains_anomaly":
                        anomaly_counts[vital] = anomaly_counts.get(vital, 0) + 1
        
        # Display most common issues
        if anomaly_counts:
            print("  Most common issues:")
            for vital, count in sorted(anomaly_counts.items(), key=lambda x: x[1], reverse=True)[:3]:
                print(f"    - {vital}: {count} occurrences") 