
from pathlib import Path
import os
import jwt
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
import re
import bcrypt
import joblib
import pandas as pd
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from decimal import Decimal, ROUND_HALF_UP
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.database import Base, engine, SessionLocal
from app.models import (
    CloudProvider,
    CloudService,
    ServicePrice,
    User,
    ActivityHistory
   
)
from app.schemas import (
    CostEstimateRequest,
    StorageEstimateRequest,
    DatabaseEstimateRequest,
    RecommendationRequest,
    WorkloadForecastRequest,
    CloudShiftMigrationRequest,
      UserRegisterRequest,
      UserLoginRequest
)

from app.cloudshift_mapping import get_service_mapping
load_dotenv()

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")

if not JWT_SECRET_KEY:
    raise RuntimeError("JWT_SECRET_KEY is missing from .env")

JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
security = HTTPBearer()




# Create database tables
Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
# Verify JWT and identify the logged-in user
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credentials.credentials

    try:
        payload = jwt.decode(
            token,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM]
        )

        user_id = int(payload.get("sub"))

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"}
        )

    except (jwt.InvalidTokenError, TypeError, ValueError):
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"}
        )

    user = db.query(User).filter(
        User.id == user_id,
        User.is_active == True
    ).first()

    if not user:
        raise HTTPException(
            status_code=401,
            detail="User not found or inactive",
            headers={"WWW-Authenticate": "Bearer"}
        )

    return user
app = FastAPI(
    title="ChooseCloud API",
    description="Intelligent Multi-Cloud Cost Prediction and Recommendation System",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:1234"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)
# User Registration API
@app.post("/api/auth/register", status_code=status.HTTP_201_CREATED)
def register_user(
    request: UserRegisterRequest,
    db: Session = Depends(get_db)
):
    # Validate email format
    email = request.email.strip().lower()

    if not re.fullmatch(
        r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
        email
    ):
        raise HTTPException(
            status_code=400,
            detail="Invalid email address"
        )

    # Check whether email already exists
    existing_user = db.query(User).filter(
        User.email == email
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=409,
            detail="Email is already registered"
        )

    # Hash password using bcrypt
    password_hash = bcrypt.hashpw(
        request.password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")

    # Create new user
    new_user = User(
        name=request.name.strip(),
        email=email,
        password_hash=password_hash
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "Registration successful",
        "user": {
            "id": new_user.id,
            "name": new_user.name,
            "email": new_user.email
        }
    }

# Insert cloud providers if they do not exist
def seed_providers():
    db = SessionLocal()

    try:
        if db.query(CloudProvider).count() == 0:
            providers = [
                CloudProvider(
                    name="Amazon Web Services",
                    code="AWS",
                    description="Compute, storage and database services"
                ),
                CloudProvider(
                    name="Microsoft Azure",
                    code="AZURE",
                    description="Enterprise cloud and application hosting"
                ),
                CloudProvider(
                    name="Google Cloud",
                    code="GCP",
                    description="Cloud infrastructure and data services"
                )
            ]

            db.add_all(providers)
            db.commit()
    finally:
        db.close()


# Insert services associated with each provider
def seed_services():
    db = SessionLocal()

    service_data = [
        ("AWS", "Amazon EC2", "Compute",
         "Virtual server and computing service"),

        ("AWS", "Amazon S3", "Storage",
         "Object storage service"),

        ("AWS", "Amazon RDS", "Database",
         "Managed relational database service"),

        ("AZURE", "Azure Virtual Machines", "Compute",
         "Virtual machine computing service"),

        ("AZURE", "Azure Blob Storage", "Storage",
         "Object storage service"),

        ("AZURE", "Azure Database for PostgreSQL", "Database",
 "Managed PostgreSQL relational database service"),

        ("GCP", "Compute Engine", "Compute",
         "Virtual machine computing service"),

        ("GCP", "Cloud Storage", "Storage",
         "Object storage service"),

        ("GCP", "Cloud SQL", "Database",
         "Managed relational database service")
    ]

    try:
        for code, name, category, description in service_data:

            provider = db.query(CloudProvider).filter_by(
                code=code
            ).first()

            if provider is None:
                continue

            existing = db.query(CloudService).filter_by(
                provider_id=provider.id,
                service_name=name
            ).first()

            if existing is None:
                service = CloudService(
                    provider_id=provider.id,
                    service_name=name,
                    category=category,
                    description=description
                )

                db.add(service)

        db.commit()

    finally:
        db.close()


seed_providers()
seed_services()


@app.get("/api/health")
def home():
    return {
        "message": "Welcome to ChooseCloud API",
        "status": "Running"
    }


# Return complete provider information from database
@app.get("/api/providers")
def get_providers(db: Session = Depends(get_db)):

    providers = db.query(CloudProvider).all()

    return {
        "providers": [
            {
                "id": provider.id,
                "name": provider.name,
                "code": provider.code,
                "description": provider.description
            }
            for provider in providers
        ]
    }


# Return cloud services with their provider details
@app.get("/api/services")
def get_services(db: Session = Depends(get_db)):

    results = (
        db.query(CloudService, CloudProvider)
        .join(
            CloudProvider,
            CloudService.provider_id == CloudProvider.id
        )
        .all()
    )

    return {
        "services": [
            {
                "id": service.id,
                "service_name": service.service_name,
                "category": service.category,
                "description": service.description,
                "provider_name": provider.name,
                "provider_code": provider.code
            }
            for service, provider in results
        ]
    }

# View all available pricing records
@app.get("/api/prices")
def get_prices(db: Session = Depends(get_db)):

    results = (
        db.query(ServicePrice, CloudService, CloudProvider)
        .join(
            CloudService,
            ServicePrice.service_id == CloudService.id
        )
        .join(
            CloudProvider,
            CloudService.provider_id == CloudProvider.id
        )
        .filter(ServicePrice.is_active == True)
        .all()
    )

    return {
        "prices": [
            {
                "price_id": price.id,
                "provider": provider.code,
                "service": service.service_name,
                "category": service.category,
                "region": price.region,
                "configuration": price.configuration,
                "billing_unit": price.billing_unit,
                "unit_price": float(price.unit_price),
                "currency": price.currency,
                "exchange_rate_to_inr": float(
                    price.exchange_rate_to_inr
                ),
                "source_url": price.source_url,
                "verified_at": price.verified_at.isoformat()
            }
            for price, service, provider in results
        ]
    }


# Calculate estimated cost in INR
@app.post("/api/cost/estimate")
def estimate_cost(
    request: CostEstimateRequest,
    db: Session = Depends(get_db)
):

    price = db.query(ServicePrice).filter(
        ServicePrice.id == request.price_id,
        ServicePrice.is_active == True
    ).first()

    if price is None:
        raise HTTPException(
            status_code=404,
            detail="Active pricing record not found."
        )

    original_cost = (
        price.unit_price * request.usage_quantity
    )

    total_inr = (
        original_cost * price.exchange_rate_to_inr
    )

    return {
        "price_id": price.id,
        "usage_quantity": float(request.usage_quantity),
        "billing_unit": price.billing_unit,
        "original_currency": price.currency,
        "original_cost": round(float(original_cost), 4),
        "exchange_rate_to_inr": float(
            price.exchange_rate_to_inr
        ),
        "estimated_cost_inr": round(float(total_inr), 2),
        "region": price.region,
        "source_url": price.source_url,
        "verified_at": price.verified_at.isoformat()
    }

@app.post("/api/storage/estimate")
def estimate_storage_cost(
    request: StorageEstimateRequest,
    db: Session = Depends(get_db)
):
    storage_prices = (
        db.query(ServicePrice, CloudService, CloudProvider)
        .join(
            CloudService,
            ServicePrice.service_id == CloudService.id
        )
        .join(
            CloudProvider,
            CloudService.provider_id == CloudProvider.id
        )
        .filter(
            CloudService.category == "Storage",
            ServicePrice.is_active.is_(True)
        )
        .all()
    )

    if not storage_prices:
        raise HTTPException(
            status_code=404,
            detail="No storage pricing records found"
        )

    results = []

    for price, service, provider in storage_prices:
        original_cost = price.unit_price * request.storage_gb

        total_inr = (
            original_cost * price.exchange_rate_to_inr
        ).quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP
        )

        results.append({
            "provider": provider.name,
            "service": service.service_name,
            "configuration": price.configuration,
            "region": price.region,
            "storage_gb": request.storage_gb,
            "billing_unit": price.billing_unit,
            "price_per_gb_month": price.unit_price,
            "currency": price.currency,
            "estimated_cost_usd": original_cost,
            "estimated_cost_inr": total_inr,
            "source_url": price.source_url
        })

    return {
        "storage_type": "Standard / Hot storage",
        "billing_period": "Monthly",
        "results": results
    }


@app.post("/api/database/estimate")
def estimate_database_cost(
    request: DatabaseEstimateRequest,
    db: Session = Depends(get_db)
):
    database_prices = (
        db.query(ServicePrice, CloudService, CloudProvider)
        .join(
            CloudService,
            ServicePrice.service_id == CloudService.id
        )
        .join(
            CloudProvider,
            CloudService.provider_id == CloudProvider.id
        )
        .filter(
            CloudService.category == "Database",
            ServicePrice.is_active.is_(True)
        )
        .all()
    )

    if not database_prices:
        raise HTTPException(
            status_code=404,
            detail="No database pricing records found"
        )

    provider_data = {}

    for price, service, provider in database_prices:
        if provider.id not in provider_data:
            provider_data[provider.id] = {
                "provider": provider.name,
                "service": service.service_name,
                "compute": None,
                "storage": None
            }

        if price.billing_unit == "1 Hour":
            provider_data[provider.id]["compute"] = price

        elif price.billing_unit == "1 GB/Month":
            provider_data[provider.id]["storage"] = price

    results = []

    for data in provider_data.values():
        compute = data["compute"]
        storage = data["storage"]

        if compute is None or storage is None:
            continue

        compute_cost = compute.unit_price * request.usage_hours
        storage_cost = storage.unit_price * request.storage_gb

        compute_inr = (
            compute_cost * compute.exchange_rate_to_inr
        )

        storage_inr = (
            storage_cost * storage.exchange_rate_to_inr
        )

        total_inr = (compute_inr + storage_inr).quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP
        )

        results.append({
            "provider": data["provider"],
            "service": data["service"],
            "region": compute.region,
            "compute_configuration": compute.configuration,
            "storage_configuration": storage.configuration,
            "usage_hours": float(request.usage_hours),
            "storage_gb": float(request.storage_gb),
            "compute_cost_usd": round(float(compute_cost), 4),
            "storage_cost_usd": round(float(storage_cost), 4),
            "total_cost_usd": round(
                float(compute_cost + storage_cost), 4
            ),
            "compute_cost_inr": round(float(compute_inr), 2),
            "storage_cost_inr": round(float(storage_inr), 2),
            "estimated_cost_inr": float(total_inr),
            "compute_source_url": compute.source_url,
            "storage_source_url": storage.source_url
        })

    if not results:
        raise HTTPException(
            status_code=404,
            detail="Complete compute and storage pricing not available"
        )

    results.sort(key=lambda item: item["estimated_cost_inr"])

    return {
        "database_type": "PostgreSQL",
        "billing_period": "Monthly",
        "exchange_rate": "Stored exchange rates are applied",
        "cheapest_provider": results[0]["provider"],
        "lowest_estimated_cost_inr": results[0]["estimated_cost_inr"],
        "results": results
    }
@app.post("/api/recommend")
def recommend_cloud_provider(
    request: RecommendationRequest,
    db: Session = Depends(get_db)
):
    compute_hours = request.compute_hours
    storage_gb = request.storage_gb
    database_hours = request.database_hours
    database_storage_gb = request.database_storage_gb

    compute_prices = (
        db.query(ServicePrice, CloudService, CloudProvider)
        .join(CloudService, ServicePrice.service_id == CloudService.id)
        .join(CloudProvider, CloudService.provider_id == CloudProvider.id)
        .filter(
            CloudService.category == "Compute",
            ServicePrice.is_active.is_(True),
            ServicePrice.billing_unit == "1 Hour"
        )
        .all()
    )

    storage_prices = (
        db.query(ServicePrice, CloudService, CloudProvider)
        .join(CloudService, ServicePrice.service_id == CloudService.id)
        .join(CloudProvider, CloudService.provider_id == CloudProvider.id)
        .filter(
            CloudService.category == "Storage",
            ServicePrice.is_active.is_(True),
            ServicePrice.billing_unit == "1 GB/Month"
        )
        .all()
    )

    database_prices = (
        db.query(ServicePrice, CloudService, CloudProvider)
        .join(CloudService, ServicePrice.service_id == CloudService.id)
        .join(CloudProvider, CloudService.provider_id == CloudProvider.id)
        .filter(
            CloudService.category == "Database",
            ServicePrice.is_active.is_(True)
        )
        .all()
    )

    results = []

    for provider in db.query(CloudProvider).all():
        compute = next(
            (p for p, s, pr in compute_prices if pr.id == provider.id),
            None
        )

        storage = next(
            (p for p, s, pr in storage_prices if pr.id == provider.id),
            None
        )

        database_compute = next(
            (p for p, s, pr in database_prices
             if pr.id == provider.id and p.billing_unit == "1 Hour"),
            None
        )

        database_storage = next(
            (p for p, s, pr in database_prices
             if pr.id == provider.id and p.billing_unit == "1 GB/Month"),
            None
        )

        if not all([
            compute,
            storage,
            database_compute,
            database_storage
        ]):
            continue

        compute_cost = (
            compute.unit_price * compute_hours
            * compute.exchange_rate_to_inr
        )

        storage_cost = (
            storage.unit_price * storage_gb
            * storage.exchange_rate_to_inr
        )

        database_compute_cost = (
            database_compute.unit_price * database_hours
            * database_compute.exchange_rate_to_inr
        )

        database_storage_cost = (
            database_storage.unit_price * database_storage_gb
            * database_storage.exchange_rate_to_inr
        )

        total_cost = (
            compute_cost
            + storage_cost
            + database_compute_cost
            + database_storage_cost
        ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        results.append({
            "provider": provider.name,
            "compute_cost_inr": round(float(compute_cost), 2),
            "storage_cost_inr": round(float(storage_cost), 2),
            "database_compute_cost_inr": round(
                float(database_compute_cost), 2
            ),
            "database_storage_cost_inr": round(
                float(database_storage_cost), 2
            ),
            "total_estimated_cost_inr": float(total_cost)
        })

    if not results:
        raise HTTPException(
            status_code=404,
            detail="Complete pricing data is not available for comparison."
        )

    results.sort(
        key=lambda item: item["total_estimated_cost_inr"]
    )

    return {
        "recommendation_type": "Rule-based cost recommendation",
        "recommended_provider": results[0]["provider"],
        "estimated_total_cost_inr": results[0]["total_estimated_cost_inr"],
        "results": results
    }

@app.post("/api/cloudshift/analyze")
def analyze_cloud_migration(
    request: CloudShiftMigrationRequest,
    db: Session = Depends(get_db)
):
    source_provider = db.query(CloudProvider).filter(
        CloudProvider.name == request.source_provider
    ).first()

    target_provider = db.query(CloudProvider).filter(
        CloudProvider.name == request.target_provider
    ).first()

    if not source_provider or not target_provider:
        raise HTTPException(
            status_code=404,
            detail="Source or target cloud provider was not found."
        )

    if source_provider.id == target_provider.id:
        raise HTTPException(
            status_code=400,
            detail="Source and target providers must be different."
        )

    def find_priced_service(
        provider_name,
        category,
        required_units,
        allowed_names=None
    ):
        services = (
            db.query(CloudService)
            .join(
                CloudProvider,
                CloudService.provider_id == CloudProvider.id
            )
            .filter(
                CloudProvider.name == provider_name,
                CloudService.category == category
            )
            .order_by(CloudService.id)
            .all()
        )

        for service in services:

            if (
                allowed_names is not None
                and service.service_name not in allowed_names
            ):
                continue

            prices = {}

            for unit in required_units:
                price = (
                    db.query(ServicePrice)
                    .filter(
                        ServicePrice.service_id == service.id,
                        ServicePrice.billing_unit == unit,
                        ServicePrice.is_active.is_(True)
                    )
                    .first()
                )

                if not price:
                    break

                prices[unit] = price

            if len(prices) == len(required_units):
                return service, prices

        return None, None

    category_requirements = [
        {
            "category": "Compute",
            "quantities": {
                "1 Hour": request.compute_hours
            }
        },
        {
            "category": "Storage",
            "quantities": {
                "1 GB/Month": request.storage_gb
            }
        },
        {
            "category": "Database",
            "quantities": {
                "1 Hour": request.database_hours,
                "1 GB/Month": request.database_storage_gb
            }
        }
    ]

    source_total = Decimal("0")
    target_total = Decimal("0")
    breakdown = []

    for requirement in category_requirements:

        category = requirement["category"]
        quantities = requirement["quantities"]
        required_units = list(quantities.keys())

        source_service, source_prices = find_priced_service(
            source_provider.name,
            category,
            required_units
        )

        if not source_service:
            raise HTTPException(
                status_code=404,
                detail=(
                    f"Complete active source pricing is unavailable "
                    f"for {source_provider.name} - {category}."
                )
            )

        mapping = get_service_mapping(
            source_service.service_name,
            target_provider.name
        )

        if not mapping:
            raise HTTPException(
                status_code=404,
                detail=(
                    f"No service mapping is available for "
                    f"{source_service.service_name}."
                )
            )

        candidate_names = [
            item["service"]
            for item in mapping["target_services"]
        ]

        target_service, target_prices = find_priced_service(
            target_provider.name,
            category,
            required_units,
            candidate_names
        )

        if not target_service:
            raise HTTPException(
                status_code=404,
                detail=(
                    f"No mapped target service with complete active "
                    f"pricing is available for {category} in "
                    f"{target_provider.name}."
                )
            )

        source_category_cost = Decimal("0")
        target_category_cost = Decimal("0")

        price_details = {}

        for unit, quantity in quantities.items():

            source_price = source_prices[unit]
            target_price = target_prices[unit]

            source_cost = (
                source_price.unit_price
                * quantity
                * source_price.exchange_rate_to_inr
            )

            target_cost = (
                target_price.unit_price
                * quantity
                * target_price.exchange_rate_to_inr
            )

            source_category_cost += source_cost
            target_category_cost += target_cost

            price_details[unit] = {
                "quantity": float(quantity),
                "source_unit_price": float(source_price.unit_price),
                "target_unit_price": float(target_price.unit_price)
            }

        source_category_cost = source_category_cost.quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP
        )

        target_category_cost = target_category_cost.quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP
        )

        source_total += source_category_cost
        target_total += target_category_cost

        mapping_item = next(
            (
                item
                for item in mapping["target_services"]
                if item["service"] == target_service.service_name
            ),
            {}
        )

        breakdown.append({
            "category": category,
            "source_service": source_service.service_name,
            "target_service": target_service.service_name,
            "mapping_reason": mapping_item.get("reason"),
            "source_configuration": [
                source_prices[unit].configuration
                for unit in required_units
            ],
            "target_configuration": [
                target_prices[unit].configuration
                for unit in required_units
            ],
            "source_monthly_cost_inr": float(source_category_cost),
            "target_monthly_cost_inr": float(target_category_cost),
            "price_details": price_details
        })

    source_total = source_total.quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP
    )

    target_total = target_total.quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP
    )

    savings = source_total - target_total

    if source_total > 0:
        savings_percentage = (
            savings / source_total * Decimal("100")
        ).quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP
        )
    else:
        savings_percentage = Decimal("0")

    if savings > 0:
        recommendation = "Potential monthly cost saving"
    elif savings < 0:
        recommendation = "Migration may increase monthly cost"
    else:
        recommendation = "No estimated monthly cost difference"

    return {
        "feature": "CloudShift",
        "analysis_type": "Rule-based migration cost analysis",
        "source_provider": source_provider.name,
        "target_provider": target_provider.name,
        "source_monthly_cost_inr": float(source_total),
        "target_monthly_cost_inr": float(target_total),
        "estimated_monthly_savings_inr": float(savings),
        "estimated_savings_percentage": float(savings_percentage),
        "recommendation": recommendation,
        "migration_costs_included": False,
        "service_mappings": breakdown,"migration_costs_included": False,
"service_mappings": breakdown,
"migration_readiness_checks": [
    {
        "title": "Database compatibility",
        "description": "Verify database engine, version, extensions and schema compatibility."
    },
    {
        "title": "Compute compatibility",
        "description": "Verify operating system, CPU architecture, memory and runtime requirements."
    },
    {
        "title": "Storage compatibility",
        "description": "Review storage formats, access methods, permissions and replication requirements."
    },
    {
        "title": "Network and security",
        "description": "Review network connectivity, firewall rules, identity and access permissions."
    },
    {
        "title": "Data transfer and downtime",
        "description": "Estimate data transfer volume, transfer duration and acceptable downtime."
    },
    {
        "title": "Backup and rollback",
        "description": "Prepare backups, migration testing and a rollback strategy."
    }
],

        "notice": (
            "These are indicative monthly infrastructure estimates "
            "based on stored pricing records. One-time migration, "
            "data transfer, downtime, licensing and operational costs "
            "are excluded. Service mappings do not guarantee "
            "technical compatibility. Review configurations and "
            "database engines before migration."
        )
    }

@app.post("/api/workload/forecast")
def forecast_workload(request: WorkloadForecastRequest):
    """
    Forecast aggregated data-centre CPU and memory usage
    for 5, 10 or 15 minutes ahead.
    """

    if request.horizon_minutes not in [5, 10, 15]:
        raise HTTPException(
            status_code=422,
            detail="horizon_minutes must be 5, 10 or 15."
        )

    # Locate the trained model
    model_path = (
        Path(__file__).resolve().parent.parent
        / "ml"
        / "saved_model"
        / f"linear_regression_{request.horizon_minutes}min.joblib"
    )

    if not model_path.exists():
        raise HTTPException(
            status_code=503,
            detail="The requested workload forecasting model is unavailable."
        )

    try:
        observations = request.observations

        feature_columns = [
            "avg_cpu",
            "avg_mem",
            "avg_assigned_mem",
            "avg_cycles_per_instruction"
        ]

        lag_values = [0, 1, 2, 3, 6, 12]

        feature_names = []
        feature_values = []

        # Construct the same 24 features used during training
        for column in feature_columns:
            for lag in lag_values:
                feature_names.append(f"{column}_lag_{lag}")

                observation = observations[-1 - lag]
                feature_values.append(
                    getattr(observation, column)
                )

        input_data = pd.DataFrame(
            [feature_values],
            columns=feature_names
        )

        # Load the correct saved model
        model = joblib.load(model_path)

        # Generate predictions
        predictions = model.predict(input_data)

        predicted_cpu = float(predictions[0][0])
        predicted_memory = float(predictions[0][1])

        return {
            "forecast_horizon_minutes": request.horizon_minutes,
            "predicted_avg_cpu": round(predicted_cpu, 6),
            "predicted_avg_cpu_percentage": round(
                predicted_cpu * 100, 2
            ),
            "predicted_avg_memory": round(predicted_memory, 6),
            "predicted_avg_memory_percentage": round(
                predicted_memory * 100, 2
            ),
            "scope": "Aggregated data-centre workload forecast",
            "model": f"Linear Regression ({request.horizon_minutes} min)",
            "data_source": "Bundled aggregated workload dataset"
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Workload forecasting failed: {str(error)}"
        )


@app.get("/api/workload/latest-observations")
def get_latest_workload_observations():
    """Return the latest 13 aggregated workload observations."""

    dataset_path = (
        Path(__file__).resolve().parent.parent
        / "ml"
        / "dataset"
        / "instance_usage_grouped_300_seconds_month.csv"
    )

    if not dataset_path.exists():
        raise HTTPException(
            status_code=503,
            detail="Workload dataset is unavailable."
        )

    try:
        df = pd.read_csv(dataset_path)

        columns = [
            "avg_cpu",
            "avg_mem",
            "avg_assigned_mem",
            "avg_cycles_per_instruction"
        ]

        if not all(column in df.columns for column in columns):
            raise ValueError("Required dataset columns are missing.")

        observations = (
            df[columns]
            .tail(13)
            .to_dict(orient="records")
        )

        if len(observations) != 13:
            raise ValueError("At least 13 observations are required.")

        return {
            "observations": observations,
            "observation_count": len(observations),
            "data_source": "Bundled aggregated workload dataset"
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to load workload observations: {str(error)}"
        )
# Generate JWT access token
def create_access_token(user_id: int):
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": str(user_id),
        "exp": expire
    }

    return jwt.encode(
        payload,
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM
    )


# User Login API
@app.post("/api/auth/login")
def login_user(
    request: UserLoginRequest,
    db: Session = Depends(get_db)
):
    email = request.email.strip().lower()

    # Find registered user
    user = db.query(User).filter(
        User.email == email
    ).first()

    if not user or not user.is_active:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    # Verify password against stored bcrypt hash
    password_valid = bcrypt.checkpw(
        request.password.encode("utf-8"),
        user.password_hash.encode("utf-8")
    )

    if not password_valid:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    # Generate JWT
    access_token = create_access_token(user.id)

    return {
        "message": "Login successful",
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email
        }
    }
@app.get("/api/auth/me")
def get_logged_in_user(
    current_user: User = Depends(get_current_user)
):
    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email
    }
# Get currently authenticated user
@app.get("/api/auth/me")
def get_logged_in_user(
    current_user: User = Depends(get_current_user)
):
    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email
    }
# Serve React frontend
STATIC_DIR = Path(__file__).resolve().parent.parent / "static"

app.mount(
    "/",
    StaticFiles(directory=STATIC_DIR, html=True),
    name="frontend"
)