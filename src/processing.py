import random
import json
import re
import pandas as pd
import numpy as np
from src.prompts import processing_prompts
import string
import math
import typo
from datetime import datetime, timedelta
from datetime import time as dt_time
from copy import deepcopy 
import asyncio
import time
from contextvars import ContextVar
import ast

import os
from dotenv import load_dotenv
from openai import OpenAI
from foundry_sdk.v2.language_models.utils import get_openai_base_url, get_http_client
from foundry_sdk._core.context_and_environment_vars import HOSTNAME_VAR, TOKEN_VAR

load_dotenv()

_loop_semaphore: ContextVar[asyncio.Semaphore] = ContextVar("_loop_semaphore", default=None)
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# FOUNDRY SPECIFIC FUNCTIONS

# If you plan on using this pipeline on another platform, please adapt the following functions.

# 1 - call_llm
# 2 - read_write_data

def call_llm(prompt: str, model: str = "ri.language-model-service..language-model.gpt-4-o", temp: float = 0.7, max_attempts: int = 5, chat_history = None) -> str:
    """
    Send a prompt to a chat-based LLM and return the model's text response.

    Builds a chat completion request using the provided prompt and optional
    conversation history, calls the model, and returns the raw response text.
    If the request fails, it retries up to `max_attempts` times.

    Parameters
    ----------
    prompt : str
        The user prompt appended as the latest message in the conversation.

    model : object
        Model client implementing `create_chat_completion(request)`.

    temp : float, default=0.7
        Sampling temperature controlling response randomness.

    max_attempts : int, default=3
        Number of retry attempts if the LLM call fails.

    chat_history : list[str] | None, default=None
        Optional alternating list of messages:
        [user_0, assistant_0, user_1, assistant_1, ...].
        The prompt is added as the final user message.

    Returns
    -------
    str
        Raw text content from the model response, or None if all attempts fail.
    """
    HOSTNAME_VAR.set(os.getenv("FOUNDRY_HOSTNAME"))
    TOKEN_VAR.set(os.getenv("TOKEN") or os.getenv("FOUNDRY_TOKEN"))
    token = os.getenv("TOKEN")
    client = OpenAI(
        api_key=token,
        base_url=get_openai_base_url(preview=True),
        http_client=get_http_client(preview=True),
    )

    if not chat_history:
        messages = [{"role": "user", "content": prompt}]
    else:
        messages = [
            {"role": "user" if i % 2 == 0 else "assistant", "content": chat_history[i]}
            for i in range(len(chat_history))
        ]
        messages.append({"role": "user", "content": prompt})

    for attempt in range(max_attempts):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temp,
            )
            return str(response.choices[0].message.content)
        except Exception as e:
            print(f"LLM call failed with error: {e} on attempt {attempt + 1}/{max_attempts}. Retrying...")
            time.sleep( (attempt+1)**2 *10)

    print(f"Failed after {max_attempts} attempts.")
    return None


def read_write_data(table_name: str, read_or_write: str, data: pd.DataFrame = None) -> pd.DataFrame:
    """
    Read from or write a pandas DataFrame to a CSV file in the data/ directory.

    Depending on `read_or_write`, this function either retrieves a table
    as a pandas DataFrame or writes the provided DataFrame to the table.

    Parameters
    ----------
    table_name : str
        Name of the dataset table to read from or write to.

    read_or_write : str
        Operation to perform: either `"read"` or `"write"`.

    data : pd.DataFrame | None, default=None
        DataFrame to write when `read_or_write="write"`. Ignored for reads.

    Returns
    -------
    pd.DataFrame | None
        Returns the table as a pandas DataFrame when reading.
        Returns None when writing.

    Raises
    ------
    Exception
        If `read_or_write` is not `"read"` or `"write"`, or if writing
        without providing `data`.
    """

    if read_or_write == "read":
        return pd.read_csv(os.path.join(_REPO_ROOT, "data", f"{table_name}.csv"))
    elif read_or_write == "write" and data is not None:
        out_dir = os.path.join(_REPO_ROOT, "data")
        os.makedirs(out_dir, exist_ok=True)
        data.to_csv(os.path.join(out_dir, f"{table_name}.csv"), index=False)
    else:
        raise Exception("Error: Check read_or_write is one of 'read' or 'write' and data is not None")

    return None

# NON FOUNDRY SPECIFIC FUNCTIONS


async def call_llm_async(prompt: str, model, temp: float = 0.7, max_attempts: int = 5, chat_history = None):
    """
    Async wrapper for the synchronous LLM call, limited to 'llm_semaphore' concurrent calls.
    """
    sem = _loop_semaphore.get()
    if sem is None:
        sem = asyncio.Semaphore(8)
        _loop_semaphore.set(sem)

    async with sem:
        return await asyncio.to_thread(
            call_llm, prompt, model, temp, max_attempts, chat_history
        )
    

def remove_failures(list_to_clean, item_type = "item", replace_list = None):
    """
    Removes or replaces dicts containing a 'FAILURE' key.

    Args:
        list_to_clean (list): The list to clean.
        item_type (str): Label for print messages.
        replace_list (list, optional): If provided, use these items as replacements
                                       for failed ones at the same index.

    Returns:
        tuple: (cleaned_list, removed_indices)
    """
    cleaned_list = []
    removed_items = []
    for i, item in enumerate(list_to_clean):
        if isinstance(item, dict) and "FAILURE" in item:
            removed_items.append(i)
            if replace_list:
                cleaned_list.append(replace_list[i])
            else:
                cleaned_list.append(None)
                print(f"Removing {item_type} at index {i} due to incorrectly compiled JSON")
        else:
            cleaned_list.append(item)
    return cleaned_list, removed_items

def clean_outputs(raw_outputs: list, cleaning_type: str, model = None, verbose = False):
    """
    Tries to parse a list of raw strings into a list of valid JSON object. For each string, if the output is not valid JSON,
    it attempts to extract the JSON substring using regex and then an LLM.
    
    cleaning_type is the data format you want returned, either "list" or "dictionary"
    """
    
    if cleaning_type not in ["dictionary", "list"]:
        print("Invalid cleaning_type")
        return None
    
    clean_outputs = {i: None for i in range(len(raw_outputs))}
    raw_outputs = {i: output for i, output in enumerate(raw_outputs)}
    
    raw_outputs_copy = raw_outputs.copy()
    for i, value in raw_outputs_copy.items():
        if not isinstance(value, str):
            if (cleaning_type == "list" and isinstance(value, list)) or \
               (cleaning_type == "dictionary" and isinstance(value, dict)):
                clean_outputs[i] = value
            else:
                clean_outputs[i] = None
            raw_outputs.pop(i)
            continue
        cleaning_steps = [       # Order matters
            (r'//.*', ''),       # remove // comments
            (r'# .*', ''),       # remove # comments
            (r'```', ''),        # remove ```
            (r'json', ''),       # remove json
            (r'\.\.\.', ''),     # remove ...
            (r'python', ''),     # remove python
            (r'},\s*\]', '}]')  # fix trailing comma before ]
        ]
        
        for pattern, replacement in cleaning_steps:
            value = re.sub(pattern, replacement, value)
        new_value = value
        
        try:
            clean_outputs[i] = json.loads(new_value)
            raw_outputs.pop(i)
        except json.JSONDecodeError:
            raw_outputs[i] = new_value
            pass   
    
    raw_outputs_copy = raw_outputs.copy()
    for i, value in raw_outputs_copy.items():
        
        pattern = r"\{.*\}" if cleaning_type == "dictionary" else r"\[.*\]"
        json_match = re.search(pattern, value, re.DOTALL)
        
        if json_match:
            try:
                clean_outputs[i] = json.loads(json_match.group())
                raw_outputs.pop(i)
            except json.JSONDecodeError:
                raw_outputs[i] = value  # Keep original value, not new_value
                if verbose:
                    print(f"Error reading {cleaning_type}, attempting to clean with LLM...")
                pass   
        else:
            if verbose:
                print(f"No {cleaning_type} pattern found in output {i}")
         
    if model is not None:
        raw_outputs_copy = raw_outputs.copy()
        for i, value in raw_outputs_copy.items():
            try:
                prompt = processing_prompts["clean_outputs_prompt"].substitute(
                    CLEANING_TYPE = cleaning_type,
                    VALUE = value
                )
                llm_output = call_llm(prompt, model)
                        
                for pattern, replacement in cleaning_steps:
                    llm_output = re.sub(pattern, replacement, llm_output)
                
                pattern = r"\{.*\}" if cleaning_type == "dictionary" else r"\[.*\]"
                json_match = re.search(pattern, llm_output, re.DOTALL)
                
                if json_match:
                    clean_outputs[i] = json.loads(json_match.group())
                else:
                    raise ValueError("No JSON pattern found in LLM output")
                
            except Exception as e:
                print(f"Error cleaning with LLM: {e}, returning raw_output:", value)
                clean_outputs[i] = {"FAILURE": value}
                
    else:
        raw_outputs_copy = raw_outputs.copy()
        for i, value in raw_outputs_copy.items():
            print("No model provided, returning raw output:", value)
            clean_outputs[i] = {"FAILURE": value}  # Store just the value, not the whole dict
    
    result = [value for key, value in clean_outputs.items()]
    
    return result
        
def clean_int(raw_output):
    """Clean an LLM output into an integer"""
    
    try:
        return int(raw_output)
    except ValueError:
        pass

    try:
        match = re.search(r'-?\d+', raw_output)
        if match:
            return int(match.group())
    except Exception:
        pass

    return random.randint(0,30)

async def add_abbreviations_to_dict(note, model, sections_to_ignore, add_to_content, add_to_headings):
    """
    Iterates over a nested note dictionary, adding abbreviations to values and/or keys.
    - Processes nested dicts fully.
    - Skips any top-level key listed in sections_to_ignore (and does not recurse into it).
    - Keeps heading and content updates separate so they don't clobber each other.
    - Rebuilds the dict preserving insertion order.
    """
    strings_to_process = []
    string_metadata = []  # list of tuples ("heading"|"content", path_list)

    def collect_strings(obj, path=None):
        if path is None:
            path = []
        for key, value in obj.items():
            current_path = path + [key]
            if key in sections_to_ignore:
                continue

            if add_to_headings and isinstance(key, str):
                strings_to_process.append(key)
                string_metadata.append(("heading", current_path))

            if isinstance(value, dict):
                collect_strings(value, current_path)
            else:
                if add_to_content and isinstance(value, str):
                    strings_to_process.append(value)
                    string_metadata.append(("content", current_path))

    collect_strings(note)

    total_abbreviations = 0
    if strings_to_process:
        processed_strings = await add_abbreviations_to_strings(strings_to_process, model)
        total_abbreviations = sum(num for _, num in processed_strings)
    else:
        processed_strings = []

    heading_updates = {}
    content_updates = {}
    for (string_type, path), (processed_text, num) in zip(string_metadata, processed_strings):
        tup = tuple(path)
        if string_type == "heading":
            heading_updates[tup] = processed_text
        else:  # "content"
            content_updates[tup] = processed_text

    def rebuild(obj, path=None):
        if path is None:
            path = []
        new_obj = {}
        for key, value in obj.items():
            current_path = path + [key]
            tup_path = tuple(current_path)

            if key in sections_to_ignore:
                new_obj[key] = value
                continue

            new_key = heading_updates.get(tup_path, key)

            if isinstance(value, dict):
                new_value = rebuild(value, current_path)
            else:
                new_value = content_updates.get(tup_path, value)

            new_obj[new_key] = new_value
        return new_obj

    new_note = rebuild(note)
    return new_note, total_abbreviations


async def add_abbreviations_to_strings(texts, model):
    """
    Process multiple texts at once using call_llm_async.
    """
    if not texts:
        return []
    
    # Create prompts for all texts
    prompts = []
    for text in texts:
        prompts.append(processing_prompts["add_abbreviations_prompt"].substitute(
            TEXT = text
        ))
        
    # Pass list of prompts to call_llm_async
    tasks = [call_llm_async(prompt, model) for prompt in prompts]
    
    outputs = await asyncio.gather(*tasks)
    
    # Clean and process outputs
    cleaned_outputs = clean_outputs(outputs, "dictionary", model)
    
    results = []
    for i, output in enumerate(cleaned_outputs):
        try:
            results.append((output["text"], clean_int(output["number_of_abbreviations"])))
        except (KeyError, TypeError, ValueError) as e:
            print(f"Error processing output {i+1}: {e}. Using original text.")
            results.append((texts[i], 0)) 
    
    return results
    

def add_typos_to_dict(note: dict, typo_rate: float, sections_to_ignore: list):
    """
    Iterates over a nested note dictionary, adding typos to values but not keys. The typo_rate is the probability a word will have a typo.
    """
    total_number_of_typos = 0
    
    for key, value in note.items():
        if isinstance(value, dict):
            note[key], number_of_typos = add_typos_to_dict(value, typo_rate, sections_to_ignore)
            total_number_of_typos += number_of_typos
            
        else:
            
            if not isinstance(value, str):
                text = str(note[key])
            else:
                text = note[key]
            
            if (key != "note_subject") and (key not in sections_to_ignore):
                try:
                    note_with_typos, number_of_typos = add_typos_to_string(text, typo_rate)
                    note[key] = note_with_typos
                    total_number_of_typos += number_of_typos
                except:
                    print(f"Could not add typo to {key}")
                
    
    return note, total_number_of_typos

def add_typos_to_string(note, typo_rate):
    """
    Adds typos to a string. The typo_rate is the probability a word will have a typo.
    """
    
    number_of_words = len(note.split(" "))
    note_obj = typo.StrErrer(note)
    
    # Calculate the number of iterations to apply typos based on typo_rate.
    iterations = math.floor(number_of_words * typo_rate)
    remainder = (number_of_words * typo_rate) % 1
    if remainder > 0 and random.random() < remainder:
        iterations += 1
    
    typo_methods  = ["char_swap",
                    "missing_char", 
                    "extra_char", 
                    "nearby_char", 
                    "skipped_space", 
                    "random_space",
                    "repeated_char",
                    "unichar"]
    
    for _ in range(iterations):
        typo_type = random.choice(typo_methods)
        typo_method = getattr(note_obj, typo_type)
        typo_method()
        
    return note_obj.result, iterations

def combine_template_sections(new_section, combine_sections, note):
    """
    Combines sections in a note. 
    If the sections to be combined includes a dictionary then the new
    section will be in dictionary format. Otherwise simply concatenated
    the subsidiary section descriptions.
    """    
    for section in combine_sections:
        extra_value = pop_nested_value(note, section)
        update_nested_value(note, new_section, extra_value)
        
    return note

def pop_nested_value(d, target_key):
    for key, value in d.items():
        if key == target_key:
            return d.pop(key)
        elif isinstance(value, dict):
            result = pop_nested_value(value, target_key)
            if result is not None:
                return result

def update_nested_value(d, target_key, extra_value):
    for key, value in d.items():
        if key == target_key:
            if isinstance(d[key], dict):
                if isinstance(extra_value, dict):
                    d[key] |= extra_value
                elif isinstance(extra_value, str):
                    last_key = list(d[key].keys())[-1]
                    d[key][last_key] += f"\n\n{extra_value}"
            elif isinstance(d[key], str):
                if isinstance(extra_value, dict):
                    d[key] += "\n"
                    d[key] += "\n".join(f"{k}: {v}" for k, v in extra_value.items())
                if isinstance(extra_value, str):
                    d[key] += f"\n{extra_value}"
        elif isinstance(value, dict):
            update_nested_value(value, target_key, extra_value)


def combine_patients_and_admissions(patient_df, admission_df):
    
    patients_and_admissions = []

    remove_admission_keys = [
        "diagnosis_confirmed_by", "novel_disease",
    ]
    
    for row_index in range(len(patient_df)):
        patient = json.loads(patient_df.iloc[row_index, 0])
        admission = json.loads(admission_df.iloc[row_index, 0])
        
        # Remove unwanted keys if they exist
        for key in remove_admission_keys:
            admission.pop(key, None)
        
        # Just keep the admission as-is, no swapping logic
        joint_details = patient
        joint_details["admission_details"] = admission
        patients_and_admissions.append(joint_details)
        
    return patients_and_admissions




def clean_patient_details(patient_details: dict):
    """
    Removes extraneous information from patient details to stop it beinging 
    included in notes.
    """
    fields_to_remove = ["address", "contact_number", "gp_details", "next_of_kin", 
                        "medical_record_number"]
    
    clean_patient_details = patient_details.copy()
    
    for field in fields_to_remove:
        try:
            clean_patient_details.pop(field)
        except KeyError:
            print(f"{field} key not present in patient details")
            pass
    return clean_patient_details

def clean_event_details(event_details: dict):
    """
    Removes extraneous information from event details to stop it 
    beinging included in notes.
    """
    fields_to_remove = ["date", "time"]
    
    clean_event_details = event_details.copy()
    for field in fields_to_remove:
        try:
            clean_event_details.pop(field)
        except KeyError:
            print(f"{field} key not present in patient details")
            pass
    return clean_event_details

def normalise_array_struct_column(df: pd.DataFrame, column: str) -> pd.DataFrame:	
    """	
    Normalise a column for PyArrow ARRAY<STRUCT>:	
    - Converts strings like '[value]' or "['value']" into Python lists	
    - Converts strings like '["a", "b"]' or '[a, b]' into Python lists	
    - Wraps scalars as dicts	
    - Traverses nested dicts inside lists to normalise bracketed strings	
    """	
    	
    bracket_pattern = re.compile(r"^\[(.*)\]$")  # detect strings in brackets	
    	
    def normalise_value(x):	
        if x is None or (isinstance(x, float) and pd.isna(x)):	
            return None	
        	
        # handle list/tuple/np.ndarray	
        if isinstance(x, (list, tuple, np.ndarray)):	
            return [normalise_value(e) if isinstance(e, (list, tuple, np.ndarray, dict, str)) else e for e in x]	
        	
        # handle dict	
        if isinstance(x, dict):	
            out = {}	
            for k, v in x.items():	
                if isinstance(v, str):	
                    s = v.strip()	
                    # try JSON parse first	
                    try:	
                        parsed = json.loads(s)	
                        out[k] = normalise_value(parsed)	
                        continue	
                    except json.JSONDecodeError:	
                        pass	
                    # try Python literal (handles single quotes)	
                    try:	
                        parsed = ast.literal_eval(s)	
                        out[k] = normalise_value(parsed)	
                        continue	
                    except Exception:	
                        pass	
                    # detect bracketed string '[value_a, value_b,...]'	
                    m = bracket_pattern.match(s)	
                    if m:	
                        inner = m.group(1).strip()	
                        # split by comma if multiple values	
                        if ',' in inner:	
                            items = [item.strip().strip('"').strip("'") for item in inner.split(',')]	
                            out[k] = items	
                        else:	
                            out[k] = [inner]	
                    else:	
                        out[k] = s	
                elif isinstance(v, (list, tuple, np.ndarray, dict)):	
                    out[k] = normalise_value(v)	
                else:	
                    out[k] = v	
            return out	
        	
        # handle string	
        if isinstance(x, str):	
            s = x.strip()	
            try:	
                parsed = json.loads(s)	
                return normalise_value(parsed)	
            except json.JSONDecodeError:	
                try:	
                    parsed = ast.literal_eval(s)	
                    return normalise_value(parsed)	
                except Exception:	
                    # detect bracketed string '[value_a, value_b,...]'	
                    m = bracket_pattern.match(s)	
                    if m:	
                        inner = m.group(1).strip()	
                        if ',' in inner:	
                            items = [item.strip().strip('"').strip("'") for item in inner.split(',')]	
                            return items	
                        else:	
                            return [inner]	
                    return s	
        	
        # fallback for scalar	
        return x	
    	
    df[column] = df[column].apply(normalise_value)	
    return df

def create_admission_window(start_date_str, end_date_str):
    """
    Creates a list of date strings between start and end dates (inclusive).

    Args:
        start_date_str (str): Start date in YYYY-MM-DD format
        end_date_str (str): End date in YYYY-MM-DD format

    Returns:
        list: List of date strings formatted as YYYY-MM-DD
    """
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
    end_date = datetime.strptime(end_date_str, "%Y-%m-%d")

    dates = []
    current_date = start_date

    while current_date <= end_date:
        dates.append(current_date.strftime("%Y-%m-%d"))
        current_date += timedelta(days=1)

    return dates

def random_24_hour_time(elective_hour_start:int,
                        elective_hour_end:int,
                        ae_hour_start:int,
                        ae_hour_end:int,
                        generate_elective=False):
    """
    Generates a random 24-hour time.

    Returns:
        str: Time formatted as HH:MM
    """
    if generate_elective:
        hour = random.randint(elective_hour_start, elective_hour_end)
    else:
        hour = random.randint(ae_hour_start, ae_hour_end)
        
    minute = random.randrange(0, 55, 5)

    return dt_time(hour, minute, 0).strftime("%H:%M")


def build_output_info(template: dict) -> str:
    lines = []

    keep_key = ["note_subject", "note_type", "Content"]

    # 1. Fixed-order bullets for first keys (except Content)
    for key in keep_key:
        if key.lower() != "content" and key in template:
            lines.append(f"- {key}: {template[key]}")

    # Detect if Content exists (case-insensitive)
    content_key = next((k for k in template if k.lower() == "content"), None)
    content_value = template.get(content_key) if content_key else None

    # Collect remaining items not in keep_key
    remaining_items = [
        (k, v) for k, v in template.items() 
        if k not in keep_key and (content_key is None or k != content_key)
    ]

    # Handle Content (if exists)
    if content_value:
        # Content line always comes first
        content_line = f"- {content_key}: {content_value}."
        lines.append(content_line)

        # Add remaining items if they exist
        if remaining_items:
            lines.append("  Other information that could be included in Content:")
            random.shuffle(remaining_items)
            for key, value in remaining_items:
                lines.append(f"    - You could include information on {key}; this could be about {value}.")

    # No Content: only show remaining items if they exist
    elif remaining_items:
        lines.append("- Possible additional Content could include:")
        random.shuffle(remaining_items)
        for key, value in remaining_items:
            lines.append(f"  - You could include information on {key}; this could be about {value}.")

    return "\n".join(lines)


