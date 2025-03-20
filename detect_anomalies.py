#!/usr/bin/env python3
"""
Quick script to test anomaly detection on generated data.
"""
import json
import sys
sys.path.append('.')
from src.anomaly_detection.detector import SimpleAnomalyDetector

detector = SimpleAnomalyDetector()
anomalies_found = 0
total_records = 0

with open('patient_data.jsonl', 'r') as f:
    for line in f:
        total_records += 1
        data = json.loads(line)
        anomalies = detector.check_vital_thresholds(data)
        if anomalies:
            anomalies_found += 1
            print(f'Found anomaly for patient {data["patient_id"][-6:]}:')
            for a in anomalies:
                print(f'  - {a["vital"]}: {a["value"]} ({a["reason"]})')
            print()

print(f'Processed {total_records} records, found {anomalies_found} anomalies') 