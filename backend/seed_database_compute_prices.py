
from decimal import Decimal, ROUND_HALF_UP

from app.database import SessionLocal
from app.models import ServicePrice, CloudService

EXCHANGE_RATE = Decimal("94.1997")

database_prices = [
    {
        "service_id": 3,
        "region": "Asia Pacific (Mumbai) - ap-south-1",
        "configuration": "db.t3.large | 2 vCPU | 8 GiB | On-Demand | Single-AZ",
        "unit_price": Decimal("0.212000"),
        "source_url": "https://calculator.aws/",
    },
    {
        "service_id": 6,
        "region": "Central India - centralindia",
        "configuration": "B2ms | 2 vCores | 8 GiB | Burstable | Single Server",
        "unit_price": Decimal("0.196000"),
        "source_url": "https://azure.microsoft.com/en-in/pricing/calculator/",
    },
    {
        "service_id": 9,
        "region": "Mumbai - asia-south1",
        "configuration": "db-standard-2 | 2 vCPU | 7.5 GiB | Enterprise | Single Zone",
        "unit_price": Decimal("0.162205"),
        "source_url": "https://cloud.google.com/products/calculator",
    },
]

db = SessionLocal()

try:
    for item in database_prices:
        service = db.query(CloudService).filter(
            CloudService.id == item["service_id"],
            CloudService.category == "Database"
        ).first()

        if not service:
            raise ValueError(
                f"Database service ID {item['service_id']} not found"
            )

        existing = db.query(ServicePrice).filter(
            ServicePrice.service_id == item["service_id"],
            ServicePrice.billing_unit == "1 Hour",
            ServicePrice.is_active == True
        ).first()

        if existing:
            print(f"Skipped: {service.service_name} already has an active hourly price")
            continue

        price = ServicePrice(
            service_id=item["service_id"],
            region=item["region"],
            configuration=item["configuration"],
            billing_unit="1 Hour",
            unit_price=item["unit_price"],
            currency="USD",
            exchange_rate_to_inr=EXCHANGE_RATE,
            source_url=item["source_url"],
            is_active=True,
        )

        db.add(price)
        print(f"Prepared: {service.service_name} - ${item['unit_price']}/hour")

    db.commit()
    print("\nDatabase compute prices inserted successfully!")

except Exception:
    db.rollback()
    raise

finally:
    db.close()
