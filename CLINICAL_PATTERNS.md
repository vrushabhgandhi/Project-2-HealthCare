# Clinical Urgency Patterns

This document explains the clinical patterns used by the Healthcare Intake Assistant to detect urgent cases.

## Urgent Pattern Detection

The system uses two approaches to detect urgency:

### 1. **Keyword-Based Detection** (Explicit Red Flags)

Individual keywords that immediately indicate emergency:
- Chest pain
- Difficulty breathing / Shortness of breath
- Severe headache
- Sudden weakness
- Confusion
- Loss of consciousness
- Severe bleeding
- Severe allergic reaction
- Signs of stroke
- Severe abdominal pain
- Poisoning
- Overdose

### 2. **Pattern-Based Detection** (Symptom Combinations)

**Medical conditions detected through symptom patterns:**

#### **Pattern 1: Possible Meningitis** 🚨
- **Threshold:** 2 out of 3 symptoms required
- **Symptoms:** Headache + Stiff Neck + Fever
- **Example:** "Terrible headache for 3 days, stiff neck, and fever"
- **Clinical Reason:** Meningitis is life-threatening and requires immediate hospitalization
- **Action:** Flag as HIGH urgency

#### **Pattern 2: Severe Infection / Sepsis** 🚨
- **Threshold:** 2 out of 2 symptoms required
- **Symptoms:** High Fever + Rash
- **Example:** "High fever of 103F with a rash on their body"
- **Clinical Reason:** Fever + rash combination indicates serious infection (strep, scarlet fever, etc.)
- **Action:** Flag as HIGH urgency

#### **Pattern 3: Possible Cardiac Event** 🚨
- **Threshold:** 2 out of 3 symptoms required
- **Symptoms:** Chest Pain + Shortness of Breath + Pressure
- **Example:** "Chest pain with shortness of breath when I move around"
- **Clinical Reason:** Classic cardiac event indicators
- **Action:** Flag as HIGH urgency

#### **Pattern 4: Respiratory Distress** 🚨
- **Threshold:** 2 out of 3 symptoms required
- **Symptoms:** Difficulty Breathing + Chest Pain + Shortness of Breath
- **Example:** "Difficulty breathing and chest pain"
- **Clinical Reason:** Severe respiratory compromise
- **Action:** Flag as HIGH urgency

#### **Pattern 5: Severe Throat Infection** 🚨
- **Threshold:** 3 out of 4 symptoms required
- **Symptoms:** High Fever + Sore Throat + Rash + Difficulty Swallowing
- **Example:** "High fever with sore throat, difficulty swallowing and a rash on their body"
- **Clinical Reason:** Indicates strep throat or epiglottitis (can lead to airway obstruction)
- **Action:** Flag as HIGH urgency

---

## Results After Enhancement

### **Patient P001: Severe Headache with Stiff Neck**
- **Description:** "Terrible headache for 3 days, stiff neck and sensitivity to light"
- **Pattern Detected:** ✅ **Possible Meningitis** (Headache + Stiff Neck + implied fever in severity)
- **Before Fix:** ❌ Urgency: Low
- **After Fix:** ✅ Urgency: **High**

### **Patient P006: High Fever with Rash**
- **Description:** "High fever of 103F along with a sore throat and difficulty swallowing. They also have a rash on their body"
- **Pattern Detected:** ✅ **Severe Throat Infection** (High Fever + Sore Throat + Rash + Difficulty Swallowing)
- **Before Fix:** ❌ Urgency: Low
- **After Fix:** ✅ Urgency: **High**

---

## Clinical Safety Notes

1. **Pattern Detection is Supplementary:** These patterns are intended to assist, not replace, clinical judgment
2. **False Negatives Possible:** Atypical presentations may be missed
3. **Always Verify:** Healthcare providers should always verify with patient follow-up questions
4. **Not Diagnostic:** These patterns indicate urgency level, not diagnosis
5. **Emergency Contact:** Patients flagged as High should be triaged for urgent evaluation

---

## Future Enhancements

Additional patterns that could be added:
- Abdominal pain + vomiting + fever (appendicitis)
- Severe headache + neck stiffness + rash (meningococcemia)
- Shortness of breath + chest pain + leg swelling (PE/DVT)
- Altered mental status + fever (encephalitis/sepsis)
- Anaphylaxis indicators (swelling + breathing difficulty + rash)
