from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from models import Patient, Diagnosis
from schemas import DiagnosisCreate, PatientCreate
from utils import get_record, create_log


class PatientService:
    @staticmethod
    async def register_diagnosis(
        provider_id: int, diagnosis_data: DiagnosisCreate, db: AsyncSession
    ) -> dict:
        user = await get_record(db, Patient, patient_id=diagnosis_data.patient_id)
        if not user:
            raise HTTPException(status_code=400, detail="Patient not found")

        new_diagnosis = Diagnosis(
            provider_id=provider_id,
            patient_id=diagnosis_data.patient_id,
            prediction=diagnosis_data.prediction,
        )

        db.add(new_diagnosis)
        await db.commit()
        await db.refresh(new_diagnosis)

        await create_log(
            action=f"Registered Diagnosis for {user.patient_name}",
            provider_id=provider_id,
            db=db,
        )
        return {"message": "Diagnosis registered successfully"}

    @staticmethod
    async def register_patient_service(
        patient_data: PatientCreate, db: AsyncSession, provider_id: int
    ):
        existing_user = await get_record(
            db, Patient, patient_email=patient_data.patient_email
        )
        if existing_user:
            raise HTTPException(
                status_code=400, detail="Patient Email already registered"
            )

        new_patient = Patient(
            provider_id=provider_id,
            patient_name=patient_data.patient_name,
            patient_age=patient_data.patient_age,
            patient_gender=patient_data.patient_gender,
            patient_email=patient_data.patient_email,
            patient_notes=patient_data.patient_notes,
        )

        db.add(new_patient)
        await db.commit()
        await db.refresh(new_patient)

        await create_log(
            action=f"Registered Patient: {patient_data.patient_name}",
            provider_id=provider_id,
            db=db,
        )
        return {"message": "Successful", "patient_id": new_patient.patient_id}
