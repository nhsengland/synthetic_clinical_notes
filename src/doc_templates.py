document_templates = {
    
    "patient_details": {
        "patient_id": "<Patient ID>",
        "name": "<Patient Name>",
        "date_of_birth": "<Patient Date of Birth",
        "age": "<Patient Age>",
        "gender": "<Patient Gender>",
        "address": "<England Address of Patient>",
        "contact_number": "<Patient UK Phone Number>",
        "allergies": "[<List of allergies; leave blank if the patient has no allergies>]",
        "next_of_kin": {
            "name": "<Next of Kin Name>",
            "relationship": "<Next of Kin Relationship>",
            "contact_number": "<Next of Kin UK Phone Number>"
        },
        "gp_details": {
            "name": "<GP Name>",
            "practice_name": "<GP Practice Name>",
            "address": "<Practice Address>",
            "contact_number": "<Practice UK Phone Number>"
        },
    },
    "emergency_admission_details": {
        "date": "<Admission Date with format %Y-%m-%d>",
        "time": "<Admission TimeStamp>",
        "method": "<Should be 'A&E'>",
        "chief_complaint": "<The primary symptom, concern, or reason that prompted the individual to attend A&E>",
        "ED_diagnosis": "<The main diagnosis made in A&E, if applicable>",
        "triage_category": "<Triage Level>",
        "allergies": "[<List of allergies; leave blank if the patient has no allergies>]",
        "current_medications": "[<List of Allergies>]",
        "past_medical_history": "[<List of Previous Medical Issues>]",
        "admitting_consultant": "<Admitting Consultant>",
        "ward": "<Admission Ward>",
        "specialty": "<Specialty the patient was admitted to>",
        "admission_type": "emergency",
        "surgery_required": "<If surgery is required during this admission, this should be 'True', otherwise 'False'>"
    },
    "novel_disease_admission_details": {
        "date": "<Admission Date with format %Y-%m-%d>",
        "time": "<Admission TimeStamp>",
        "method": "<Should be 'A&E'>",
        "chief_complaint": "<The primary symptom, concern, or reason that prompted the individual to attend A&E>",
        "ED_diagnosis": "<The main diagnosis made in A&E, if applicable>",
        "diagnosis_confirmed_by": "<You must only use the confirmed by information given word for word>",
        "diagnosis_supported_by": "<You must only use the supported by information given word for word>",
        "novel_disease": "<Set this to True>",
        "supporting_symptoms": "<You must use all Additional Symptoms Provided word for word including unknown words>",
        "supporting_info": "<You must only use the additional information given word for word including unknown words, or NA if it states NA>",
        "triage_category": "<Triage Level>",
        "allergies": "[<List of allergies; leave blank if the patient has no allergies>]",
        "current_medications": "[<List of Allergies>]",
        "past_medical_history": "[<List of Previous Medical Issues>]",
        "admitting_consultant": "<Admitting Consultant>",
        "ward": "<Admission Ward>",
        "specialty": "<Specialty the patient was admitted to>",
        "admission_type": "emergency",
        "surgery_required": "<If surgery is required during this admission, this should be 'True', otherwise 'False'>"
    },
    "elective_admission_details": {
        "date": "<Admission Date with format %Y-%m-%d>",
        "time": "<Admission TimeStamp>",
        "method": "<Either booked or from a waiting list>",
        "procedure": "<The procedure the patient is being admitted for>",
        "allergies": "[<List of allergies; leave blank if the patient has no allergies>]",
        "current_medications": "[<List of Allergies>]",
        "past_medical_history": "[<List of Previous Medical Issues>]",
        "admitting_consultant": "<Admitting Consultant>",
        "ward": "<Admission Ward>",
        "specialty": "<Specialty the patient was admitted to>",
        "admission_type": "elective",
    },
    "event": {
#        "reasoning": "Reasoning for event",
        "event_type": "Type of event",
        "date": "Date of event",
        "time": "Time of event",
        "summary": "Short 1 sentence summary of the event",
#        "staff": "[<List of staff involved>]",
#        "details": "Details of the event",
#        "next_steps_decision": "Decision taken by clinicians for next treatment step",
#        "day_number": "How many days since patient admission did the event take place on",
#        "event_number": "The number of the event, starting from 0 and increasing",
    },
    
    "event_details": {
        "staff": "[<List of staff involved, usually only one member of staff per event.>]",
        "details": "A short description of the event.",
        "next_steps_decision": "Decision taken by clinicians for next treatment step. Only include medications that are starting, stopping, or changing. DO NOT write phrases like 'continue aspirin 75 mg OD'. Do not mention any ward rounds or monitoring of vital signs.",
    },
    
    "ED event": {
        "note_subject": "Short title for the note, e.g. 'ED triage', 'ED POC', 'ED Treatment Form', 'ED', 'ED Review'",
        "note_type": "Should be 'ED'",
        "Content": "Written in plain text (NOT markdown), the content of the note in a clincally relevant format for the given event, Only include clinically relevant information."
    },
    
    # https://www.heidihealth.com/templates/er-note-26372955
    "ED review and hand-over": {
        "note_subject": "Short title for the note - usually 'ED Depart Summary'",
        "note_type": "Should be 'ED Depart Summary'",
        "Patient": "Name of Patient",
        "Age": "Age of patient",
        "Sex": "Patient sex",
        "NHS No.:": "Patient NHS number",
        "Date/Time": "Date and time of review and handover",
        "Seen By": "Staff member who performed the review",
        "Presenting Complaint": "A short description of the reason for admission. Should be very brief.",
        "History of Presenting Complaint": "How the presenting complaint developed prior to the patient attending ED, as explained by the patient. Make sure that what is recorded here are SYMPTOMS not SIGNS, i.e. written exactly as reported by the patient with no technical medical language. If the presenting complaint is pain, use the SOCRATES acronym with each aspect on a new line to ensure all relevant details are clearly recorded:\nSite: Where is the pain located?\nOnset: When did the pain start? Was it sudden or gradual?\nCharacter: How would you describe the pain (e.g., sharp, dull, throbbing)?\nRadiates: Does the pain spread to other areas of the body?\nAssociations: Are there any other symptoms accompanying the pain (e.g., nausea, vomiting)?\nTiming: How often does the pain occur? Is it constant or intermittent?\nExacerbating factors: What makes the pain worse?\nSeverity: On a scale of 0-10, how severe is the pain?\nDo not include a review of systems here. Do not include things that have happened in ED so far.",
        "Past Medical History": "Long term conditions and past problems including any major surgeries the patient has had. This section should be a bulleted list. Do not include the patient's current acute issues. If no previous history then record as nil.",
        "Medications": "Currently prescribed medications. Include the dosage and frequency",
        "Allergies": "Any patient allergies.",
        "Social History": "Details of patient living situation etc.",
        "Family History": "Medical history of close blood relatives.",
        "Systems Review": "Inventory of body systems obtained through questions to the patient. This is often where red flags should be ruled out. This section should be structured with a new line for each system.",
        "On Examination": "Examination findings. Include the patient's general appearance at the beginning, followed by a detailed description of what was examined and the results. Ensure that the examination is sufficiently exhaustive from a medico-legal perspective. Do not include observations such as heart rate, blood pressure and temperature. Do not include imaging or blood test results.",
        "Observations": {
            "BP": "Blood pressure",
            "HR": "Heart rate",
            "RR": "Respiratory rate",
            "Temp": "Patient temperature",
            "SPO2": "Blood oxygen saturation",
        },
        "Investigations": "any investigation results such as imaging results or ECGs. Do not include lab tests like bloods or urine tests. Include any pending investigations. If applicable report blood gas values (PaO₂, PaCO₂) in kPa",
        "Test Results": "any lab test results e.g. blood tests or urine tests. Do not state what the normal range is. Do not include imaging results. If results are still pending, this should be stated, but be specific about which test results are pending.",             
        "Impression": "Suspected diagnosis/diagnoses with precipitant, for example, 'exacerbation of heart failure secondary to x y z'. This should be concise - only one or two lines. Do not explain the reasoning for the suspected diagnosis. If there is more than one possibility, differentials should be included here.",
        "Referral": "Brief record of hand-over to admitting ward, e.g. 'Referred to geriatrics', 'Referred to general medicine', 'Accepted by general medicine', 'Accepted by respiratory'",        
        "Plan": "Treatment plan for the patient. If there is more than one component, this should be a plain text numbered or bulleted list with a new line for each item, not a python list. Only include medications that are starting, stopping, or changing. DO NOT write phrases like 'continue aspirin 75 mg OD'. Do not mention any ward rounds or monitoring of vital signs. Each item should be precise, for example, state exactly which tests or medications the patient needs. Do not include patient education.",
    },

    "emergency admission": {
        "note_subject": "Short title for the note - either 'Medical Clerking' if admitting to a medical specialty or 'Surgical Clerking' if admitting to a surgical specialty",
        "note_type": "The type of note. Often this should be 'Medicine Inpatients' if admitting to a medical specialty or 'Surgery Inpatients' if admitting to a surgical specialty, but sometimes it can be specialty specific, e.g. 'Orthopaedics Inpatients' or 'Cardiology Inpatients'",
        "Clerking Doctor": "Name and role of the doctor who is writing this note. This should only include one doctor. Do not include any nurses in this field.",
        "Presenting Complaint": "A short description of the reason for admission. Should be very brief.",
        "History of Presenting Complaint": "How the presenting complaint developed prior to the patient attending ED, as explained by the patient. Make sure that what is recorded here are SYMPTOMS not SIGNS, i.e. written exactly as reported by the patient with no technical medical language. If the presenting complaint is pain, use the SOCRATES acronym with each aspect on a new line to ensure all relevant details are clearly recorded:\nSite: Where is the pain located?\nOnset: When did the pain start? Was it sudden or gradual?\nCharacter: How would you describe the pain (e.g., sharp, dull, throbbing)?\nRadiates: Does the pain spread to other areas of the body?\nAssociations: Are there any other symptoms accompanying the pain (e.g., nausea, vomiting)?\nTiming: How often does the pain occur? Is it constant or intermittent?\nExacerbating factors: What makes the pain worse?\nSeverity: On a scale of 0-10, how severe is the pain?\nDo not include a review of systems here. Do not include things that have happened in ED.",
        "Review of Systems": "Inventory of body systems obtained through questions to the patient. This is often where red flags should be ruled out. This section should be structured with a new line for each system.",
        "Past Medical History": "Long term conditions and past problems including any major surgeries the patient has had. This section should be a bulleted list. Do not include the patient's current acute issues. If no previous history then record as nil.",
        "Medications": "Currently prescribed medications. Include the dosage and frequency",
        "Allergies": "Any patient allergies.",
        "Social History": "Details of patients living situation that could be clinically significant. This should be bulleted and to the point. It should include the patient's mobility status and whether they need help with activities of daily living. It should also contain details of habits such as exercise, alcohol, smoking, or other recreational drug use. If relevant, it could also include occupational history and travel history. Do not include the names or contact details of family members.",
        "Family History": "Medical history of close blood relatives.",
        "On Examination": "Examination findings. Include the patient's general appearance at the beginning, followed by a detailed description of what was examined and the results. Ensure that the examination is sufficiently exhaustive from a medico-legal perspective. Do not include observations such as heart rate, blood pressure and temperature. Do not include imaging or blood test results.",
        "Observations": {
            "HR": "Heart rate (BPM)",
            "BP": "Blood Pressure (mmHg)",
            "RR": "Respiratory rate (br/min)",
            "Temp": "Temperature (Degrees Celcius. DO NOT use Fahrenheit)",
            "SpO2": "Oxygen saturation",
        },
        "Investigations": "any investigation results such as imaging results or ECGs. Do not include lab tests like bloods or urine tests. Include any pending investigations. If applicable report blood gas values (PaO₂, PaCO₂) in kPa",
        "Test Results": "any lab test results e.g. blood tests or urine tests. Do not state what the normal range is. Do not include imaging results. If results are still pending, this should be stated, but be specific about which test results are pending.",     
        "Impression": "Suspected diagnosis/diagnoses with precipitant, for example, 'exacerbation of heart failure secondary to x y z'. This should be concise - only one or two lines. Do not explain the reasoning for the suspected diagnosis. If there is more than one possibility, differentials should be included here.",
        "Plan": "Treatment plan for the patient. If there is more than one component, this should be a plain text numbered or bulleted list with a new line for each item, not a python list. Only include medications that are starting, stopping, or changing. DO NOT write phrases like 'continue aspirin 75 mg OD'. Do not mention any ward rounds or monitoring of vital signs. Each item should be precise, for example, state exactly which tests or medications the patient needs. Do not include patient education.",
    },

    "elective admission": {
        "note_subject": "Short title for the note - usually 'Surgical Clerking'",
        "note_type": "The type of note. Often this should be 'Surgery Inpatients', but sometimes it can be specialty specific, e.g. 'Orthopaedics Inpatients'",
        "Clerking Doctor": "Name and role of the doctor who is writing this note. This should only include one doctor. Do not include any nurses in this field.",
        "Presenting Complaint": "A short description of the reason the patient is being admitted for surgery. Should be very brief.",
        "Procedure": "Procedure patient is being admitted for.",
        "On Examination": "Examination findings. Include the patient's general appearance at the beginning, followed by a detailed description of what was examined and the results. Ensure that the examination is sufficiently exhaustive from a medico-legal perspective. Do not include observations such as heart rate, blood pressure and temperature. Do not include imaging or blood test results.",
        "Observations": {
            "HR": "Heart rate (BPM)",
            "BP": "Blood Pressure (mmHg)",
            "RR": "Respiratory rate (br/min)",
            "Temp": "Temperature (Degrees Celcius. DO NOT use Fahrenheit)",
            "SpO2": "Oxygen saturation",
        },
        "Investigations": "any investigation results such as imaging results or ECGs. Do not include lab tests like bloods or urine tests. Including any pending investigations. If applicable report blood gas values (PaO₂, PaCO₂) in kPa",
        "Test Results": "any lab test results e.g. blood tests or urine tests. Do not state what the normal range is. Do not include imaging results. If results are still pending, this should be stated, but be specific about which test results are pending.",
        "Plan": "Treatment plan for the patient. If there is more than one component, this should be a plain text numbered or bulleted list with a new line for each item, not a python list. Only include medications that are starting, stopping, or changing. DO NOT write phrases like 'continue aspirin 75 mg OD'. Do not mention any ward rounds or monitoring of vital signs. Each item should be precise, for example, state exactly which tests or medications the patient needs. Do not include patient education.",
    },
    
    "operation": {
        "note_subject": "Title of the note",
        "note_type": "Usually 'Theatre notes'",
        "Surgeon": "Name of surgeon leading the operation",
        "Assistant": "Name of assistant surgeon in operation",
        "Anaesthetist": "Anaesthetist involved in operation",
        "Anaesthesia Type": "Type of anaesthesia used in the operation",
        "Procedure": "Name of procedure performed",
        "Incision": "Where was the incision made during surgery",
        "Diagnosis": "Diagnosis of patient made during surgery",
        "Findings": "Any findings from surgery. If relevant, include details of surrounding tissue such as signs of inflammation.",
        "Tissue Removed": "Any tissue removed from patient during surgery",
        "Prostheses or Implants": "Any prosthetics or implants used during surgery",
        "Closure Technique": "How the incision was closed at conclusion of surgery",
        "Estimated Blood Loss": "Patient blood lost during surgery, if any",
        "Complications": "Any complications that occurred during surgery",
        "Post-Operative Care": "Any post operation care needed by patient. If there is more than one component, this should be a plain text numbered or bulleted list with a new line for each item, not a python list. Only include medications that are starting, stopping, or changing. Do not mention any ward rounds or monitoring of vital signs. Do not include any tests that are not needed. Each item should be precise, for example, state exactly which tests or medications the patient needs.",
        "Plan": "Other next steps not already mentioned under Post-Operative Care, e.g. specimens to be sent to histology. If there is more that one component, this should be a plain text numbered or bulleted list with a new line for each item, not a python list."
    },
    
    "general ward round": {
        "note_subject": "A short title for the note which is usually heavily abbreviated and should be no longer than 15 characters e.g. 'AMWR' for a ward round that occurs in the morning, or 'PMWR' for a ward round in the afternoon. Can also contain information about the specialty and who is present, e.g. 'WR AAU' and 'AAU PMWR' are ward rounds in the Acute Assessment Unit (AAU); 'Resp cons AMWR' is a morning ward round in the respiratory ward led by a respiratory consultant; 'PMBR' is an afternoon board round, i.e. more of the multi-disciplinary team are present compared to a normal ward round.",
        "note_type": "The type of note. Often this should be 'Medicine Inpatients' for medical specialties or 'Surgery Inpatients' for surgical specialties, but sometimes it can be specialty specific, e.g. 'Orthopaedics Inpatients' or 'Cardiology Inpatients'",
        "Clinician Leading Ward Round": "Name and role of doctor",
        "Presenting Complaint": "Initial patient complaint which lead to admission. Do not include any additional details about how long the symptoms had been going on.",
        "Issues": "A python dictionary of the acute clinical problems the patient is being actively treated for in hospital, ordered from most severe to least. Each key should be an acute problem where the value is the corresponding list of supporting details, as per this example: {'1. Problem name': ['Supporting detail 1', 'Supporting detail 2'], '2. Problem name': ['Supporting detail 1', 'Supporting detail 2']}. The problem name should be the acute diagnosis or condition being treated in hospital. This should always be a DIAGNOSIS or SUSPECTED DIAGNOSIS, never a symptom or state such as post-operative recovery (in this case the problem name should always be the original diagnosis that was treated via surgery). Supporting details are short comments such as severity markers, relevant investigation results, day of illness, or current management. Example: {'1. Lower Respiratory Tract Infection': ['CRP 112 mg/L', 'WBC 12.5 x10^9/L', 'Continued Oxygen dependency']}. Do not include chronic comorbidities such as hypertension or diabetes. Do not include functional states or background factors such as deconditioning or frailty. Do not include normal findings or negative results. Do not include problems being monitored for but not currently present. Keep each entry short, structured, and problem-oriented. If there is only one issue, only include one issue.",
        "Today": {
            "On Review": "What the patient says about how they are feeling during the ward round.",
            "Investigations": "any new investigations such as imaging results or ECGs. Do not include lab tests like bloods or urine tests. If applicable report blood gas values (PaO₂, PaCO₂) in kPa",
            "Test Results": "any new lab test results, e.g. blood tests or urine tests. Do not include old results from ED. Do not state what the normal range is. Do not include imaging results. If results are still pending, this should be stated, but be specific about which test results are pending.",
            "Observations": {
                "HR": "Heart rate (BPM)",
                "BP": "Blood Pressure (mmHg)",
                "RR": "Respiratory rate (br/min)",
                "Temp": "Temperature (Degrees Celcius. DO NOT use Fahrenheit)",
                "SpO2": "Oxygen saturation",
            },
            "On Examination": "Examination findings. Include the patient's general appearance at the beginning, followed by a detailed description of what was examined and the results. Ensure that the examination is sufficiently exhaustive from a medico-legal perspective. Do not include observations such as heart rate, blood pressure and temperature. Do not include imaging or blood test results.",
        },
        "Plan": "Treatment plan for the patient. If there is more than one component, this should be a plain text numbered or bulleted list with a new line for each item, not a python list. Only include medications that are starting, stopping, or changing. DO NOT write phrases like 'continue aspirin 75 mg OD'. Do not mention any ward rounds or monitoring of vital signs. Do not include patient education. Do not include any tests that are not needed. Each item should be precise, for example, state exactly which tests or medications the patient needs. If relevant, you could include discharge planning, e.g. 'Review tomorrow for possible discharge'.",
    },
    "post take ward round": {
        "note_subject": "A short title for the note - usually just four letters: 'PTWR'",
        "note_type": "The type of note. Often this should be 'Medicine Inpatients' for medical specialties or 'Surgery Inpatients' for surgical specialties, but sometimes it can be specialty specific, e.g. 'Orthopaedics Inpatients' or 'Cardiology Inpatients'",
        "Clinician Leading Ward Round": "Name and role of the consultant leading the ward round.",
        "Presenting Complaint": "Initial patient complaint which lead to admission",
        "History of Presenting Complaint": "Often this section will only say 'hx noted thank you' and nothing else.",
        "Issues": "A python dictionary of the acute clinical problems the patient is being actively treated for in hospital, ordered from most severe to least. Each key should be an acute problem where the value is the corresponding list of supporting details, as per this example: {'1. Problem name': ['Supporting detail 1', 'Supporting detail 2'], '2. Problem name': ['Supporting detail 1', 'Supporting detail 2']}. The problem name should be the acute diagnosis or condition being treated in hospital. This should always be a DIAGNOSIS or SUSPECTED DIAGNOSIS, never a symptom or state such as post-operative recovery (in this case the problem name should always be the original diagnosis that was treated via surgery). Supporting details are short comments such as severity markers, relevant investigation results, day of illness, or current management. Example: {'1. Lower Respiratory Tract Infection': ['CRP 112 mg/L', 'WBC 12.5 x10^9/L', 'Continued Oxygen dependency']}. Do not include chronic comorbidities such as hypertension or diabetes. Do not include functional states or background factors such as deconditioning or frailty. Do not include normal findings or negative results. Do not include problems being monitored for but not currently present. Keep each entry short, structured, and problem-oriented. If there is only one issue, only include one issue.",
        "On Review": "What the patient says about how they are feeling during the ward round.",
        "Investigations": "any new investigations such as imaging results or ECGs since admission. Do not include lab tests like bloods or urine tests. If applicable report blood gas values (PaO₂, PaCO₂) in kPa",
        "Test Results": "any new test results since admission, e.g. blood tests or urine tests. Do not include old results from ED. Do not state what the normal range is. Do not include imaging results. If results are still pending, this should be stated, but be specific about which test results are pending.",
        "Observations": {
            "HR": "Heart rate (BPM)",
            "BP": "Blood Pressure (mmHg)",
            "RR": "Respiratory rate (br/min)",
            "Temp": "Temperature (Degrees Celcius. DO NOT use Fahrenheit)",
            "SpO2": "Oxygen saturation",
            },
        "On Examination": "Examination findings. Include the patient's general appearance at the beginning, followed by a detailed description of what was examined and the results. Ensure that the examination is sufficiently exhaustive from a medico-legal perspective. Do not include observations such as heart rate, blood pressure and temperature. Do not include imaging or blood test results.",
        "Plan": "Treatment plan for the patient. If there is more that one component, this should be a plain text numbered or bulleted list with a new line for each item, not a python list. Only include medications that are starting, stopping, or changing. DO NOT write phrases like 'continue aspirin 75 mg OD'. Do not mention any ward rounds or monitoring of vital signs. Each item should be precise, for example, state exactly which tests or medications the patient needs. Do not include patient education."    
    },
    "inter-specialty review": {
        "note_subject": "A short title for the note, usually heavily abbreviated - often refers to the specialty of the reviewing doctor, e.g. 'Gastro note' or 'Gastro, gen surg and Radiology discussion'",
        "note_type": "The type of note. Often this should be 'Medicine Inpatients' for medical specialties or 'Surgery Inpatients' for surgical specialties, but sometimes it can be specialty specific, e.g. 'Orthopaedics Inpatients' or 'Cardiology Inpatients'",
        "Staff": "The name, role and specialty of the doctor writing the note. Do not include any other members of staff here.",
        "Additional Clinical History": "Any additional previous medical history of patient",
        "Issues": "A python dictionary of the acute clinical problems the patient is being actively treated for in hospital, ordered from most severe to least. Each key should be an acute problem where the value is the corresponding list of supporting details, as per this example: {'1. Problem name': ['Supporting detail 1', 'Supporting detail 2'], '2. Problem name': ['Supporting detail 1', 'Supporting detail 2']}. The problem name should be the acute diagnosis or condition being treated in hospital. This should always be a DIAGNOSIS or SUSPECTED DIAGNOSIS, never a symptom or state such as post-operative recovery (in this case the problem name should always be the original diagnosis that was treated via surgery). Supporting details are short comments such as severity markers, relevant investigation results, day of illness, or current management. Example: {'1. Lower Respiratory Tract Infection': ['CRP 112 mg/L', 'WBC 12.5 x10^9/L', 'Continued Oxygen dependency']}. Do not include chronic comorbidities such as hypertension or diabetes. Do not include functional states or background factors such as deconditioning or frailty. Do not include normal findings or negative results. Do not include problems being monitored for but not currently present. Keep each entry short, structured, and problem-oriented. If there is only one issue, only include one issue.",
        "Safety Alerts": "Any special attention or awareness that should be given to patient",
        "Medications": "Currently prescribed medications. Include the dosage and frequency",
        "Physical Examination": "Examination findings. Include the patient's general appearance at the beginning, followed by a detailed description of what was examined and the results. Ensure that the examination is sufficiently exhaustive from a medico-legal perspective. Do not include observations such as heart rate, blood pressure and temperature. Do not include imaging or blood test results.",
        "Test Results": "any lab test results e.g. blood tests or urine tests. Do not state what the normal range is. Do not include imaging results. If results are still pending, this should be stated, but be specific about which test results are pending.",
        "Investigations": "any investigation results such as imaging results or ECGs. Do not include lab tests like bloods or urine tests. Including any pending investigations. If applicable report blood gas values (PaO₂, PaCO₂) in kPa",
        "Future Orders": "Any further tests, investigations or prescriptions for patient",
        "Care Plan Outcomes": "Decisions made about the patient's care plan during the inter-specialty review",
    },    
    "nursing": {
        "note_subject": "A short title for the note, usually heavily abbreviated",
        "note_type": "Type of note - should be 'Nursing'",
        "Content": "The content of the nursing note in a clinically relevant format for the given event and staff writing style. Do NOT write in markdown.",
    },
    "misc": {
        "note_subject": "A short title for the note, usually heavily abbreviated.",
        "note_type": "The type of note. Often this should be 'Medicine Inpatients' for medical specialties or 'Surgery Inpatients' for surgical specialties, but sometimes it can be specialty specific, e.g. 'Orthopaedics Inpatients' or 'Cardiology Inpatients'",
        "Content": "The content of the miscellaneaous note for the given event. Sometimes the content will be empty and this note will only have a title. Should consider the staff writing style, but generally be shorter than other notes for the same given writing style. This section should never be longer than a few words. Do NOT write in markdown.",
    },
    "therapy": {
        "note_subject": "A short title which should state the type of therapy recieved by the patient. Usually heavily abbreviated.",
        "note_type": "The type of note. Often this should be 'Therapies Inpatients', but sometimes it can be more specific, e.g. 'Dietetics Documentation' or 'Physiotherapy Documentation'",
        "Content": "Written in plain text (NOT markdown), the content of the therapy note in a clincally relevant format for the given event and staff writing style, including the therapists name",
    },
    "pre-op assessment": {
        "note_subject": "Short title for the note - for example 'Pre-op Clinic' or 'Pre-op Assessment'",
        "note_type": "The type of note. Often this should be 'Surgery Outpatients', but sometimes it can be specialty specific, e.g. 'Orthopaedics Outpatients'",
        "Pre-clerking Doctor": "Name and role of the doctor who is writing this note. This should only include one doctor. Do not include any nurses in this field.",
        "Presenting Complaint": "A short description of the reason the patient has been referred for surgery. Should be very brief.",
        "Procedure": "The surgery the patient will be admitted for.",
        "History of Presenting Complaint": "How the presenting complaint developed prior to the patient being referred for surgery, as explained by the patient. Make sure that what is recorded here are SYMPTOMS not SIGNS, i.e. written exactly as reported by the patient with no technical medical language. If the presenting complaint is pain, use the SOCRATES acronym with each aspect on a new line to ensure all relevant details are clearly recorded:\nSite: Where is the pain located?\nOnset: When did the pain start? Was it sudden or gradual?\nCharacter: How would you describe the pain (e.g., sharp, dull, throbbing)?\nRadiates: Does the pain spread to other areas of the body?\nAssociations: Are there any other symptoms accompanying the pain (e.g., nausea, vomiting)?\nTiming: How often does the pain occur? Is it constant or intermittent?\nExacerbating factors: What makes the pain worse?\nSeverity: On a scale of 0-10, how severe is the pain?",
        "Past Medical History": "Long term conditions and past problems including any major surgeries the patient has had. This section should be a bulleted list. Do not include the patient's current acute issues.",
        "Medications": "Currently prescribed medications. Include the dosage and frequency",
        "Allergies": "Any patient allergies.",
        "Social History": "Details of patients living situation that could be clinically significant. This should be bulleted and to the point. It should include the patient's mobility status and whether they need help with activities of daily living. It should also contain details of habits such as exercise, alcohol, smoking, or other recreational drug use. If relevant, it could also include occupational history and travel history. Do not include the names or contact details of family members.",
        "Family History": "Medical history of close blood relatives.",
        "On Examination": "Examination findings. Include the patient's general appearance at the beginning, followed by a detailed description of what was examined and the results. Ensure that the examination is sufficiently exhaustive from a medico-legal perspective. Do not include observations such as heart rate, blood pressure and temperature. Do not include imaging or blood test results.",
        "Observations": {
            "HR": "Heart rate (BPM)",
            "BP": "Blood Pressure (mmHg)",
            "RR": "Respiratory rate (br/min)",
            "Temp": "Temperature (Degrees Celcius. DO NOT use Fahrenheit)",
            "SpO2": "Oxygen saturation",
        },
        "Investigations": "any investigation results such as imaging results or ECGs. Do not include lab tests like bloods or urine tests. Including any pending investigations. If applicable report blood gas values (PaO₂, PaCO₂) in kPa",
        "Test Results": "any lab test results e.g. blood tests or urine tests. Do not state what the normal range is. Do not include imaging results. If results are still pending, this should be stated, but be specific about which test results are pending.",
        "Plan": "Treatment plan for the patient. If there is more than one component, this should be a plain text numbered or bulleted list with a new line for each item, not a python list. Only include medications that are starting, stopping, or changing. DO NOT write phrases like 'continue aspirin 75 mg OD'. Do not mention any ward rounds or monitoring of vital signs. Each item should be precise, for example, state exactly which tests or medications the patient needs. Do not include patient education.",
    },
    "anaesthetics assessment": {
        "note_subject": "A short title for the note. Usually heavily abbreviated.",
        "note_type": "The type of note, usually 'Anaesthetic Documentation'",
        "Content": "Written in plain text (NOT markdown), the content of the note in a clincally relevant format for the given event and staff writing style, including the anaesthetist's name.",
    },
    "pre-op consent": {
        "note_subject": "A short title for the note. Usually heavily abbreviated.",
        "note_type": "The type of note, usually 'Pre-op Consent'",
        "Content": "Written in plain text (NOT markdown), the content of the note in a clincally relevant format for the given event and staff writing style.",
    },
    "pre-op checklist": {
        "note_subject": "A short title for the note. Usually heavily abbreviated.",
        "note_type": "The type of note, usually 'Pre-op Checklist'",
        "Content": "Written in plain text (NOT markdown), the content of the note in a clincally relevant format for the given event and staff writing style.",
    },
    "post-anaesthesia recovery": {
        "note_subject": "A short title for the note. Usually heavily abbreviated.",
        "note_type": "The type of note, usually 'Anaesthetic Documentation'",
        "Content": "Written in plain text (NOT markdown), the content of the note in a clincally relevant format for the given event and staff writing style, including the name of the post-anaesthesia care staff member.",
    },    
    "simple_note_template": {
        "note_subject": "A short title for the note.",
        "note_type": "Type of note.",
        "Content": "The content of the note can be in any order and can combine sections. Please use the content information to fill out this section. Do NOT write in markdown.",
    },
    "orthopaedic referral": {
        "note_subject": "A short title for the note. Usually heavily abbreviated.",
        "note_type": "orthopaedic referral",
        "Content": "Written in plain text (NOT markdown). A concise, professional orthopaedic referral letter in a semi-structured clinical style. The letter should follow a logical flow: an optional header (date, addressee, patient identifiers if provided), a brief opening sentence indicating referral, a short paragraph summarising relevant background (past medical history and medications only if available), and a clear, well-written description of the presenting complaint (including mechanism of injury, key symptoms, examination findings, and any investigations or management already performed). The tone should be formal but natural, allowing slight variation in phrasing rather than rigid templating. Include a polite closing that invites specialist input. Only include details explicitly provided in the source information, and omit any sections where information is missing rather than inventing content.",
    }
}

# Keys should already exist in the template
template_sections_to_combine = {
    "ED event": {
        "Content": []
    },
    "ED review and hand-over": {
        # Read this as: combine Presenting Complaint into History of Presenting Complaint
        "Presenting Complaint": ["History of Presenting Complaint"],
        "On Examination": ["Observations"],
    },        
    "emergency admission": {
        "Presenting Complaint": ["History of Presenting Complaint"],
        "Investigations": ["Test Results"]
    },
    "elective admission": {
        "Investigations": ["Test Results"],
    },
    "operation": {
        "Procedure": ["Incision", "Closure Technique"]
    },
    "general ward round": {
        "Investigations": ["Test Results"],
    },
    "post take ward round": {
        "Presenting Complaint": ["History of Presenting Complaint"],
        "Investigations": ["Test Results"],
    },
    "inter-specialty review": {
        "Investigations": ["Test Results"],
    },
    "nursing": {
        "Content" : [],
    },
    "misc": {
        "Content" : [],
    },
    "therapy": {
        "Content": [],
    },
    "pre-op assessment": {
        "Investigations": ["Test Results"],
    },
    "anaesthetics assessment": {
        "Content": [],
    },
    "pre-op consent": {
        "Content": [],
    },
    "pre-op checklist": {
        "Content": [],
    },
    "post-anaesthesia recovery": {
        "Content": [],
    },
    "orthopaedic referral": {
        "Content": [],
    },
    
}