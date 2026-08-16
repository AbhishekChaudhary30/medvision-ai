def generate_clinical_suggestions(
    modality: str, 
    predicted_class: str, 
    confidence: float,
    patient_age: int | None = None,
    patient_gender: str | None = None,
    clinical_notes: str | None = None
) -> str:
    """Generate highly detailed, actionable clinical suggestions combining AI output and patient context."""
    
    # Base Patient Context string
    context_parts = []
    if patient_age: context_parts.append(f"{patient_age}yo")
    if patient_gender: context_parts.append(f"{patient_gender}")
    context_str = " ".join(context_parts) if context_parts else "Unknown Patient"
    
    # Notes context
    notes_str = f" Clinical Context: '{clinical_notes}'." if clinical_notes else ""
    
    # --- Radiography (X-Ray) ---
    if modality == "chest-xray":
        if predicted_class == "PNEUMONIA":
            base = f"High confidence of Pneumonia detected for {context_str}.{notes_str}" if confidence > 0.8 else f"Possible Pneumonia detected for {context_str}.{notes_str}"
            action = "Suggest immediate pulmonology consultation. Consider broad-spectrum antibiotics, monitor oxygen saturation, and follow-up CXR in 48 hours."
            return f"{base} ACTION: {action}"
        else:
            return f"No definitive signs of Pneumonia for {context_str}.{notes_str} Routine clinical follow-up as dictated by symptoms."

    elif modality == "bone-xray":
        if predicted_class == "FRACTURE":
            base = f"Radiographic evidence of FRACTURE for {context_str}.{notes_str}"
            action = "Immobilize the affected area. Urgent orthopedic consult required for casting or surgical intervention. Prescribe analgesics."
            return f"{base} ACTION: {action}"
        return "No acute fracture detected. Consider MRI if occult fracture suspected."

    elif modality == "dental-xray":
        if predicted_class == "CARIES/DECAY":
            return f"Dental Caries identified for {context_str}. ACTION: Schedule restorative dentistry (fillings). Advise on oral hygiene."
        return "Healthy dentition. Continue routine biannual checkups."

    # --- CT Scans ---
    elif modality == "head-ct":
        if predicted_class == "HEMORRHAGE":
            base = f"CRITICAL: Intracranial HEMORRHAGE detected for {context_str}.{notes_str}"
            action = "STAT Neurosurgery and Neurology consult. Control blood pressure, reverse anticoagulants if applicable, prepare for potential surgical evacuation."
            return f"{base} ACTION: {action}"
        return f"No acute intracranial hemorrhage detected for {context_str}. If stroke suspected, consider CTA or MRI Brain."

    elif modality == "chest-ct":
        if predicted_class == "MALIGNANT NODULE":
            return f"Suspicious MALIGNANT NODULE in Chest CT for {context_str}.{notes_str} ACTION: Urgent oncology referral. Schedule PET-CT for staging and image-guided biopsy."
        return "Benign appearing pulmonary structures. Routine screening based on patient risk factors."

    elif modality == "abdomen-ct":
        if predicted_class == "APPENDICITIS":
            return f"Evidence of APPENDICITIS for {context_str}.{notes_str} ACTION: NPO, start IV antibiotics, STAT General Surgery consult for appendectomy."
        return "No acute abdominal pathology detected on CT."

    # --- MRI Scans ---
    elif modality == "brain-mri":
        if predicted_class == "TUMOR":
            return f"Intracranial MASS/TUMOR detected on MRI for {context_str}.{notes_str} ACTION: Urgent neuro-oncology referral. Consider contrast-enhanced MRI for detailed mapping and plan for stereotactic biopsy."
        return "No gross structural abnormalities or masses detected in brain parenchyma."

    elif modality == "spine-mri":
        if predicted_class == "HERNIATED DISC":
            return f"Herniated Disc detected for {context_str}.{notes_str} ACTION: Physical therapy evaluation. NSAIDs and Gabapentin for radiculopathy. Refer to spine specialist if symptoms are refractory."
        return "Spinal alignment and disc spaces within normal limits."

    elif modality == "knee-mri":
        if predicted_class == "ACL TEAR":
            return f"ACL TEAR identified for {context_str}.{notes_str} ACTION: Orthopedic surgery referral for reconstructive surgery planning. Prescribe knee brace and physical therapy."
        return "Cruciate ligaments appear intact."

    # --- Ultrasound ---
    elif modality == "fetal-ultrasound":
        if predicted_class == "STRUCTURAL ANOMALY":
            return f"Fetal STRUCTURAL ANOMALY detected.{notes_str} ACTION: Refer to Maternal-Fetal Medicine (MFM) specialist immediately. Consider amniocentesis for genetic karyotyping."
        return "Normal fetal growth and anatomy. Continue routine prenatal care."

    elif modality == "echocardiogram":
        if predicted_class == "HEART FAILURE / REDUCED EF":
            return f"Reduced Ejection Fraction detected for {context_str}.{notes_str} ACTION: Initiate guideline-directed medical therapy (GDMT) for Heart Failure (Beta-blockers, ACEi/ARB). Cardiology referral."
        return "Normal left ventricular ejection fraction and valve function."

    elif modality == "abdominal-ultrasound":
        if predicted_class == "CHOLELITHIASIS (GALLSTONES)":
            return f"Gallstones detected for {context_str}.{notes_str} ACTION: If symptomatic (biliary colic), refer for elective cholecystectomy. Advise low-fat diet."
        return "Normal gallbladder and biliary tree."

    # --- Pathology/Other ---
    elif modality == "skin-lesion":
        if predicted_class == "MELANOMA":
            return f"Highly suspicious lesion for MELANOMA for {context_str}.{notes_str} ACTION: Urgent Dermatology referral for wide local excision and histopathological staging."
        return "Lesion appears benign. Annual dermoscopy screening recommended."

    elif modality == "retinal-fundus":
        if predicted_class == "DIABETIC RETINOPATHY":
            return f"Diabetic Retinopathy signs present for {context_str}.{notes_str} ACTION: Strict glycemic control. Referral to ophthalmology for possible laser photocoagulation or anti-VEGF therapy."
        return "Normal retinal fundus. Annual diabetic eye exams advised."

    elif modality == "histopathology":
        if predicted_class == "INVASIVE CARCINOMA":
            return f"INVASIVE CARCINOMA identified in tissue slide for {context_str}.{notes_str} ACTION: Tumor board review required. Stage patient via PET-CT and schedule oncology consultation for systemic therapy/surgery."
        return "Benign tissue histology. No malignancy identified."

    elif modality == "mammography":
        if "BIRADS-4/5" in predicted_class or "MALIGNANT" in predicted_class:
            return f"Suspicious mammographic findings (BI-RADS 4/5) for {context_str}.{notes_str} ACTION: Urgent referral for ultrasound-guided core needle biopsy. Discuss oncology options."
        return "Negative for malignancy (BI-RADS 1). Continue routine annual screening."

    elif modality == "colonoscopy":
        if "ADENOMATOUS POLYP" in predicted_class:
            return f"Adenomatous Polyp detected during colonoscopy for {context_str}.{notes_str} ACTION: Complete polypectomy and send for histopathological grading. Schedule surveillance colonoscopy in 3 years."
        return "Normal colonic mucosa. Routine screening based on patient age and risk factors."

    # Fallback
    if "NORMAL" in predicted_class or "BENIGN" in predicted_class or "HEALTHY" in predicted_class:
         return f"Findings appear within normal limits for {context_str}. Routine clinical follow-up."
    return f"Anomaly detected ({predicted_class}) for {context_str}.{notes_str} Requires clinical correlation and specialist referral."
