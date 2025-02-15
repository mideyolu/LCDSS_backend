#### app/schemas.py
from pydantic import BaseModel, EmailStr
from datetime import datetime

class ProviderCreate(BaseModel):
    provider_username: str
    provider_email: EmailStr
    provider_password: str

class ProviderLogin(BaseModel):
    provider_email: EmailStr
    provider_password: str

class Response(BaseModel):
    message: str

class MessageResponse(BaseModel):
    message: str

class LoginToken(BaseModel):
    access_token: str
    token_type: str
    provider_id: int
    provider_username: str
    provider_email: str

# Schema for creating a new Patient (receiving data from the frontend)
class PatientCreate(BaseModel):
    patient_name: str
    patient_age: int
    patient_gender: str
    patient_email: str
    patient_notes: str

# Schema for creating a new Diagnosis (for prediction results)
class DiagnosisCreate(BaseModel):
    provider_id: int
    patient_id: int
    prediction: str

# Schema for getting dashbaord data (Patient categories)
class ProviderDashboardStats(BaseModel):
    total_patients: int
    benign_cases: int
    malignant_cases: int
    normal_cases: int

# Schema for getting chart data (Patient data)
class ChartAnalytics(BaseModel):
    total_male: int
    total_female: int
    total_normal: int
    total_benign: int
    total_malignant: int

# Schema for getting Patient data (Patient Data)
class PatientData(BaseModel):
    patient_name: str
    patient_age : int
    patient_gender: str
    patient_email: EmailStr
    patient_notes: str
    prediction: str

# Schema for getting Log data (Provider, Patient Data)
class LogData(BaseModel):
    total_log : int
    action: str
    created_at: datetime


class ChangePasswordSchema(BaseModel):
    email: EmailStr
    new_password: str
