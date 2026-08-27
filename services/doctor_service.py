from datetime import datetime, timezone

from fastapi import HTTPException, UploadFile
from sqlmodel import Session, select

from models.appointments import Appointments, AppointmentStatus
from models.doctor_hospital import Doctor_Hospital
from models.doctors import Doctors
from models.hospitals import Hospitals
from models.notifications import NotificationType
from models.timeslots import Timeslots
from models.users import UserRole, Users
from schemas.doctor import (
    DoctorHospitalAdminUpdate,
    DoctorOut,
    DoctorRegister,
    DoctorSecurityAnswerUpdate,
    DoctorUpdate,
    TimeSlotCreate,
)
from services.notification_service import (
    create_notification,
    notify_hospital,
    notify_role,
)
from utils.file_storage import (
    create_user_folder,
    delete_file_by_url,
    delete_user_folder,
    save_verification_doc,
)
from utils.security import hash_password, verify_password


async def register_doctor(
    data: DoctorRegister,
    license_photo: UploadFile,
    session: Session,
    current_hospital: Users,
):
    existing = session.exec(select(Users).where(Users.email == data.email)).first()
    if existing:
        raise HTTPException(status_code=400, detail="email already registered")

    existing_rez = session.exec(
        select(Doctors).where(Doctors.license_number == data.license_number)
    ).first()
    if existing_rez:
        raise HTTPException(
            status_code=400, detail="Doctor license_number already taken..."
        )

    hospital = session.exec(
        select(Hospitals).where(Hospitals.user_id == current_hospital.id)
    ).first()
    if hospital is None or hospital.id is None:
        raise HTTPException(status_code=404, detail="hospital profile not found..")

    user = Users(
        email=data.email,
        password_hash=hash_password(data.password),
        role=UserRole.doctor,
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    if user.id is None:
        raise HTTPException(status_code=500, detail="User ID generation failed")

    create_user_folder(user.id)
    license_photo_url = await save_verification_doc(
        license_photo, user.id, "license_photos"
    )

    doctor = Doctors(
        user_id=user.id,
        hospital_id=hospital.id,
        name=data.name,
        phone=data.phone,
        department=data.department,
        speciality=data.speciality,
        bio=data.bio,
        address=data.address,
        license_number=data.license_number,
        license_photo_url=license_photo_url,
        years_experience=data.years_experience,
    )
    session.add(doctor)
    session.commit()
    session.refresh(doctor)

    if doctor.id is None:
        raise HTTPException(status_code=500, detail="Doctor ID generation failed")

    cond = Doctor_Hospital(hospital_id=hospital.id, doctor_id=doctor.id)
    session.add(cond)
    session.commit()

    notify_role(
        session,
        UserRole.admin,
        NotificationType.doctor_registered,
        "New doctor pending verification",
        f"{doctor.name} was registered by {hospital.name} and needs verification.",
        related_id=doctor.id,
        related_type="doctor",
    )

    return {"message": f"{doctor.name} has been registered!"}


def list_doctors(
    session: Session,
    hospital_id: int | None = None,
    department: str | None = None,
    speciality: str | None = None,
    search: str | None = None,
):
    query = select(Doctors).where(Doctors.is_verified == True)
    if hospital_id is not None:
        query = query.where(Doctors.hospital_id == hospital_id)
    if department:
        query = query.where(Doctors.department == department)
    if speciality:
        query = query.where(Doctors.speciality == speciality)
    if search:
        query = query.where(Doctors.name.like(f"%{search}%"))
    return session.exec(query).all()


def list_doctors_for_own_hospital(hospital: Hospitals, session: Session):
    return session.exec(select(Doctors).where(Doctors.hospital_id == hospital.id)).all()


def get_doctor(doctor_id: int, session: Session):
    doctor = session.exec(
        select(Doctors).where(Doctors.id == doctor_id, Doctors.is_verified == True)
    ).first()
    if doctor is None:
        raise HTTPException(status_code=404, detail="Doctor not found..")
    return doctor


def verify_doctor(hospital_id: int, doctor_id: int, session: Session):
    doctor = get_doctor_admin(hospital_id, doctor_id, session)
    doctor.is_verified = True
    session.add(doctor)
    session.commit()
    session.refresh(doctor)
    create_notification(
        session,
        doctor.user_id,
        NotificationType.doctor_verified,
        "You're verified!",
        "Your identity has been verified. You can fully access mediSyncer now.",
        related_id=doctor.id,
        related_type="doctor",
    )

    notify_hospital(
        session,
        doctor.hospital_id,
        NotificationType.doctor_verified,
        "Doctor verified",
        f"Dr. {doctor.name} has been verified by admin and is now fully active.",
        related_id=doctor.id,
        related_type="doctor",
    )

    return {"message": f"{doctor.name} has been verified!"}


def create_timeslot(data: TimeSlotCreate, doctor: Doctors, session: Session):
    existing = session.exec(
        select(Timeslots).where(
            Timeslots.doctor_id == doctor.id,
            Timeslots.appointment_at == data.appointment_at,
        )
    ).first()
    if existing:
        raise HTTPException(
            status_code=400, detail="Timeslot already exists for this time"
        )

    if doctor.id is None:
        raise HTTPException(status_code=500, detail="Doctor id cant be generated")

    slot = Timeslots(
        doctor_id=doctor.id,
        hospital_id=doctor.hospital_id,
        appointment_at=data.appointment_at,
        is_available=True,
    )
    session.add(slot)
    session.commit()
    session.refresh(slot)

    return slot


def list_doctor_timeslots(
    doctor_id: int, session: Session, available_only: bool = True
):
    query = select(Timeslots).where(Timeslots.doctor_id == doctor_id)

    if available_only:
        query = query.where(Timeslots.is_available == True)
        query = query.where(Timeslots.appointment_at >= datetime.now(timezone.utc))

    query = query.order_by(Timeslots.appointment_at)
    return session.exec(query).all()


def get_my_profile(doctor: Doctors, session: Session):
    now = datetime.now(timezone.utc)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    real_patient_statuses = [AppointmentStatus.confirmed, AppointmentStatus.completed]

    total_patients = session.exec(
        select(Appointments.patient_id)
        .where(
            Appointments.doctor_id == doctor.id,
            Appointments.status.in_(real_patient_statuses),
        )
        .distinct()
    ).all()

    patients_this_month = session.exec(
        select(Appointments.patient_id)
        .where(
            Appointments.doctor_id == doctor.id,
            Appointments.status.in_(real_patient_statuses),
            Appointments.appointment_at >= month_start,
        )
        .distinct()
    ).all()

    return {
        **doctor.model_dump(),
        "patients_this_month": len(patients_this_month),
        "total_patients": len(total_patients),
        "has_security_answer": doctor.security_answer_hash is not None,
    }


def update_doctor_profile(doctor: Doctors, data: DoctorUpdate, session: Session):
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(doctor, key, value)
    session.add(doctor)
    session.commit()
    session.refresh(doctor)
    return doctor


def update_doctor_admin(
    doctor: Doctors,
    data: DoctorHospitalAdminUpdate,
    session: Session,
):
    update_data = data.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(doctor, key, value)

    session.add(doctor)
    session.commit()
    session.refresh(doctor)

    return doctor


async def update_doctor_profile_pic(
    doctor: Doctors, file: UploadFile, session: Session
):
    old_url = doctor.profile_pic_url
    image_url = await save_verification_doc(file, doctor.user_id, "profile_pics")

    doctor.profile_pic_url = image_url
    session.add(doctor)
    session.commit()
    session.refresh(doctor)
    delete_file_by_url(old_url)
    return doctor


def list_all_doctors_by_hospital(hospital_id: int, session: Session):
    hospital = session.get(Hospitals, hospital_id)
    if hospital is None:
        raise HTTPException(status_code=404, detail="Hospital not found..")
    return session.exec(select(Doctors).where(Doctors.hospital_id == hospital_id)).all()


def get_doctor_admin(hospital_id: int, doctor_id: int, session: Session):
    doctor = session.get(Doctors, doctor_id)
    if doctor is None:
        raise HTTPException(status_code=404, detail="Doctor not found..")
    if doctor.hospital_id != hospital_id:
        raise HTTPException(
            status_code=404, detail="Doctor doesn't belong to this hospital."
        )
    return doctor


def delete_doctor_admin(
    hospital_id: int,
    doctor_id: int,
    session: Session,
):
    doctor = session.get(Doctors, doctor_id)

    if doctor is None:
        raise HTTPException(
            status_code=404,
            detail="Doctor not found.",
        )

    if doctor.hospital_id != hospital_id:
        raise HTTPException(
            status_code=404,
            detail="Doctor doesn't belong to this hospital.",
        )

    appointment = session.exec(
        select(Appointments).where(Appointments.doctor_id == doctor_id)
    ).first()

    if appointment:
        raise HTTPException(
            status_code=409,
            detail=(
                "This doctor cannot be deleted because they have existing appointments."
            ),
        )

    doctor_name = doctor.name
    user_id = doctor.user_id
    timeslots = session.exec(
        select(Timeslots).where(Timeslots.doctor_id == doctor_id)
    ).all()

    for timeslot in timeslots:
        session.delete(timeslot)

    doctor_hospital = session.exec(
        select(Doctor_Hospital).where(
            Doctor_Hospital.doctor_id == doctor_id,
            Doctor_Hospital.hospital_id == hospital_id,
        )
    ).first()

    if doctor_hospital:
        session.delete(doctor_hospital)

    session.delete(doctor)
    user = session.get(Users, user_id)

    if user:
        session.delete(user)

    session.commit()
    delete_user_folder(user_id)

    return {"message": f"{doctor_name} has been deleted successfully."}


def update_doctor_security_answer(
    doctor: Doctors, user: Users, data: DoctorSecurityAnswerUpdate, session: Session
):
    if not verify_password(data.current_password, user.password_hash):
        raise HTTPException(status_code=401, detail="current password is incorrect.")

    doctor.security_answer_hash = hash_password(data.security_answer.strip().lower())
    session.add(doctor)
    session.commit()
    session.refresh(doctor)

    return {"message": "Security answer has been updated.."}
