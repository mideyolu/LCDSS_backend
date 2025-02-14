from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class Provider(SQLModel, table=True):
    provider_id: Optional[int] = Field(default=None, primary_key=True)
    provider_username: str
    provider_email: str
    provider_password: str

class Patient(SQLModel, table=True):
    patient_id: Optional[int] = Field(default=None, primary_key=True)
    provider_id: int = Field(foreign_key="provider.provider_id")
    patient_name: str
    patient_age: int
    patient_gender: str
    patient_email: str
    patient_notes: Optional[str]

class Diagnosis(SQLModel, table=True):
    diagnosis_id: Optional[int] = Field(default=None, primary_key=True)
    provider_id: int = Field(foreign_key="provider.provider_id")
    patient_id: int = Field(foreign_key="patient.patient_id")
    prediction: str

class Log(SQLModel, table=True):
    log_id: Optional[int] = Field(default=None, primary_key=True)
    action: str
    created_at: datetime
    provider_id: int = Field(foreign_key="provider.provider_id")
