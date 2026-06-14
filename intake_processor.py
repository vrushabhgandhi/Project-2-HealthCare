"""GenAI-powered healthcare patient intake processor using Groq."""

import os
import json
from typing import Optional
from dataclasses import dataclass, asdict
from groq import Groq
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class PatientIntake:
    """Structured patient intake form from natural language description."""
    patient_id: str
    chief_complaint: str
    duration: str
    severity: str
    current_medications: list[str]
    allergies: str
    urgency_level: str  # "High", "Medium", "Low"
    urgent_symptoms: list[str]  # Symptoms needing immediate attention
    suggested_questions: list[str]  # Follow-up questions for provider
    summary_for_provider: str


class IntakeProcessor:
    """Processes patient intake descriptions using Groq LLM."""
    
    # Urgent symptoms that need immediate medical attention
    URGENT_KEYWORDS = [
        "chest pain", "difficulty breathing", "shortness of breath",
        "severe headache", "sudden weakness", "confusion", "loss of consciousness",
        "severe bleeding", "severe allergic reaction", "signs of stroke",
        "severe abdominal pain", "poisoning", "overdose"
    ]
    
    # Clinical patterns that indicate urgency (symptom combinations)
    URGENT_PATTERNS = [
        # Meningitis indicators
        {
            "name": "possible_meningitis",
            "symptoms": ["headache", "stiff neck", "fever"],
            "severity_threshold": 2  # At least 2 symptoms needed
        },
        # Severe infection/sepsis indicators
        {
            "name": "severe_infection",
            "symptoms": ["fever", "rash"],
            "severity_threshold": 2
        },
        # Cardiac event indicators
        {
            "name": "cardiac_event",
            "symptoms": ["chest pain", "shortness of breath", "pressure"],
            "severity_threshold": 2
        },
        # Respiratory distress
        {
            "name": "respiratory_distress",
            "symptoms": ["difficulty breathing", "chest pain", "shortness of breath"],
            "severity_threshold": 2
        },
        # Severe throat infection
        {
            "name": "severe_infection",
            "symptoms": ["high fever", "sore throat", "rash", "difficulty swallowing"],
            "severity_threshold": 3
        }
    ]
    
    def __init__(self, model: Optional[str] = None, api_key: Optional[str] = None):
        """Initialize the intake processor with Groq client."""
        self.model = model or os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
        api_key = api_key or os.getenv("GROQ_API_KEY")
        
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        
        self.client = Groq(api_key=api_key)
    
    def process_intake(self, patient_input: dict) -> PatientIntake:
        """
        Process raw patient input into structured intake form.
        
        Args:
            patient_input: Dict with 'patient_id' and 'description'
            
        Returns:
            PatientIntake object with structured data
        """
        patient_id = patient_input.get("patient_id", "UNKNOWN")
        description = patient_input.get("description", "")
        
        logger.info(f"Processing intake for patient {patient_id}")
        
        # Get AI analysis
        analysis = self._analyze_with_groq(description)
        
        # Check for urgent symptoms using keywords and clinical patterns
        urgent_symptoms = self._check_urgency(description, analysis)
        
        # Determine urgency level
        if urgent_symptoms:
            urgency_level = "High"
            logger.warning(f"Patient {patient_id} flagged as HIGH urgency: {urgent_symptoms}")
        else:
            urgency_level = "Low"
        
        result = PatientIntake(
            patient_id=patient_id,
            chief_complaint=analysis.get("chief_complaint", "Not specified"),
            duration=analysis.get("duration", "Not specified"),
            severity=analysis.get("severity", "Moderate"),
            current_medications=analysis.get("current_medications", []),
            allergies=analysis.get("allergies", "None reported"),
            urgency_level=urgency_level,
            urgent_symptoms=urgent_symptoms,
            suggested_questions=analysis.get("suggested_questions", []),
            summary_for_provider=analysis.get("summary_for_provider", "")
        )
        
        logger.info(f"Intake processed. Urgency: {urgency_level}, Symptoms: {urgent_symptoms}")
        return result
    
    def _analyze_with_groq(self, description: str) -> dict:
        """
        Use Groq to extract structured intake information.
        
        Returns:
            Dict with structured patient information
        """
        prompt = f"""Analyze this patient intake description and respond with valid JSON only:

Patient Description: {description}

Extract and structure the following information. Respond with ONLY a valid JSON object (no markdown, no code blocks):
{{
    "chief_complaint": "Main reason for visit in 5-10 words",
    "duration": "How long symptoms have been present",
    "severity": "Mild, Moderate, or Severe",
    "current_medications": ["medication1", "medication2"],
    "allergies": "List of allergies or 'None reported'",
    "suggested_questions": [
        "Clinically relevant follow-up question 1",
        "Clinically relevant follow-up question 2",
        "Clinically relevant follow-up question 3"
    ],
    "summary_for_provider": "1-2 sentence clinical summary for the doctor"
}}

Focus on:
- Symptoms and their duration
- Current medications mentioned
- Any allergies mentioned
- Severity level from patient description
- Clinical relevance for follow-up
"""
        
        try:
            message = self.client.chat.completions.create(
                model=self.model,
                max_tokens=500,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            response_text = message.choices[0].message.content.strip()
            
            # Clean up response (remove markdown if present)
            if response_text.startswith("```"):
                response_text = response_text.split("```")[1]
                if response_text.startswith("json"):
                    response_text = response_text[4:]
            
            result = json.loads(response_text)
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Groq response: {e}")
            return {
                "chief_complaint": "Unable to analyze",
                "duration": "Unknown",
                "severity": "Unknown",
                "current_medications": [],
                "allergies": "Unknown",
                "suggested_questions": ["Please provide more details about your symptoms"],
                "summary_for_provider": "Patient intake processing failed - please obtain details manually"
            }
        except Exception as e:
            logger.error(f"Groq API error: {type(e).__name__}: {str(e)}")
            logger.debug(f"Full traceback:", exc_info=True)
            return {}
    
    def _check_urgency(self, description: str, analysis: dict) -> list[str]:
        """
        Check if patient has urgent symptoms using keyword and pattern matching.
        
        Returns:
            List of urgent symptoms found
        """
        urgent_symptoms = []
        description_lower = description.lower()
        
        # 1. Check for explicit urgent keywords
        for keyword in self.URGENT_KEYWORDS:
            if keyword in description_lower:
                urgent_symptoms.append(keyword.title())
        
        # 2. Check for clinical patterns (symptom combinations)
        for pattern in self.URGENT_PATTERNS:
            matched_symptoms = []
            
            for symptom in pattern["symptoms"]:
                if symptom.lower() in description_lower:
                    matched_symptoms.append(symptom)
            
            # If enough symptoms from this pattern are present, flag as urgent
            if len(matched_symptoms) >= pattern["severity_threshold"]:
                logger.info(f"Detected urgent pattern '{pattern['name']}' with symptoms: {matched_symptoms}")
                
                # Add the pattern name as context
                if pattern["name"] == "possible_meningitis":
                    urgent_symptoms.append("Possible Meningitis (Headache + Stiff Neck + Fever)")
                elif pattern["name"] == "severe_infection":
                    urgent_symptoms.append("Possible Severe Infection (Fever + Rash)")
                elif pattern["name"] == "cardiac_event":
                    urgent_symptoms.append("Possible Cardiac Event (Chest Pain + Breathlessness)")
                elif pattern["name"] == "respiratory_distress":
                    urgent_symptoms.append("Respiratory Distress (Breathing Difficulty)")
        
        return urgent_symptoms
    
    def process_batch(self, patient_inputs: list[dict]) -> dict:
        """
        Process multiple patient intakes and generate summary.
        
        Args:
            patient_inputs: List of patient intake dicts
            
        Returns:
            Summary with all processed intakes
        """
        logger.info(f"Processing batch of {len(patient_inputs)} patient intakes")
        
        results = []
        urgent_count = 0
        
        for patient_input in patient_inputs:
            result = self.process_intake(patient_input)
            results.append(asdict(result))
            
            if result.urgency_level == "High":
                urgent_count += 1
        
        summary = {
            "total_patients": len(patient_inputs),
            "urgent_cases": urgent_count,
            "routine_cases": len(patient_inputs) - urgent_count,
            "intakes": results
        }
        
        logger.info(f"Batch complete: {urgent_count} urgent, {len(patient_inputs) - urgent_count} routine")
        return summary
