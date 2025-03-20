import os
import sys
import json
from datetime import datetime

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

try:
    from pyspark.sql import SparkSession
    from pyspark.sql.types import StructType, StructField, StringType, DoubleType, BooleanType, TimestampType
    from pyspark.sql.functions import col, udf, explode, split, from_json, window
except ImportError:
    print("PySpark is not installed. Run: pip install pyspark")
    sys.exit(1)

from src.anomaly_detection.detector import SimpleAnomalyDetector

class PatientDataProcessor:
    """
    Process patient data using PySpark.
    This is a simple implementation for learning purposes.
    """
    
    def __init__(self):
        # Initialize Spark session
        self.spark = SparkSession.builder \
            .appName("PatientDataProcessor") \
            .master("local[*]") \
            .getOrCreate()
        
        # Set log level to reduce verbosity
        self.spark.sparkContext.setLogLevel("WARN")
        
        # Create anomaly detector
        self.anomaly_detector = SimpleAnomalyDetector()
        
        # Define schema for patient data
        self.patient_schema = StructType([
            StructField("patient_id", StringType(), True),
            StructField("timestamp", StringType(), True),
            StructField("heart_rate", DoubleType(), True),
            StructField("temperature", DoubleType(), True),
            StructField("blood_pressure", StringType(), True),
            StructField("oxygen_saturation", DoubleType(), True), 
            StructField("respiratory_rate", DoubleType(), True),
            StructField("contains_anomaly", BooleanType(), True),
            StructField("anomaly_vital", StringType(), True)
        ])
        
        print("Initialized PySpark processor")
    
    def process_batch_data(self, input_path):
        """Process a batch of patient data from a file."""
        print(f"Processing batch data from {input_path}")
        
        # Read data
        df = self.spark.read.json(input_path, schema=self.patient_schema)
        
        # Show the data
        print("Sample of patient data:")
        df.show(5, truncate=False)
        
        # Basic statistics
        print("Basic statistics for vital signs:")
        df.select("heart_rate", "temperature", "oxygen_saturation", "respiratory_rate") \
          .describe() \
          .show()
        
        # Count anomalies
        anomaly_count = df.filter(df.contains_anomaly == True).count()
        total_count = df.count()
        print(f"Found {anomaly_count} anomalies out of {total_count} records ({anomaly_count/total_count*100:.2f}%)")
        
        # Group anomalies by type
        print("Anomalies by vital sign:")
        df.filter(df.contains_anomaly == True) \
          .groupBy("anomaly_vital") \
          .count() \
          .show()
        
        # Group by patient
        print("Records by patient:")
        df.groupBy("patient_id") \
          .count() \
          .show()
        
        return df
    
    def setup_streaming(self, checkpoint_dir="checkpoint"):
        """Set up a streaming context to read from a directory."""
        # Create a checkpoint directory if it doesn't exist
        if not os.path.exists(checkpoint_dir):
            os.makedirs(checkpoint_dir)
        
        # Define UDF for anomaly detection
        def detect_anomalies(data_str):
            try:
                # Parse the JSON string
                data = json.loads(data_str)
                
                # Detect anomalies
                anomalies = self.anomaly_detector.check_vital_thresholds(data)
                
                # Return results
                return json.dumps({
                    "patient_id": data.get("patient_id"),
                    "timestamp": data.get("timestamp"),
                    "anomalies": anomalies,
                    "has_anomalies": len(anomalies) > 0
                })
            except Exception as e:
                return json.dumps({"error": str(e)})
        
        # Register the UDF
        detect_anomalies_udf = udf(detect_anomalies, StringType())
        
        # Return the UDF for use in streaming
        return detect_anomalies_udf
    
    def process_stream(self, input_dir="stream_input", output_dir="stream_output", checkpoint_dir="checkpoint"):
        """
        Process a stream of patient data.
        This simulates reading from EventHub by watching a directory.
        """
        print(f"Setting up streaming from {input_dir}")
        
        # Create directories if they don't exist
        for dir_path in [input_dir, output_dir, checkpoint_dir]:
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
        
        # Create streaming DataFrame from the input directory
        streaming_df = self.spark.readStream \
            .format("json") \
            .schema(self.patient_schema) \
            .option("maxFilesPerTrigger", 1) \
            .load(input_dir)
        
        # Process the streaming data
        processed_df = streaming_df.withColumn(
            "timestamp", 
            col("timestamp").cast(TimestampType())
        )
        
        # Group by window to create batch-like views of the stream
        windowed_df = processed_df \
            .groupBy(window(col("timestamp"), "1 minute"), "patient_id") \
            .agg({"heart_rate": "avg", "temperature": "avg", "oxygen_saturation": "avg", "respiratory_rate": "avg"}) \
            .withColumnRenamed("avg(heart_rate)", "avg_heart_rate") \
            .withColumnRenamed("avg(temperature)", "avg_temperature") \
            .withColumnRenamed("avg(oxygen_saturation)", "avg_oxygen") \
            .withColumnRenamed("avg(respiratory_rate)", "avg_respiratory")
        
        # Count anomalies in each window
        anomaly_counts = processed_df \
            .filter(col("contains_anomaly") == True) \
            .groupBy(window(col("timestamp"), "1 minute"), "patient_id", "anomaly_vital") \
            .count()
        
        # Write the output
        query1 = windowed_df.writeStream \
            .outputMode("complete") \
            .format("console") \
            .option("truncate", False) \
            .start()
        
        query2 = anomaly_counts.writeStream \
            .outputMode("complete") \
            .format("console") \
            .option("truncate", False) \
            .start()
        
        # Save the results to CSV files
        query3 = windowed_df.writeStream \
            .outputMode("append") \
            .format("csv") \
            .option("path", os.path.join(output_dir, "averages")) \
            .option("checkpointLocation", os.path.join(checkpoint_dir, "averages")) \
            .start()
        
        query4 = anomaly_counts.writeStream \
            .outputMode("append") \
            .format("csv") \
            .option("path", os.path.join(output_dir, "anomalies")) \
            .option("checkpointLocation", os.path.join(checkpoint_dir, "anomalies")) \
            .start()
        
        print("Streaming queries started. Press Ctrl+C to stop.")
        
        try:
            # Keep the program running until terminated
            query1.awaitTermination()
        except KeyboardInterrupt:
            print("Terminating streams...")
            query1.stop()
            query2.stop()
            query3.stop()
            query4.stop()
            print("Streams terminated.")
    
    def stop(self):
        """Stop the Spark session."""
        self.spark.stop()
        print("Spark session stopped.")

# Example usage
if __name__ == "__main__":
    # Create processor
    processor = PatientDataProcessor()
    
    try:
        # Process a batch of data
        if len(sys.argv) > 1 and sys.argv[1] == "--stream":
            # Process streaming data
            processor.process_stream()
        else:
            # Process batch data
            processor.process_batch_data("patient_data.jsonl")
    except KeyboardInterrupt:
        print("Processing stopped by user")
    finally:
        # Stop Spark
        processor.stop() 