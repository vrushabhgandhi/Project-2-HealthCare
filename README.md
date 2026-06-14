# 🏥 Healthcare Intake Assistant

A GenAI-powered patient intake form processor that converts unstructured patient descriptions into structured medical intake data using natural language processing.

## What It Does

1. **Reads** patient-provided symptom descriptions (e.g., "I've had a bad headache for 3 days with nausea")
2. **Structures** into medical intake form fields (chief complaint, symptom duration, severity)
3. **Flags** urgent symptoms for immediate medical attention
4. **Suggests** relevant follow-up questions for the doctor
5. **Extracts** medication and allergy information
6. **Generates** a summary for the healthcare provider

## Quick Start

### Setup
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### Configure
```bash
cp .env.sample .env
# Edit .env and add your Groq API key
```

### Run

#### Command-line Mode
```bash
python process_intake.py
```

#### 🎨 Streamlit Web UI (Recommended)
```bash
streamlit run app_intake.py
```

This launches an interactive web interface at `http://localhost:8501` where you can:
- 👤 Process individual patient intakes in real-time
- 👥 Upload and process batch JSON files
- 🚨 View urgent/routine case breakdown
- 📋 Access clinical pattern detection details
- 📥 Download structured intake data

## Project Structure
```
healthcare-intake-assistant/
├── requirements.txt
├── .env.sample
├── README.md
├── CLINICAL_PATTERNS.md        # Clinical pattern documentation
├── app_intake.py               # 🎨 Streamlit web UI
├── process_intake.py           # Command-line pipeline
├── intake_processor.py         # GenAI intake analysis logic
├── debug_groq.py              # API connection test
├── data/
│   └── sample_patient_input.json
└── outputs/
    └── intake_forms.json
```

## Example Usage

```python
from intake_processor import IntakeProcessor

processor = IntakeProcessor()

# Process patient intake
patient_input = {
    "patient_id": "P001",
    "description": "I've had severe headaches for 3 days. They come and go. I also have nausea and sensitivity to light. No fever that I know of. Taking Tylenol but it only helps a little."
}

result = processor.process_intake(patient_input)
print(result.chief_complaint)     # "Severe headaches with nausea"
print(result.urgency_level)       # "High" or "Low"
print(result.suggested_questions) # ["When did symptoms start?", ...]
```

## Output Example

```json
{
  "patient_id": "P001",
  "chief_complaint": "Severe headaches with nausea and photosensitivity",
  "duration": "3 days",
  "severity": "Severe",
  "current_medications": ["Tylenol"],
  "allergies": "None reported",
  "urgency_level": "High",
  "urgent_symptoms": ["Severe headache", "Photosensitivity"],
  "suggested_questions": [
    "Any recent head injuries or trauma?",
    "Have you experienced fever?",
    "Any vision changes?"
  ],
  "summary_for_provider": "Patient reports 3-day history of severe headaches with nausea and light sensitivity. Taking Tylenol with minimal relief. Requires urgent evaluation for possible migraine or meningitis."
}
```

## GenAI Features

- **Smart Extraction:** Uses Groq to parse unstructured patient descriptions
- **Medical Understanding:** Categorizes symptoms by urgency and relevance
- **Intelligent Questions:** Suggests clinically relevant follow-up questions
- **Plain Language:** Converts medical information into accessible summaries
- **Privacy-Aware:** Minimal data retention, audit-friendly
