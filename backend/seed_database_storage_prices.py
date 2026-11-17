
from decimal import Decimal

from app.database import SessionLocal
from app.models import ServicePrice, CloudService

EXCHANGE_RATE = Decimal("94.1997")

database_storage_prices = [
    {
        "service_id": 3,
        "region": "Asia Pacific (Mumbai) - ap-south-1",
        "configuration": "General Purpose SSD gp3 | 20 GB",
        "storage_gb": Decimal("20"),
        "unit_price": Decimal("0.131000"),
        "source_url": "https://calculator.aws/",
    },
    {
        "service_id": 6,
        "region": "Central India - centralindia",
        "configuration": "Premium SSD | 8 GiB",
        "storage_gb": Decimal("8"),
        "unit_price": Decimal("0.131000"),
        "source_url": "https://azure.microsoft.com/en-in/pricing/calculator/",
    },
    {
        "service_id": 9,
        "region": "Mumbai - asia-south1",
        "configuration": "SSD provisioned storage | 10 GiB input (calculator displayed 11 GiB)",
        "storage_gb": Decimal("11"),
        "unit_price": Decimal("0.203636"),
        "source_url": "https://cloud.google.com/products/calculator",
    },
]

db = SessionLocal()

try:
    for item in database_storage_prices:
        service = db.query(CloudService).filter(
            CloudService.id == item["service_id"],
            CloudService.category == "Database"
        ).first()

        if not service:
            raise ValueError(f"Database service ID {item['service_id']} not found")

        existing = db.query(ServicePrice).filter(
            ServicePrice.service_id == item["service_id"],
            ServicePrice.billing_unit == "1 GB/Month",
            ServicePrice.is_active == True
        ).first()

        if existing:
            print(f"Skipped: {service.service_name} already has an active storage price")
            continue

        price = ServicePrice(
            service_id=item["service_id"],
            region=item["region"],
            configuration=item["configuration"],
            billing_unit="1 GB/Month",
            unit_price=item["unit_price"],
            currency="USD",
            exchange_rate_to_inr=EXCHANGE_RATE,
            source_url=item["source_url"],
            is_active=True,
        )

        db.add(price)
        print(
            f"Prepared: {service.service_name} - "
            f"${item['unit_price']}/GB/month"
        )

    db.commit()
    print("\nDatabase storage prices inserted successfully!")

except Exception:
    db.rollback()
    raise

finally:
    db.close()
