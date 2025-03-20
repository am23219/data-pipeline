#!/bin/bash

# Simple script to run the patient monitoring pipeline

# Define colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Patient Monitoring Pipeline${NC}"
echo "----------------------------------------"

# Check if Python and pip are installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python 3 is not installed. Please install Python 3 to continue.${NC}"
    exit 1
fi

# Function to print help
print_help() {
    echo "Usage: ./run_pipeline.sh [OPTION]"
    echo ""
    echo "Options:"
    echo "  generate   Generate sample patient data"
    echo "  batch      Process data in batch mode (default)"
    echo "  stream     Process data in streaming mode"
    echo "  help       Show this help message"
    echo ""
    echo "Examples:"
    echo "  ./run_pipeline.sh generate   # Generate sample data for 60 seconds"
    echo "  ./run_pipeline.sh batch      # Process existing data in batch mode"
    echo "  ./run_pipeline.sh stream     # Process data in streaming mode"
}

# Check if the .env file exists
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}Warning: .env file not found. Creating from .env.example${NC}"
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo -e "${YELLOW}Created .env file from .env.example. Please update with your actual settings.${NC}"
    else
        echo -e "${RED}Error: .env.example not found. Please create a .env file manually.${NC}"
        exit 1
    fi
fi

# Check if virtual environment exists, create if not
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv venv
    source venv/bin/activate
    echo -e "${YELLOW}Installing dependencies...${NC}"
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

echo -e "${GREEN}Using Python:${NC} $(which python)"

# Create necessary directories
mkdir -p stream_input stream_output checkpoint

# Parse command line arguments
MODE="batch"
if [ $# -gt 0 ]; then
    case $1 in
        generate)
            MODE="generate"
            ;;
        batch)
            MODE="batch"
            ;;
        stream)
            MODE="stream"
            ;;
        help)
            print_help
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            print_help
            exit 1
            ;;
    esac
fi

# Additional parameters
DURATION=60
PATIENTS=5
DETECTOR="simple"
INPUT_FILE="patient_data.jsonl"

# Run the pipeline
echo -e "${GREEN}Running pipeline in ${MODE} mode...${NC}"
python src/main.py --mode ${MODE} --duration ${DURATION} --patients ${PATIENTS} --detector ${DETECTOR} --input ${INPUT_FILE}

echo -e "${GREEN}Pipeline execution complete!${NC}"

# Deactivate virtual environment
deactivate 