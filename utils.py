import pandas as pd
from datetime import datetime, timedelta
import random
import json

def calculate_bed_occupancy(patients, department=None):
    """Calculate bed occupancy statistics."""
    if department:
        dept_patients = [p for p in patients if p['department'] == department]
    else:
        dept_patients = patients
    
    total_beds = {
        'Cardiology': 50,
        'Neurology': 40,
        'Oncology': 60,
        'Pediatrics': 45,
        'Emergency': 30,
        'Intensive Care Unit (ICU)': 25,
        'Maternity': 35,
        'Orthopedics': 40,
        'Surgery': 30,
        'Radiology': 10
    }
    
    # Count occupied beds by department
    occupied_beds = {}
    for dept in total_beds.keys():
        occupied = len([p for p in patients if p['department'] == dept and p['status'] == 'Admitted'])
        occupied_beds[dept] = occupied
    
    # Calculate occupancy rates
    occupancy_rates = {}
    for dept, beds in total_beds.items():
        occupied = occupied_beds.get(dept, 0)
        occupancy_rates[dept] = {
            'occupied': occupied,
            'available': max(0, beds - occupied),
            'total': beds,
            'occupancy_rate': (occupied / beds) * 100 if beds > 0 else 0
        }
    
    return occupancy_rates

def calculate_patient_flow(patients, days=7):
    """Calculate patient admissions and discharges over the past N days."""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # Initialize data structure
    flow_data = []
    for i in range(days + 1):
        date = start_date + timedelta(days=i)
        date_str = date.strftime('%Y-%m-%d')
        flow_data.append({
            'date': date_str,
            'admissions': 0,
            'discharges': 0
        })
    
    # Count admissions and discharges
    for patient in patients:
        admit_date = datetime.fromisoformat(patient['admission_date']).date()
        discharge_date = datetime.fromisoformat(patient['discharge_date']).date() if patient['discharge_date'] else None
        
        # Check admission date
        delta = (admit_date - start_date.date()).days
        if 0 <= delta <= days:
            flow_data[delta]['admissions'] += 1
        
        # Check discharge date
        if discharge_date:
            delta = (discharge_date - start_date.date()).days
            if 0 <= delta <= days:
                flow_data[delta]['discharges'] += 1
    
    return flow_data

def get_patient_statistics(patients):
    """Calculate various statistics about patients."""
    if not patients:
        return {}
    
    # Basic counts
    total_patients = len(patients)
    admitted = len([p for p in patients if p['status'] == 'Admitted'])
    discharged = total_patients - admitted
    
    # Age statistics
    ages = [p['age'] for p in patients]
    avg_age = sum(ages) / len(ages)
    
    # Risk distribution
    risk_levels = {}
    for p in patients:
        risk = p.get('risk_level', 'Unknown')
        risk_levels[risk] = risk_levels.get(risk, 0) + 1
    
    # Department distribution
    dept_dist = {}
    for p in patients:
        dept = p['department']
        dept_dist[dept] = dept_dist.get(dept, 0) + 1
    
    # Average risk score
    risk_scores = [p.get('risk_score', 0) for p in patients if 'risk_score' in p]
    avg_risk = sum(risk_scores) / len(risk_scores) if risk_scores else 0
    
    return {
        'total_patients': total_patients,
        'admitted': admitted,
        'discharged': discharged,
        'average_age': round(avg_age, 1),
        'risk_distribution': risk_levels,
        'department_distribution': dept_dist,
        'average_risk_score': round(avg_risk, 2)
    }

def filter_patients(patients, filters):
    """Filter patients based on provided criteria."""
    filtered = patients
    
    if 'department' in filters and filters['department']:
        filtered = [p for p in filtered if p['department'] == filters['department']]
    
    if 'risk_level' in filters and filters['risk_level']:
        filtered = [p for p in filtered if p.get('risk_level') == filters['risk_level']]
    
    if 'status' in filters and filters['status']:
        filtered = [p for p in filtered if p['status'] == filters['status']]
    
    if 'search' in filters and filters['search']:
        search_term = filters['search'].lower()
        filtered = [
            p for p in filtered
            if (search_term in p['first_name'].lower() or
                search_term in p['last_name'].lower() or
                search_term in p['medical_record_number'].lower() or
                search_term in p['room'].lower())
        ]
    
    return filtered

def patients_to_dataframe(patients):
    """Convert patient data to a pandas DataFrame for display."""
    if not patients:
        return pd.DataFrame()
    
    # Flatten the patient data for display
    flat_patients = []
    for p in patients:
        flat = {
            'ID': p['patient_id'],
            'MRN': p['medical_record_number'],
            'Name': f"{p['last_name']}, {p['first_name']}",
            'Age': p['age'],
            'Gender': p['gender'],
            'Department': p['department'],
            'Room': p['room'],
            'Admission Date': p['admission_date'].split('T')[0],
            'Status': p['status'],
            'Diagnosis': p['diagnosis'],
            'Risk Level': p.get('risk_level', 'Not Assessed'),
            'Risk Score': p.get('risk_score', 0)
        }
        flat_patients.append(flat)
    
    return pd.DataFrame(flat_patients)
