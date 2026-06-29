from .appointments import Appointments
from .consultations import Consultations
from .doctor_hospital import Doctor_Hospital
from .doctors import Doctors
from .hospitals import Hospitals
from .medical_history import Medical_History
from .medications import Medications
from .patients import Patients
from .prescriptions import Prescriptions
from .timeslots import Timeslots
from .users import Users

__all__ = [
    "Users",
    "Patients",
    "Doctors",
    "Hospitals",
    "Doctor_Hospital",
    "Appointments",
    "Medical_History",
    "Prescriptions",
    "Consultations",
    "Medications",
    "Timeslots",
]
