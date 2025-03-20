import os
import sys
import numpy as np
from sklearn.ensemble import IsolationForest
import pandas as pd

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from config.settings import VITAL_RANGES

class SimpleAnomalyDetector:
    """Simple threshold-based anomaly detector for patient vitals."""
    
    def __init__(self):
        self.vital_ranges = VITAL_RANGES
    
    def check_vital_thresholds(self, patient_data):
        """
        Check if vitals are outside normal ranges.
        Returns a list of anomalies found.
        """
        anomalies = []
        
        # Check heart rate
        heart_rate = patient_data.get("heart_rate")
        if heart_rate:
            hr_range = self.vital_ranges["heart_rate"]
            if heart_rate < hr_range["min"]:
                anomalies.append({
                    "vital": "heart_rate",
                    "value": heart_rate,
                    "reason": "below normal",
                    "threshold": hr_range["min"],
                    "severity": "medium"
                })
            elif heart_rate > hr_range["max"]:
                anomalies.append({
                    "vital": "heart_rate",
                    "value": heart_rate,
                    "reason": "above normal",
                    "threshold": hr_range["max"],
                    "severity": "medium"
                })
            
            # Check critical thresholds
            if heart_rate < hr_range["critical_min"]:
                anomalies.append({
                    "vital": "heart_rate",
                    "value": heart_rate,
                    "reason": "critically low",
                    "threshold": hr_range["critical_min"],
                    "severity": "high"
                })
            elif heart_rate > hr_range["critical_max"]:
                anomalies.append({
                    "vital": "heart_rate",
                    "value": heart_rate,
                    "reason": "critically high",
                    "threshold": hr_range["critical_max"],
                    "severity": "high"
                })
        
        # Check temperature
        temperature = patient_data.get("temperature")
        if temperature:
            temp_range = self.vital_ranges["temperature"]
            if temperature < temp_range["min"]:
                anomalies.append({
                    "vital": "temperature",
                    "value": temperature,
                    "reason": "below normal",
                    "threshold": temp_range["min"],
                    "severity": "medium"
                })
            elif temperature > temp_range["max"]:
                anomalies.append({
                    "vital": "temperature",
                    "value": temperature,
                    "reason": "above normal",
                    "threshold": temp_range["max"],
                    "severity": "medium"
                })
            
            # Check critical thresholds
            if temperature < temp_range["critical_min"]:
                anomalies.append({
                    "vital": "temperature",
                    "value": temperature,
                    "reason": "critically low",
                    "threshold": temp_range["critical_min"],
                    "severity": "high"
                })
            elif temperature > temp_range["critical_max"]:
                anomalies.append({
                    "vital": "temperature",
                    "value": temperature,
                    "reason": "critically high",
                    "threshold": temp_range["critical_max"],
                    "severity": "high"
                })
        
        # Check oxygen saturation
        oxygen = patient_data.get("oxygen_saturation")
        if oxygen:
            oxygen_range = self.vital_ranges["oxygen_saturation"]
            if oxygen < oxygen_range["min"]:
                anomalies.append({
                    "vital": "oxygen_saturation",
                    "value": oxygen,
                    "reason": "below normal",
                    "threshold": oxygen_range["min"],
                    "severity": "medium"
                })
            
            # Check critical threshold
            if oxygen < oxygen_range["critical_min"]:
                anomalies.append({
                    "vital": "oxygen_saturation",
                    "value": oxygen,
                    "reason": "critically low",
                    "threshold": oxygen_range["critical_min"],
                    "severity": "high"
                })
        
        # Check respiratory rate
        resp_rate = patient_data.get("respiratory_rate")
        if resp_rate:
            resp_range = self.vital_ranges["respiratory_rate"]
            if resp_rate < resp_range["min"]:
                anomalies.append({
                    "vital": "respiratory_rate",
                    "value": resp_rate,
                    "reason": "below normal",
                    "threshold": resp_range["min"],
                    "severity": "medium"
                })
            elif resp_rate > resp_range["max"]:
                anomalies.append({
                    "vital": "respiratory_rate",
                    "value": resp_rate,
                    "reason": "above normal",
                    "threshold": resp_range["max"],
                    "severity": "medium"
                })
            
            # Check critical thresholds
            if resp_rate < resp_range["critical_min"]:
                anomalies.append({
                    "vital": "respiratory_rate",
                    "value": resp_rate,
                    "reason": "critically low",
                    "threshold": resp_range["critical_min"],
                    "severity": "high"
                })
            elif resp_rate > resp_range["critical_max"]:
                anomalies.append({
                    "vital": "respiratory_rate",
                    "value": resp_rate,
                    "reason": "critically high",
                    "threshold": resp_range["critical_max"],
                    "severity": "high"
                })
        
        # Check blood pressure
        if "blood_pressure" in patient_data:
            try:
                # Parse the blood pressure string (e.g., "120/80")
                bp_parts = patient_data["blood_pressure"].split("/")
                systolic = int(bp_parts[0])
                diastolic = int(bp_parts[1])
                
                # Check systolic
                systolic_range = self.vital_ranges["blood_pressure_systolic"]
                if systolic < systolic_range["min"]:
                    anomalies.append({
                        "vital": "blood_pressure_systolic",
                        "value": systolic,
                        "reason": "below normal",
                        "threshold": systolic_range["min"],
                        "severity": "medium"
                    })
                elif systolic > systolic_range["max"]:
                    anomalies.append({
                        "vital": "blood_pressure_systolic",
                        "value": systolic,
                        "reason": "above normal",
                        "threshold": systolic_range["max"],
                        "severity": "medium"
                    })
                
                # Check critical thresholds for systolic
                if systolic < systolic_range["critical_min"]:
                    anomalies.append({
                        "vital": "blood_pressure_systolic",
                        "value": systolic,
                        "reason": "critically low",
                        "threshold": systolic_range["critical_min"],
                        "severity": "high"
                    })
                elif systolic > systolic_range["critical_max"]:
                    anomalies.append({
                        "vital": "blood_pressure_systolic",
                        "value": systolic,
                        "reason": "critically high",
                        "threshold": systolic_range["critical_max"],
                        "severity": "high"
                    })
                
                # Check diastolic
                diastolic_range = self.vital_ranges["blood_pressure_diastolic"]
                if diastolic < diastolic_range["min"]:
                    anomalies.append({
                        "vital": "blood_pressure_diastolic",
                        "value": diastolic,
                        "reason": "below normal",
                        "threshold": diastolic_range["min"],
                        "severity": "medium"
                    })
                elif diastolic > diastolic_range["max"]:
                    anomalies.append({
                        "vital": "blood_pressure_diastolic",
                        "value": diastolic,
                        "reason": "above normal",
                        "threshold": diastolic_range["max"],
                        "severity": "medium"
                    })
                
                # Check critical thresholds for diastolic
                if diastolic < diastolic_range["critical_min"]:
                    anomalies.append({
                        "vital": "blood_pressure_diastolic",
                        "value": diastolic,
                        "reason": "critically low",
                        "threshold": diastolic_range["critical_min"],
                        "severity": "high"
                    })
                elif diastolic > diastolic_range["critical_max"]:
                    anomalies.append({
                        "vital": "blood_pressure_diastolic",
                        "value": diastolic,
                        "reason": "critically high",
                        "threshold": diastolic_range["critical_max"],
                        "severity": "high"
                    })
                
                # Check pulse pressure (difference between systolic and diastolic)
                pulse_pressure = systolic - diastolic
                if pulse_pressure > 50:
                    anomalies.append({
                        "vital": "pulse_pressure",
                        "value": pulse_pressure,
                        "reason": "abnormal systolic-diastolic difference",
                        "threshold": 50,
                        "severity": "medium"
                    })
                
            except (ValueError, IndexError) as e:
                # Handle invalid blood pressure format
                pass
        
        return anomalies

class StatisticalAnomalyDetector:
    """
    A more advanced anomaly detector using statistical methods.
    This is just a basic implementation using Isolation Forest.
    """
    
    def __init__(self):
        self.model = IsolationForest(contamination=0.05, random_state=42)
        self.history = {}
        self.is_trained = False
    
    def add_to_history(self, patient_id, data_point):
        """Add a data point to the patient's history."""
        if patient_id not in self.history:
            self.history[patient_id] = []
        
        # Extract the numeric vitals
        vitals = {
            "heart_rate": data_point.get("heart_rate", 0),
            "temperature": data_point.get("temperature", 0),
            "respiratory_rate": data_point.get("respiratory_rate", 0),
            "oxygen_saturation": data_point.get("oxygen_saturation", 0)
        }
        
        # Parse blood pressure
        if "blood_pressure" in data_point:
            try:
                bp_parts = data_point["blood_pressure"].split("/")
                vitals["systolic"] = int(bp_parts[0])
                vitals["diastolic"] = int(bp_parts[1])
            except (ValueError, IndexError):
                vitals["systolic"] = 0
                vitals["diastolic"] = 0
        
        # Add to history
        self.history[patient_id].append(vitals)
    
    def detect_anomalies(self, patient_id, new_data_point):
        """
        Detect anomalies using the Isolation Forest algorithm.
        Returns a boolean indicating if an anomaly was detected.
        """
        # Make sure we have enough data points
        if patient_id not in self.history or len(self.history[patient_id]) < 10:
            # Not enough data yet
            return False
        
        # Get the patient's history
        patient_history = self.history[patient_id]
        
        # Convert to DataFrame
        df = pd.DataFrame(patient_history)
        
        # Train the model if not already trained
        if not self.is_trained:
            self.model.fit(df)
            self.is_trained = True
        
        # Extract new data point features
        new_point = {
            "heart_rate": new_data_point.get("heart_rate", 0),
            "temperature": new_data_point.get("temperature", 0),
            "respiratory_rate": new_data_point.get("respiratory_rate", 0),
            "oxygen_saturation": new_data_point.get("oxygen_saturation", 0)
        }
        
        # Parse blood pressure
        if "blood_pressure" in new_data_point:
            try:
                bp_parts = new_data_point["blood_pressure"].split("/")
                new_point["systolic"] = int(bp_parts[0])
                new_point["diastolic"] = int(bp_parts[1])
            except (ValueError, IndexError):
                new_point["systolic"] = 0
                new_point["diastolic"] = 0
        
        # Predict
        new_df = pd.DataFrame([new_point])
        prediction = self.model.predict(new_df)
        
        # Isolation Forest returns -1 for anomalies and 1 for normal points
        return prediction[0] == -1

# Example usage
if __name__ == "__main__":
    # Create a simple detector
    detector = SimpleAnomalyDetector()
    
    # Test with a normal data point
    normal_data = {
        "patient_id": "test-patient-001",
        "heart_rate": 75.0,
        "temperature": 37.0,
        "blood_pressure": "120/80",
        "oxygen_saturation": 98.0,
        "respiratory_rate": 16.0
    }
    
    anomalies = detector.check_vital_thresholds(normal_data)
    print(f"Normal data anomalies: {anomalies}")
    
    # Test with an abnormal data point
    abnormal_data = {
        "patient_id": "test-patient-002",
        "heart_rate": 135.0,
        "temperature": 39.5,
        "blood_pressure": "160/95",
        "oxygen_saturation": 88.0,
        "respiratory_rate": 26.0
    }
    
    anomalies = detector.check_vital_thresholds(abnormal_data)
    print(f"Abnormal data anomalies: {len(anomalies)}")
    for anomaly in anomalies:
        print(f"  - {anomaly['vital']}: {anomaly['value']} ({anomaly['reason']})")
    
    # Try out the statistical detector
    print("\nTesting statistical detector:")
    stat_detector = StatisticalAnomalyDetector()
    
    # Add some history data
    for i in range(20):
        data = {
            "heart_rate": 70 + i % 10,
            "temperature": 36.5 + (i % 10) / 10,
            "blood_pressure": f"{120 + i % 10}/{75 + i % 5}",
            "oxygen_saturation": 97 + (i % 3),
            "respiratory_rate": 15 + (i % 5)
        }
        stat_detector.add_to_history("test-patient-003", data)
    
    # Test with a normal point
    normal = {
        "heart_rate": 75,
        "temperature": 37.0,
        "blood_pressure": "125/75",
        "oxygen_saturation": 98,
        "respiratory_rate": 16
    }
    
    is_anomaly = stat_detector.detect_anomalies("test-patient-003", normal)
    print(f"Normal point is anomaly: {is_anomaly}")
    
    # Test with an abnormal point
    abnormal = {
        "heart_rate": 150,
        "temperature": 40.0,
        "blood_pressure": "180/100",
        "oxygen_saturation": 85,
        "respiratory_rate": 30
    }
    
    is_anomaly = stat_detector.detect_anomalies("test-patient-003", abnormal)
    print(f"Abnormal point is anomaly: {is_anomaly}") 