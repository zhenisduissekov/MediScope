import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import time
from patient_generator import generate_patients, save_patients_to_json, load_patients_from_json
from ai_predictor import batch_update_risk
import utils

# Page configuration
st.set_page_config(
    page_title="MediScope - Healthcare Data Platform",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    .stMetric {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .stMetric h3 {
        color: #666;
        font-size: 0.9rem;
        margin-bottom: 0.5rem;
    }
    .stMetric div[data-testid="stMetricValue"] > div {
        font-size: 1.5rem;
        font-weight: 600;
        color: #1e3a8a;
    }
    .stButton>button {
        background-color: #3b82f6;
        color: white;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        border: none;
    }
    .stButton>button:hover {
        background-color: #2563eb;
        color: white;
    }
    .department-card {
        background-color: white;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .risk-critical { color: #dc2626; font-weight: bold; }
    .risk-high { color: #ea580c; font-weight: bold; }
    .risk-medium { color: #d97706; font-weight: bold; }
    .risk-low { color: #16a34a; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'patients' not in st.session_state:
    # Try to load existing data or generate new data
    try:
        patients = load_patients_from_json('data/patients.json')
        if not patients:
            raise FileNotFoundError
        st.session_state.patients = patients
    except (FileNotFoundError, json.JSONDecodeError):
        # Generate new patient data if file doesn't exist or is invalid
        patients = generate_patients(50)
        # Add risk assessment to patients
        patients = batch_update_risk(patients)
        st.session_state.patients = patients
        save_patients_to_json(patients, 'data/patients.json')

# Sidebar
st.sidebar.title("MediScope")
st.sidebar.markdown("### Filters")

# Department filter
departments = sorted(list(set(p['department'] for p in st.session_state.patients)))
selected_department = st.sidebar.selectbox(
    "Select Department",
    ["All Departments"] + departments,
    index=0
)

# Risk level filter
risk_levels = ["All Risk Levels", "Critical", "High", "Medium", "Low"]
selected_risk = st.sidebar.selectbox(
    "Select Risk Level",
    risk_levels,
    index=0
)

# Status filter
statuses = ["All Statuses", "Admitted", "Discharged"]
selected_status = st.sidebar.selectbox(
    "Select Status",
    statuses,
    index=0
)

# Search
search_term = st.sidebar.text_input("Search Patients")

# Apply filters
filters = {}
if selected_department != "All Departments":
    filters['department'] = selected_department
if selected_risk != "All Risk Levels":
    filters['risk_level'] = selected_risk
if selected_status != "All Statuses":
    filters['status'] = selected_status
if search_term:
    filters['search'] = search_term

# Filter patients
filtered_patients = utils.filter_patients(st.session_state.patients, filters)

# Sidebar actions
st.sidebar.markdown("---")
st.sidebar.markdown("### Actions")

if st.sidebar.button("🔄 Refresh Data"):
    # Generate a few new patients and add to existing ones
    new_patients = generate_patients(5)
    new_patients = batch_update_risk(new_patients)
    st.session_state.patients.extend(new_patients)
    save_patients_to_json(st.session_state.patients, 'data/patients.json')
    st.experimental_rerun()

if st.sidebar.button("🆕 Generate New Dataset"):
    # Generate a completely new dataset
    st.session_state.patients = batch_update_risk(generate_patients(50))
    save_patients_to_json(st.session_state.patients, 'data/patients.json')
    st.experimental_rerun()

# Main content
st.title("🏥 MediScope - Healthcare Data Platform")
st.markdown("### Real-time Hospital Dashboard")

# Calculate statistics
stats = utils.get_patient_statistics(st.session_state.patients)
bed_occupancy = utils.calculate_bed_occupancy(st.session_state.patients)
patient_flow = utils.calculate_patient_flow(st.session_state.patients, days=7)

# KPI Cards
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Patients", stats['total_patients'])

with col2:
    st.metric("Currently Admitted", stats['admitted'])

with col3:
    st.metric("Average Age", f"{stats['average_age']} years")

with col4:
    st.metric("Avg. Risk Score", f"{stats['average_risk_score']}/15")

# Bed Occupancy Chart
st.markdown("### Bed Occupancy by Department")
bed_data = []
for dept, data in bed_occupancy.items():
    bed_data.append({
        'Department': dept,
        'Occupied': data['occupied'],
        'Available': data['available'],
        'Occupancy Rate': data['occupancy_rate']
    })

df_beds = pd.DataFrame(bed_data).sort_values('Occupancy Rate', ascending=False)

fig_beds = px.bar(
    df_beds,
    x='Department',
    y=['Occupied', 'Available'],
    title='Bed Occupancy by Department',
    labels={'value': 'Number of Beds', 'variable': 'Status'},
    color_discrete_map={'Occupied': '#3b82f6', 'Available': '#e5e7eb'},
    barmode='group',
    height=400
)

# Add occupancy rate as text on the bars
for i, row in df_beds.iterrows():
    fig_beds.add_annotation(
        x=row['Department'],
        y=row['Occupied'] + row['Available'] + 1,
        text=f"{row['Occupancy Rate']:.1f}%",
        showarrow=False,
        font=dict(size=10)
    )

st.plotly_chart(fig_beds, use_container_width=True)

# Patient Flow Chart
st.markdown("### Patient Flow (Last 7 Days)")
df_flow = pd.DataFrame(patient_flow)
df_flow_melted = df_flow.melt(id_vars=['date'], value_vars=['admissions', 'discharges'], 
                             var_name='Type', value_name='Count')

# Convert Type to title case for display
df_flow_melted['Type'] = df_flow_melted['Type'].str.title()

fig_flow = px.line(
    df_flow_melted,
    x='date',
    y='Count',
    color='Type',
    title='Admissions vs Discharges',
    labels={'date': 'Date', 'Count': 'Number of Patients'},
    color_discrete_map={'Admissions': '#10b981', 'Discharges': '#3b82f6'},
    markers=True,
    height=400
)

# Add data points
fig_flow.update_traces(
    mode='lines+markers',
    line=dict(width=2.5),
    marker=dict(size=8)
)

st.plotly_chart(fig_flow, use_container_width=True)

# Risk Distribution
st.markdown("### Patient Risk Distribution")

# Create columns for the charts
risk_col1, risk_col2 = st.columns([2, 1])

with risk_col1:
    # Risk level distribution (pie chart)
    risk_dist = stats['risk_distribution']
    df_risk = pd.DataFrame({
        'Risk Level': list(risk_dist.keys()),
        'Count': list(risk_dist.values())
    })
    
    # Sort by count
    df_risk = df_risk.sort_values('Count', ascending=False)
    
    # Create a color map for risk levels
    color_map = {
        'Critical': '#dc2626',
        'High': '#ea580c',
        'Medium': '#d97706',
        'Low': '#16a34a',
        'Unknown': '#9ca3af'
    }
    
    # Map colors to the risk levels in the data
    colors = [color_map.get(level, '#9ca3af') for level in df_risk['Risk Level']]
    
    fig_risk_pie = px.pie(
        df_risk,
        values='Count',
        names='Risk Level',
        title='Patients by Risk Level',
        color='Risk Level',
        color_discrete_map=color_map,
        hole=0.4,
        height=400
    )
    
    st.plotly_chart(fig_risk_pie, use_container_width=True)

with risk_col2:
    # Department distribution (for the selected risk level if any)
    if selected_risk != "All Risk Levels":
        dept_risk = {}
        for dept in departments:
            count = len([p for p in st.session_state.patients 
                       if p['department'] == dept and p.get('risk_level') == selected_risk])
            if count > 0:
                dept_risk[dept] = count
        
        df_dept_risk = pd.DataFrame({
            'Department': list(dept_risk.keys()),
            'Count': list(dept_risk.values())
        }).sort_values('Count', ascending=True)
        
        if not df_dept_risk.empty:
            fig_dept_risk = px.bar(
                df_dept_risk,
                y='Department',
                x='Count',
                title=f'Departments with {selected_risk} Risk Patients',
                orientation='h',
                color='Department',
                height=max(300, len(df_dept_risk) * 25)  # Dynamic height based on number of departments
            )
            
            # Remove legend and adjust layout
            fig_dept_risk.update_layout(
                showlegend=False,
                yaxis_title=None,
                xaxis_title='Number of Patients',
                margin=dict(l=0, r=0, t=40, b=20)
            )
            
            st.plotly_chart(fig_dept_risk, use_container_width=True)
        else:
            st.info(f"No patients with {selected_risk} risk level found.")
    else:
        # Show department distribution
        dept_dist = stats['department_distribution']
        df_dept = pd.DataFrame({
            'Department': list(dept_dist.keys()),
            'Count': list(dept_dist.values())
        }).sort_values('Count', ascending=True)
        
        fig_dept = px.bar(
            df_dept,
            y='Department',
            x='Count',
            title='Patients by Department',
            orientation='h',
            color='Department',
            height=max(300, len(df_dept) * 25)  # Dynamic height based on number of departments
        )
        
        # Remove legend and adjust layout
        fig_dept.update_layout(
            showlegend=False,
            yaxis_title=None,
            xaxis_title='Number of Patients',
            margin=dict(l=0, r=0, t=40, b=20)
        )
        
        st.plotly_chart(fig_dept, use_container_width=True)

# Patient List
st.markdown("### Patient List")

# Convert filtered patients to DataFrame for display
df_patients = utils.patients_to_dataframe(filtered_patients)

if not df_patients.empty:
    # Format the DataFrame for display
    display_columns = {
        'Name': 'Name',
        'Age': 'Age',
        'Gender': 'Gender',
        'Department': 'Department',
        'Room': 'Room',
        'Status': 'Status',
        'Risk Level': 'Risk Level',
        'Admission Date': 'Admission Date',
        'Diagnosis': 'Diagnosis'
    }
    
    # Reorder and select only the columns we want to display
    df_display = df_patients[list(display_columns.keys())].copy()
    df_display.columns = [display_columns[col] for col in df_display.columns]
    
    # Apply styling to the Risk Level column
    def color_risk(val):
        if val == 'Critical':
            return 'background-color: #fee2e2; color: #b91c1c; font-weight: bold;'
        elif val == 'High':
            return 'background-color: #ffedd5; color: #9a3412; font-weight: bold;'
        elif val == 'Medium':
            return 'background-color: #fef3c7; color: #92400e; font-weight: bold;'
        elif val == 'Low':
            return 'background-color: #dcfce7; color: #166534; font-weight: bold;'
        return ''
    
    # Apply the styling
    styled_df = df_display.style.applymap(
        color_risk,
        subset=['Risk Level']
    )
    
    # Display the styled DataFrame
    st.dataframe(
        styled_df,
        use_container_width=True,
        height=400,
        hide_index=True,
        column_config={
            'Name': st.column_config.TextColumn("Name"),
            'Age': st.column_config.NumberColumn("Age"),
            'Gender': st.column_config.TextColumn("Gender"),
            'Department': st.column_config.TextColumn("Department"),
            'Room': st.column_config.TextColumn("Room"),
            'Status': st.column_config.TextColumn("Status"),
            'Risk Level': st.column_config.TextColumn("Risk Level"),
            'Admission Date': st.column_config.DateColumn("Admission Date"),
            'Diagnosis': st.column_config.TextColumn("Diagnosis")
        }
    )
    
    # Add a download button for the filtered data
    csv = df_patients.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Patient Data (CSV)",
        data=csv,
        file_name=f"patient_data_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )
else:
    st.info("No patients match the selected filters.")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; font-size: 0.9rem; margin-top: 2rem;'>
        <p>MediScope - Healthcare Data Platform</p>
        <p>Last updated: {}</p>
    </div>
    """.format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
    unsafe_allow_html=True
)
