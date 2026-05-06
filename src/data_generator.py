from src.prompts import patient_and_admission_prompts, patient_journey_prompts, clinical_note_prompts
from src.doc_templates import document_templates, template_sections_to_combine
from src.dataset_utils import generate_staff_gmc_and_pin, add_sign_off_to_note, prepare_note_data, prepare_patient_data, prepare_admission_data, prepare_encounter_data, prepare_evaluation_data, write_dataset, format_note, get_journey_evaluation_details, generate_staff_gmc_and_pin
from src.processing import call_llm, call_llm_async, read_write_data, clean_outputs, remove_failures, clean_int, combine_patients_and_admissions, clean_patient_details, combine_template_sections, add_abbreviations_to_dict, add_typos_to_dict, normalise_array_struct_column, create_admission_window, random_24_hour_time, build_output_info
from config.params import PARAMS
from config.config import CONFIG

import random
import json
import re
import pandas as pd
import numpy as np
import string
from datetime import datetime, timedelta, time
import asyncio
import uuid
from itertools import zip_longest
import ast

# Contains functions classes used to generate synthetic journeys and clinical notes

# - Helper Functions
# - generate_patients
# - generate_admissions
# - generate_journeys
# - generate_clinical_notes
# - add_augmentations


# __________________ HELPER FUNCTIONS ___________________
# Used in multiple classes.

def generate_random_person(
        patient_df,
        name_only = False, 
        last_name_only = False
    ):
    """
    Generates a random person, which can include: name, gender and address.
    """
    if last_name_only:
        names = patient_df[["GENDER", "LAST"]].sample(1).values[0]
    else:
        names = patient_df[["GENDER", "FIRST", "MIDDLE", "LAST"]].sample(1).values[0]
        
    person_gender = names[0]
    clean_names = [name for name in names[1:] if not pd.isna(name)]
    person_name = ' '.join(clean_names)
    
    if last_name_only:
        if person_gender == "M":
            person_name = f"Mr {person_name}"
        else:
            titles = ["Mrs", "Miss"]
            person_name = f"{random.choice(titles)} {person_name}"
    
    if name_only:
        return {"name": person_name}
    
    address = patient_df[["ADDRESS", "CITY", "POSTCODE"]].sample(1).values[0]
    person_address = ' '.join(address)
    return {"name": person_name, "gender": person_gender, "address": person_address}


def generate_hospital_staff(
        patient_df,
        N, 
        titles = ["Dr.", "Nurse", "Therapist", ""], 
        doctor_roles = CONFIG["doctor_roles"],
        therapist_roles = CONFIG["therapist_roles"]
    ):
    """
    Generates a list of length N of random names.

    When N = 1 AND only one title is present, generates 1 staff member.
    If N > 1, ensure a complete sample of different roles.
    """
    staff_names = []
    minimum_N = 0
    
    # First generate atleast one role for each doctor
    if "Dr." in titles:
        minimum_N += len(doctor_roles)
        for role in doctor_roles:
            random_person = generate_random_person(patient_df, name_only = True)["name"]
            staff_names.append(f"Dr. {random_person} ({role})")
            
    # Then, generate at least one role per therapist
    if "Therapist" in titles:
        minimum_N += len(therapist_roles)
        for role in therapist_roles:
            random_person = generate_random_person(patient_df, name_only = True)["name"]
            staff_names.append(f"Therapist {random_person} ({role})")
    
    # Then, generate atleast 2 nurses
    if "Nurse" in titles:
        minimum_N += 2
        for i in range(2):
            random_person = generate_random_person(patient_df, name_only = True)["name"]
            staff_names.append(f"Nurse {random_person}")
    
    if N > 1 or len(staff_names) == 0:  
        # Check N is large enough
        if N < minimum_N:
            print(f"Number of staff generated is too small, generating {minimum_N} staff")
            N = minimum_N

        # Generate remaining staff randomly with no specified job role
        for i in range(N - minimum_N):
            random_person = generate_random_person(patient_df, name_only = True)["name"]
            title = random.choice(titles)
            if title:
                staff_names.append(f'{title} {random_person}')

    return staff_names


# __________________ GENERATE PATIENTS ___________________

class generate_patients():
    """
    Generates a list of realistic patients.
    """

    def __init__(
        self,
        names_df = None,
        generate_patient_information = None,
        number_of_generations = None,
        bias_tests = None,
        model = None
    ):
        # Data
        self.names_df = names_df if names_df is not None else read_write_data(PARAMS["pipeline_config"]["patients_input_dataset"], "read")
        # Params
        self.generate_patient_information = generate_patient_information if generate_patient_information is not None else PARAMS["pipeline_config"]["generate_patient_information"]
        self.number_of_generations = number_of_generations if number_of_generations is not None else PARAMS["pipeline_config"]["number_of_generations"]
        self.bias_tests = bias_tests if bias_tests is not None else PARAMS["pipeline_config"]["bias_testing"]
        # Model
        self.model = model if model is not None else PARAMS["pipeline_config"]["model"]
        self.list_of_patients_df = None
        self.allergy_prevalence = CONFIG["allergy_prevalence"]

    
    def generate_patient_allergies(self, allergy_prevalence):
        """
        Generate possible allergies for a patient.
        """
        allergies = [a for a, p in allergy_prevalence.items() if p > random.random()]

        if len(allergies) == 0:
            allergies = ["None"]

        return ", ".join(allergies)

    
    async def generate_patients(self, last_name_only = False):
        """
        Uses an LLM call to generate a list of patients with details.
        """
        N = self.number_of_generations
        last_name_only = True if self.bias_tests is not None and "gender" in self.bias_tests else False
        
        patients_info = [generate_random_person(self.names_df, last_name_only = last_name_only) for i in range(N)]
        gps = [generate_hospital_staff(self.names_df, 1, titles = ["Dr."], doctor_roles = ["GP"]) for i in range(N)]
        allergies = [self.generate_patient_allergies(self.allergy_prevalence) for i in range(N)]
        ages = [random.randint(
            PARAMS["pipeline_config"]["minimum_patient_age"],
            PARAMS["pipeline_config"]["maximum_patient_age"]
        ) for i in range(N)]

    
        prompts = [patient_and_admission_prompts["generate_patient_prompt"].substitute(
            NAME = patients_info[i]["name"],
            ADDRESS = patients_info[i]["address"],
            GP = gps[i][0],
            ALLERGIES = allergies[i],
            OUTPUT_FORMAT = json.dumps(document_templates["patient_details"], indent = 2),
            AGE = ages[i],
        ) for i in range(N)]
        
        tasks = [call_llm_async(prompt, self.model) for prompt in prompts]
        
        raw_patient_details = await asyncio.gather(*tasks)
        
        return raw_patient_details

    async def run(self, return_output=False):
        if self.generate_patient_information:
            print(f'Generating {self.number_of_generations} patients...', end = " ")

            patients_information = await self.generate_patients()
            
            patients_information = clean_outputs(patients_information,"dictionary",self.model)
            patients_information, removed_ids = remove_failures(patients_information)
            
            if removed_ids:
                print(f"Patients {removed_ids} removed due to incorrect json compilation")
        
            for patient_information in patients_information:   
                patient_information["patient_id"] = str(uuid.uuid4())
                patient_information["medical_record_number"] = str(random.randint(100000000, 999999999))
                patient_information["nhs_number"] = str(random.randint(100000000, 999999999))

            list_of_patients = [json.dumps(patient_information) for patient_information in patients_information]
            list_of_patients_df = pd.DataFrame(list_of_patients)

            print("DONE")
            self.list_of_patients_df = list_of_patients_df
            
            if return_output:
                return list_of_patients_df
        else:
            print("SKIPPING PATIENT GENERATION")

    def write_patients_to_dataset(self):
        if self.list_of_patients_df.empty or self.list_of_patients_df is None:
            raise ValueError("Dataset is empty — refusing to overwrite intermediate_patients")

        read_write_data("intermediate_patients", "write", self.list_of_patients_df)

        


# ___________________ GENERATE ADMISSIONS ___________________


class generate_admissions():
    """
    Generates reason for admission for each patient.
    """
    
    def __init__(
        self,
        patients = None,
        names_df = None,
        notional_complaints_stats = None,
        elective_procedures = None,
        generate_admissions_information = None,
        number_of_generations = None,
        elective_admission_rate = None,
        novel_disease_rate = None,
        use_rare_admissions = None,
        model = None
    ):
        # Data
        self.patients = patients if patients is not None else read_write_data("intermediate_patients", "read")
        self.names_df = names_df if names_df is not None else read_write_data(PARAMS["pipeline_config"]["patients_input_dataset"], "read")
        self.notional_complaints_stats = notional_complaints_stats if notional_complaints_stats is not None else read_write_data(
            PARAMS["pipeline_config"]["emergency_admissions_dataset"], "read"
        )
        self.elective_procedures = elective_procedures if elective_procedures is not None else read_write_data(
            PARAMS["pipeline_config"]["elective_admissions_dataset"], "read"
        )
        # Params
        self.generate_admission_information = generate_admissions_information if generate_admissions_information is not None else PARAMS["pipeline_config"]["generate_admission_information"]
        self.number_of_generations = number_of_generations if number_of_generations else PARAMS["pipeline_config"]["number_of_generations"]
        self.elective_admission_rate = elective_admission_rate if elective_admission_rate is not None else PARAMS["pipeline_config"]["elective_admission_rate"]
        self.use_rare_admissions = use_rare_admissions if use_rare_admissions is not None else PARAMS["pipeline_config"]["use_rare_admissions"]
        self.novel_disease_rate = novel_disease_rate if novel_disease_rate is not None else PARAMS["pipeline_config"]["novel_disease_rate"]
        # Model
        self.model = model if model is not None else PARAMS["pipeline_config"]["model"]
        # Initialise data
        self.emergency_admission_complaints = self.initialise_admission_data("emergency")
        self.elective_procedures = self.initialise_admission_data("procedure")

        admission_start = PARAMS["pipeline_config"]["admission_start"]
        admission_end = PARAMS["pipeline_config"]["admission_end"]
        
        self.admission_window = create_admission_window(admission_start, admission_end)
        self.elective_start_hour =  PARAMS["pipeline_config"]["elective_start_hour"]
        self.elective_end_hour =  PARAMS["pipeline_config"]["elective_end_hour"]
        self.ae_start_hour =  PARAMS["pipeline_config"]["ae_start_hour"]
        self.ae_end_hour =  PARAMS["pipeline_config"]["ae_end_hour"]
        self.list_of_admissions_df = None

    
    async def generate_all_admissions(self, patients_information):
        """
        Uses an LLM to generate a list of admission reasons.
        """
        prompts =  [
            self.generate_elective_admission_prompt(patient_information)
            if self.elective_admission_rate > random.random()
            else self.generate_emergency_admission_prompt(patient_information)
            for patient_information in patients_information
        ]
        
        tasks = [call_llm_async(prompt, self.model) for prompt in prompts]
        
        all_admissions = await asyncio.gather(*tasks)
        
        return all_admissions

    def generate_emergency_admission_prompt(self, patient_details):
        """
        Generates a prompt to create an emergency admission.
        """
        
        admission_consultant = generate_hospital_staff(self.names_df, 1, titles = ["Dr."], doctor_roles = ["Consultant"])
        
        complaint = self.generate_emergency_admission_complaint(patient_details["gender"][0], int(patient_details["age"]))

        admission_date =  random.choice(self.admission_window)
        admission_time = random_24_hour_time(self.elective_start_hour,
                                     self.elective_end_hour,
                                     self.ae_start_hour,
                                     self.ae_end_hour,
                                     generate_elective=False)
        
        novel_disease_flag = complaint["novel_disease_flag"]

        if novel_disease_flag == 1:
            
            prompt = patient_and_admission_prompts["novel_disease_admission_prompt"].substitute(
                PATIENT_DETAILS = json.dumps(patient_details),
                CHIEF_COMPLAINT = complaint["chief_complaint"],
                ADMISSION_CONSULTANT = admission_consultant,
                DIAGNOSIS = complaint["diagnosis"],
                ADDITIONAL_SYMPTOMS = complaint["additional_symptoms"],
                ADDITIONAL_INFO = complaint["additional_info"],
                CONFIRMED_BY = complaint["confirmed_by"],
                SUPPORTED_BY = complaint["supported_by"],
                ADMISSION_DATE = admission_date,
                ADMISSION_TIME = admission_time,
                OUTPUT_FORMAT = json.dumps(document_templates["novel_disease_admission_details"], indent = 2)
            )
        else:
            prompt = patient_and_admission_prompts["emergency_admission_prompt"].substitute(
                PATIENT_DETAILS = json.dumps(patient_details),
                CHIEF_COMPLAINT = complaint["chief_complaint"],
                ADMISSION_CONSULTANT = admission_consultant,
                DIAGNOSIS = complaint["diagnosis"],
                ADMISSION_DATE = admission_date,
                ADMISSION_TIME = admission_time,
                OUTPUT_FORMAT = json.dumps(document_templates["emergency_admission_details"], indent = 2)
            )
        
        return prompt
    
    def generate_elective_admission_prompt(self, patient_details):
        """
        Generates a prompt to create an elective admission.
        """
        
        admission_consultant = generate_hospital_staff(self.names_df, 1, titles = ["Dr."], doctor_roles = ["Consultant"])
        
        procedure = self.generate_elective_procedure(patient_details["gender"][0], int(patient_details["age"]))

        admission_date =  random.choice(self.admission_window)
        admission_time = random_24_hour_time(self.elective_start_hour,
                                     self.elective_end_hour,
                                     self.ae_start_hour,
                                     self.ae_end_hour,
                                     generate_elective=True)
    
        prompt = patient_and_admission_prompts["elective_admission_prompt"].substitute(
            PATIENT_DETAILS = json.dumps(patient_details),
            PROCEDURE = procedure["procedure"],
            ADMISSION_CONSULTANT = admission_consultant,
            SPECIALITY = procedure["speciality"],
            ADMISSION_DATE = admission_date,
            ADMISSION_TIME = admission_time,
            OUTPUT_FORMAT = json.dumps(document_templates["elective_admission_details"], indent = 2)
        )
        
        return prompt

    def initialise_admission_data(self, admission_type):
        """
        If admission_type is "emergency":
        - Reads data on chief complaints and diagnoses from notional input file and prepares for use in generate_admission_complaint.
        If admission_type is "procedure":
        - Reads data on elective procedures from notional input file and prepares for use in generate_admission_complaint.
        Filters to patients above the minimum age in params who were admitted.
        """        

        if admission_type == "emergency":
            df = self.notional_complaints_stats
        elif admission_type == "procedure":
            df = self.elective_procedures
        else:
            print("ERROR - Not a valid a admission reason.")
            return None

        max_age = PARAMS["pipeline_config"]["maximum_patient_age"]
        
        df["age_lower"] = df["Age_Category"].str.split(r"[-+]+").str.get(0)
        df["age_lower"] = pd.to_numeric(df["age_lower"], errors="coerce").astype('Int64')
        df["age_upper"] = df["Age_Category"].str.split(r"[-+]+").str.get(1)
        df["age_upper"] = pd.to_numeric(df["age_upper"], errors="coerce").astype('Int64').fillna(max_age)
        
        gender_dictionary = {
            "Male": "M",
            "Female": "F"
        }


        if admission_type == "emergency":
            
            if not self.use_rare_admissions:
                df = df[df["rare_disease"] == 0].copy()

            df["Sex_Category"] = df["Sex_Category"].map(gender_dictionary)
            df["ChiefComplaintDescription"] = df["ChiefComplaintDescription"].str.split("\s+\(").str.get(0)
            df["DiagnosisDescription"] = df["DiagnosisDescription"].str.split("\s+\(").str.get(0)
            
            columns_to_keep = [
                "ChiefComplaintDescription",
                "DiagnosisDescription",
                "NovelDiseaseFlag",
                "AdditionalSymptoms",
                "AdditionalInformation",
                "ConfirmedBy",
                "SupportedBy",
                ]

            
            df = df[(df["age_lower"] >= PARAMS["pipeline_config"]["minimum_patient_age"]) &  (df["age_upper"] <= PARAMS["pipeline_config"]["maximum_patient_age"])]
            df = df[columns_to_keep + ["age_lower", "age_upper", "Sex_Category", "count"]]
            
            return df

        elif admission_type == "procedure":

            df.rename(columns={"Sex": "Sex_Category"}, inplace=True)
            df["Sex_Category"] = df["Sex_Category"].map(gender_dictionary)
            df = df[(df["age_lower"] >= PARAMS["pipeline_config"]["minimum_patient_age"]) & (df["age_upper"] <= PARAMS["pipeline_config"]["maximum_patient_age"])]
            df = df[["Speciality", "Procedure", "age_lower", "age_upper", "Sex_Category"]]
            
            return df
        

    def generate_emergency_admission_complaint(self, gender: str, age: int):
        """
        This function takes a dataframe of chief complaints (df) and filters to the gender it was passed.
        The gender argument should take the value "M" or "F".
        It then randomly samples from this filtered dataframe using the count column as weights.
        It returns an age, chief complaint and diagnosis in a dictionary.
        """    

        novel_disease_flag = np.random.binomial(1, self.novel_disease_rate)

        admission_complaints_df = self.emergency_admission_complaints[
            (self.emergency_admission_complaints["Sex_Category"] == gender)
            & (self.emergency_admission_complaints["age_lower"] <= age)
            & (self.emergency_admission_complaints["age_upper"] >= age)
            & (self.emergency_admission_complaints["NovelDiseaseFlag"] == novel_disease_flag)
        ]
    
        if len(admission_complaints_df) == 0:
            print(f"ERROR - there are no rows in emergency admissions dataset for a {gender} patient of age {age} years, and novel_disease flag {novel_disease_flag}")
        
        sampled_details = admission_complaints_df.sample(1, weights="count").to_dict("records")[0]

        if novel_disease_flag == 1:
            
            return {
                "chief_complaint": sampled_details["ChiefComplaintDescription"], 
                "diagnosis": sampled_details["DiagnosisDescription"],
                "novel_disease_flag": novel_disease_flag,
                "additional_symptoms": sampled_details["AdditionalSymptoms"],
                "additional_info": sampled_details["AdditionalInformation"],
                "confirmed_by":sampled_details["ConfirmedBy"],
                "supported_by":sampled_details["SupportedBy"]
                }
        else:
            return {
                "chief_complaint": sampled_details["ChiefComplaintDescription"], 
                "diagnosis": sampled_details["DiagnosisDescription"],
                "novel_disease_flag": novel_disease_flag,
                }
    
    def generate_elective_procedure(self, gender: str, age: int):
        """
        This function takes a dataframe of chief complaints (df) and filters to the gender it was passed.
        The gender argument should take the value "M" or "F".
        It then randomly samples from this filtered dataframe using the count column as weights.
        It returns an age, chief complaint and diagnosis in a dictionary.
        """    
        elective_procedures_df = self.elective_procedures
        elective_procedures_df = elective_procedures_df[
            (elective_procedures_df["Sex_Category"] == gender)
            & (elective_procedures_df["age_lower"] <= age)
            & (elective_procedures_df["age_upper"] >= age)
        ]
    
        if len(elective_procedures_df) == 0:
            print(f"ERROR - there are no rows in the elective procedures dataset for a {gender} patient of age {age} years")
        
        sampled_details = elective_procedures_df.sample(1).to_dict("records")[0]
        
        return {
            "procedure": sampled_details["Procedure"], 
            "speciality": sampled_details["Speciality"],
            }

    
    async def generate_length_of_stay(self, patient_admissions):
        """
        Uses an LLM to estimate the lenght of stay for each patient.
        """
    
        prompts = [patient_and_admission_prompts["length_of_stay_prompt"].substitute(
            PATIENT_ADMISSION_DETAILS = json.dumps(patient_admission_details, indent = 2)
        ) for patient_admission_details in patient_admissions]
        
        tasks = [call_llm_async(prompt, self.model) for prompt in prompts]
        
        all_length_of_stays = await asyncio.gather(*tasks)
        
        return all_length_of_stays

    async def run(self, return_output=False):
        if self.generate_admission_information:
            print(f'Generating {self.number_of_generations} admissions...', end = " ")
            
            patients_information = [json.loads(patient_row.iloc[0]) for i, patient_row in self.patients.iterrows()]

            admissions_information = await self.generate_all_admissions(patients_information)
            admissions_information = clean_outputs(admissions_information,"dictionary",self.model)
            
            admissions_information, removed_ids = remove_failures(admissions_information)
            if removed_ids:
                print(f"Admissions {removed_ids} removed due to incorrect json compilation")
            
            expected_lengths_of_stay = await self.generate_length_of_stay(admissions_information)
            expected_lengths_of_stay = [clean_int(LoS) for LoS in expected_lengths_of_stay]
            
            for LoS, patient_information, admission_information in zip(expected_lengths_of_stay, patients_information, admissions_information):
                admission_information["patient_id"] = patient_information["patient_id"]
                admission_information["medical_record_number"] = patient_information["medical_record_number"]
                admission_information["nhs_number"] = patient_information["nhs_number"]
                admission_information["bed_location"] = random.choice(["A", "B", "C"]) + "0" + random.choice(string.digits)
                admission_information["expected_length_of_stay"] = str(LoS)
            
            list_of_admissions = [json.dumps(admission_information) for admission_information in admissions_information]
                    
            self.list_of_admissions_df = pd.DataFrame(list_of_admissions)
            
            print("DONE")
            if return_output:
                return self.list_of_admissions_df
            
        else:
            print("SKIPPING ADMISSION GENERATION")

    def write_admissions_to_dataset(self):
        if self.list_of_admissions_df is None:
            raise ValueError("Dataset is None — refusing to overwrite intermediate_admissions")
        if self.list_of_admissions_df.empty:
            raise ValueError("Dataset is empty — refusing to overwrite intermediate admissions")

        read_write_data("intermediate_admissions", "write", self.list_of_admissions_df)

                    

    

# ____________________ GENERATE_JOURNEYS  _____________________


class generate_journeys():
    """
    Generates a unique journey through hospital for each patient.
    """

    def __init__(
        self,
        patients = None,
        admissions = None,
        name_df = None,
        intermediate_hospital_staff = None,
        generate_patient_journey = None,
        complex_journey_rate = None,
        number_of_staff_names = None,
        generate_new_staff_per_patient = None,
        use_intermediate_hospital_staff = None,
        set_new_hospital_staff = None,
        LLM_validator_iterations = None,
        event_types = None,
        add_abbreviations_to_content = None,
        add_abbreviations_to_headings = None,
        filter_journey = None,
        model = None,
    ):
        # Params
        self.generate_patient_journey = generate_patient_journey if generate_patient_journey is not None else PARAMS["pipeline_config"]["generate_patient_journey"]
        self.complex_journey_rate = complex_journey_rate if complex_journey_rate is not None else PARAMS["pipeline_config"]["complex_journey_rate"]
        self.number_of_staff_names = number_of_staff_names if number_of_staff_names is not None else PARAMS["pipeline_config"]["number_of_staff_names"]
        self.generate_new_staff_per_patient = generate_new_staff_per_patient if generate_new_staff_per_patient is not None else PARAMS["pipeline_config"]["generate_new_staff_per_patient"]
        self.use_intermediate_hospital_staff = use_intermediate_hospital_staff if use_intermediate_hospital_staff is not None else PARAMS["pipeline_config"]["use_intermediate_hospital_staff"]
        self.set_new_hospital_staff = set_new_hospital_staff if set_new_hospital_staff is not None else PARAMS["pipeline_config"]["set_new_hospital_staff"]
        self.LLM_validator_iterations = LLM_validator_iterations if LLM_validator_iterations is not None else PARAMS["pipeline_config"]["LLM_validator_iterations_patient_journey"]
        self.event_types = event_types if event_types is not None else CONFIG["possible_event_types"]
        self.style_instructions = CONFIG["style_instructions"]
        self.add_abbreviations_to_content = add_abbreviations_to_content if add_abbreviations_to_content is not None else PARAMS["pipeline_config"]["add_abbreviations_to_content"]
        self.add_abbreviations_to_headings = add_abbreviations_to_headings if add_abbreviations_to_headings is not None else PARAMS["pipeline_config"]["add_abbreviations_to_headings"]
        self.filter_journey = filter_journey if filter_journey is not None else PARAMS["pipeline_config"]["filter_journey"]
        # Data
        self.patients = patients if patients is not None else read_write_data("intermediate_patients", "read")
        self.admissions = admissions if admissions is not None else  read_write_data("intermediate_admissions", "read")
        self.name_df = name_df if name_df is not None else  read_write_data(PARAMS["pipeline_config"]["patients_input_dataset"], "read")
        if self.use_intermediate_hospital_staff:
            try:
                self.intermediate_hospital_staff = intermediate_hospital_staff if intermediate_hospital_staff is not None else  read_write_data("intermediate_hospital_staff", "read") # TODO - check what happens if this dataset is empty
            except:
                print("Error - Cannot use previous hospital staff, generating new staff.")
                self.use_intermediate_hospital_staff = False
        # Model
        self.model = model if model is not None else PARAMS["pipeline_config"]["model"]

        self.list_of_staff_personas_df = None
        self.patient_journeys_df = None
        self.filter_journeys_df = None
        self.hospital_staff_personas_df = None

    
    def generate_patient_journey_prompt(self, admission, length_of_stay, approx_events_per_day):
        """
        Creates a prompt for generating a patient journey.
        """
        admission_date = admission["admission_details"]["date"]
        admission_time = admission["admission_details"]["time"]
        discharge_date = (pd.to_datetime(admission_date) + pd.Timedelta(f"{length_of_stay}D")).strftime("%Y-%m-%d")
        number_of_events = str(approx_events_per_day*int(length_of_stay))
        emergency_surgery_instructions = ""
        if "novel_disease" in admission["admission_details"].keys():
            admission_instructions = patient_journey_prompts["emergency_admission_instructions_prompt"]
            
            if str(admission["admission_details"]["surgery_required"]).lower() in ['true', 'y', 'yes']: # emergency surgery
                emergency_surgery_instructions = patient_journey_prompts["emergency_surgery_instructions_prompt"]
            
            admission_reason = patient_journey_prompts["novel_disease_reason_prompt"].substitute(
                CHIEF_COMPLAINT = admission["admission_details"]["chief_complaint"],
                ADDITIONAL_SYMPTOMS = admission["admission_details"]["supporting_symptoms"],
                DIAGNOSIS = admission["admission_details"]["ED_diagnosis"],
                DIAGNOSIS_CONFIRMED_BY = admission["admission_details"]["diagnosis_confirmed_by"],
                DIAGNOSIS_SUPPORTED_BY = admission["admission_details"]["diagnosis_supported_by"]
            )
            
        elif "ED_diagnosis" in admission["admission_details"].keys(): # emergency admission
            admission_instructions = patient_journey_prompts["emergency_admission_instructions_prompt"]
            
            if str(admission["admission_details"]["surgery_required"]).lower() in ['true', 'y', 'yes']: # emergency surgery
                emergency_surgery_instructions = patient_journey_prompts["emergency_surgery_instructions_prompt"]
    
            admission_reason = patient_journey_prompts["emergency_admission_reason_prompt"].substitute(
                CHIEF_COMPLAINT = admission["admission_details"]["chief_complaint"],
                DIAGNOSIS = admission["admission_details"]["ED_diagnosis"]
            )
    
        else: # elective surgery
            admission_instructions = patient_journey_prompts["elective_admission_instructions_prompt"]
            admission_reason = patient_journey_prompts["elective_admission_reason_prompt"].substitute(
                PROCEDURE = admission["admission_details"]["procedure"]
            )

    
        nursing_note_instruction = patient_journey_prompts["nursing_note_instruction_prompt"] if "nursing" in CONFIG["possible_event_types"].keys() else ""
        misc_note_instruction = patient_journey_prompts["misc_note_instruction_prompt"] if "misc" in CONFIG["possible_event_types"].keys() else ""
        therapy_note_instruction = patient_journey_prompts["therapy_note_instruction_prompt"] if "therapy" in CONFIG["possible_event_types"].keys() else ""
        inter_speciality_review_instruction = patient_journey_prompts["inter_speciality_review_instruction_prompt"] if "inter-speciality review" in CONFIG["possible_event_types"].keys() else ""
    
        prompt = patient_journey_prompts["simple_patient_journey_prompt"].substitute(
            POSSIBLE_EVENT_TYPES = [key for key in CONFIG["possible_event_types"].keys()],
            ADMISSION_INSTRUCTIONS = admission_instructions,
            EMERGENCY_SURGERY_INSTRUCTIONS = emergency_surgery_instructions,
            NURSING_NOTE_INSTRUCTION = nursing_note_instruction,
            THERAPY_NOTE_INSTRUCTION = therapy_note_instruction,
            MISC_NOTE_INSTRUCTION = misc_note_instruction,
            INTER_SPECIALITY_REVIEW_INSTRUCTION = inter_speciality_review_instruction,
            ADMISSION_DATE = admission_date,
            ADMISSION_TIME = admission_time, 
            DISCHARGE_DATE = discharge_date,
            LENGTH_OF_STAY = length_of_stay,
            APPROX_EVENTS_PER_DAY = approx_events_per_day,
            NUMBER_OF_EVENTS = number_of_events,
            ADMISSION_REASON = admission_reason,
            OUTPUT_FORMAT = json.dumps(document_templates["event"], indent = 2)
        )
    
        return prompt

    
    def test_events_complete_prompts(self, events):
        """
        Creates a list of prompts which will check if an enitre journey has been generated.
        """
        prompts = []
    
        for event in events:
            prompts.append(patient_journey_prompts["test_events_complete_prompt"].substitute(
                EVENT = event
            ))
            
        return prompts
    
    async def generate_patient_journeys(self, model, patient_admission_details, lengths_of_stays, approx_events_per_day = 7):  
        """
        Generates a simple patient journey for each patient.
        """
        simple_journey_prompts = [self.generate_patient_journey_prompt(admission, length_of_stay, approx_events_per_day) for admission, length_of_stay in zip(patient_admission_details, lengths_of_stays)]
        simple_journey_tasks = [call_llm_async(prompt, model) for prompt in simple_journey_prompts]
        raw_journeys = await asyncio.gather(*simple_journey_tasks)
        raw_journey_lists = [[j] for j in raw_journeys]
    
        journey_complete_prompts = self.test_events_complete_prompts(raw_journeys)
        journey_complete_tasks = [call_llm_async(prompt, model) for prompt in journey_complete_prompts]
        complete_journeys = await asyncio.gather(*journey_complete_tasks)
        full_outputs = [False if "YES" in journey else True for journey in complete_journeys]
    
        for journey_i, (full_output, simple_journey_prompt, raw_journey) in enumerate(zip(full_outputs, simple_journey_prompts, raw_journeys)):
            # Assuming uncommon so not asyncronous
            chat_history = []
            new_raw_journey = [raw_journey]
            for i in range(5):
                if full_output == False:
                    chat_history.extend([simple_journey_prompt, raw_journey])
                    print(f"Generating more events for journey {journey_i}...", end = " ")
                    prompt = patient_journey_prompts["continue_journey_prompt"]
                    raw_response = await call_llm_async(prompt, self.model, chat_history = chat_history)
                    journey_complete = await call_llm_async(self.test_events_complete_prompts([raw_response])[0], model)
                    full_output = False if "YES" in journey_complete else True
                    new_raw_journey.append(raw_response)
                else:
                    break
            raw_journey_lists[journey_i] = new_raw_journey
    
        return raw_journey_lists

    async def validate_simple_patient_journeys(self,
                                        model,
                                        patient_journeys,
                                        admissions,
                                        complaint_col = "chief_complaint",
                                        diagnosis_col = "ED_diagnosis",
                                        procedure_col = "procedure"
                                       ):
        """
        Uses an LLM to validate a simple patient journey.
        """
    
        prompts = []
        
        for patient_journey, admission in zip(patient_journeys,admissions):
            if "novel_disease" in admission["admission_details"].keys():
                
                journey_info = patient_journey_prompts["novel_disease_reason_prompt"].substitute(
                    CHIEF_COMPLAINT = admission["admission_details"]["chief_complaint"],
                    ADDITIONAL_SYMPTOMS = admission["admission_details"]["supporting_symptoms"],
                    DIAGNOSIS = admission["admission_details"]["ED_diagnosis"],
                    DIAGNOSIS_CONFIRMED_BY = admission["admission_details"]["diagnosis_confirmed_by"],
                    DIAGNOSIS_SUPPORTED_BY = admission["admission_details"]["diagnosis_supported_by"]
                )
            elif admission["admission_details"]["admission_type"] == "emergency":
                journey_info = patient_journey_prompts["emergency_journey_information_prompt"].substitute(
                    ADMISSION = admission['admission_details'][complaint_col],
                    DIAGNOSIS = admission['admission_details'][diagnosis_col]
                )  
            elif admission["admission_details"]["admission_type"] == "elective":
                journey_info = patient_journey_prompts["elective_journey_admission_prompt"].substitute(
                    PROCEDURE = admission['admission_details'][procedure_col]
                )
    
            prompt = patient_journey_prompts["validate_simple_journey_prompt"].substitute(
                EVENT_FORMAT = json.dumps(document_templates["event"], indent = 2),
                JOURNEY_INFORMATION = journey_info,
                PATIENT_JOURNEY = json.dumps(patient_journey, indent = 2)
            )
            prompts.append(prompt)
    
        tasks = [call_llm_async(prompt, model) for prompt in prompts]
        
        validations = await asyncio.gather(*tasks)
        
        return validations


    async def generate_event_details(self, model, event_i, journey_matrix, patient_admission_details, staff_names, length_of_stays):
        """
        Generates additional details for each event in a patient journey.
        """

        prompts = []
        for journey_i in range(len(journey_matrix[0])):
            if journey_matrix[event_i][journey_i] is not None:
                event = journey_matrix[event_i][journey_i]
                full_journey = [events[journey_i] for events in journey_matrix if events[journey_i] is not None]
                admission_date = patient_admission_details[journey_i]["admission_details"]["date"]
                novel_disease = patient_admission_details[journey_i].get("novel_disease", None)
                discharge_date = (pd.to_datetime(admission_date) + pd.Timedelta(f"{length_of_stays[journey_i]}D"))
                discharge_date_string = discharge_date.strftime("%Y-%m-%d")
                days_left = (discharge_date - pd.to_datetime(event["date"])).days
                current_staff_names = staff_names[journey_i]
            
                if event_i == 0:
                    event_instructions = patient_journey_prompts["first_event_instructions_prompt"].substitute(
                        FULL_JOURNEY = json.dumps(full_journey, indent = 2),
                        FIRST_EVENT = json.dumps(full_journey[0], indent = 2)
                    )
            
                elif event_i == len(full_journey):
                    event_instructions = patient_journey_prompts["last_event_instructions_prompt"].substitute(
                        PREVIOUS_JOURNEY = json.dumps(full_journey, indent = 2),
                        FINAL_EVENT = json.dumps(full_journey[-1], indent = 2)
                    )
            
                else:
                    event_instructions = patient_journey_prompts["event_instructions_prompt"].substitute(
                        PREVIOUS_EVENTS = json.dumps(full_journey[:event_i], indent = 2),
                        CURRENT_EVENT = json.dumps(full_journey[event_i], indent = 2),
                        LATER_EVENTS = json.dumps(full_journey[event_i+1:], indent = 2)
                    )
            
                event_type_description = self.event_types[event['event_type']] if event["event_type"] in self.event_types.keys() else ""

                prompt = patient_journey_prompts["generate_event_details_prompt"].substitute(
                    EVENT_TYPE = event["event_type"],
                    EVENT_TYPE_DESCRIPTION = event_type_description,
                    ADMISSION_DATE = admission_date,
                    DISCHARGE_DATE = discharge_date_string,
                    CURRENT_DATE = event["date"],
                    CURRENT_TIME = event["time"],
                    DAYS_LEFT = days_left,
                    PATIENT_INFORMATION = json.dumps(patient_admission_details[journey_i], indent = 2),
                    EVENT_INSTRUCTIONS = event_instructions,
                    STAFF_NAMES = json.dumps(current_staff_names, indent = 2),
                    OUTPUT_FORMAT = json.dumps(document_templates["event_details"], indent = 2)
                    
                )
                prompts.append(prompt)
    
            else:
                prompts.append(None)
                
        tasks = [
            call_llm_async(prompt, model) if prompt is not None else asyncio.sleep(0, result=None)
            for prompt in prompts
        ]
        events = await asyncio.gather(*tasks)
        
        return events


    def generate_staff_personas(self, staff_names, abbreviates_content_prob, abbreviates_headers_prob):
        """
        Assign each member of staff in a patient journey a persona.
        """
        staff_personas = {}
        
        for staff in staff_names:
            staff_personas[staff] = {}
            persona = random.choice(list(self.style_instructions.keys()))
            staff_personas[staff]["style"] = self.style_instructions[persona]
            
            template_combine_sections = self.generate_template_sections_to_combine()
            staff_personas[staff]["template_combine_sections"] = template_combine_sections
            
            staff_personas[staff]["abbreviates_content"] = random.random() < abbreviates_content_prob
            staff_personas[staff]["abbreviates_headers"] = random.random() < abbreviates_headers_prob
            staff_personas[staff]["typo_rate"] = random.uniform(0.3, 1)
            staff_personas[staff]["id"] = generate_staff_gmc_and_pin(staff)
            
        
        return staff_personas

        
    def generate_template_sections_to_combine(self):
        """
        Randomly generate a list of note sections which a persona will combine
        for each event type.
        """
        staff_sections = {}
        for event_type, sections in template_sections_to_combine.items():
            n_sections = random.randint(0, len(sections))
            collapse_sections = dict(random.sample(list(sections.items()), n_sections))
            staff_sections[event_type] = collapse_sections
        return staff_sections


    async def run(self, get_lengths = True, return_outputs = False):
        """
        Creates patient journeys by:
        
         - Generating simple journeys
         - Validating simple journeys
         - Adding extra details
        """
        if self.generate_patient_journey:
            patients_and_admissions = combine_patients_and_admissions(self.patients, self.admissions)
            
            #complex_journeys = [self.complex_journey_rate > random.random() for i in range(len(patients_and_admissions))]
            lengths_of_stays = [admission["admission_details"]["expected_length_of_stay"] for admission in patients_and_admissions]
            admission_consultants = [admission["admission_details"]["admitting_consultant"] for admission in patients_and_admissions]

            hospital_staff_personas = None
            if self.generate_new_staff_per_patient == True:
                # Generate new hospital staff per patient
                all_staff_names = [[admission_consultant] + generate_hospital_staff(self.name_df, self.number_of_staff_names) for admission_consultant in admission_consultants]
            elif self.generate_new_staff_per_patient == False and self.use_intermediate_hospital_staff == False:
                # Generate staff once, and give all patients the same hospital staff
                hospital_staff = generate_hospital_staff(self.name_df, self.number_of_staff_names)
                all_staff_names = [[admission_consultant] + hospital_staff for admission_consultant in admission_consultants]
            else:
                intermediate_hospital_staff = self.intermediate_hospital_staff
                hospital_personas = json.loads(intermediate_hospital_staff.iloc[0].iloc[0])
                hospital_staff_personas = hospital_personas
                hospital_staff = [
                    list(json.loads(v).keys())[0]
                    for v in hospital_staff_personas.values()
                ]
                all_staff_names = [
                    [admission_consultant] + hospital_staff
                    for admission_consultant in admission_consultants
                ]
            
            list_of_staff_personas = []

            # START GENERATING SIMPLE JOURNEYS
            print("Generating simple journeys...", end = " ")

            simple_patient_journeys = await self.generate_patient_journeys(self.model, patients_and_admissions, lengths_of_stays)
            
            max_attempts = 5
            clean_journeys = []
            for journey_i, (journey, admission, length_of_stay) in enumerate(zip(simple_patient_journeys, patients_and_admissions, lengths_of_stays)):
                new_journey = journey
                for attempt in range(max_attempts):
                    if any([isinstance(segment, dict) and "FAILURE" in segment.keys() for segment in clean_outputs(new_journey, "list", self.model)]):
                        print(f"Regenerating journey {journey_i} due to error.")
                        new_journey = await self.generate_patient_journeys(self.model, [admission], [length_of_stay])
                    else:
                        clean_journeys.append([event for journey_segment in clean_outputs(new_journey, "list", self.model) for event in journey_segment])
                        break
                else:
                    print(f"WARNING: Failed to generate valid journey after {max_attempts} attempts.")
                    print(f"Skipping patient {journey_i}")

            # START VALIDATING SIMPLE JOURNEYS
            print("Validating simple journeys...")

            validator_changes = {f"Patient_{i}" : 0 for i in range(len(simple_patient_journeys))}
            for validator_i in range(self.LLM_validator_iterations):
                
                validations = await self.validate_simple_patient_journeys(self.model, clean_journeys, patients_and_admissions)
                clean_validations = clean_outputs(validations, "dictionary", self.model)
                validated_journeys = []
                for journey_i, (validation, original_journey) in enumerate(zip(clean_validations, clean_journeys)):
                    if "changes" in validation and (validation["changes"] == True or validation["changes"] == "True"):
                        journey_data = validation["journey"]
                        if isinstance(journey_data, str):
                            validated_journeys.append(clean_outputs([journey_data], "list", self.model)[0])
                        else:
                            validated_journeys.append(journey_data) 
                        validator_changes[f"Patient_{journey_i}"] += 1
                    else: 
                        validated_journeys.append(original_journey)
                clean_journeys = validated_journeys
            
            print("Validator Changes:\n", validator_changes)

            # GENERATE EXTRA DETAILS
            print("Generating extra details...", end = " ")

            journey_matrix = [list(journey) for journey in zip_longest(*clean_journeys, fillvalue=None)]

            new_journey_matrix = []
            for event_i, current_events in enumerate(journey_matrix):
                extra_details = await self.generate_event_details(self.model, event_i, journey_matrix, patients_and_admissions ,all_staff_names, lengths_of_stays)
                clean_extra_details = clean_outputs(extra_details, "list", self.model)
                new_events_i = [
                    None if original_details is None or new_details is None 
                    else original_details | new_details for original_details, new_details in zip(current_events, clean_extra_details)
                ]
        
                for event in new_events_i:
                    if event is not None:
                        event.pop("summary", None)
                    
                new_journey_matrix.append(new_events_i)
            
            detailed_journeys = []
            for journey_i in range(len(clean_journeys)):
                detailed_journeys.append(
                    [events[journey_i] for events in new_journey_matrix if events[journey_i] is not None]
                )

            # GENERATE STAFF PERSONAS
            print("Generating staff personas...", end = " ")
            # Generated after the jouney incase new staff are added by the LLM

            if self.generate_new_staff_per_patient:
                number_of_hospital_staff = 0
            elif self.generate_new_staff_per_patient == False and self.use_intermediate_hospital_staff == False:
                # Generate once for all hospital staff
                hospital_staff_personas = {
                    f'persona_{i+1}': json.dumps({name: info})
                    for i, (name, info) in enumerate(
                        self.generate_staff_personas(
                            hospital_staff,
                            self.add_abbreviations_to_content,
                            self.add_abbreviations_to_headings,
                        ).items()
                    )
                }
                number_of_hospital_staff = len(hospital_staff)
            else:
                hospital_staff_personas = hospital_staff_personas
                number_of_hospital_staff = len(hospital_staff)
                
            for journey_i, journey in enumerate(detailed_journeys):
                staff = []
                for event in journey:
                    if isinstance(event["staff"], str):
                        staff.extend(event["staff"].strip("[]").split(","))
                    elif isinstance(event["staff"], list):
                        staff.extend(event["staff"])

                journey_staff = list(set(staff + all_staff_names[journey_i]))
                if self.generate_new_staff_per_patient == False:
                    # Get unique staff from this journey
                    journey_staff = [s for s in journey_staff if s not in hospital_staff]
                
                staff_personas = {
                    f'persona_{i+1+number_of_hospital_staff}': json.dumps({name: info})
                    for i, (name, info) in enumerate(
                        self.generate_staff_personas(
                            journey_staff,
                            self.add_abbreviations_to_content,
                            self.add_abbreviations_to_headings,
                        ).items()
                    )
                }

                if self.generate_new_staff_per_patient == False:
                    staff_personas = hospital_staff_personas | staff_personas
        
                list_of_staff_personas.append(json.dumps(staff_personas))

            self.list_of_staff_personas_df = pd.DataFrame(list_of_staff_personas)

            if hospital_staff_personas is not None:
                self.hospital_staff_personas_df = pd.DataFrame([json.dumps(hospital_staff_personas)])
            else:
                self.hospital_staff_personas_df = pd.DataFrame()

            # SAVE
            print("Creating full detailed journeys...", end = " ")
            detailed_journeys = [json.dumps(journey) for journey in detailed_journeys]
            
            
            # FILTER JOURNEYS

            filtered_journeys = []
            patient_journeys = pd.DataFrame(detailed_journeys)
            self.patient_journeys_df = patient_journeys
            
            if self.filter_journey:
                print("Filtering journeys...")
                for i, row in patient_journeys.iterrows():
                    
                    row = json.loads(row.iloc[0])
                    
                    events_to_remove = [
                        event["event_type"] for event in row
                        if event is not None and event["event_type"] not in self.event_types.keys()
                    ]
                    
                    print(f"Patient {i} - Removing events: {events_to_remove}")
                    
                    filtered_patient_journey = [
                        json.dumps(event) for event in row if event is not None and event["event_type"] not in events_to_remove
                    ]
                
                    filtered_journeys.append(filtered_patient_journey)

                self.filter_journeys_df = pd.DataFrame(filtered_journeys)

            if get_lengths:
                journeys = filtered_journeys if self.filter_journey else detailed_journeys

                for i, journey_row in enumerate(journeys):
                    print(f"Journey {i} has length {len(journey_row)}")

            print("DONE")
            if return_outputs:
                journeys = filtered_journeys if self.filter_journey else detailed_journeys
                return journeys

                        
        else:
            print("SKIPPING JOURNEY GENERATION")


    def write_journeys_to_dataset(self):

        if self.list_of_staff_personas_df is None:
            raise ValueError("Dataset is None — refusing to overwrite intermediate_staff_personas")
        if self.list_of_staff_personas_df.empty:
            raise ValueError("Dataset is empty — refusing to overwrite intermediate_staff_personas")

        if self.patient_journeys_df is None:
            raise ValueError("Dataset is None — refusing to overwrite intermediate_journeys")
        if self.patient_journeys_df.empty:
            raise ValueError("Dataset is empty — refusing to overwrite intermediate_journeys")

        if self.filter_journey and self.filter_journeys_df is None:
            raise ValueError("Dataset is None — refusing to overwrite intermediate_filtered_journeys")
        if self.filter_journey and self.filter_journeys_df.empty:
            raise ValueError("Dataset is empty — refusing to overwrite intermediate_filtered_journeys")

        if self.set_new_hospital_staff  and self.hospital_staff_personas_df is None:
            raise ValueError("Dataset is None — refusing to overwrite intermediate_hospital_staff")
        if self.set_new_hospital_staff  and self.hospital_staff_personas_df.empty:
            raise ValueError("Dataset is empty — refusing to overwrite intermediate_hospital_staff")

        read_write_data("intermediate_staff_personas", "write", self.list_of_staff_personas_df)
        read_write_data("intermediate_journeys", "write", self.patient_journeys_df)
        
        if self.set_new_hospital_staff:
            # If not using previous hospital staff, save the new hospital staff
            read_write_data("intermediate_hospital_staff", "write",self.hospital_staff_personas_df)

        if self.filter_journey:
            read_write_data("intermediate_filtered_journeys", "write", self.filter_journeys_df)




# ____________________ GENERATE_CLINICAL_NOTES  _____________________


class generate_clinical_notes():
    """
    Generate clinical notes for each journey step of each patient.
    """
    
    def __init__(
        self,
        filtered_journeys = None,
        detailed_journeys = None,
        staff_personas = None,
        patients = None,
        admissions = None,
        doc_templates = None, 
        TEST_MODE = None,
        combine_sections = None,
        filter_journey = None,
        simple_template_only = None,
        generate_clinical_notes = None,
        model = None,
    ):
        # Params
        self.TEST_MODE = TEST_MODE if TEST_MODE is not None else PARAMS["pipeline_config"]["TEST_MODE"]
        self.combine_sections = combine_sections if combine_sections is not None else PARAMS["pipeline_config"]["combine_sections"]
        self.filter_journey = filter_journey if filter_journey is not None else PARAMS["pipeline_config"]["filter_journey"]
        self.simple_template_only = simple_template_only if simple_template_only is not None else PARAMS["pipeline_config"]["simple_template_only"]
        self.generate_notes = generate_clinical_notes if generate_clinical_notes is not None else PARAMS["pipeline_config"]["generate_clinical_notes"]
        self.document_templates = doc_templates if doc_templates is not None else document_templates # imported from doc_templates.py
        # Data
        if self.filter_journey:
            self.journeys = filtered_journeys if filtered_journeys is not None else read_write_data("intermediate_filtered_journeys", "read")
        else:
            self.journeys = detailed_journeys if detailed_journeys is not None else read_write_data("intermediate_journeys", "read")
        self.staff_personas = staff_personas if staff_personas is not None else read_write_data("intermediate_staff_personas", "read")
        self.patients = patients if patients is not None else read_write_data("intermediate_patients", "read")
        self.admissions = admissions if admissions is not None else  read_write_data("intermediate_admissions", "read")
        self.patients_and_admissions = combine_patients_and_admissions(self.patients, self.admissions)
        # Model
        self.model = model if model is not None else PARAMS["pipeline_config"]["model"]
        self.final_patient_notes_df = None


    def generate_patient_examinations(self, model, patient_info: dict, journey_event: dict, patient_journey: list):
        
        prompt = clinical_note_prompts["generate_patient_examinations_prompt"].substitute(
            PATIENT_INFORMATION = patient_info,
            CURRENT_EVENT = json.dumps(journey_event, indent = 2),
            PREVIOUS_EVENTS = json.dumps(patient_journey, indent = 2)
        )
        
        raw_examinations = call_llm(prompt, model)
        
        return raw_examinations
    
    def generate_red_flags(self, model, patient_info: dict, journey_event: dict, patient_journey: list):
        """
        Determins the relevant red flags to check for a patient with the following primary complaint
        """
        prompt = clinical_note_prompts["generate_red_flags_prompt"].substitute(
            PRIMARY_COMPLAINT = patient_info["admission_details"]["chief_complaint"],
            CURRENT_EVENT = json.dumps(journey_event, indent = 2),
            PREVIOUS_EVENTS = json.dumps(patient_journey, indent = 2)
        )
        
        symptom_list = call_llm(prompt, model)
        
        return symptom_list

    
    async def generate_clinical_notes(self, model, patient_info: dict, journey_events: list, output_templates: list, personas: list, display_prompt: bool = False) -> str:
        """
        Generates a list of clinical notes for a single patient.
        """
        prompts = []
        previous_events = []
        
        for i, journey_event in enumerate(journey_events):
            if isinstance(journey_event["staff"], list):
                staff_member = journey_event["staff"][0]
            elif isinstance(journey_event["staff"], str):
                staff_member = journey_event["staff"].strip("[]").split(",")[0]
            else:
                staff_member = {"style": "Concise note form"}
            persona = personas.get(staff_member).get("style", "Consise note form")
            template = document_templates.get(journey_event.get("event_type"), "None")
            event_type = journey_event.get("event_type")
            
            if "On Examination" in template.keys():
                relevant_exams = self.generate_patient_examinations(model, patient_info, journey_event, journey_events) #TO DO: parallel LLM calls?
                examination_info = clinical_note_prompts["examination_info_prompt"].substitute(
                    RELEVANT_EXAMS = relevant_exams
                )
            else:
                examination_info = ""
    
            if event_type in ["ED review and hand-over", "emergency_admission"]:
                red_flag_symptoms = self.generate_red_flags(model, patient_info, journey_event, journey_events)
                red_flag_info = clinical_note_prompts["red_flag_info_prompt"].substitute(
                    RED_FLAGS = red_flag_symptoms
                )
            else:
                red_flag_info = ""

            if self.simple_template_only:
                output_info = build_output_info(template)
                simple_template = self.document_templates["simple_note_template"]
                
                prompts.append(clinical_note_prompts["simple_clinical_note_prompt"].substitute(
                    EVENT_TYPE = event_type,
                    EVENT_TYPE_DESCRIPTION = CONFIG["possible_event_types"][event_type], 
                    PERSONA = persona,
                    PATIENT_INFORMATION = json.dumps(patient_info, indent = 2),
                    RELEVANT_EVENT = json.dumps(journey_event, indent = 2),
                    PREVIOUS_EVENTS = json.dumps(previous_events, indent = 2),
                    EXAMINATION_INFORMATION = examination_info,
                    RED_FLAG_INFORMATION = red_flag_info,
                    OUTPUT_INFO = output_info,
                    SIMPLE_OUTPUT_FORMAT = json.dumps(simple_template, indent = 2)  
                ))
            else:
                prompts.append(clinical_note_prompts["clinical_note_prompt"].substitute(
                    EVENT_TYPE = event_type,
                    EVENT_TYPE_DESCRIPTION = CONFIG["possible_event_types"][event_type], 
                    PERSONA = persona,
                    PATIENT_INFORMATION = json.dumps(patient_info, indent = 2),
                    RELEVANT_EVENT = json.dumps(journey_event, indent = 2),
                    PREVIOUS_EVENTS = json.dumps(previous_events, indent = 2),
                    EXAMINATION_INFORMATION = examination_info,
                    RED_FLAG_INFORMATION = red_flag_info,
                    OUTPUT_FORMAT = json.dumps(template, indent = 2)                  
                ))
            
            previous_events.append(journey_event)
        
        if display_prompt:
            print(prompts)
        
        tasks = [call_llm_async(prompt, model) for prompt in prompts]
        
        clinical_notes = await asyncio.gather(*tasks)
        
        return clinical_notes


    async def validate_responses(self, model, documents: list, journey_events, patient_info: dict, output_templates: dict) -> str:
        """
        Uses an LLM-as-a-Judge to validate clinical notes.
        """
        results = [None] * len(documents)
        previous_events = []
        tasks = []
        positions = []
        
        for i, (document, journey_event) in enumerate(zip(documents, journey_events)):
            if journey_event.get("event_type") != "misc":
                if self.simple_template_only:
                    template = output_templates.get("simple_note_template", {})
                else:
                    template = output_templates.get(journey_event.get("event_type"), {})
                    
                prompt = clinical_note_prompts["validate_responses_prompt"].substitute(
                    CONTENT = json.dumps(template, indent = 4),
                    CLINICAL_DOCUMENT = json.dumps(document, indent = 2),
                    CURRENT_EVENT = json.dumps(journey_event, indent = 2),
                    PATIENT_INFORMATION = json.dumps(patient_info, indent = 2),
                    PATIENT_JOURNEY = json.dumps(previous_events, indent = 2),
                )
                tasks.append(call_llm_async(prompt, model))
                positions.append(i)
    
            previous_events.append(journey_event)
        
            if journey_event.get("event_type") == "misc":
                results[i] = json.dumps({
                  "title": "MISC_NOTE",
                  "content": document,
                  "changes": False
                })
        
        if tasks:
            llm_outputs = await asyncio.gather(*tasks)
            for pos, out in zip(positions, llm_outputs):
                results[pos] = out
                
        return results

    

    def remove_structures(self, struct):
        """
        Convert a structured clinical problem dictionary into unstructured text.
        """
    
        # Convert string to dict if needed
        if isinstance(struct, str):
            try:
                struct = ast.literal_eval(struct)
            except Exception:
                return struct  # return original if parsing fails
    
        if not isinstance(struct, dict):
            return str(struct)
    
        problems = []
    
        for problem, details in struct.items():
    
            problem_name = problem.split(". ", 1)[-1]
    
            if isinstance(details, list) and details:
                problems.append(f"{problem_name}: {', '.join(details)}")
            else:
                problems.append(problem_name)
    
        return ". ".join(problems) + "."
        
    
    async def run(self, return_output:bool):
        """
        Generates clinical notes for each step of a patients journey.
        """
        if self.generate_notes:

            if self.TEST_MODE:
                print("TEST MODE: Generating 1 clinical note per patient")
                journeys = self.journeys[["0"]]
            else:
                journeys = self.journeys

            final_patient_documents = []
    
            for (journey_i, journey_row), (patient_i, patient_row), (persona_i, persona_row) in zip(
                journeys.iterrows(), enumerate(self.patients_and_admissions), self.staff_personas.iterrows()):
                print(f"Patient {patient_i}:", end  = " ")
    
                journey_row = [json.loads(journey) for journey in journey_row if not pd.isna(journey)]
                persona_row = json.loads(persona_row.iloc[0])
                patient_row = clean_patient_details(patient_row)

                list_of_staff_personas = {
                    k: v
                    for item in persona_row.values()
                    for k, v in (
                        json.loads(item) if isinstance(item, str) else item
                    ).items()
                }
    
                print("Generating Notes...", end = " ")
                raw_notes = await self.generate_clinical_notes(self.model, patient_row, journey_row, self.document_templates, list_of_staff_personas)
                notes = clean_outputs(raw_notes,"dictionary",self.model)
                for note in notes:
                    if "Issues" in note:
                        if PARAMS["pipeline_config"]["simple_template_only"]:
                            note["Issues"] = self.remove_structures(note["Issues"])
                        else:
                            note["Issues"] = clean_outputs(note["Issues"], "list", self.model)[0]
                notes, removed_ids = remove_failures(notes)
                if removed_ids:
                    print(f"Note {removed_ids} removed due to incorrect json compilation")
    
                print("Validating Notes...", end = " ")
                all_changes = 0
                for i in range(PARAMS["pipeline_config"]["LLM_validator_iterations_clinical_note"]):
                    validated_notes = await self.validate_responses(self.model, notes, journey_row, patient_row, document_templates)
                    clean_validated_notes = clean_outputs(validated_notes, "dictionary", self.model)
                    clean_validated_notes, removed_ids = remove_failures(clean_validated_notes, replace_list = notes) # if note is a failure, replace with non-validated
                    if removed_ids:
                        print(f"Note {removed_ids} could not be validated in validator iteration {i} due to incorrect json compilation")
                        
                    notes = clean_outputs([val_note.get("content", note) for val_note, note in zip(clean_validated_notes, notes)], "dictionary", self.model) # If note has no content key, replace with orignal note.
                    all_changes += sum([1 for note in clean_validated_notes if note.get("changes", False) in (True, "True")]) # changes not always a valid key, LLM outputs it incorrectly.
                print(f"Estimated {all_changes} changes...", end = " ")
    
                if self.combine_sections:
                    combined_notes = []
                    print("Combining sections...", end = " ")
                    staff_members = [event["staff"].strip("[]").split(",")[0] if isinstance(event["staff"], str) else event["staff"][0] for event in journey_row]
                    sections_to_combine = [list_of_staff_personas.get(staff_member).get("template_combine_sections").get(j.get("event_type"))
                                          for j, staff_member in zip(journey_row, staff_members)]
                    for note, sections in zip(notes, sections_to_combine):
                        for section, combine_sections in sections.items():
                            try:
                                 note = combine_template_sections(section, combine_sections, note)
                            except:
                                print(f"failed to combine note sections: {sections_to_combine}")
                        combined_notes.append(note)
                    
                    notes = combined_notes
    
                final_patient_documents.append([json.dumps(n) for n in notes])
                
            print("DONE")
            self.final_patient_notes_df = pd.DataFrame(final_patient_documents)
            
            if return_output:
                return final_patient_documents

        else:
            print("SKIPPING NOTE GENERATION")

    def write_patient_documents_to_dataset(self):
        
        if self.final_patient_notes_df is None:
            raise ValueError("Dataset is None — refusing to overwrite intermediate_clean_clinical_notes")
        if self.final_patient_notes_df.empty:
            raise ValueError("Dataset is empty — refusing to overwrite intermediate_clean_clinical_notes")

        read_write_data("intermediate_clean_clinical_notes", "write", self.final_patient_notes_df)




# ____________________ ADD AUGMENTATIONS ____________________

class add_augmentations():
    """
    Adds spelling mistakes and abbreviations to clinical notes.
    """

    def __init__(
        self,
        clinical_notes = None,
        staff_personas = None,
        filtered_journeys = None,
        detailed_journeys = None,
        add_abbreviations_to_content = None,
        add_abbreviations_to_headings = None,    
        add_signature = None,
        sections_to_ignore_abbreviations = None,
        filter_journey = None,
        typo_rate = None,
        model = None
    ):
        # Params
        self.add_abbreviations_to_content = add_abbreviations_to_content if add_abbreviations_to_content is not None else PARAMS["pipeline_config"]["add_abbreviations_to_content"]
        self.add_abbreviations_to_headings = add_abbreviations_to_headings if add_abbreviations_to_headings is not None else PARAMS["pipeline_config"]["add_abbreviations_to_headings"]
        self.add_signature = add_signature if add_signature is not None else PARAMS["pipeline_config"]["add_signature"]
        self.sections_to_ignore_abbreviations = sections_to_ignore_abbreviations if sections_to_ignore_abbreviations is not None else CONFIG["sections_to_ignore_abbreviations"]
        self.typo_rate = typo_rate if typo_rate is not None else PARAMS["pipeline_config"]["typo_rate"]
        self.filter_journeys = filter_journey if filter_journey is not None else PARAMS["pipeline_config"]["filter_journey"]
        # Data
        self.clinical_notes = clinical_notes if clinical_notes is not None else read_write_data("intermediate_clean_clinical_notes", "read")
        self.staff_personas = staff_personas if staff_personas is not None else read_write_data("intermediate_staff_personas", "read")
        if self.filter_journeys:
            self.journeys = filtered_journeys if filtered_journeys is not None else  read_write_data("intermediate_filtered_journeys", "read")
        else:
            self.journeys = detailed_journeys if detailed_journeys is not None else  read_write_data("intermediate_journeys", "read")
        # Model
        self.model = model if model is not None else PARAMS["pipeline_config"]["model"]
        self.clean_final_patient_df = None

    async def run(self, return_output=False):

        clean_final_patient_documents = []

        for (notes_i, notes_row), (persona_i, persona_row), (journey_i, journey_row) in zip(
            self.clinical_notes.iterrows(),
            self.staff_personas.iterrows(), 
            self.journeys.iterrows()
        ):
            journey_row = [json.loads(journey) for journey in journey_row if not pd.isna(journey)]
            persona_row = json.loads(persona_row.iloc[0])

            list_of_staff_personas = {}
            for item in persona_row.values():
                list_of_staff_personas.update(json.loads(item))

            print(f"Patient {notes_i}")
            augmented_notes = []

            for note_i, note in enumerate([n for n in notes_row if not pd.isna(n)]):
                print(f"Note: {note_i}:", end = " ")
                note = json.loads(note)

                if "FAILURE" not in note.keys() and any([self.add_abbreviations_to_content,
                                                    self.add_abbreviations_to_headings,	
                                                    self.add_signature]):

                    if isinstance(journey_row[note_i]["staff"], list):
                        staff_member = journey_row[note_i]["staff"][0]
                        staff_persona = list_of_staff_personas[staff_member]
                    else:
                        staff_member = journey_row[note_i]["staff"].strip("[]").split(",")[0]
                        staff_persona = list_of_staff_personas[staff_member]

                    if self.add_abbreviations_to_content or self.add_abbreviations_to_headings:
                        note, total_number_of_abbreviations = await add_abbreviations_to_dict(
                            note,
                            self.model,
                            self.sections_to_ignore_abbreviations,
                            staff_persona["abbreviates_content"],
                            staff_persona["abbreviates_headers"]
                        )
                
                        print(f"Added (Estimated) {total_number_of_abbreviations} Abbreviations.", end = " ")
                
                    if self.typo_rate > 0:
                        # if PARAMS["pipeline_config"]["bias_testing"] is not None:
                        #     print("WARNING: We reccomend setting typo_rate to 0 if testing for bias as typos are randomly generated")
                        personal_typo_rate = staff_persona["typo_rate"] * self.typo_rate
                        note, total_number_of_typos = add_typos_to_dict(note, personal_typo_rate, CONFIG["sections_to_ignore_typos"])
                        print(f"Added {total_number_of_typos} typos.")

                    if self.add_signature:
                        staff_member_id = list_of_staff_personas[staff_member]["id"]
                        note = add_sign_off_to_note(note,
                                                    staff_member,
                                                    staff_member_id)
            
                    augmented_notes.append(json.dumps(note))

                else:
                    print("Skipping, note failed to generate")
                    
            clean_final_patient_documents.append(augmented_notes)

        self.clean_final_patient_df = pd.DataFrame(clean_final_patient_documents)
                
        print("DONE")
        if return_output:
            return clean_final_patient_documents

    def write_final_documents_to_dataset(self):
        
        if self.clean_final_patient_df is None:
            raise ValueError("Dataset is None — refusing to overwrite the list_of_staff_personas_df")
        if self.clean_final_patient_df.empty:
            raise ValueError("Dataset is empty — refusing to overwrite the list_of_staff_personas_df")

        read_write_data("intermediate_augmented_clinical_notes", "write",self.clean_final_patient_df)



# ____________________ SAVE FINAL OUTPUTS ____________________

class save_final_outputs():
    """
    Saves the final clincial notes
    """

    def __init__(
        self,
        clinical_notes = None,
        augmented_clinical_notes = None,
        filtered_journeys = None,
        detailed_journeys = None,
        patients = None,
        admissions = None,
        add_abbreviations_to_content = None,
        add_abbreviations_to_headings = None,    
        add_signature = None,
        filter_journey = None,
        generate_patient_information = None,
        site_name = None,
        site_code = None,
        model = None
    ):
        # Params 
        self.add_abbreviations_to_content = add_abbreviations_to_content if add_abbreviations_to_content is not None else PARAMS["pipeline_config"]["add_abbreviations_to_content"]
        self.add_abbreviations_to_headings = add_abbreviations_to_headings if add_abbreviations_to_headings is not None else PARAMS["pipeline_config"]["add_abbreviations_to_headings"]
        self.add_signature = add_signature if add_signature is not None else PARAMS["pipeline_config"]["add_signature"]
        self.filter_journeys = filter_journey if filter_journey is not None else PARAMS["pipeline_config"]["filter_journey"]
        self.generate_patient_information = generate_patient_information if generate_patient_information is not None else  PARAMS["pipeline_config"]["generate_patient_information"],
        self.site_name = site_name if site_name is not None else PARAMS["pipeline_config"]["site_name"]
        self.site_code = site_code if site_code is not None else PARAMS["pipeline_config"]["site_code"]
        # Data
        if any([
            self.add_abbreviations_to_content,
            self.add_abbreviations_to_headings,
            self.add_signature 
        ]):
            self.clinical_notes = augmented_clinical_notes if augmented_clinical_notes is not None else read_write_data("intermediate_augmented_clinical_notes", "read")
        else:
            self.clinical_notes = clinical_notes if clinical_notes is not None else read_write_data("intermediate_clean_clinical_notes", "read")
        if self.filter_journeys:
            self.journeys = filtered_journeys if filtered_journeys is not None else read_write_data("intermediate_filtered_journeys", "read")
        else:
            self.journeys = detailed_journeys if detailed_journeys is not None else read_write_data("intermediate_journeys", "read")
        self.patients = patients if patients is not None else read_write_data("intermediate_patients", "read")
        self.admissions = admissions if admissions is not None else read_write_data("intermediate_admissions", "read")
        self.patients_and_admissions = combine_patients_and_admissions(self.patients, self.admissions)
        #Model
        self.model = model if model is not None else PARAMS["pipeline_config"]["model"]


    def run(
        self,
        run_name,
        current_time,
        version_tag
    ):
        patients_output_data = []
        admissions_output_data = []
        encounters_output_data = []
        notes_output_data = []
        evaluation_output_data = []
        journey_metrics = []

        print("Preparing data...", end = " ")
        for patient_admission, (journey_i, journey_row), (notes_i, notes_row) in zip(
            self.patients_and_admissions, self.journeys.iterrows(), self.clinical_notes.iterrows()):

            patient_admission["admission_details"]["admission_id"] = str(uuid.uuid4())
            patient_admission["admission_details"]["encounter_id"] = str(uuid.uuid4())

            patient_data = prepare_patient_data(patient_admission)
            patients_output_data.append(patient_data.copy())
            
            # admission
            admission_data = prepare_admission_data(
                patient_admission, 
                version_tag,
                self.site_name,
                self.site_code
            )
            admissions_output_data.append(admission_data.copy())
            
            #encounter
            encounter_data = prepare_encounter_data(patient_admission)
            encounters_output_data.append(encounter_data.copy())
            
            # journey metrics
            journey_row = [json.loads(j) for j in journey_row.to_list() if not pd.isna(j)]
            journey_eval = get_journey_evaluation_details(patient_admission,
                                                          journey_row,
                                                          patient_admission["admission_details"]["expected_length_of_stay"],
                                                          run_name,
                                                          current_time)
            journey_metrics.append(journey_eval)
            
            # clinical notes and journeys
            for event, note in zip(journey_row, notes_row):
                if not pd.isna(note):
                    note = json.loads(note)
                    note_with_metadata = prepare_note_data(patient_admission,
                                                       event,
                                                       note)
        
                    notes_output_data.append(note_with_metadata.copy())
                
                    evaluation_data = prepare_evaluation_data(note_with_metadata.copy(),
                                                   [j for j in journey_row if not pd.isna(j)],
                                                   event,
                                                   patient_data,
                                                   run_name,
                                                   current_time)
                    evaluation_output_data.append(evaluation_data.copy())

        evaluation_output_df = pd.DataFrame(evaluation_output_data)
        evaluation_output_df = normalise_array_struct_column(evaluation_output_df, "journey") # journey is the only struct where this might occur.
        
        # Saving
        print("Saving Data...", end  = " ")
        if self.generate_patient_information:
            write_dataset(patients_output_data, "patients_output", True)
        write_dataset(admissions_output_data, "admissions", True)
        write_dataset(encounters_output_data, "encounters", True)
        write_dataset(journey_metrics, "journey_metrics", True)
        write_dataset(notes_output_data, "clinical_notes", True)
        write_dataset(evaluation_output_df, "journeys", True)

        print("DONE")