
from decimal import Decimal
from app.database import SessionLocal
from app.models import ServicePrice

EXCHANGE_RATE = Decimal("94.1997")

storage_prices = [
    {
        "service_id": 2,
        "region": "Asia Pacific (Mumbai) - ap-south-1",
        "configuration": "S3 Standard | Frequent Access | On-Demand",
        "billing_unit": "1 GB/Month",
        "unit_price": Decimal("0.025"),
        "currency": "USD",
        "exchange_rate_to_inr": EXCHANGE_RATE,
        "source_url": "https://aws.amazon.com/s3/pricing/",
    },
    {
        "service_id": 5,
        "region": "Central India - centralindia",
        "configuration": "Blob Hot LRS | General Block Blob v2",
        "billing_unit": "1 GB/Month",
        "unit_price": Decimal("0.020"),
        "currency": "USD",
        "exchange_rate_to_inr": EXCHANGE_RATE,
        "source_url": "https://prices.azure.com/",
    },
    {
        "service_id": 8,
        "region": "Mumbai - asia-south1",
        "configuration": "Cloud Storage Standard | Regional",
        "billing_unit": "1 GB/Month",
        "unit_price": Decimal("0.023"),
        "currency": "USD",
        "exchange_rate_to_inr": EXCHANGE_RATE,
        "source_url": "https://cloud.google.com/storage/pricing",
    },
]


def seed_prices():
    db = SessionLocal()

    try:
        inserted = 0

        for price_data in storage_prices:
            existing = (
                db.query(ServicePrice)
                .filter(
                    ServicePrice.service_id == price_data["service_id"],
                    ServicePrice.region == price_data["region"],
                    ServicePrice.configuration == price_data["configuration"],
                )
                .first()
            )

            if existing:
                print(f"Already exists: {price_data['configuration']}")
                continue

            db.add(ServicePrice(**price_data))
            inserted += 1

        db.commit()
        print(f"Successfully inserted {inserted} storage pricing records.")

    except Exception as error:
        db.rollback()
        print("Error inserting prices:", error)

    finally:
        db.close()


if __name__ == "__main__":
    seed_prices()
