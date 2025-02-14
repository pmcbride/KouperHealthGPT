# %%
import gradio as gr
from openai import OpenAI
import dotenv
dotenv.load_dotenv()
from openai import OpenAI
from pydantic import BaseModel, Field
from typing import Optional, Any
import json
import inspect
import datetime

from typing import Optional, Any, List, Dict
from gradio import ChatMessage
import yaml

from swarm import (
    Swarm,
    Agent
)
from swarm.repl import run_demo_loop

# from utils import (
#     display_json,
#     obj2dict,
#     obj2txt,
#     pretty_print,
#     pretty_print_conversation,
# )

from data import (
    PATIENT_DATA,
    PROVIDER_DIRECTORY,
    ACCEPTED_INSURANCES,
    SELF_PAY_COSTS,
)

client = Swarm()
# client = OpenAI(max_retries=5)

# from fastapi import FastAPI

# Create a FastAPI instance
# app = FastAPI(title="Care Coordinator Assistant API")

# ----------------------------
# Function Definitions
# ----------------------------
def get_patient_id(patient_id: int):
    """
    Retrieve patient details and appointment history from the external API.
    Required Parameters: patient_id (integer or string).
    """
    try:
        for patient in PATIENT_DATA:
            if int(patient["id"]) == int(patient_id):
                return patient
    except Exception as e:
        print(f"Error: {e}")
    return f"Patient {patient_id} not found."

def get_patient_data(first_name: str, last_name: str, dob: str):
    """
    Purpose: Retrieve the patient’s information (ID, name, DOB, past appointments, referred providers, etc.).
    Required Parameters: first_name, last_name, dob (str as MM/DD/YYYY).
    Returns: Dictionary with patient data or None if not found.
    """
    for patient in PATIENT_DATA:
        if (patient["name"].lower() == f"{first_name} {last_name}".lower()) and (patient["dob"] == dob):
            return patient
    return f"Error: Patient {first_name} {last_name} with DOB {dob} not found."

def get_patient_referrals(first_name: str, last_name: str, dob: str):
    """
    Purpose: Retrieve the patient's referred providers.
    Required Parameters: first_name, last_name, dob
    Returns: List of referred providers or None if not found.
    """
    patient = get_patient_data(first_name, last_name, dob)
    if patient:
        return patient.get("referred_providers", [])
    return f"Error: Patient {first_name} {last_name} with DOB {dob} not found."

def get_patient_appointments(first_name: str, last_name: str, dob: str):
    """
    Purpose: Retrieve the patient's past appointments.
    Required Parameters: first_name, last_name, dob
    Returns: List of past appointments or None if not found.
    """
    patient = get_patient_data(first_name, last_name, dob)
    if patient:
        return patient.get("appointments", [])
    return f"Error: Patient {first_name} {last_name} with DOB {dob} not found."

def get_provider_names():
    """
    Return a list of provider names from the provider directory.
    """
    return [provider["name"] for provider in PROVIDER_DIRECTORY]

PROVIDER_NAMES = get_provider_names()

def get_provider_directory():
    """
    Return all providers in the directory
    """
    return PROVIDER_DIRECTORY

def get_providers_by_specialty(specialty: str):
    """
    Given a specialty, return a list of providers with that specialty.
    """
    return [provider for provider in PROVIDER_DIRECTORY if provider["specialty"] == specialty] or f"Error: No providers found with specialty {specialty}."

def get_provider_locations(provider_name: str):
    """
    Given a provider name, return a list of available location choices by concatenating
    the department name and its address.
    """
    for provider in PROVIDER_DIRECTORY:
        if provider["name"] == provider_name:
            locations = []
            for dept in provider["departments"]:
                loc = f"{dept['name']} ({dept['address']})"
                locations.append(loc)
            return locations
    print(f"Error: Provider {provider_name} not found, please select from the available providers: {PROVIDER_NAMES}.")
    return f"Error: Provider {provider_name} not found, please select from the available providers: {PROVIDER_NAMES}."

def get_provider_hours(provider_name: str):
    """
    Given a provider name, return a list of available appointment times.
    """
    for provider in PROVIDER_DIRECTORY:
        if provider["name"] == provider_name:
            return [dept["hours"] for dept in provider["departments"]]
    print(f"Error: Provider {provider_name} not found, please select from the available providers: {PROVIDER_NAMES}.")
    return f"Error: Provider {provider_name} not found, please select from the available providers: {PROVIDER_NAMES}."

def get_provider_location_hours(provider_name: str):
    """
    Given a provider name, return a dictionary of available location choices and their hours.
    """
    location_hours = {}
    for provider in PROVIDER_DIRECTORY:
        if provider["name"] == provider_name:
            for dept in provider["departments"]:
                loc = dept["name"]
                hours = dept["hours"]
                location_hours[loc] = hours
            return location_hours
    print(f"Error: Provider {provider_name} not found, please select from the available providers: {PROVIDER_NAMES}.")
    return f"Error: Provider {provider_name} not found, please select from the available providers: {PROVIDER_NAMES}."

def get_provider_specialty(provider_name: str):
    """
    Given a provider name, return the provider's specialty.
    """
    for provider in PROVIDER_DIRECTORY:
        if provider["name"] == provider_name:
            return provider["specialty"]
    print(f"Error: Provider {provider_name} not found, please select from the available providers: {PROVIDER_NAMES}.")
    return f"Error: Provider {provider_name} not found, please select from the available providers: {PROVIDER_NAMES}."

def list_accepted_insurances():
    """
    List all accepted insurance providers.
    """
    return ACCEPTED_INSURANCES

def check_insurance(insurance_provider: str):
    """
    Check if the hospital accepts the specified insurance provider.
    """
    return insurance_provider in ACCEPTED_INSURANCES

def get_provider_info(provider_name: str):
    """
    Given a provider name, return the provider's information.
    """
    for provider in PROVIDER_DIRECTORY:
        if provider["name"] == provider_name:
            return provider
    print(f"Error: Provider {provider_name} not found, please select from the available providers: {PROVIDER_NAMES}.")
    return f"Error: Provider {provider_name} not found, please select from the available providers: {PROVIDER_NAMES}."

WEEKDAYS = ["M", "Tu", "W", "Th", "F", "Sa", "Su"]
WEEKDAY_INDEX_MAP = {
    0: "M",
    1: "Tu",
    2: "W",
    3: "Th",
    4: "F",
    5: "Sa",
    6: "Su"
}
WEEKDAY_MAP = {
    "M": "Monday",
    "Tu": "Tuesday",
    "W": "Wednesday",
    "Th": "Thursday",
    "F": "Friday",
    "Sa": "Saturday",
    "Su": "Sunday",
}
WEEKDAY_ABBR_MAP = {
    "Monday": "M",
    "Tuesday": "Tu",
    "Wednesday": "W",
    "Thursday": "Th",
    "Friday": "F",
    "Saturday": "Sa",
    "Sunday": "Su",
}


def convert_weekdays_to_list(weekdays_str):
    """ Convert a string representation of weekdays (e.g. "M-W, F") to a list of weekday abbreviations. """
    weekdays = []
    for day in weekdays_str.split(","):
        if "-" in day:
            start, end = day.split("-")
            start_index = WEEKDAYS.index(start)
            end_index = WEEKDAYS.index(end)
            weekdays.extend(WEEKDAYS[start_index:end_index + 1])
        else:
            weekdays.append(day)
    return weekdays


def convert_hours_to_datetime(hours_str):
    """
    Convert a string representation of weekday-range and hours-range (e.g. "M-F 9am-5pm") to datetime objects.
    """
    weekdays, hours = hours_str.split(" ")
    start_hour, end_hour = hours.split("-")
    start_hour = datetime.datetime.strptime(start_hour, "%I%p").time()
    end_hour = datetime.datetime.strptime(end_hour, "%I%p").time()
    return weekdays, start_hour, end_hour

def convert_weekday_time_to_datetime(weekday_str, time_str):
    """
    Convert a string representation of weekday and time (e.g. "M 9am") to a datetime object.
    """
    weekday = WEEKDAY_ABBR_MAP.get(weekday_str, "")
    time = datetime.datetime.strptime(time_str, "%I%p").time()
    return weekday, time

def check_provider_availability(provider: str, desired_weekday_time_str: str):
    """
    Check if the specified provider is available at the given appointment time.
    Provider names are all in the format "Last, First" without any prefixes or suffixes.
    The desired_weekday_time_str should be in the format "D H(ampm)" (e.g. "M 9am").
    Available weekday values are "M", "Tu", "W", "Th", "F", "Sa", "Su".
    Required Parameters: provider (string), desired_weekday_time_str (string).
    Returns a dict: {
         "provider_available": bool,
         "available_departments": list,
         "alternative_providers": list
    }.
    """
    print(f"Checking availability for provider {provider} at {desired_weekday_time_str}.")
    # Check if the provider is in list of provider names
    if provider not in PROVIDER_NAMES:
        print(f"Error: Provider {provider} not found, please select from the available providers: {PROVIDER_NAMES}.")
        return f"Error: Provider {provider} not found, please select from the available providers: {PROVIDER_NAMES}."

    try:
        # Expecting format like "M 9am"
        # desired_weekday_time_str = "T 11am"
        parts = desired_weekday_time_str.split()
        if len(parts) != 2:
            print("Invalid format. Expected format is 'D H(ampm)', e.g., 'M 9am'.")
            return "Invalid format. Expected format is 'D H(ampm)', e.g., 'M 9am'."
        desired_day = parts[0]
        if desired_day not in WEEKDAYS:
            print(f"Invalid weekday '{desired_day}'. Valid options are: {WEEKDAYS}.")
            return f"Invalid weekday '{desired_day}'. Valid options are: {WEEKDAYS}."
        desired_time = datetime.datetime.strptime(parts[1], "%I%p").time()
    except Exception as e:
        print(f"Error parsing desired_weekday_time_str: {e}")
        return f"Error parsing desired_weekday_time_str: {e}"

    def is_available_in_department(hours_str):
        """
        Helper: Checks if the desired time falls within the department's operating hours.
        """
        try:
            weekdays_str, start_time, end_time = convert_hours_to_datetime(hours_str)
            valid_days = convert_weekdays_to_list(weekdays_str)
        except Exception as e:
            # In case of any parsing errors, consider this department as unavailable.
            return False
        if desired_day in valid_days and start_time <= desired_time <= end_time:
            return True
        return False

    # Check availability for the specified provider.
    prov_info = get_provider_info(provider)
    if isinstance(prov_info, str):
        # Provider not found.
        print(f"Error: Provider {provider} not found, please select from the available providers: {PROVIDER_NAMES}.")
        return f"Error: Provider {provider} not found, please select from the available providers: {PROVIDER_NAMES}."

    available_departments = []
    for dept in prov_info.get("departments", []):
        if is_available_in_department(dept.get("hours", "")):
            location_info = f"{dept.get('name', 'Unknown')} ({dept.get('address', 'Unknown')})"
            available_departments.append(location_info)

    provider_available = bool(available_departments)

    alternative_providers = []
    # If the provider is not available, look for alternatives.
    specialty = prov_info.get("specialty", "")
    for prov in get_providers_by_specialty(specialty):
        if prov["name"] == provider:
            continue  # Skip the original provider.
        alt_depts = []
        for dept in prov.get("departments", []):
            if is_available_in_department(dept.get("hours", "")):
                location_info = f"{dept.get('name', 'Unknown')} ({dept.get('address', 'Unknown')})"
                alt_depts.append(location_info)
        if alt_depts:
            alternative_providers.append({"name": prov["name"], "available_departments": alt_depts})

    return {
        "provider_available": provider_available,
        "available_departments": available_departments,
        "alternative_providers": alternative_providers
    }


def test_provider_availability():
    """
    Test function to check provider availability.
    """
    provider = "House, Gregory"
    # desired_datetime = datetime.datetime(2025, 1, 15, 10, 0)  # Monday at 10:00 AM
    desired_weekday_time_str = "M 10am"
    provider_availability = check_provider_availability(provider, desired_weekday_time_str)
    availability, alternatives = list(provider_availability.values()) #provider_availability["provider_available"], provider_availability["alternative_providers"]
    print(f"Provider {provider} is {'available' if availability else 'not available'} at {desired_datetime.time()}.")
    if alternatives:
        print("Alternative providers:", alternatives)
    else:
        print("No alternative providers available.")

def get_care_coordinator_assistant_prompt():
    """
    Return the instructions for the Care Coordinator Assistant.
    """
    with open("careCoordinatorAssistantPrompt.txt", "r") as file:
        return file.read()

SYSTEM_PROMPT = """
You are a Care Coordinator Assistant helping nurses book appointments and answer questions related to provider availability, insurance acceptance, and previous patient history. Guide the nurse step-by-step based on the case context. Your task is to guide the nurse based on a defined engagement process and context about the specific case. As an intelligent agent, you must be able to account for any exceptions and edge cases that may come up in real world use cases and make sure to ask questions and gather more information before making decisions about a patient's sensitive health information. Your initial goal is to help the nurse book appointments for their patient for some referrals following a hospital visit. The assistant should guide the nurse to book the correct appointments and answer any questions.

In order to book an appointment, the nurse needs to know:

1. Patient information:
   - Need the first name, last name and dob of the patient to look them up in the system.
   - Once you have this information, confirm the patient data by calling `get_patient_data` to display the rest of the patient's data like primary care provider, referred providers, and appointments.
   - Once the patient is confirmed, remind the nurse to input the patient id (field "id" with integer value in patient data) into the form field to fill out the rest of the patient's information.
2. Determine which appointments to book based on the patient's referred providers:
   - Use the patient data or call calling `get_patient_referrals` to determine the latest referrals to book an appointment for.
   - Display the referred providers list to the nurse as a numbered list and ask which referral they would like to book an appointment for next.
   - Repeat Steps 3 through 6 for each referral.
3. Determine provider for referral:
   - Once the nurse selects a referral confirm the provider based on the patient's primary care provider or previous appointments.
   - If no provider is specified, call `get_providers_by_specialty` to get a list of providers with the same specialty and ask the nurse to select one.
   - If a provider is specified, confirm with the nurse before proceeding.
   - Let the nurse know that they can also select the provider from a dropdown list of available providers.
4. Determine the type of appointment: "NEW" or "ESTABLISHED"
   - Use the patient data to determine based on the patient's appointments history
   - If the patient has had no appointments with the provider, suggest a "NEW" appointment
   - If the patient has had appointments with the provider, suggest an "ESTABLISHED" appointment
   - Confirm with the nurse before proceeding and let them know they can select the appointment type using the radio button.
5. Determine the time and location of the appointment
   - Start off by suggesting the first available time slot for the provider and call `check_provider_availability` first to make sure the provider is available at that time.
   - If the provider is not available at that time, then show their full schedule and suggest another time.
   - If the nurse suggests another provider or time then call `check_provider_availability` to confirm the availability.
   - Confirm the location of the appointment based on the provider's department and address and let the nurse know they can select the location from a dropdown list of available locations.
6. Book the appointment for referral:
   - Confirm the appointment details with the nurse and let them know that the appointment has been successfully booked.
   - Call `book_appointment` to book the appointment and provide the nurse with the appointment confirmation details.
7. Remember to repeat Steps 3 through 6 for each referral.
   - Display the remaining referrals to the nurse as a numbered list and ask which referral they would like to book an appointment for next.

Some other potential questions the assistant should be able to answer:

* If <provider> is not available at <given time>, what other providers are available? Call `check_provider_availability` to check.
* Does the hospital accept <insurance provider>? What should I do if not? Call `check_insurance` to check.
* Has the patient booked with this provider before? Call `get_patient_appointments` to check and make sure the patient has had an appointment with the provider before and the appointment status shows completed or some equivalent that shows the patient was seen.
"""

def book_appointment(
    patient_id: int,
    provider: str,
    appointment_weekday_time_str: str,
    appointment_type: str,
    location: str,
):
    """
    Book an appointment with the provided details.
    Required Parameters:
      - patient_id (int): Unique identifier for the patient.
      - provider (str): Name of the provider.
      - appointment_weekday_time_str (str): Appointment time in the format "D H(ampm)" (e.g., "M 10am").
      - appointment_type (str): Appointment type, either "NEW" or "ESTABLISHED".
      - location (str): Selected location for the appointment in the format "Department (Address)". E.g., "Main Clinic (123 Main St)".
    Returns:
      A string with the appointment confirmation details if booking is successful, or an error message otherwise.
    """

    # Validate patient
    patient_data = get_patient_id(patient_id)
    if isinstance(patient_data, str):
        return f"Error: Patient with ID {patient_id} not found."

    # Validate provider
    provider_data = get_provider_info(provider)
    if isinstance(provider_data, str):
        return f"Error: Provider '{provider}' not found, please select from the available providers: {PROVIDER_NAMES}."

    # Validate appointment type
    if appointment_type not in ["NEW", "ESTABLISHED"]:
        return "Error: Appointment type must be 'NEW' or 'ESTABLISHED'."

    # Validate appointment_weekday_time_str (expected format: "D H(ampm)", e.g., "M 10am")
    try:
        parts = appointment_weekday_time_str.split()
        if len(parts) != 2:
            return "Error: Appointment time must be in the format 'D H(ampm)', e.g., 'M 10am'."
        weekday, time_str = parts
        # Validate weekday abbreviation: it should be one of the accepted abbreviations
        valid_weekdays = ["M", "Tu", "W", "Th", "F", "Sa", "Su"]
        if weekday not in valid_weekdays:
            return f"Error: Weekday '{weekday}' is invalid. Valid options are: {valid_weekdays}."
        # Validate time format
        datetime.datetime.strptime(time_str, "%I%p")
    except Exception as e:
        return f"Error: Invalid appointment time format. {e}"

    # Validate location: must be one of the available locations for the provider.
    available_locations = get_provider_locations(provider)
    if location not in available_locations:
        return f"Error: The location '{location}' is not available for provider '{provider}'. Available locations: {available_locations}"

    # If all validations pass, confirm the booking.
    appointment_confirmation = (
        "**Successful Booking:**\n"
        f"  - Patient: {patient_data['name']} (DOB: {patient_data['dob']})\n"
        f"  - Provider: {provider}\n"
        f"  - Location: {location}\n"
        f"  - Date & Time: {appointment_weekday_time_str}\n"
        f"  - Appointment Type: {appointment_type}\n"
    )
    return appointment_confirmation


def provide_self_pay_info(specialty):
    """
    Provide self-pay cost details based on the specialty if insurance is not accepted.
    Required Parameters: specialty (string).
    Returns the cost as an integer or an error message if not available.
    """
    return SELF_PAY_COSTS.get(specialty, "Cost information not available.")


care_coordinator_agent = Agent(
    name="Care Coordinator Assistant",
    # instructions=get_care_coordinator_assistant_prompt(),
    instructions=SYSTEM_PROMPT,
    functions=[
        get_patient_id,
        get_patient_data,
        get_patient_referrals,
        get_patient_appointments,
        get_provider_directory,
        get_providers_by_specialty,
        get_provider_names,
        get_provider_locations,
        get_provider_hours,
        get_provider_info,
        check_provider_availability,
        list_accepted_insurances,
        check_insurance,
        book_appointment,
        provide_self_pay_info,
    ],
)


def user(user_message, chat_history: list):
    return "", chat_history + [{"role": "user", "content": user_message}]

def bot(chat_history: list):
    response_stream = client.run(
        agent=care_coordinator_agent,
        messages=chat_history,
        stream=True,
    )
    # user_message="Hello, I need to book an appointment for a patient."
    # chat_history=[]
    # chat_history += [{"role": "user", "content": user_message}]
    chat_history.append({"role": "assistant", "content": ""})
    for chunk in response_stream:
        print(chunk)
        response_text = chunk.get("content", None)
        if response_text is not None:
            chat_history[-1]["content"] += response_text
            yield chat_history

#%%
with gr.Blocks(css="#chatbot { height: 80vh !important; }") as demo:
    gr.Markdown("## Care Coordinator Assistant")

    with gr.Row():
        # Left Column: Chat Interface
        with gr.Column(scale=2):
            gr.Markdown("### Chat with Assistant")
            chatbot = gr.Chatbot(
                type="messages",
                elem_id="chatbot",
                # examples=[{"role":"user", "content": "Hello, I need to book an appointment for a patient."}],
            )
            chat_input = gr.Textbox(
                label="Chat Input",
                placeholder="Type your message here...",
                show_label=False,
                container=False,
            )
            # clear = gr.ClearButton([chat_input, chatbot])
            clear = gr.Button("Clear")

            # Submit chat input to update the chat history
            chat_input.submit(
                fn=user,
                inputs=[chat_input, chatbot],
                outputs=[chat_input, chatbot],
                queue=False
            ).then(
                fn=bot,
                inputs=chatbot,
                outputs=chatbot,
            )
            clear.click(lambda: None, None, chatbot, queue=False)

        # Right Column: Appointment & Patient Form
        with gr.Column(scale=1):
            gr.Markdown("### Patient Information")
            patient_id_input = gr.Textbox(
                label="Patient ID",
                interactive=True,
            )
            first_name_input = gr.Textbox(
                label="First Name",
                interactive=True,
            )
            last_name_input = gr.Textbox(
                label="Last Name",
                interactive=True,
            )
            dob_input = gr.Textbox(
                label="DOB",
                interactive=True,
            )
            pcp_input = gr.Textbox(
                label="Primary Care Provider",
                interactive=False,
            )
            gr.Markdown("### Referred Providers")
            referred = gr.Markdown(
                label="Referred Providers",
                value="",
                container=True,
            )
            gr.Markdown("### Past Appointments")
            appointments = gr.Markdown(
                label="Past Appointments",
                value="",
                container=True,
            )
            gr.Markdown("### Appointment Booking")
            provider_dropdown = gr.Dropdown(
                label="Select Provider",
                choices=PROVIDER_NAMES,
                interactive=True,
            )
            appointment_type = gr.Radio(
                label="Appointment Type",
                choices=["NEW", "ESTABLISHED"],
                interactive=True,
            )
            location_dropdown = gr.Dropdown(
                label="Select Location",
                choices=[], #get_provider_locations(provider_dropdown.value),
                interactive=True,
            )
            available_hours_text = gr.Textbox(
                label="Available Appointment Times",
                value=", ".join(get_provider_hours(provider_dropdown.value)),
                interactive=False,
            )
            appointment_time_input = gr.Textbox(
                label="Input Appointment Time",
                placeholder="e.g., M 9am",
                interactive=True,
            )

            book_confirmation = gr.Markdown(
                label="Booking Confirmation",
                value="",
                container=True,
            )
            # Book appointment button: Use all form data to run book_appointment and display the output.
            book_button = gr.Button("Book Appointment")
            book_button.click(
                fn=book_appointment,
                inputs=[patient_id_input, provider_dropdown, appointment_time_input, appointment_type, location_dropdown],
                outputs=book_confirmation
            )

            def render_appointments_markdown(appointments: List[Dict[str, Any]]):
                """
                Render the list of appointments as a Markdown-formatted table
                """
                # appointments = f"```yaml\n{yaml.dump(patient.get('appointments', []), sort_keys=False)}```"
                if not appointments:
                    return ""
                table = "| Date | Time | Provider | Status |\n| --- | --- | --- | --- |\n"
                for appt in appointments:
                    table += f"| {appt['date']} | {appt['time']} | {appt['provider']} | {appt['status']} |\n"
                return table

            def render_referred_providers_markdown(referred_providers: List[str]):
                """
                Render the list of referred providers as a Markdown-formatted numbered list
                """
                # referred = f"```yaml\n{yaml.dump(patient.get('referred_providers', []), sort_keys=False)}```"
                if not referred_providers:
                    return ""
                referral_strings = []
                for i, prov in enumerate(referred_providers):
                    speciality = prov.get("specialty", "")
                    provider = prov.get("provider", "")
                    referral_strings.append(f"{i+1}. {speciality} Appointment" + (f"\n   - Provider: {provider}" if provider else ""))
                return "\n".join(referral_strings)

            # When the patient ID is changed, update the patient information
            def update_patient_fields(patient_id: int | str):
                """ Update the patient form fields based on the patient ID (integer). """
                global first_name, last_name, dob, pcp, referred, appointments
                patient = get_patient_id(patient_id)
                if isinstance(patient, str):
                    return "", "", "", "", "", ""
                names = patient.get("name", "").split(" ", 1)
                first_name = names[0] if names else ""
                last_name = names[1] if len(names) > 1 else ""
                dob = patient.get("dob", "")
                pcp = patient.get("pcp", "")
                referred = render_referred_providers_markdown(patient.get('referred_providers', []))
                appointments = render_appointments_markdown(patient.get('appointments', []))
                return first_name, last_name, dob, pcp, referred, appointments


            patient_id_input.submit(
                fn=update_patient_fields,
                inputs=patient_id_input,
                outputs=[first_name_input, last_name_input, dob_input, pcp_input, referred, appointments]
            )

            # This function takes the selected provider and returns an update for the location dropdown.
            def update_locations(selected_provider):
                """ Update the location dropdown choices based on the selected provider. """
                locations = get_provider_locations(selected_provider) or []
                if not isinstance(locations, (list, tuple)):
                    locations = []
                # In Gradio, you can update component properties by returning a component update.
                return gr.update(choices=locations)

            # When the provider selection changes, update the location dropdown choices.
            provider_dropdown.change(
                update_locations,
                inputs=provider_dropdown,
                outputs=location_dropdown,
            )

            def render_available_hours(provider_name, location_name):
                """ Update the available hours text based on the selected provider. """
                # available_hours = get_provider_hours(provider_name)
                location_hours = get_provider_location_hours(provider_name)
                if not location_hours:
                    return ""
                loc_hours_list = [f"{hours} ({loc})" for loc, hours in location_hours.items() if loc in location_name]
                return "\n".join(loc_hours_list)

            location_dropdown.change(
                fn=render_available_hours,
                inputs=[provider_dropdown, location_dropdown],
                outputs=available_hours_text
            )

if __name__ == "__main__":
    demo.launch(
        debug=True,
        share=False,
        server_name="0.0.0.0",
        pwa=True
    )

# Mount the Gradio app at the '/ui' endpoint of the FastAPI app.
# app.mount("/ui", demo.app)

# if __name__ == "__main__":
#     import uvicorn
#     # Run the FastAPI server with uvicorn.
#     uvicorn.run(app, host="0.0.0.0", port=8000)
