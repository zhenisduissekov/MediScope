import random
from faker import Faker
from datetime import datetime, timedelta
import json
import numpy as np

fake = Faker()

# Common departments in a hospital
departments = [
    'Cardiology', 'Neurology', 'Oncology', 'Pediatrics', 'Emergency',
    'Intensive Care Unit (ICU)', 'Maternity', 'Orthopedics', 'Surgery', 'Radiology'
]

# Common diagnoses
common_diagnoses = {
    'Cardiology': ['Hypertension', 'Coronary Artery Disease', 'Arrhythmia', 'Heart Failure'],
    'Neurology': ['Migraine', 'Epilepsy', 'Stroke', 'Parkinson\'s'],
    'Oncology': ['Breast Cancer', 'Lung Cancer', 'Leukemia', 'Lymphoma'],
    'Emergency': ['Fracture', 'Laceration', 'Concussion', 'Burn'],
    'Pediatrics': ['Asthma', 'Ear Infection', 'Bronchiolitis', 'Gastroenteritis']
}

def generate_vitals(age):
    """Generate realistic vital signs based on patient age."""
    # Base vitals with some randomness
    if age < 1:  # Infant
        heart_rate = random.randint(100, 160)
        bp_systolic = random.randint(65, 100)
        bp_diastolic = random.randint(40, 70)
        temp = round(random.uniform(36.5, 37.5), 1)
        resp_rate = random.randint(20, 40)
    elif age < 12:  # Child
        heart_rate = random.randint(70, 120)
        bp_systolic = random.randint(80, 110)
        bp_diastolic = random.randint(50, 80)
        temp = round(random.uniform(36.0, 37.2), 1)
        resp_rate = random.randint(16, 30)
    else:  # Adult
        heart_rate = random.randint(60, 100)
        bp_systolic = random.randint(90, 140)
        bp_diastolic = random.randint(60, 90)
        temp = round(random.uniform(36.2, 37.2), 1)
        resp_rate = random.randint(12, 20)
    
    # Add some random variation
    heart_rate += random.randint(-5, 5)
    bp_systolic += random.randint(-5, 5)
    bp_diastolic += random.randint(-3, 3)
    temp += round(random.uniform(-0.2, 0.2), 1)
    
    return {
        'heart_rate': max(40, min(heart_rate, 200)),
        'blood_pressure': f"{max(60, min(bp_systolic, 200))}/{max(40, min(bp_diastolic, 120))}",
        'temperature': round(max(35.0, min(temp, 39.0)), 1),
        'respiratory_rate': max(8, min(resp_rate, 40)),
        'oxygen_saturation': random.randint(90, 100),
        'timestamp': datetime.now().isoformat()
    }

def generate_patient():
    """Generate a simulated patient record."""
    age = random.randint(1, 100)
    gender = random.choice(['Male', 'Female'])
    department = random.choice(departments)
    
    # Generate a realistic admission date (within last 14 days)
    admission_date = datetime.now() - timedelta(days=random.randint(0, 14))
    
    # Generate a realistic discharge date (if applicable)
    if random.random() < 0.7:  # 70% chance patient is still admitted
        discharge_date = None
        status = 'Admitted'
    else:
        discharge_days = random.randint(1, 30)  # Stay duration 1-30 days
        discharge_date = admission_date + timedelta(days=discharge_days)
        status = 'Discharged'
    
    # Get appropriate diagnosis based on department
    diagnosis_category = random.choice(list(common_diagnoses.keys()))
    diagnosis = random.choice(common_diagnoses[diagnosis_category])
    
    # Generate vitals
    vitals = generate_vitals(age)
    
    patient = {
        'patient_id': fake.uuid4(),
        'medical_record_number': f"MRN{fake.unique.random_number(digits=8)}",
        'first_name': fake.first_name_male() if gender == 'Male' else fake.first_name_female(),
        'last_name': fake.last_name(),
        'age': age,
        'gender': gender,
        'department': department,
        'room': f"{random.choice(['A', 'B', 'C', 'D'])}{random.randint(100, 599)}",
        'admission_date': admission_date.isoformat(),
        'discharge_date': discharge_date.isoformat() if discharge_date else None,
        'status': status,
        'diagnosis': diagnosis,
        'vitals': vitals,
        'risk_score': None  # Will be calculated by AI predictor
    }
    
    return patient

def generate_patients(count=10):
    """Generate multiple patient records."""
    return [generate_patient() for _ in range(count)]

def save_patients_to_json(patients, filename='data/patients.json'):
    """Save patient data to a JSON file."""
    with open(filename, 'w') as f:
        json.dump(patients, f, indent=2, default=str)

def load_patients_from_json(filename='data/patients.json'):
    """Load patient data from a JSON file."""
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

if __name__ == "__main__":
    # Generate and save sample patient data
    patients = generate_patients(50)
    save_patients_to_json(patients)
    print(f"Generated {len(patients)} patient records in data/patients.json")
