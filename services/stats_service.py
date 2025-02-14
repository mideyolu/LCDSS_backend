from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from models import Patient, Diagnosis, Log
from utils import get_count
from typing import List
from schemas import ProviderDashboardStats, PatientData, ChartAnalytics, LogData

class DashboardService:
    @staticmethod
    async def get_dashboard_data(provider_id: int, db: AsyncSession)-> dict:
        total_patients = await get_count(db, Patient, provider_id=provider_id)

        counts = {
            prediction: await get_count(db, Diagnosis, provider_id=provider_id, prediction=prediction)
            for prediction in ["Benign cases", "Malignant cases", "Normal cases"]
        }

        return ProviderDashboardStats(
            total_patients=total_patients,
            benign_cases=counts["Benign cases"],
            malignant_cases=counts["Malignant cases"],
            normal_cases=counts["Normal cases"],
        )

    @staticmethod
    async def get_patients_data(provider_id: int, db: AsyncSession)-> List[PatientData]:
        query = (
            select(
                Patient.patient_name,
                Patient.patient_age,
                Patient.patient_gender,
                Patient.patient_email,
                Patient.patient_notes,
                Diagnosis.prediction
            )
            .join(Diagnosis, Patient.patient_id == Diagnosis.patient_id)
            .where(Patient.provider_id == provider_id)
        )
        results = await db.execute(query)
        patient_data = results.fetchall()

        return [
            PatientData(
                patient_name=row.patient_name,
                patient_age=row.patient_age,
                patient_gender=row.patient_gender,
                patient_email=row.patient_email,
                patient_notes=row.patient_notes,
                prediction=row.prediction,
            )
            for row in patient_data
        ]

    @staticmethod
    async def get_chart_data(provider_id: int, db: AsyncSession)-> ChartAnalytics:
        genders = ["Male", "Female"]
        gender_counts = {gender: await get_count(db, Patient, provider_id=provider_id, patient_gender=gender) for gender in genders}

        diagnosis_counts = {
            prediction: await get_count(db, Diagnosis, provider_id=provider_id, prediction=prediction)
            for prediction in ["Normal cases", "Benign cases", "Malignant cases"]
        }

        return ChartAnalytics(
            total_male=gender_counts["Male"],
            total_female=gender_counts["Female"],
            total_normal=diagnosis_counts["Normal cases"],
            total_benign=diagnosis_counts["Benign cases"],
            total_malignant=diagnosis_counts["Malignant cases"]
        )

    @staticmethod
    async def get_provider_log(provider_id: int, db: AsyncSession)-> List[LogData]:
        query_log = (
            select(Log.action, Log.created_at)
            .where(Log.provider_id == provider_id)
            .order_by(Log.created_at.desc())
            .limit(5)
        )
        log_details = await db.execute(query_log)
        logs = log_details.fetchall()

        return [
            LogData(total_log=5, action=log.action, created_at=log.created_at) if logs else LogData(total_log=5, action="No logs available", created_at=None)
            for log in logs
        ]
