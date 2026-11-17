
from decimal import Decimal
from pydantic import BaseModel, Field
from typing import List

class CostEstimateRequest(BaseModel):
    price_id: int = Field(gt=0)
    usage_quantity: Decimal = Field(gt=0)


class StorageEstimateRequest(BaseModel):
    storage_gb: Decimal = Field(gt=0)


class DatabaseEstimateRequest(BaseModel):
    usage_hours: Decimal = Field(gt=0, le=744)
    storage_gb: Decimal = Field(gt=0)
class RecommendationRequest(BaseModel):
    compute_hours: Decimal = Field(gt=0, le=744)
    storage_gb: Decimal = Field(gt=0)
    database_hours: Decimal = Field(gt=0, le=744)
    database_storage_gb: Decimal = Field(gt=0)
class WorkloadObservation(BaseModel):
    avg_cpu: float = Field(ge=0, le=1)
    avg_mem: float = Field(ge=0, le=1)
    avg_assigned_mem: float = Field(ge=0, le=1)
    avg_cycles_per_instruction: float = Field(gt=0)


class WorkloadForecastRequest(BaseModel):
    observations: List[WorkloadObservation] = Field(
        min_length=13,
        max_length=13
    )
    horizon_minutes: int = Field(
        default=5,
        description="Forecast horizon: 5, 10 or 15 minutes"
    )

class CloudShiftMigrationRequest(BaseModel):
    source_provider: str = Field(min_length=1)
    target_provider: str = Field(min_length=1)

    compute_hours: Decimal = Field(gt=0, le=744)
    storage_gb: Decimal = Field(gt=0)

    database_hours: Decimal = Field(gt=0, le=744)
    database_storage_gb: Decimal = Field(gt=0)
    
class UserRegisterRequest(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: str = Field(min_length=5, max_length=255)
    password: str = Field(min_length=8, max_length=72)


class UserLoginRequest(BaseModel):
    email: str = Field(min_length=5, max_length=255)
    password: str = Field(min_length=1, max_length=72)