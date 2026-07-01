from fastapi import APIRouter

from api.v1.routes.appointment import router as appointment_router
from api.v1.routes.auth import router as auth_router
from api.v1.routes.consultation import router as consultation_router
from api.v1.routes.doctor import router as doctor_router
from api.v1.routes.hospital import router as hospital_router
from api.v1.routes.medical_history import router as medical_history_router
from api.v1.routes.medication import router as medication_router
from api.v1.routes.patient import router as patient_router
from api.v1.routes.prescription import router as prescription_router
from api.v1.routes.test import router as test_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(test_router)
api_router.include_router(auth_router)
api_router.include_router(hospital_router)
api_router.include_router(doctor_router)
api_router.include_router(patient_router)
api_router.include_router(appointment_router)
api_router.include_router(medication_router)
api_router.include_router(prescription_router)
api_router.include_router(consultation_router)
api_router.include_router(medical_history_router)
