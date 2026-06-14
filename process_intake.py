#!/usr/bin/env python3
"""
Main pipeline for processing patient intake forms using Groq GenAI.

Usage:
    python process_intake.py
"""

import json
from pathlib import Path
from dotenv import load_dotenv
from intake_processor import IntakeProcessor


def main():
    """Process patient intake submissions."""
    
    # Load environment variables
    load_dotenv()
    
    # Setup paths
    data_dir = Path("data")
    output_dir = Path("outputs")
    output_dir.mkdir(exist_ok=True)
    
    # Load sample patient inputs
    input_file = data_dir / "sample_patient_input.json"
    with open(input_file) as f:
        patient_inputs = json.load(f)
    
    print("\n" + "="*70)
    print("🏥 HEALTHCARE PATIENT INTAKE ASSISTANT")
    print("="*70)
    print(f"Processing {len(patient_inputs)} patient intakes using Groq Llama 3.1...\n")
    
    # Initialize processor
    processor = IntakeProcessor()
    
    # Process all intakes
    summary = processor.process_batch(patient_inputs)
    
    # Save results
    output_file = output_dir / "intake_forms.json"
    with open(output_file, "w") as f:
        json.dump(summary, f, indent=2)
    
    # Display results
    print("\n" + "="*70)
    print("📋 INTAKE PROCESSING SUMMARY")
    print("="*70)
    print(f"Total Patients: {summary['total_patients']}")
    print(f"🚨 Urgent Cases: {summary['urgent_cases']}")
    print(f"✅ Routine Cases: {summary['routine_cases']}")
    print("\n" + "-"*70)
    print("DETAILED INTAKE FORMS:")
    print("-"*70)
    
    for intake in summary["intakes"]:
        urgency_icon = "🚨" if intake["urgency_level"] == "High" else "✅"
        
        print(f"\n{urgency_icon} PATIENT ID: {intake['patient_id']}")
        print(f"   Chief Complaint: {intake['chief_complaint']}")
        print(f"   Severity: {intake['severity']} | Duration: {intake['duration']}")
        print(f"   Medications: {', '.join(intake['current_medications']) if intake['current_medications'] else 'None'}")
        print(f"   Allergies: {intake['allergies']}")
        
        if intake['urgent_symptoms']:
            print(f"   ⚠️  URGENT SYMPTOMS: {', '.join(intake['urgent_symptoms'])}")
        
        print(f"   Suggested Questions:")
        for i, question in enumerate(intake['suggested_questions'][:2], 1):
            print(f"      {i}. {question}")
        
        print(f"   Provider Summary: {intake['summary_for_provider']}")
    
    print("\n" + "="*70)
    print(f"Results saved to: {output_file}")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
