import os
import sys
import json
import logging
from datetime import datetime

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from config.settings import ALERT_LEVELS, LOG_FILE, LOG_LEVEL

class PatientAlertManager:
    """
    Manages alerts generated from patient data anomalies.
    """
    
    def __init__(self, log_file=LOG_FILE):
        # Set up logging
        self.logger = logging.getLogger("PatientAlertSystem")
        
        # Set log level
        log_level = getattr(logging, LOG_LEVEL.upper(), logging.INFO)
        self.logger.setLevel(log_level)
        
        # Create file handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level)
        
        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        
        # Create formatter and add to handlers
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Add handlers to logger
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        # Alert history
        self.alert_history = {}
    
    def process_anomalies(self, patient_id, timestamp, vitals, anomalies):
        """
        Process a list of anomalies and generate appropriate alerts.
        """
        if not anomalies:
            return
        
        # Determine overall alert level based on anomaly severity
        alert_level = "LOW"
        for anomaly in anomalies:
            severity = anomaly.get("severity", "low").upper()
            if ALERT_LEVELS.get(severity, 1) > ALERT_LEVELS.get(alert_level, 1):
                alert_level = severity
        
        # Format alert message
        alert_msg = self._format_alert_message(patient_id, timestamp, vitals, anomalies, alert_level)
        
        # Log the alert based on its level
        if alert_level == "LOW":
            self.logger.info(alert_msg)
        elif alert_level == "MEDIUM":
            self.logger.warning(alert_msg)
        elif alert_level == "HIGH":
            self.logger.error(alert_msg)
        elif alert_level == "CRITICAL":
            self.logger.critical(alert_msg)
        
        # Store in history
        if patient_id not in self.alert_history:
            self.alert_history[patient_id] = []
        
        self.alert_history[patient_id].append({
            "timestamp": timestamp,
            "level": alert_level,
            "anomalies": anomalies,
            "vitals": vitals
        })
    
    def _format_alert_message(self, patient_id, timestamp, vitals, anomalies, level):
        """Format alert message for logging."""
        anomaly_list = ""
        for i, anomaly in enumerate(anomalies, 1):
            vital = anomaly["vital"]
            value = anomaly["value"]
            reason = anomaly["reason"]
            threshold = anomaly.get("threshold", "N/A")
            
            if "above" in reason:
                comparison = ">"
            elif "below" in reason:
                comparison = "<"
            else:
                comparison = "!="
            
            anomaly_list += f"  {i}. {vital} {reason}: {value} {comparison} {threshold}\n"
        
        # Format vitals for display
        vitals_display = "Vital signs:\n"
        if "heart_rate" in vitals:
            vitals_display += f"  Heart rate: {vitals['heart_rate']} bpm\n"
        if "temperature" in vitals:
            vitals_display += f"  Temperature: {vitals['temperature']} °C\n"
        if "blood_pressure" in vitals:
            vitals_display += f"  Blood pressure: {vitals['blood_pressure']} mmHg\n"
        if "oxygen_saturation" in vitals:
            vitals_display += f"  Oxygen saturation: {vitals['oxygen_saturation']}%\n"
        if "respiratory_rate" in vitals:
            vitals_display += f"  Respiratory rate: {vitals['respiratory_rate']} breaths/min\n"
        
        # Create full message
        message = f"[{level}] Patient {patient_id} at {timestamp}\n{anomaly_list}\n{vitals_display}"
        
        return message
    
    def get_patient_alerts(self, patient_id, limit=10):
        """Get recent alerts for a patient."""
        if patient_id not in self.alert_history:
            return []
        
        return self.alert_history[patient_id][-limit:]
    
    def export_alerts_to_json(self, filename="patient_alerts.json"):
        """Export all alerts to a JSON file."""
        with open(filename, 'w') as f:
            json.dump(self.alert_history, f, indent=2)
        
        print(f"Exported {sum(len(alerts) for alerts in self.alert_history.values())} alerts to {filename}")

# Example usage
if __name__ == "__main__":
    # Create alert manager
    alert_manager = PatientAlertManager()
    
    # Sample patient data with anomalies
    patient_data = {
        "patient_id": "test-patient-002",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "vitals": {
            "heart_rate": 135.0,
            "temperature": 39.5,
            "blood_pressure": "125/85",
            "oxygen_saturation": 94.0,
            "respiratory_rate": 18.0
        },
        "anomalies": [
            {
                "vital": "heart_rate",
                "value": 135.0,
                "reason": "above normal",
                "threshold": 100,
                "severity": "medium"
            },
            {
                "vital": "temperature",
                "value": 39.5,
                "reason": "critically high",
                "threshold": 38.5,
                "severity": "high"
            }
        ]
    }
    
    # Process the anomalies
    alert_manager.process_anomalies(
        patient_data["patient_id"],
        patient_data["timestamp"],
        patient_data["vitals"],
        patient_data["anomalies"]
    )
    
    # Get recent alerts for the patient
    recent_alerts = alert_manager.get_patient_alerts(patient_data["patient_id"])
    print(f"Recent alerts for patient: {len(recent_alerts)}")
    
    # Export alerts to JSON
    alert_manager.export_alerts_to_json("demo_alerts.json") 