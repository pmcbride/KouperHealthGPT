# Mini Care Coordinator Assistant

Your task is to design and implement a Care Coordinator Assistant that will help a nurse take
the correct next steps when helping a patient. The assistant guides the nurse based on a
defined engagement process and context about the specific case. As an intelligent agent, it
should also be able to account for any exceptions and edge cases that may come up in real
world use cases.

## Scenario

A nurse is booking appointments for patient John Doe for some referrals following a hospital
visit. The assistant should guide the nurse to book the correct appointments and answer any
questions. In order to book an appointment, the nurse needs to know:

1. first name, last name and dob of the patient
2. the provider/doctor for the appointment
3. the type of appointment
4. the location of the appointment

Some other potential questions the assistant should be able to answer:

* If <provider> is not available at <given time>, what other providers are available?
* Does the hospital accept <insurance provider>? What should I do if not?
* Has the patient booked with this provider before?

## Submission

Your solution should encompass:
* Integration with a large language model (LLM) service to generate responses
* Utilization of the API to access contextual information
* An application featuring a user interface component for interacting with the assistant

## Materials
You are provided the following:
* A data sheet containing information about the hospital system
* An API for retrieving contextual information

# Questions



## Questions:

1. Im a little confused about the referred providers list.
   - What exactly does a "referral following a hospital visit" entail and how does it relate to the referred providers list? I just want to be clear on the terminology and the process since "referred providers list" could just be a list of providers the patient has been referred to in the past, not necessarily a to-do list of appointments to schedule.
   - Or maybe providers on the referred list means insurance will cover them or something since the patient was referred to them, and other providers would be self-pay?
   - After gathering the patient's information, is the nurse supposed to book an appointment for each item in the referred providers list?
   - If yes, should the nurse help the patient book an appointment for each provider in the referred providers list?
   - Should we assume the missing provider info for `specialty: Primary Care` is the patient's PCP?
2. How are we supposed to determine any kind of insurance information?
   - There's no insurance information in the provider directory or patient data
   - Do we assume the `Accepted Insurances` list pertains to all providers and hospitals/departments in the directory or just the referred ones?
   - Is insurance accepted based on the provider or the hospital/department? If it depends, then how?
   - I don't think the nurse will know this information, and while they can ask the patient, the patient may not know either. It would be better to have the insurance information in the patient data or available to lookup through the API.

## Scenario

A nurse is booking appointments for patient John Doe for some referrals following a hospital
visit. The assistant should guide the nurse to book the correct appointments and answer any
questions. In order to book an appointment, the nurse needs to know:

1. first name, last name and dob of the patient
2. the provider/doctor for the appointment
3. the type of appointment
4. the location of the appointment

## Data

```yaml
Patients:
  - id: 1
    name: John Doe
    dob: 01/01/1975
    pcp: Dr. Meredith Grey
    ehrId: 1234abcd
    referred_providers:
      - provider: House, Gregory MD
        specialty: Orthopedics
      - specialty: Primary Care

Provider Directory:
  # Primary Care Providers:
  - name: Grey, Meredith
    certification: MD
    specialty: Primary Care
    departments:
      - name: Sloan Primary Care
        phone: (710) 555-2070
        address: 202 Maple St, Winston-Salem, NC 27101
        hours: M-F 9am-5pm

  # Orthopedics Providers:
  - name: House, Gregory
    certification: MD
    specialty: Orthopedics
    departments:
      - name: PPTH Orthopedics
        phone: (445) 555-6205
        address: 101 Pine St, Greensboro, NC 27401
        hours: M-W 9am-5pm
      - name: Jefferson Hospital
        phone: (215) 555-6123
        address: 202 Maple St, Claremont, NC 28610
        hours: Th-F 9am-5pm

Payment Information:
  Accepted Insurances:
    - Medicaid
    - United Health Care
    - Blue Cross Blue Shield of North Carolina
    - Aetna
    - Cigna

  Self-pay:
    - Primary Care: $150
    - Orthopedics: $300
    - Surgery: $1000
```


### Example Flask API

```python
# app.py
from flask import Flask, jsonify

app = Flask(__name__)


@app.route("/", methods=["GET"])
def healthcheck():
    return jsonify("Hello World")


@app.route("/patient/<patient_id>", methods=["GET"])
def get_data(patient_id):
    if int(patient_id) == 1:
        data = {
            "id": 1,
            "name": "John Doe",
            "dob": "01/01/1975",
            "pcp": "Dr. Meredith Grey",
            "ehrId": "1234abcd",
            "referred_providers": [
                {"provider": "House, Gregory MD", "specialty": "Orthopedics"},
                {"specialty": "Primary Care"},
            ],
            "appointments": [
                {
                    "date": "3/05/18",
                    "time": "9:15am",
                    "provider": "Dr. Meredith Grey",
                    "status": "completed",
                },
                {
                    "date": "8/12/24",
                    "time": "2:30pm",
                    "provider": "Dr. Gregory House",
                    "status": "completed",
                },
                {
                    "date": "9/17/24",
                    "time": "10:00am",
                    "provider": "Dr. Meredith Grey",
                    "status": "noshow",
                },
                {
                    "date": "11/25/24",
                    "time": "11:30am",
                    "provider": "Dr. Meredith Grey",
                    "status": "cancelled",
                },
            ],
        }
        return jsonify(data)


if __name__ == "__main__":
    app.run(debug=True)
```

## Data

```yaml
Patients:
  - id: 1
    name: John Doe
    dob: 01/01/1975
    pcp: Dr. Meredith Grey
    ehrId: 1234abcd
    referred_providers:
      - provider: House, Gregory MD
        specialty: Orthopedics
      - specialty: Primary Care

Provider Directory:
  # Primary Care Providers:
  - name: Grey, Meredith
    certification: MD
    specialty: Primary Care
    departments:
      - name: Sloan Primary Care
        phone: (710) 555-2070
        address: 202 Maple St, Winston-Salem, NC 27101
        hours: M-F 9am-5pm

  # Orthopedics Providers:
  - name: House, Gregory
    certification: MD
    specialty: Orthopedics
    departments:
      - name: PPTH Orthopedics
        phone: (445) 555-6205
        address: 101 Pine St, Greensboro, NC 27401
        hours: M-W 9am-5pm
      - name: Jefferson Hospital
        phone: (215) 555-6123
        address: 202 Maple St, Claremont, NC 28610
        hours: Th-F 9am-5pm

Payment Information:
  Accepted Insurances:
    - Medicaid
    - United Health Care
    - Blue Cross Blue Shield of North Carolina
    - Aetna
    - Cigna

  Self-pay:
    - Primary Care: $150
    - Orthopedics: $300
    - Surgery: $1000
```


### Patients:

```yaml
# Description: This file contains the data for the patients in the system.

# Patients:
- id: 1
  name: John Doe
  dob: 01/01/1975
  pcp: Dr. Meredith Grey
  ehrId: 1234abcd
  referred_providers:
    - provider: House, Gregory MD
      specialty: Orthopedics
    - specialty: Primary Care
  appointments:
    - date: 3/05/18
      time: 9:15am
      provider: Dr. Meredith Grey
      status: completed
    - date: 8/12/24
      time: 2:30pm
      provider: Dr. Gregory House
      status: completed
    - date: 9/17/24
      time: 10:00am
      provider: Dr. Meredith Grey
      status: noshow
    - date: 11/25/24
      time: 11:30am
      provider: Dr. Meredith Grey
      status: cancelled
```

### Provider Directory:

```yaml
# Description: This file contains the data for the providers in the system.

Insurance Information:
  Accepted Insurances:
    - Medicaid
    - United Health Care
    - Blue Cross Blue Shield of North Carolina
    - Aetna
    - Cigna

  Self-pay:
    - Primary Care: $150
    - Orthopedics: $300
    - Surgery: $1000

# Primary Care Providers:
- name: Grey, Meredith
  certification: MD
  specialty: Primary Care
  departments:
    - name: Sloan Primary Care
      phone: (710) 555-2070
      address: 202 Maple St, Winston-Salem, NC 27101
      hours: M-F 9am-5pm
- name: Perry, Chris
  certification: FNP
  specialty: Primary Care
  departments:
    - name: Sacred Heart Surgical Department
      phone: (339) 555-7480
      address: 123 Main St, Raleigh, NC 27601
      hours: M-W 9am-5pm

# Orthopedics Providers:
- name: House, Gregory
  certification: MD
  specialty: Orthopedics
  departments:
    - name: PPTH Orthopedics
      phone: (445) 555-6205
      address: 101 Pine St, Greensboro, NC 27401
      hours: M-W 9am-5pm
    - name: Jefferson Hospital
      phone: (215) 555-6123
      address: 202 Maple St, Claremont, NC 28610
      hours: Th-F 9am-5pm
- name: Brennan, Temperance
  certification: PhD, MD
  specialty: Orthopedics
  departments:
    - name: Jefferson Hospital
      phone: (215) 555-6123
      address: 202 Maple St, Claremont, NC 28610
      hours: Tu-Th 10am-4pm

# Surgery Providers:
- name: Yang, Cristina
  certification: MD
  specialty: Surgery
  departments:
    - name: Seattle Grace Cardiac Surgery
      phone: (710) 555-3082
      address: 456 Elm St, Charlotte, NC 28202
      hours: M-F 9am-5pm
```

```text
Provider Directory
- Grey, Meredith
  - certification: MD
  - specialty: Primary Care
  - department:
    - name: Sloan Primary Care
    - phone: (710) 555-2070
    - address: 202 Maple St, Winston-Salem, NC 27101
    - hours: M-F 9am-5pm
- House, Gregory
  - certification: MD
  - specialty: Orthopedics
  - department:
    - name: PPTH Orthopedics
    - phone: (445) 555-6205
    - address: 101 Pine St, Greensboro, NC 27401
    - hours: M-W 9am-5pm
  - department:
    - name: Jefferson Hospital
    - phone: (215) 555-6123
    - address: 202 Maple St, Claremont, NC 28610
    - hours: Th-F 9am-5pm
- Yang, Cristina
  - certification: MD
  - specialty: Surgery
  - department:
    - name: Seattle Grace Cardiac Surgery
    - phone: (710) 555-3082
    - address: 456 Elm St, Charlotte, NC 28202
    - hours: M-F 9am-5pm
- Perry, Chris
  - certification: FNP
  - specialty: Primary Care
  - department:
    - name: Sacred Heart Surgical Department
    - phone: (339) 555-7480
    - address: 123 Main St, Raleigh, NC 27601
    - hours: M-W 9am-5pm
Brennan, Temperance
  - certification: PhD, MD
  - specialty: Orthopedics
  - department:
    - name: Jefferson Hospital
    - phone: (215) 555-6123
    - address: 202 Maple St, Claremont, NC 28610
    - hours: Tu-Th 10am-4pm

Appointments:
  Times:
    - appointments can only be booked within office hours
    -
  Types:
    - NEW appointment is 30 minutes long, ESTABLISHED appointment is 15 minutes long
    - An appointment is ESTABLISHED if the patient has been seen the provider in the least 5 years
    - otherwise the appointment type is NEW
  Arrival:
    - New patients should arrive 30 minutes early
    - Establish patients are encouraged to arrive 10 minutes before appointment

Accepted Insurances:
- Medicaid
- United Health Care
- Blue Cross Blue Shield of North Carolina
- Aetna
- Cigna

Self-pay:
- Primary Care: $150
- Orthopedics: $300
- Surgery: $1000
```