#### app/routes/route.py

from fastapi import APIRouter, Depends, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from schemas import (
    ProviderCreate,
    ProviderLogin,
    MessageResponse,
    PatientCreate,
    LoginToken,
    ProviderDashboardStats,
    PatientData,
    LogData,
    ChartAnalytics,
    DiagnosisCreate,
    ChangePasswordSchema,
    Response
)
from utils import get_current_provider
from database import get_db
from typing import List

from services.detect_services import detect_service
from services.auth_service import AuthenticationService
from services.stats_service import DashboardService
from services.patient_service import PatientService


router = APIRouter()


# **Status Check**
@router.get("/home")
async def home():
    return {"Message": "Live"}

# ======================
## Authentication Service
# ======================


# **Signup Route**
@router.post("/signup", response_model=Response)
async def signup(provider: ProviderCreate, db: AsyncSession = Depends(get_db)):
    return await AuthenticationService.signup(provider, db)


# **Login Route**
@router.post("/login", response_model=LoginToken)
async def login(provider: ProviderLogin, db: AsyncSession = Depends(get_db)):
    return await AuthenticationService.login(provider, db)


# **Change Password Route**
@router.put("/change-password")
async def change_password(
    password_data: ChangePasswordSchema, db: AsyncSession = Depends(get_db)
):
    return await AuthenticationService.change_password(password_data, db)


# **Logout Route**
@router.post("/logout")
async def logout(
    provider_id: int = Depends(get_current_provider), db: AsyncSession = Depends(get_db)
):
    return await AuthenticationService.logout(provider_id, db)


# **Detect Route**
@router.post("/detect")
async def detect(file: UploadFile, provider_id: int = Depends(get_current_provider)):
    return await detect_service(file, provider_id)


# ======================
## Patient Service
# ======================


# **Register Patient Data Route**
@router.post("/patients")
async def register_patient(
    patient_data: PatientCreate,
    db: AsyncSession = Depends(get_db),
    provider_id: int = Depends(get_current_provider),
):
    return await PatientService.register_patient_service(patient_data, db, provider_id)


# **Register Result Data Route**
@router.post("/results")
async def diagnosis_route(
    diagnosis_data: DiagnosisCreate,
    provider_id: int = Depends(get_current_provider),
    db: AsyncSession = Depends(get_db),
):
    return await PatientService.register_diagnosis(provider_id, diagnosis_data, db)


# ======================
## Dashboard Service
# ======================


# **Get Dashbaord Data Route**
@router.get("/dashboard", response_model=ProviderDashboardStats)
async def dashboard_data(
    db: AsyncSession = Depends(get_db), provider_id: int = Depends(get_current_provider)
):
    return await DashboardService.get_dashboard_data(provider_id, db)


# **Get Patient Data**
@router.get("/patients_data", response_model=List[PatientData])
async def patients_data(
    db: AsyncSession = Depends(get_db), provider_id: int = Depends(get_current_provider)
):
    return await DashboardService.get_patients_data(provider_id, db)


# **Get Chart Data**
@router.get("/chart_data", response_model=ChartAnalytics)
async def chart_data(
    db: AsyncSession = Depends(get_db), provider_id: int = Depends(get_current_provider)
):
    return await DashboardService.get_chart_data(provider_id, db)


# **Get Log Data**
@router.get("/provider_log", response_model=List[LogData])
async def provider_log(
    db: AsyncSession = Depends(get_db), provider_id: int = Depends(get_current_provider)
):
    return await DashboardService.get_provider_log(provider_id, db)
