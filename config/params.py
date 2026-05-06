# PARAMS

# This contains the basic params needed to run the pipeline. Please see config.py to see more change more details of the pipeline.

PARAMS = {
    "pipeline_config": {
        "TEST_MODE": False, # If True, runs pipeline in test mode and generates one clinical note per patient
        "model" : "ri.language-model-service..language-model.gpt-5-1", # The name of the LLM you would like to use. 
        "generate_patient_information": True, # If True, generate patient information
        "generate_admission_information": True, # If True, generate admission details for patients
        "generate_patient_journey": True, # If True, generate patient journey
        "number_of_generations": 1, # The number of patient journeys to generate
        "admission_start": "2026-01-01", # The start of the range of when admissions can happen.
        "admission_end": "2026-01-07", # The start of the range of when admissions end. 
        "elective_start_hour": 7, # The starting hour for elective admissions. (This is 24 hrs)
        "elective_end_hour": 18, # The ending hour for elective admissions. (This is 24 hrs)
        "ae_start_hour": 0, # The starting hour for A&E admissions. (This is 24 hours)
        "ae_end_hour": 22, # The starting hour for A&E admissions. (This is 24 hours)
        "filter_journey": True, # If true, filters out events NOT in possible_event_types
        "simple_template_only":False, # If true, it will try to remove structure from the notes.
        "generate_clinical_notes": True, # If True, generates clinical notes
        "LLM_validator_iterations_clinical_note": 1, # The number of times an LLM validator should be used for each clinical note generation
        "LLM_validator_iterations_patient_journey": 1, # The number of times an LLM validator should be used for each journey generation
        "add_abbreviations_to_content": 1, # The probability a member of staff adds abbreviations to the content of notes
        "add_abbreviations_to_headings": 0.2, # The probability a member of staff  adds abbreviations to the section headings of notes
        "typo_rate": 0.04, # Probability a word will have a typo
        "number_of_staff_names": 20, # The number of staff names (approximately) to generate for each patient journey
        "use_intermediate_hospital_staff" : False, # Whether to use the same staff as saved in intermediate_hospital_staff
        "set_new_hospital_staff" : False, # Whether to save new hospital staff to intermediate_hospital_staff
        "generate_new_staff_per_patient": True, # If True, generates unique staff members for each patient. Else, each patient has the same members of staff.
        "complex_journey_rate": 0.0, # The rate to include complex journeys - those containing medical contradictions and multiple possible diagnoses.
        "novel_disease_rate": 0, # For the table this sets it as a novel disease rate.
        "elective_admission_rate": 1, # The chance of a patient having an elective admission as opposed to emergency
        "use_rare_admissions": True, # If true, includes rare reasons for admissions
        "combine_sections": True, # If True then some staff members will combine template sections when writing patient notes.
        "add_signature": True, # If True, adds staff signature to end of note.
        "bias_testing": None, # If not None, an array of ["gender"].
        "minimum_patient_age": 18, # Minimum patient age when generating patient admission
        "maximum_patient_age": 90,# Maximum patient age when generating patient admission
        "site_name": "Bramble Trust", # None, or name of trust
        "site_code": "BRT12", # None, or code of trust
        "elective_admissions_dataset" : "orthopaedic_elective_admissions_data", # Name of dataset to read elective admissions
        "emergency_admissions_dataset" : "orthopaedic_emergency_admissions_data", # Name of dataset to read emergency admissions
        "patients_input_dataset" : "example_names_input_data", # Name of dataset containing patients input data, such as names
    },
}

if PARAMS["pipeline_config"]["TEST_MODE"]:
    print("TEST MODE ACTIVE")