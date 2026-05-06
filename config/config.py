# CONFIG

# This file contains params we expect you are unlikely to need to change when using the pipeline. Please see params.py for other params.


CONFIG = {
    "possible_event_types" : {
        "ED event": "This is a specific care event that happens to the patient in the emergency department. It could be triage, streaming, observations or investigation. The event details should be short - no more than two sentences, describing a simple event. This event should never be attended by a doctor, only by a nurse or other member of staff.",
        "ED review and hand-over": "This is when the patient leaves the emergency department to be admitted onto a ward. The patient is handed over to the ward care team, and a summary of the patient's time in the emergency department is written by an emergency medicine doctor.",
        "emergency admission": "This is when the patient arrives on the ward after being admitted through A&E. A medical doctor from the ward care team examines the patient and conducts a thorough review of the patient to understand the history of the presenting complaint. This should never be lead by the admitting consultant.",
        "elective admission": "This is when a patient arrives in a ward as part of an elective admission. A medical doctor from the ward examines the patient to ensure they are fit for the elective procedure they were admitted for.",
        "post take ward round": "This is the first ward round after the patient is admitted. This event is typically attended by the admitting consultant and never a nurse.",
        "general ward round": "This is any ward round that happens after the initial post take ward round.  This event is typically lead by a specialty registrar or consultant, but never a nurse or a foundation trainee.",
        "pre-op assessment": "This is when a patient visits the hospital as an outpatient 1-2 weeks prior to elective surgery. A resident doctor takes the patient's history, undertakes relevant tests, ensures the patient's condition is optimised for surgery, and plans for any potential complications.",
        "anaesthetics assessment": "This is when a patient is seen by an anaesthetist, who determines whether the patient is fit to undergo an anaesthetic, and decides what kind of anaesthetic is most appropriate based on their level of comorbid disease and the complexity of the surgery. This event requires and anaesthetist.",
        "pre-op consent": "This is when the procedure is explained to the patient, the patient is given a chance to ask questions, and their consent to the procedure is formally recorded. A doctor must be present for this.",
        "pre-op checklist": "This is when it is confirmed that all required preparations for surgery have been made.",
        "operation": "This is when the patient undergoes an operation. This event requires a specialist surgical doctor.",
        "post-anaesthesia recovery": "This is necessary after general, epidural or spinal anaesthesia. The patient is observed by an anaesthetist until they have stable cardiovascular and respiratory systems and are awake and able to communicate.",
        "inter-specialty review": "This is when a senior doctor from a *different* specialty is asked to advise on the patient's care.", # not used in respiratory specialty
        "nursing" : "This could include charting events such as documenting medications administered, vital signs, physical assessments, and interventions. They could also include a description of a nursing visit, a specific care event, or a summary of care.",
        "misc" : "This could include next of kin being contacted, GPs contacted, capacity information, or consent information. They could also be part of a different event but that wasn't the clinical part of the event, just some admin that was done. This will be a very short and basic event, with only one thing occuring in each event.",
        "therapy": "This could include encounters such as physical therapies, speech and language therapies and dietary therapies among others depending on patient needs.",
        "orthopaedic referral": "orthopaedic referral must occur after initial assessment for an orthopaedic condition. This is when an orthopaedic surgeon is asked to review the patient and provide their expert opinion on the management of a musculoskeletal problem. This event requires an orthopaedic surgeon.",
        }, # Event types to NOT filter out
    "doctor_roles" : [
        "ED Doctor",
        "ED Consultant",
        "Foundation Trainee",
        "Specialty Registrar",
        "Consultant",
        "Surgeon",
        "Orthopaedic Surgeon"
    ],
    "therapist_roles" : [
        "Speech and Language",
        "Physical",
        "Dietry",
    ],
    "sections_to_ignore_typos" : [
        "note_subject",
        "note_type",
        "Patient",
        "Age",
        "Sex",
        "NHS No.:",
        "Staff",
        "Surgeon",
        "Assistant",
        "Anaesthetist",
        "Clinician Leading Ward Round",
        "Signature",
        "Clerking Doctor",
        "Day of Admission"
    ],
    "sections_to_ignore_abbreviations" : [
        "note_subject",
        "note_type",
        "Patient",
        "Age",
        "Sex",
        "NHS No.:",
        "HR",
        "BP",
        "RR",
        "Temp",
        "SpO2",
        "Day of Admission"
    ],
    "style_instructions" : {
        "concise": "Use very short, clear sentences. Avoid filler words and redundancy. Ensure all details are written down but there is no extra information. Ensure each section is as short as possible.",
        "bullet_points": "Present information as bullet points for easy readability. Bullet points are written using '-', but write nothing else in markdown form. You do not need to use full sentences, each bullet point can be in concise note form.",
        "note": "Write in incredibly short notes. Notes need to only make sense to fellow medical staff, so can be include abbreviations and shortened words. Ensure each section is short. You may leave sections blank if they are not neccesary.",
        "abcde":"Write in short and concise note form. When describing patient physical examinations, write notes using the ABCDE approach. Create 5 short bullet points - one for each section labelled: A,B,C,D,E. Ensure each section is short."
        # We reccomend you DO NOT include the following as they were judged as unrealsitc by clinicians.
        #"neutral": "Stick to facts and observations. Avoid expressing opinions or emotions. Write in note form",
        #"verbose": "Be detailed and expansive. Explain ideas thoroughly, even if it takes more space.",
        #"narrative": "Write in a flowing, story-like manner. Connect ideas with transitions and natural pacing.",
        #"formal": "Maintain a professional tone. Avoid contractions and casual language.",
        #"informal": "Use conversational, casual language. Feel free to use contractions and a friendly tone.",
    },
    "allergy_prevalence" : {
        "pollen" : 0.29, 
        "nuts" : 0.02,
        "penicillin"  : 0.06,
        "sulfonamides": 0.04,
        "macrolides": 0.01,
        "cephalosporins": 0.01,
        "aspirin":0.02,
    }
}
