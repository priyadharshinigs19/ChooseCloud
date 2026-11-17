
from decimal import Decimal

from app.database import SessionLocal
from app.models import ServicePrice


EXCHANGE_RATE = Decimal("94.1997")

compute_prices = [
    {
        "service_id": 1,
        "region": "Asia Pacific (Mumbai) - ap-south-1",
        "configuration": "t3.large | Linux | 2 vCPU | 8 GiB RAM | On-Demand",
        "billing_unit": "1 Hour",
        "unit_price": Decimal("0.0896"),
        "currency": "USD",
        "exchange_rate_to_inr": EXCHANGE_RATE,
        "source_url": "https://aws.amazon.com/ec2/pricing/on-demand/",
    },
    {
        "service_id": 4,
        "region": "Central India - centralindia",
        "configuration": "Standard_D2as_v5 | Linux | 2 vCPU | 8 GiB RAM | On-Demand",
        "billing_unit": "1 Hour",
        "unit_price": Decimal("0.0556"),
        "currency": "USD",
        "exchange_rate_to_inr": EXCHANGE_RATE,
        "source_url": "https://prices.azure.com/",
    },
    {
        "service_id": 7,
        "region": "Mumbai - asia-south1",
        "configuration": "e2-standard-2 | Linux | 2 vCPU | 8 GiB RAM | On-Demand",
        "billing_unit": "1 Hour",
        "unit_price": Decimal("0.08048436"),
        "currency": "USD",
        "exchange_rate_to_inr": EXCHANGE_RATE,
        "source_url": "https://cloud.google.com/products/compute/pricing/general-purpose",
    },
]


def seed_prices():
    db = SessionLocal()

    try:
        inserted = 0

        for price_data in compute_prices:
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

            price = ServicePrice(**price_data)
            db.add(price)
            inserted += 1

        db.commit()
        print(f"\nSuccessfully inserted {inserted} compute pricing records.")

    except Exception as error:
        db.rollback()
        print("Error inserting prices:", error)

    finally:
        db.close()


if __name__ == "__main__":
    seed_prices()
