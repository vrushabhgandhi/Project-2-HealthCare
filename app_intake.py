#!/usr/bin/env python3
"""
Streamlit UI for Healthcare Patient Intake Assistant.

Run with: streamlit run app_intake.py
"""

import streamlit as st
import json
from pathlib import Path
from dotenv import load_dotenv
from intake_processor import IntakeProcessor

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="🏥 Healthcare Intake Assistant",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .urgent-card {
        background-color: #fff3cd;
        padding: 15px;
        border-left: 5px solid #dc3545;
        border-radius: 5px;
        margin: 10px 0;
    }
    .routine-card {
        background-color: #d1ecf1;
        padding: 15px;
        border-left: 5px solid #17a2b8;
        border-radius: 5px;
        margin: 10px 0;
    }
    .urgent {
        color: #dc3545;
        font-weight: bold;
    }
    .routine {
        color: #17a2b8;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# Title
st.title("🏥 Healthcare Patient Intake Assistant")
st.markdown("Smart clinical intake forms using Groq Llama 3.1 with clinical pattern recognition")

# Sidebar
st.sidebar.header("⚙️ Configuration")
st.sidebar.info("""
    **Clinical Pattern Detection:**
    - Meningitis (headache + stiff neck)
    - Cardiac event (chest pain + SOB)
    - Severe infection (high fever + rash)
    - And more...
""")

# Tab selection
tab1, tab2, tab3 = st.tabs(["👤 Single Patient", "👥 Batch Upload", "📊 Reports"])

# ============ TAB 1: Single Patient ============
with tab1:
    st.header("Process Single Patient Intake")
    
    col1, col2 = st.columns(2)
    
    with col1:
        patient_id = st.text_input("Patient ID", value="P001")
        description = st.text_area("Patient Symptoms & Description", 
                                  value="I've had a terrible headache for 3 days with a stiff neck and sensitivity to light",
                                  height=120)
    
    with col2:
        st.write("**System Information:**")
        st.write(f"Model: Groq Llama 3.1 8B")
        st.write(f"Pattern Detection: ✅ Enabled")
        st.write(f"Keyword Detection: ✅ Enabled")
    
    if st.button("🔍 Process Patient Intake", key="single_process"):
        with st.spinner("Analyzing patient intake with Groq AI..."):
            try:
                processor = IntakeProcessor()
                
                patient_input = {
                    "patient_id": patient_id,
                    "description": description
                }
                
                result = processor.process_intake(patient_input)
                
                # Display urgency alert
                if result.urgency_level == "High":
                    st.error(f"🚨 **HIGH URGENCY** - {patient_id}")
                else:
                    st.info(f"✅ Routine case - {patient_id}")
                
                # Main metrics
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Urgency Level", result.urgency_level)
                
                with col2:
                    st.metric("Severity", result.severity)
                
                with col3:
                    st.metric("Duration", result.duration)
                
                with col4:
                    meds_count = len(result.current_medications)
                    st.metric("Medications", meds_count)
                
                # Chief complaint
                st.subheader("📋 Chief Complaint")
                st.write(f"**{result.chief_complaint}**")
                
                # Urgent symptoms
                if result.urgent_symptoms:
                    st.subheader("🚨 Detected Urgent Symptoms/Patterns")
                    for symptom in result.urgent_symptoms:
                        st.error(f"• {symptom}")
                
                # Medical info columns
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("💊 Medications")
                    if result.current_medications:
                        for med in result.current_medications:
                            st.write(f"• {med}")
                    else:
                        st.write("None reported")
                
                with col2:
                    st.subheader("⚕️ Allergies")
                    st.write(result.allergies)
                
                # Suggested questions
                st.subheader("❓ Suggested Follow-up Questions")
                for i, question in enumerate(result.suggested_questions, 1):
                    st.write(f"{i}. {question}")
                
                # Provider summary
                st.subheader("📝 Provider Summary")
                st.info(result.summary_for_provider)
                
                # Store result
                st.session_state.last_result = result
                
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")


# ============ TAB 2: Batch Upload ============
with tab2:
    st.header("👥 Process Multiple Patient Intakes")
    
    uploaded_file = st.file_uploader("Upload JSON file with patient intakes", type="json")
    
    if uploaded_file is not None:
        try:
            # Read JSON file
            patient_inputs = json.load(uploaded_file)
            
            st.success(f"✅ Loaded {len(patient_inputs)} patient records")
            
            if st.button("🚀 Process All Patients", key="batch_process"):
                with st.spinner("Processing patient intakes with Groq AI..."):
                    processor = IntakeProcessor()
                    summary = processor.process_batch(patient_inputs)
                    
                    # Display summary metrics
                    st.subheader("📊 Summary")
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Total Patients", summary["total_patients"])
                    
                    with col2:
                        st.metric("🚨 Urgent Cases", summary["urgent_cases"])
                    
                    with col3:
                        st.metric("✅ Routine Cases", summary["routine_cases"])
                    
                    with col4:
                        urgent_percentage = (summary["urgent_cases"] / summary["total_patients"] * 100) if summary["total_patients"] > 0 else 0
                        st.metric("Urgent %", f"{urgent_percentage:.0f}%")
                    
                    # Detailed results
                    st.subheader("👥 Detailed Patient Intakes")
                    
                    for intake in summary["intakes"]:
                        if intake["urgency_level"] == "High":
                            card_class = "urgent-card"
                            status_icon = "🚨"
                        else:
                            card_class = "routine-card"
                            status_icon = "✅"
                        
                        with st.expander(f"{status_icon} {intake['patient_id']}: {intake['chief_complaint'][:50]}..."):
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.write(f"**Chief Complaint:** {intake['chief_complaint']}")
                                st.write(f"**Severity:** {intake['severity']}")
                                st.write(f"**Duration:** {intake['duration']}")
                            
                            with col2:
                                urgency_text = "🚨 HIGH" if intake["urgency_level"] == "High" else "✅ LOW"
                                st.write(f"**Urgency:** {urgency_text}")
                                
                                if intake['current_medications']:
                                    st.write(f"**Medications:** {', '.join(intake['current_medications'])}")
                                
                                st.write(f"**Allergies:** {intake['allergies']}")
                            
                            with col3:
                                if intake['urgent_symptoms']:
                                    st.write("**Detected Urgent Symptoms:**")
                                    for symptom in intake['urgent_symptoms']:
                                        st.write(f"• {symptom}")
                            
                            st.write("---")
                            st.write("**Suggested Questions:**")
                            for i, q in enumerate(intake['suggested_questions'], 1):
                                st.write(f"{i}. {q}")
                            
                            st.write("---")
                            st.write(f"**Provider Summary:** {intake['summary_for_provider']}")
                    
                    # Download results
                    results_json = json.dumps(summary, indent=2)
                    st.download_button(
                        label="📥 Download Results as JSON",
                        data=results_json,
                        file_name="intake_results.json",
                        mime="application/json"
                    )
                    
                    st.session_state.batch_summary = summary
        
        except json.JSONDecodeError:
            st.error("❌ Invalid JSON file format")
        except Exception as e:
            st.error(f"❌ Error processing file: {str(e)}")


# ============ TAB 3: Reports ============
with tab3:
    st.header("📊 Patient Intake Analysis & Reports")
    
    outputs_dir = Path("outputs")
    
    if outputs_dir.exists():
        summary_file = outputs_dir / "intake_forms.json"
        
        if summary_file.exists():
            with open(summary_file) as f:
                data = json.load(f)
            
            st.success(f"✅ Found existing analysis")
            
            # Display summary metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Patients", data["total_patients"])
            
            with col2:
                st.metric("🚨 Urgent Cases", data["urgent_cases"], 
                         delta=f"{data['urgent_cases']/data['total_patients']*100:.0f}% of total")
            
            with col3:
                st.metric("✅ Routine Cases", data["routine_cases"])
            
            with col4:
                st.metric("Urgency Rate", f"{data['urgent_cases']/data['total_patients']*100:.0f}%")
            
            # Urgency breakdown
            st.subheader("📈 Urgency Breakdown")
            col1, col2 = st.columns(2)
            
            with col1:
                st.info(f"""
                **High Urgency Cases ({data['urgent_cases']})**
                - Require immediate medical attention
                - Should be triaged first
                - May include life-threatening conditions
                """)
            
            with col2:
                st.info(f"""
                **Routine Cases ({data['routine_cases']})**
                - Standard clinic workflow
                - No immediate danger signs
                - Can be scheduled normally
                """)
            
            # Detailed patient list
            st.subheader("👥 All Patients")
            
            for intake in data["intakes"]:
                if intake["urgency_level"] == "High":
                    status_icon = "🚨"
                    with st.expander(f"{status_icon} {intake['patient_id']} [HIGH URGENCY]"):
                        st.error(f"⚠️ This patient requires urgent evaluation!")
                else:
                    status_icon = "✅"
                    with st.expander(f"{status_icon} {intake['patient_id']} [Routine]"):
                        pass
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.write(f"**Chief Complaint:** {intake['chief_complaint']}")
                    st.write(f"**Severity:** {intake['severity']}")
                    st.write(f"**Duration:** {intake['duration']}")
                
                with col2:
                    st.write(f"**Medications:** {', '.join(intake['current_medications']) if intake['current_medications'] else 'None'}")
                    st.write(f"**Allergies:** {intake['allergies']}")
                    
                    if intake['urgent_symptoms']:
                        st.write("**Urgent Patterns Detected:**")
                        for symptom in intake['urgent_symptoms']:
                            st.error(f"• {symptom}")
                
                with col3:
                    st.write("**Suggested Questions:**")
                    for q in intake['suggested_questions'][:2]:
                        st.write(f"• {q}")
                
                st.write("---")
        
        else:
            st.info("💡 No processed data yet. Run patients through the Single Patient or Batch Upload tabs first.")
    
    else:
        st.info("💡 No output directory found. Process some patient intakes first.")


# Footer
st.divider()
st.markdown("""
    <div style='text-align: center; color: #888;'>
    🏥 Healthcare Patient Intake Assistant | Clinical Pattern Recognition Enabled | Powered by Groq Llama 3.1
    </div>
    """, unsafe_allow_html=True)
