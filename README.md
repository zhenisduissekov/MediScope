# MediScope - Healthcare Data Platform

MediScope is a real-time healthcare data visualization and monitoring platform designed for hospital environments. This demo application simulates a healthcare data platform with patient monitoring, risk assessment, and hospital capacity tracking.

## Features

- **Real-time Patient Monitoring**: Track patient vitals and status in real-time
- **Risk Assessment**: AI-powered risk scoring for patients
- **Hospital Capacity**: Visualize bed occupancy and department utilization
- **Patient Flow**: Track admissions and discharges over time
- **Interactive Dashboard**: Filter and explore patient data
- **Data Export**: Export patient data for further analysis

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/mediscope.git
   cd mediscope
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Run the Streamlit app:
   ```bash
   streamlit run streamlit_app.py
   ```

2. Open your web browser and navigate to `http://localhost:8501`

3. Use the sidebar to filter patients by department, risk level, and status

## Data Generation

The application comes with a built-in patient data generator. To generate new patient data:

1. Click the "Generate New Dataset" button in the sidebar
2. Or run the patient generator script directly:
   ```bash
   python patient_generator.py
   ```

## Project Structure

```
mediscope/
├── streamlit_app.py             # Main Streamlit application
├── patient_generator.py         # Generates mock patient data
├── ai_predictor.py              # Risk assessment logic
├── utils.py                     # Helper functions
├── data/                        # Data directory
│   └── patients.json           # Patient data (auto-generated)
├── README.md                   # This file
└── requirements.txt             # Python dependencies
```

## Dependencies

- streamlit==1.32.0
- pandas==2.0.3
- numpy==1.24.4
- plotly==5.18.0
- faker==22.0.0
- python-dateutil==2.8.2

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built with ❤️ for healthcare professionals
- Inspired by real-world hospital management systems
- Powered by Streamlit and Plotly
