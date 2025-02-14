__all__ = [
    "PATIENT_DATA",
    "PROVIDER_DIRECTORY",
    "ACCEPTED_INSURANCES",
    "ACCEPTED_INSURANCES_DICT",
    "SELF_PAY_COSTS",
]

PATIENT_DATA = [
    {
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
]

PROVIDER_DIRECTORY = [
    {
        "name": "Grey, Meredith",
        "certification": "MD",
        "specialty": "Primary Care",
        "departments": [
            {
                "name": "Sloan Primary Care",
                "phone": "(710) 555-2070",
                "address": "202 Maple St, Winston-Salem, NC 27101",
                "hours": "M-F 9am-5pm",
            }
        ],
    },
    {
        "name": "Perry, Chris",
        "certification": "FNP",
        "specialty": "Primary Care",
        "departments": [
            {
                "name": "Sacred Heart Surgical Department",
                "phone": "(339) 555-7480",
                "address": "123 Main St, Raleigh, NC 27601",
                "hours": "M-W 9am-5pm",
            }
        ],
    },
    {
        "name": "House, Gregory",
        "certification": "MD",
        "specialty": "Orthopedics",
        "departments": [
            {
                "name": "PPTH Orthopedics",
                "phone": "(445) 555-6205",
                "address": "101 Pine St, Greensboro, NC 27401",
                "hours": "M-W 9am-5pm",
            },
            {
                "name": "Jefferson Hospital",
                "phone": "(215) 555-6123",
                "address": "202 Maple St, Claremont, NC 28610",
                "hours": "Th-F 9am-5pm",
            },
        ],
    },
    {
        "name": "Brennan, Temperance",
        "certification": "PhD, MD",
        "specialty": "Orthopedics",
        "departments": [
            {
                "name": "Jefferson Hospital",
                "phone": "(215) 555-6123",
                "address": "202 Maple St, Claremont, NC 28610",
                "hours": "Tu-Th 10am-4pm",
            }
        ],
    },
    {
        "name": "Yang, Cristina",
        "certification": "MD",
        "specialty": "Surgery",
        "departments": [
            {
                "name": "Seattle Grace Cardiac Surgery",
                "phone": "(710) 555-3082",
                "address": "456 Elm St, Charlotte, NC 28202",
                "hours": "M-F 9am-5pm",
            }
        ],
    },
]


ACCEPTED_INSURANCES = [
    "Medicaid",
    "United Health Care",
    "Blue Cross Blue Shield of North Carolina",
    "Aetna",
    "Cigna",
]

ACCEPTED_INSURANCES_DICT = [
    {
        "id": 1,
        "name": "Medicaid"
    },
    {
        "id": 2,
        "name": "United Health Care"
    },
    {
        "id": 3,
        "name": "Blue Cross Blue Shield of North Carolina"
    },
    {
        "id": 4,
        "name": "Aetna"
    },
    {
        "id": 5,
        "name": "Cigna"
    },
]

SELF_PAY_COSTS = {
  "Primary Care": 150,
  "Orthopedics": 300,
  "Surgery": 1000,
}
