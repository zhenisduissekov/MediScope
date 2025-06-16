import random
from datetime import datetime, timedelta
import numpy as np

def calculate_risk_score(patient):
    """
    Calculate a risk score for a patient based on various factors.
    Returns a dictionary with risk level and score components.
    """
    score = 0
    factors = {}
    
    # Age factor
    age = patient['age']
    if age > 75:
        age_score = 3
    elif age > 60:
        age_score = 2
    elif age > 40:
        age_score = 1
    else:
        age_score = 0
    score += age_score
    factors['age_score'] = age_score
    
    # Heart rate factor
    heart_rate = patient['vitals']['heart_rate']
    if heart_rate > 120 or heart_rate < 50:
        hr_score = 3
    elif heart_rate > 100 or heart_rate < 60:
        hr_score = 2
    else:
        hr_score = 0
    score += hr_score
    factors['heart_rate_score'] = hr_score
    
    # Blood pressure factor (systolic)
    bp_systolic = int(patient['vitals']['blood_pressure'].split('/')[0])
    if bp_systolic > 180 or bp_systolic < 90:
        bp_score = 3
    elif bp_systolic > 140 or bp_systolic < 100:
        bp_score = 2
    else:
        bp_score = 0
    score += bp_score
    factors['blood_pressure_score'] = bp_score
    
    # Temperature factor
    temp = patient['vitals']['temperature']
    if temp > 38.5 or temp < 35.5:
        temp_score = 2
    elif temp > 37.8 or temp < 36.0:
        temp_score = 1
    else:
        temp_score = 0
    score += temp_score
    factors['temperature_score'] = temp_score
    
    # Oxygen saturation factor
    spo2 = patient['vitals']['oxygen_saturation']
    if spo2 < 90:
        spo2_score = 3
    elif spo2 < 94:
        spo2_score = 1
    else:
        spo2_score = 0
    score += spo2_score
    factors['oxygen_score'] = spo2_score
    
    # Department factor (some departments are higher risk)
    high_risk_depts = ['Intensive Care Unit (ICU)', 'Cardiology', 'Neurology']
    medium_risk_depts = ['Emergency', 'Oncology', 'Surgery']
    
    if patient['department'] in high_risk_depts:
        dept_score = 2
    elif patient['department'] in medium_risk_depts:
        dept_score = 1
    else:
        dept_score = 0
    score += dept_score
    factors['department_score'] = dept_score
    
    # Length of stay factor (longer stays might indicate complications)
    admission_date = datetime.fromisoformat(patient['admission_date'])
    days_in_hospital = (datetime.now() - admission_date).days
    if days_in_hospital > 14:
        los_score = 2
    elif days_in_hospital > 7:
        los_score = 1
    else:
        los_score = 0
    score += los_score
    factors['length_of_stay_score'] = los_score
    
    # Determine risk level based on total score
    if score >= 10:
        risk_level = "Critical"
    elif score >= 7:
        risk_level = "High"
    elif score >= 4:
        risk_level = "Medium"
    else:
        risk_level = "Low"
    
    # Add some random variation to make it less deterministic
    if random.random() < 0.1:  # 10% chance to adjust risk level
        adjustments = ["Critical", "High", "Medium", "Low"]
        current_idx = adjustments.index(risk_level)
        if current_idx > 0 and random.random() < 0.5:
            risk_level = adjustments[current_idx - 1]
        elif current_idx < len(adjustments) - 1:
            risk_level = adjustments[current_idx + 1]
    
    return {
        'risk_level': risk_level,
        'risk_score': min(score, 15),  # Cap at 15 for visualization
        'factors': factors,
        'last_updated': datetime.now().isoformat()
    }

def update_patient_risk(patient):
    """Update a patient's risk assessment."""
    risk_assessment = calculate_risk_score(patient)
    patient['risk_assessment'] = risk_assessment
    patient['risk_level'] = risk_assessment['risk_level']
    patient['risk_score'] = risk_assessment['risk_score']
    return patient

def batch_update_risk(patients):
    """Update risk assessment for a list of patients."""
    return [update_patient_risk(p) for p in patients]
