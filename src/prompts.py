from string import Template

# This file contains all prompts used in our pipeline.

# Prompts are organised by:
# - Patients and Admissions
# - Patient Journeys
# - Clinical Notes
# - Processing
# - Evaluation Prompts

# PATIENTS AND ADMISSIONS

# This section contains the following prompts: 

# - emergency_admission_prompt
# - elective_admission_prompt
# - generate_patient_prompt
# - length_of_stay_prompt

patient_and_admission_prompts = {
    "emergency_admission_prompt" : Template("""
        
        You are an expert at generating synthetic emergency patient admissions that are clinically realistic and will be used for AI evaluation.
        It is extremely important that these emergency patient admission details are high-quality, realistic and similar to real-world data. 
        
        # Instructions:
        
        - Generate a synthetic NHS patient's emergency admission details for synthetic data generation.
        - Use the following patient details to generate the emergency admission details.
        
        # Patient Information
        
        The patient details are:
        
        ${PATIENT_DETAILS}
        
        # Admission Details
        
        The patient's admission details are:
        
        - Their presenting complaint is ${CHIEF_COMPLAINT}.
        - The admission consultant is ${ADMISSION_CONSULTANT}.
        - They are diagnosed with ${DIAGNOSIS} in the emergency department.
        - The admission date is ${ADMISSION_DATE}.
        - The admission time is ${ADMISSION_TIME}.
        
        # Output Format
        
        Your response MUST be in the following format:
        
        ${OUTPUT_FORMAT}
        """),
    "novel_disease_admission_prompt" : Template("""
        
        You are an expert at generating synthetic emergency patient admissions that are clinically realistic and will be used for AI evaluation.
        It is extremely important that these emergency patient admission details are high-quality, realistic and similar to real-world data. 
        
        # Instructions:
        
        - Generate a synthetic NHS patient's emergency admission details for synthetic data generation.
        - Use the following patient details to generate the emergency admission details.
        
        # Patient Information
        
        The patient details are:
        
        ${PATIENT_DETAILS}
        
        # Admission Details
        
        The patient's admission details are:
        
        - Their presenting complaint is ${CHIEF_COMPLAINT}.
        - The admission consultant is ${ADMISSION_CONSULTANT}.
        - They are diagnosed with ${DIAGNOSIS} in the emergency department.
        - The diagnosis is confirmed by ${CONFIRMED_BY}.
        - The diagnosis is supported by ${SUPPORTED_BY}.
        - The additional symptoms are ${ADDITIONAL_SYMPTOMS}.
        - The admission date is ${ADMISSION_DATE}.
        - The admission time is ${ADMISSION_TIME}.
        - Additional information to support diagnosis is ${ADDITIONAL_INFO}
        
        # Output Format
        
        Your response MUST be in the following format:
        
        ${OUTPUT_FORMAT}
        """),
    
    
    "elective_admission_prompt" : Template("""
        
        You are an expert at generating synthetic elective patient admissions that are clinically realistic and will be used for AI evaluation.
        It is extremely important that these elective patient admission details are high-quality, realistic and similar to real-world data. 
        
        # Instructions:
        
        - Generate a synthetic NHS patient's elective admission details for synthetic data generation.
        - Use the following patient details to generate the elective admission details.
        
        # Patient Information
        
        The patient details are:
        
        ${PATIENT_DETAILS}
        
        # Admission Details
        
        The patient's admission details are:
        
        - Their elective procedure is ${PROCEDURE}.
        - The admission consultant is ${ADMISSION_CONSULTANT}.
        - The specialty of the procedure is ${SPECIALITY}.
        - The admission date is ${ADMISSION_DATE}.
        - The admission time is ${ADMISSION_TIME}.
        
        # Output Format
        
        Your response MUST be in the following format:
        
        ${OUTPUT_FORMAT}
        """),
    
    
    "generate_patient_prompt" : Template("""
        
        You are an expert at generating synthetic patient details that are clinically realistic and will be used for AI evaluation.
        It is extremely important that these patient details are high-quality, realistic and similar to real-world data. 
        
        # Instructions:
        
        - Generate a synthetic NHS patient's details for synthetic data generation.
        - Use the following patient details to generate the details.
        
        # Patient Information
        
        - The patient's name is ${NAME}, their age is ${AGE}, their address is ${ADDRESS} and their GP is ${GP}.
        - They have the following allergies: ${ALLERGIES}
        
        # Output Format
        
        Your response MUST be in the following format:
        
        ${OUTPUT_FORMAT}
        """),
    

    "length_of_stay_prompt" : Template("""
    
        You are an expert at estimating the length of stay in days for a patient in hospital given some admission details. 
        You will be given some admission details, and you should give a single integer output which represents the length of stay in days. 
        It is extremely important that the length of stay is realistic and similar to real-world data. 
        
        # Instructions
        
        - Write a single integer output, which should represent the estimated length of stay in days for a patient in hospital. 
        
        # Patient Information
        
        Use the patient admission details to estimate the length of stay in days
        The patient admission details are:
        
        ${PATIENT_ADMISSION_DETAILS}
        
        # Output Format
        
        Only respond with a positive integer. 
        e.g. "3"
        DO NOT say "3 days"  
        
        Include nothing else in your response.
       
        # Final Instructions
        
        - You are an expert at estimating the length of stay in days for a patient in hospital given some admission details.
        - Given the patient admission details above, estimate the length of stay in days
        - Simpler admissions should return a shorter integer, like 1
        - The most complex admissions could return a number up to 30
    """),

    
                                      
}

# JOURNEYS

# This section contains the following prompts

# - emergency_admission_instructions_prompt
# - emergency_surgery_instructions_prompt
# - emergency_admission_reason_prompt
# - elective_admission_instructions_prompt
# - elective_admission_reason_prompt
# - nursing_note_instruction_prompt
# - misc_note_instruction_prompt
# - therapy_note_instruction_prompt
# - therapy_note_instruction_prompt
# - inter_specialty_review_instruction_prompt
# - simple_patient_journey_prompt
# - continue_journey_prompt
# - test_events_complete_prompt
# - first_event_instructions_prompt
# - last_event_instructions_prompt
# - event_instructions_prompt
# - generate_event_details_prompt
# - emergency_journey_information_prompt
# - elective_journey_admission_prompt
# - validate_simple_journey_prompt

patient_journey_prompts = {
    
    "emergency_admission_instructions_prompt" : """
        - The first few events should be 'ED event' notes.
        - The journey should contain exactly one 'ED review and hand-over' event.
        - After the ED summary, there should be exactly one 'emergency_admission' event. """,

    "orthopaedic_emergency_admission_instructions_prompt" : """
        - If the patient has an orthopaedic admission, the journey should contain exactly one 'orthopaedic referral' event. This is a letter written to an Orthopaedics specialist. It should occur if the patient has a non-urgent orthopaedics admission which needs a future appointment in a few days time.""",

    "emergency_surgery_instructions_prompt" : """
        - Since this surgery is non-elective, no additional 'pre-op assessment' clinic is needed.
        - After the 'post take ward round', if anaesthesia is needed, the journey should contain an 'anaesthetics assessment' event.
        - There should be a 'pre-op consent' and 'pre-op checklist' event in preparation for surgery.
        - The actual operation should be represented by an 'operation' event.
        - If relevant, the operation should be followed by a 'post-anaesthesia recovery' event.""",
    
    
    "emergency_admission_reason_prompt" : Template("""
        - The patient's presenting complaint is ${CHIEF_COMPLAINT} and they are diagnosed with ${DIAGNOSIS} in hospital. Ensure that the event types are clinically appropriate for this presenting complaint/diagnosis."""),

        
    "novel_disease_reason_prompt" : Template("""
    The patient has a novel illness/disease called ${DIAGNOSIS}. Below are instructions for how ${DIAGNOSIS} must affect the patient's journey.
    
        - Firstly the patient’s chief complaint is ${CHIEF_COMPLAINT} but the patient should have additional symptoms of ${ADDITIONAL_SYMPTOMS}.
        - ${DIAGNOSIS_SUPPORTED_BY} must be used to inform suspicion of a diagnosis of ${DIAGNOSIS}.
        - The individual must have their diagnosis confirmed later in the pathway via ${DIAGNOSIS_CONFIRMED_BY}. 
        
    You must use the information in a clinically sensible order and all novel wording must be used.
        """),
            
    
    "elective_admission_instructions_prompt" : """
        - The first event in the journey should be a 'pre-op assessment' event. This should occur 1-2 weeks before the admission.
        - If anaesthesia is required, the 'pre-op assessment' should be followed by an 'anaesthetics assessment' event, usually on the same day.
        - After this there should be a 'pre-op consent' event and a 'pre-op checklist' event. These should also be on the same day as the 'pre-op assessment'.
        - On the day of surgery, there should be exactly one 'elective admission' event.
        - The actual operation should be represented by an 'operation' event.
        - If relevant, the operation should be followed by a 'post-anaesthesia recovery' event.""",

    
    "elective_admission_reason_prompt" : Template("""
        - The elective procedure the patient has been admitted for is ${PROCEDURE}. Ensure that the event types are clinically appropriate for this presenting complaint/diagnosis."""),

    
    "nursing_note_instruction_prompt" : """
        - There should be approximately 5 'nursing' events per day while the patient is in hospital.""",

    
    "misc_note_instruction_prompt" : """
        - There should be at least a couple 'misc' events per patient journey.""",

    
     "therapy_note_instruction_prompt" : """
        - Most patients should have 1-2 'therapy' events per day while the patient is in hospital.""",

    
    "inter_specialty_review_instruction_prompt" : """
        - When input is required from a specialty other than that of the ward where the patient is staying, there should be an 'inter-specialty review' event.""",

    
    "simple_patient_journey_prompt" : Template("""
    
        You are an expert at generating synthetic patient clinical NHS pathways that are clinically realistic and will be used for AI evaluation.
        It is extremely important that these patient pathway details are high-quality, realistic and similar to real-world data. 
        
        # Instructions
        
        - Write a realistic series of documented events in a patient journey given the following admission details. You must include the entire sequence of events from start to finish.
        - The suggested event types you can use are ${POSSIBLE_EVENT_TYPES}, although you may include any events you feel are realistic. This can include events not in this list if it adds to the clinical realism.${ADMISSION_INSTRUCTIONS}${ORTHOPAEDIC_REFERRAL_INSTRUCTION}
        - The journey should contain exactly one 'post take ward round' event, which should occur on the day of admission or the day after.${EMERGENCY_SURGERY_INSTRUCTIONS}
        - There should be at least one 'general ward round' or 'post take ward round' per day while the patient is in hospital.${NURSING_NOTE_INSTRUCTION}${THERAPY_NOTE_INSTRUCTION}${MISC_NOTE_INSTRUCTION}${INTER_SPECIALITY_REVIEW_INSTRUCTION}
        - For each event, include the date and time of the event.
        - The admission date is ${ADMISSION_DATE} and the admission time is ${ADMISSION_TIME}, and the estimated discharge date is ${DISCHARGE_DATE}. The journey must last ${LENGTH_OF_STAY} days with around ${APPROX_EVENTS_PER_DAY} events per day, resulting in around ${NUMBER_OF_EVENTS} total events. You may add more events in a single day if clinically realistic. 
        ${ADMISSION_REASON}

        # Output Format
        
        Only respond with a list of events. Ensure that the output is in correct python list format like:
        [<event>,
         <event>,
         <event>,
        ]
        
        Each event MUST be in the following format:
        
        ${OUTPUT_FORMAT}
    
        Output nothing but the list. No explanations, notes, or text outside the list.
        
        # Completion Requirements
    
        - You must include the entire sequence of events from start to finish.
        - Do not truncate, summarise, or stop early. Continue until the journey is fully complete.
        - Do not omit any events for brevity
        
        # Final Instructions
        
        - You are writing a clinically realistic series of events.
        - Include the date and time of each event.
        - The events must start at the admission date (${ADMISSION_DATE}) and time (${ADMISSION_TIME}), and end at the discharge date (${DISCHARGE_DATE}). This means the journey should be ${LENGTH_OF_STAY} days long with around ${APPROX_EVENTS_PER_DAY} events per day, resulting in around ${NUMBER_OF_EVENTS} total events.
        - Include at least one general or post take ward round per day.${NURSING_NOTE_INSTRUCTION}
        - Your output MUST be a valid python list of json objects, where each json object is one event.
        - You must include the entire sequence of events from start to finish.
    """),

    "continue_journey_prompt": """
        Continue to output the remaining events.
        
        As before, response only with a list of the remaining events. Ensure that the output is in correct python list format like:
            [<event>,
             <event>,
             <event>,
            ]
        Include nothing else in your output, only the remaining events as a valid python list.
    """,
    

    "test_events_complete_prompt" : Template("""Does this LLM output end before completion of it's task?
    
        Your task is to identify whether this task was complete. You will receive a LLM generated patient journey through hospital and must judge if the LLM completed the journey.
        
        There are two methods you can use to identify if a task is complete.
    
        ## Method 1
        
        If the LLM output contains a sentence or note stating the LLM terminated the event early, respond with 'YES'.
        
        For example, the note at the end of an output could be: 
        - # Events continue for subsequent days until discharge on 2023-11-16 with similar clinical progression...
        - For brevity I have omitted the final events.
        - This is the beginning of a detailed synthetic patient pathway. If you would like me to continue generating the rest of the events for all 15 days, please confirm or let me know!
    
        If you see any messages similar to this, you must reply with "YES"

        ## Method 2

        You may assume that if the final events in the patient journey are related to the discharge, or discharge planning, that a journey is complete. In this case, respond with "NO".
    
        Method 2 MUST take priority over method 1. Even if the LLM includes a message or note at the end, if the final events are discharge related respond with "NO".

        ## Reminder
        - You wil be given a series of events representing a complete or partial patient journey.
        - You must judge whether the patient journey has finished.
        - A patient journey is complete if its final events are related to discharge, and the LLM does not add any notes stating it terminated early.
        - Your response must be YES if an LLM terminated early, or NO if not. Include nothing else in your response.
    
        The entire LLM output is: ${EVENT}    
    """),
    

    "first_event_instructions_prompt" : Template("""You are generating details for the first event in the patient journey. The patient journey will be as follows:
        ${FULL_JOURNEY}
                
        You are to add details to the first event:
                
        ${FIRST_EVENT}
        """),
    

    "last_event_instructions_prompt" : Template("""You are generating details for the final event of a patient journey. The patient journey so far has been:
    
        ${PREVIOUS_JOURNEY}
                
        You are to add details to the final event:
        
        ${FINAL_EVENT}
    """),
    

    "event_instructions_prompt" : Template("""These are events occurring before the current event:
    
        ${PREVIOUS_EVENTS}
                
        You are adding details to the current event. This is the current event:
        
        ${CURRENT_EVENT}
                
        Ensure the details you are adding make clinical sense given the future events. These events occur after the current event:
        
        ${LATER_EVENTS}
    """),
    

    "generate_event_details_prompt" : Template("""
        You are an expert in generating clinically realistic details for events in an NHS patients' journey through hospital, given information about their journey.
        It is extremely important that the event details are high-quality, realistic and similar to real-world data.
        
        # Instructions
        
        - Generate event details for an event of type ${EVENT_TYPE}. ${EVENT_TYPE_DESCRIPTION}
        - The admission date is ${ADMISSION_DATE}, and the discharge date is ${DISCHARGE_DATE}. You must create the details for an event taking place on ${CURRENT_DATE} at ${CURRENT_TIME}.
        - The details should include a short description of what happens, any decisions that are made about the next steps for the patient, and the staff involved.
        - Make sure that you describe a single, simple event. Only one thing should happen.
        - Ensure that the details of the event represent a clinically realistic next step based on what has happened to the patient so far.
        - This event takes place ${DAYS_LEFT} before the patient is discharged from hospital. Ensure that the patient's condition reflects this.
        - Explicitly name any drugs or antibiotics prescribed and provide a detailed description of any abnormal test results.
        - You should use the following patient admission information to generate realistic event details.
        
        # Patient Information
        
        ${PATIENT_INFORMATION}    
        
        # Patient Journey
        
        ${EVENT_INSTRUCTIONS}
        
        # Staff Names
        
        The following staff work at the hospital. One, two or three of them should be involved in the event. You may include additional staff if this contributes to clinical realism.
        
        ${STAFF_NAMES}
        
        Some staff members have roles contained in brackets. You may wish to use this when assigning them to events, alongside the previous events they have been involved with. If a staff member has no clear role, you can use them wherever you like as long as you preserve clinical realism. Ensure you include their role in your output.
        
        # Output Format
        
        Your output MUST be in the following format:
        
        ${OUTPUT_FORMAT}
        
        Include nothing else in your response."""),

    
    "emergency_journey_information_prompt" : Template("""
        The patients reason for admission is: ${ADMISSION}.
        The patients diagnosis is: ${DIAGNOSIS}"""),

    
    "elective_journey_admission_prompt" : Template("""
        The elective procedure the patient was admitted for is: ${PROCEDURE}"""),

    
    "validate_simple_journey_prompt" : Template("""
        You are validating a synthetic patient journey to ensure it is clinically realistic. 
        
        # Instructions
        
        - Review the following synthetic patient journey and ensure it is clinically realistic and similar to real-world data.
        - If there are any inconsistencies, or the patient journey is not realistic, revise the patient journey accordingly.
        
        # Output format
        
        Return the revised document as valid JSON with the following structure:
        
        {{
        "reasoning": "Reasoning used to evaluate the clinical realism",
        "changes": "True" or "False" depending on whether changes have been made to the patient journey,
        "journey":
            [<event>,
             <event>,
             <event>,
            ],
        "description_of_changes": "A description of the changes made to the content"
        }}
        
        Each <event> MUST be in the following format:
        
        ${EVENT_FORMAT}
        
        If "changes" is "False", you may return "events" as "None".
        
        # Detailed Instructions
        
        - Following the output schema, first output the "reasoning" key. Use the "reasoning" key to think step-by-step and reason as to whether the provided patient journey is clinically realistic.
        - If no changes are needed, return "changes" as "False", "journey" as "None" and "description_of_changes" as "None".
        - If changes are needed, return "changes" as "True" and "journey" as an edited version of the original journey edited to be more clinically realistic. "description_of_changes" should be a description of changes made to the journey.
        - Ensure you follow the output schema exactly. Do not output anything outside of the provided output schema.
        
        # Relevant Information
        
        ${JOURNEY_INFORMATION}
        
        The patient journey is as follows:
        
        ${PATIENT_JOURNEY}
        """),
}

# CLINICAL NOTES

# This section contains the following prompts:

# - generate_patient_examinations_prompt
# - generate_red_flags_prompt
# - examination_info_prompt
# - clinical_note_prompt
# - validate_responses_prompt

clinical_note_prompts = {
    "generate_patient_examinations_prompt" : Template("""
        You are an expert in medical law. You are tasked with determining which physical examinations a doctor would be legally required to perform during a medical event for a patient with the following information and previous  events in their journey.
        
        Patient Information:
        ${PATIENT_INFORMATION}
        
        Current Event in Journey:
        ${CURRENT_EVENT}
        
        Previous Patient Journey events:
        ${PREVIOUS_EVENTS}
        
        Any examinations mentioned in the current event details should be included.
        
        Return only a short list of relevant examinations which should be performed and nothing else. Do not include lab tests. Do not include measurements for heart rate, blood pressure, respiratory rate, body temperature or oxygen saturation.
        """),

    
    "generate_red_flags_prompt" : Template("""
        You are an expert in medical examinations. You are tasked with determining the relevant red flags to check for a patient with the following primary complaint and previous events in their journey.
        
        Primary Complaint:
        ${PRIMARY_COMPLAINT}
        
        Current Event in Journey:
        
        ${CURRENT_EVENT}
        
        Previous Patient Journey events:
        ${PREVIOUS_EVENTS}
        
        Red flag symptoms are signs or indicators of a potential serious underlying disease that requires urgent medical attention. 
        Example red flag symptoms to check for types of presenting complaints include the following.
        
        Chest Pain Red flags:
        - Crushing/central pain radiating to jaw/arm/back
        - Associated diaphoresis, nausea, vomiting
        - Syncope/presyncope
        - Sudden tearing pain radiating to back (dissection)
        - Pleuritic pain with haemoptysis or acute shortness of breath 
        Shortness of Breath Red flags:
        - Severe distress, accessory muscle use, unable to speak full sentences
        - Stridor or audible wheeze
        - Haemoptysis
        - Sudden onset severe shortness of breath
        - Chest pain with shortness of breath
        Abdominal Pain Red flags:
        - Haematemesis or melaena
        - Haemodynamic instability (tachycardia, hypotension)
        - Peritonism (rigid abdomen, rebound tenderness)
        - Severe, sudden-onset “tearing” pain 
        - Persistent vomiting or inability to keep fluids down
        Fall / Collapse Red flags:
        - Loss of consciousness or amnesia
        - Anticoagulant use
        - Head strike with headache, vomiting, neuro deficit
        - Chest pain or palpitations prior to fall
        - New focal weakness or speech disturbance
        Weakness Red flags:
        - Sudden onset weakness, especially unilateral
        - Associated facial droop or speech difficulty
        - Progressive ascending weakness or areflexia 
        - Bowel/bladder dysfunction (cord compression)
        - Severe headache with neuro deficit
        Dizziness / Lightheadedness Red flags:
        - Syncope or presyncope
        - Chest pain, palpitations
        - New focal neurological symptoms (diplopia, dysarthria, limb weakness, ataxia)
        - Severe occipital headache (posterior circulation stroke/bleed)
        - Persistent vomiting, inability to walk
        Headache: Common diagnoses Red flags:
        - Sudden “thunderclap” onset 
        - Worst headache of life
        - Neurological deficits, confusion, seizure
        - Fever, neck stiffness, photophobia (meningitis)
        - Immunosuppression or known cancer
        Fever Red flags:
        - Hypotension, tachycardia, altered mental status (sepsis)
        - Rigors with murmur (endocarditis)
        - Photophobia, neck stiffness (meningitis)
        - Recent surgery or indwelling devices
        - Immunocompromised patient
        Confusion / Altered Mental Stat Red flags:
        - Sudden onset with focal neurological deficit
        - Glasgow Coma Scale < 13
        - Seizures
        - Signs of sepsis (fever, hypotension)
        - Hypoglycaemia not improving with correction
        Leg Pain / Swelling Red flags:
        - Sudden onset pain/swelling, especially unilateral 
        - Red, hot, tender leg with systemic unwellness (necrotising fasciitis)
        - Non-healing ulcer, black skin patches (ischaemia)
        - Recent immobilisation, surgery, long travel
        - History of cancer or thrombophilia
        
        Your response should be a simple list of red flag symptoms to check for given the patient's journey and presenting complaint. Nothing else should be included in the response. Only mention symptoms which are highly relevant to the patient's condition.
    """),
    

    "examination_info_prompt" : Template("""
        Patient Examinations: 
        The relevant physical examinations which should be recorded as having being performed by the responsible clinician are as follows.

        ${RELEVANT_EXAMS}

        Include the results of these examinations in the "On Examination" section of the clinical note."""),

    "red_flag_info_prompt" :  Template("""
        Relevant sections of the note outlined in the template below should contain a record of all the following symptoms being checked for by the responsible clinician.

        ${RED_FLAGS}
    """),
    

    "clinical_note_prompt" : Template("""
    
        You are an expert in generating detailed, realistic and structured clinical notes for NHS patients.
        
        # Instructions
    
        - Generate a realistic clinical document of type "${EVENT_TYPE}". ${EVENT_TYPE_DESCRIPTION}.
        - Ensure that the document captures and includes all vital information from the provided event and patient information, ensuring no critical details are omitted.
        - Do not repeat information. If there are two possible sections where a critical detail could be recorded, choose only one of them. Do not include it in the other one.
        - You must adopt the following writing style: ${PERSONA}
        - The note is a synthetic NHS note so use British English and dates in DD/MM/YY format.
        - The note can only be written by ONE member of staff, but may reference other staff members. The clinician writing the note should not be referred to in the third person in the note.
        - You may assume the person reading the note is a medical expert. Use medical terminology and do not define abbreviations.
        
        # Patient and Event Details
        
        Below are the details about the patient that you will use to write a clinical note.
    
        Patient Information:
        ${PATIENT_INFORMATION}
    
        Relevant Event for the document you will write:
        ${RELEVANT_EVENT}
    
        Previous Patient Journey events:
        ${PREVIOUS_EVENTS}
        
        ${EXAMINATION_INFORMATION}
    
        ${RED_FLAG_INFORMATION}
        
        # Output Format
        
        Your output must be output as valid JSON with the following structure. Do not use any markdown formatting:
        ${OUTPUT_FORMAT}
    
        Do not add any extra keys to the above structure. Only remove keys if they are not relevant, for example, if there are no relevant test results. Do not include any python lists; all lists should be in plain text within the relevant dictionary entry.
        
        # Final Instructions
        
        - Generate a realistic, clinically accurate and faithful clinical note of type ${EVENT_TYPE}.
        - Ensure that all details are clinically appropriate and consistent with the patient information and patient journey. 
        - Adopt the following persona: ${PERSONA} Use medical terminology and do not define abbreviations. The clinician writing the note should not be referred to in the third person in the note.
        - Ensure your output is a valid JSON.
    """),
        "simple_clinical_note_prompt" : Template("""
    
        You are an expert in generating detailed, realistic and structured clinical notes for NHS patients.
        
        # Instructions
    
        - Generate a realistic clinical document of type "${EVENT_TYPE}". ${EVENT_TYPE_DESCRIPTION}.
        - Ensure that the document captures and includes all vital information from the provided event and patient information, ensuring no critical details are omitted.
        - Do not repeat information. If there are two possible sections where a critical detail could be recorded, choose only one of them. Do not include it in the other one.
        - You must adopt the following writing style: ${PERSONA}
        - The note is a synthetic NHS note so use British English and dates in DD/MM/YY format.
        - The note can only be written by ONE member of staff, but may reference other staff members. The clinician writing the note should not be referred to in the third person in the note.
        - You may assume the person reading the note is a medical expert. Use medical terminology and do not define abbreviations.
        
        # Patient and Event Details
        
        Below are the details about the patient that you will use to write a clinical note.
    
        Patient Information:
        ${PATIENT_INFORMATION}
    
        Relevant Event for the document you will write:
        ${RELEVANT_EVENT}
    
        Previous Patient Journey events:
        ${PREVIOUS_EVENTS}
        
        ${EXAMINATION_INFORMATION}
    
        ${RED_FLAG_INFORMATION}

        # Information to Include in Output

        The information below is taken from a structured output, and we want to create a more simplified output. If they suggest returning something as a dictionary or list please do not do this, write it in prose.
        
         ${OUTPUT_INFO}
        
        # Output Format
        
        Your output must be valid JSON with the following structure. All values should be a coherent sentence. You MUST NOT have any values in the JSON with a dictionary or list structure, these should all be written out in prose. Do not use any markdown formatting:
        
        ${SIMPLE_OUTPUT_FORMAT}

        Do not add any extra keys to the above structure. For every value in the dictionary above, do not include anything that looks like a python list or dictionary. All values should be prose.

        
        # Final Instructions
        
        - Generate a realistic, clinically accurate and faithful clinical note of type ${EVENT_TYPE}.
        - Ensure that all details are clinically appropriate and consistent with the patient information and patient journey. 
        - Adopt the following persona: ${PERSONA} Use medical terminology and do not define abbreviations. The clinician writing the note should not be referred to in the third person in the note.
        - Ensure your output is a valid JSON.
    """),
    

    "validate_responses_prompt" : Template("""

        You are a clinical documentation expert that is reviewing clinical documents and ensuring their faithfulness to reference material.

        # Instructions

        - Review the following clinical document and ensure that all it is faithful to the reference information. Faithfulness refers to how well the note captures and includes all vital information from the provided event and patient information, ensuring no critical details are omitted.
        - If there are any inconsistencies or missing details, revise the document accordingly.

        # Output Format

        Return the revised document as valid JSON with the following structure:
        {{
          "title": "<Title of the document>",
          "document_type": "<Type of the document>",
          "patient_id": "<Patient ID>",
          "reasoning": "Reasoning to determine the relevance",
          "content": "${CONTENT}"
          "changes": <True or False depending on whether changes have been made to the clinical note>
          "description_of_changes": "A description of the changes made to the content"
        }}

        # Relevant Information

        The current clinical document is:
        ${CLINICAL_DOCUMENT}

        The following information should be used to check the faithfulness of the clinical document.

        The current event is:
        ${CURRENT_EVENT}

        The patient information is:
        ${PATIENT_INFORMATION}

        The patient journey up to this point is:
        ${PATIENT_JOURNEY}

        # Detailed Instructions

        - Following the output schema, first output the "title", "document_"type" and "patient_id".
        - Use the "reasoning" key to think step-by-step and reason as to whether all relevant information from the patient information and patient journey is captured. Remember, it is extremely important that these clinical notes contain no contradictions to the reference material. 
        - If no changes are needed, return the original document in the "content" with the exact same JSON format, "changes" = False and the "description_of_changes" is None.
        - If changes are needed, return the altered document in the "content" with the exact same JSON format, "changes" = True and the "description_of_changes" is a string containing a description of the changes you have made.
        - You must include all of the keys in your response.
    """)
}

# PROCESSING

# This section contains the following prompts:

# - clean_outputs_prompt
# - add_abbreviations_prompt

processing_prompts = {
    "clean_outputs_prompt" : Template("""
                    You are an expert at cleaning string representations of python ${CLEANING_TYPE}s.
                    The following string was failed to parse as a ${CLEANING_TYPE} when using json.loads() in python:
                    ${VALUE}
                    Return the cleaned python ${CLEANING_TYPE}. Include nothing else in your response. 
                    """),

    
    "add_abbreviations_prompt" : Template("""
        You are augmenting synthetic clinical sentences to contain common UK medical abbreviations.
        
        Instructions:
        
        You will be given a piece of text that likely contains very few abbreviations.
        
        If the text contains terms which are often abbreviated in clinical notes, you should augment the text to contain the new abbreviations.
        - Do not change the meaning of the clinical text. Only add abbreviations if they do not change the overall clinical meaning.
        - Do not define any of your abbreviations by adding brackets. You may assume the person reading your output is a medical expert.
        - If an abbreviation is already defined in the text, remove the brackets and the definition.
        - Do not change the style of the text. Try to keep punctuation and formatting as similar as possible.
        - Do not create new abbreviations, only add abbreviations if they are often used in NHS clinical notes.
        - If you are unsure whether an abbreviation is commonly used, leave the word un-abbreviated.
        
        If the text contains no terms that should be abbreviated:
        - Return the original text with no changes.
        
        Reminder:
        - It is incredibly important you do not create new abbreviations. Do not abbreviate uncommon terms, as these are rarely abbreviated.
        - Prioritise realistic clinical notes that you would likely see in NHS documentation.
        
        For example:
        - You may abbreviate words like hypertension, 
        - Do not abbreviate words like infection or constipation, or other terms not often abbreviated.
        - If a term is defined using brackets, remove the definition. 'patient has hypertension (HTN)' would become 'patient has HTN'
    
        Output Format:
        
        Your response must be in the following json format:
        
        {{"text" : "the augmented text",
          "number_of_abbreviations": "the number of abbreviations you have added"}}
          
        Return nothing else in your output.
        
        The text you are augmenting is: ${TEXT}
        """)
}


# EVALUATION PROMPTS

# This section contains the following prompts:

# - calculate_fluency_prompt

evaluation_prompts = {
    "calculate_fluency_prompt" : Template("""
    
        You are an expert language evaluator assessing the fluency of a given text. Fluency refers to how naturally and smoothly the text reads, considering factors such as grammar, coherence, sentence structure, and ease of understanding.
    
        Evaluation Criteria:
        Rate the fluency of the text on a scale of 1 to 5, where:
    
        1 (Very Poor): The text is highly disjointed, ungrammatical, and difficult to understand. Frequent errors disrupt readability.
        2 (Poor): The text has noticeable grammatical issues, awkward phrasing, and lacks smoothness, making it somewhat difficult to read.
        3 (Acceptable): The text is mostly understandable but contains occasional awkward phrasing, grammatical mistakes, or minor clarity issues.
        4 (Good): The text is well-structured, grammatically sound, and easy to follow, with only minor issues.
        5 (Excellent): The text is exceptionally clear, natural, and well-written, with flawless grammar and a seamless flow.
        
        Instructions:
        
        Analyze the provided text based on the above fluency criteria.
        Provide a well-reasoned evaluation in free text, discussing the strengths and weaknesses of fluency. Give specific examples from the text.
        Output the result in JSON format, with "reasoning" first, followed by "score".
        
        Example Output Format:
        
        {{
          "reasoning": <Reasoning for fluency score>,
          "score": <score>
        }}
        
        Now, evaluate the following text:
        
        ${NOTE}
    """),


    "calculate_groundedness_prompt" : Template("""
        You are an expert medical evaluator assessing the groundedness of a synthetic clinical note. Groundedness refers to how well the note aligns with the given event and patient information, ensuring that it is factually consistent and logically supported.
    
        Evaluation Criteria:
        Assess the groundedness of the note based on the following:
    
        1 (Not Grounded): The note contains major inconsistencies, fabrications, or contradictions with the provided event and patient information.
        2 (Weakly Grounded): The note is mostly inconsistent but may contain some minor elements that match the provided context.
        3 (Partially Grounded): The note has some accurate information but also includes notable inconsistencies, omissions, or unverifiable claims.
        4 (Mostly Grounded): The note aligns well with the event and patient information but may have minor inconsistencies or slight extrapolations.
        5 (Fully Grounded): The note is completely consistent with the event and patient information, without any contradictions or fabrications.
        
        Instructions:
        Compare the note against the provided event and patient information to determine if it is factually accurate and contextually appropriate.
        Identify any inconsistencies, unsupported claims, or contradictions.
        Provide a well-reasoned evaluation in free text explaining your assessment. If appropriate, give specific examples from the text that reduced the groundedness score. 
        Output the result in JSON format, with "reasoning" first, followed by "score". Include nothing else in your response.
        
        Example Output Format:
        
        {{
          "reasoning": <explain your reasoning step by step>,
          "score": "<your score here>"
        }}
        
        Now, evaluate the following:
    
        Note: ${NOTE}
        
        Event: ${EVENT}
        
        Patient Information: ${PATIENT_INFO}
    """),


    "calculate_relevance_prompt" : Template("""
    
        You are an expert medical evaluator assessing the relevance of a synthetic clinical note. Relevance refers to how well the note captures and includes all vital information from the provided event and patient information, ensuring no critical details are omitted.
    
        Evaluation Criteria:
        Assess the relevance of the note based on the following:
    
        1 (Not Relevant): The note fails to reference key details from the event or contains mostly irrelevant information.
        2 (Weakly Relevant): The note captures some relevant details but misses most of the critical information.
        3 (Partially Relevant): The note includes some key details but omits or underemphasizes important aspects.
        4 (Mostly Relevant): The note covers most of the vital information with minor omissions or a slight lack of emphasis.
        5 (Fully Relevant): The note captures all critical aspects of the event with no omissions, ensuring a comprehensive and appropriate summary.
        
        Instructions:
        Compare the note against the provided event and patient information to determine if all vital details are included.
        Identify any missing, underrepresented, or unnecessary details.
        Provide a well-reasoned evaluation in free text explaining your assessment. If appropriate, give specific examples from the text that reduced the relevance score.
        Output the result in JSON format, with "reasoning" first, followed by "score". Include nothing else in your response.
        
        Example Output Format:
        
        {{
          "reasoning": <explain your reasoning step by step>,
          "score": "<your score here>"
        }}
        
        Now, evaluate the following:
        
        Note: ${NOTE}
    
        Event: ${EVENT}
    
        Patient Information: ${PATIENT_INFO}
    """)
}