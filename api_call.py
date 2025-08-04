import requests
import json
import uuid
import random
import json
from datetime import datetime, timedelta
from faker import Faker
from dotenv import load_dotenv
import os
import pandas as pd

# Load environment variables
load_dotenv()
secret_id = os.getenv("SECRET_ID")

# # Sandbox API call URL
url = "https://developers.belvo.com/_mock/apis/belvopaymentsmexico/account_movements?page=1&limit=15&from_created_date=2019-08-24&until_created_date=2019-08-24&type=credit&withdrawal_id=string&reason=withdrawal"

query = {
  "page": "1",
  "limit": "15",
  "from_created_date": "2019-08-24",
  "until_created_date": "2019-08-24",
  "type": "credit",
  "withdrawal_id": "string",
  "reason": "withdrawal"
}

# API call
headers = {"api-key-id": secret_id}
response = requests.get(url, headers=headers, params=query)
data = response.json()

# Create synthetic data

fake = Faker('es_MX')  # Mexican locale for names and RFCs

# Create amount weights
def generate_amount():
    range_choice = random.choices(
        population=["low", "mid", "high"],
        weights=[0.5, 0.4, 0.1],
        k=1
    )[0]

    if range_choice == "low":
        return round(random.uniform(50.0, 1000.0), 2)
    elif range_choice == "mid":
        return round(random.uniform(1000.0, 5000.0), 2)
    else:  # "high"
        return round(random.uniform(5000.0, 10000.0), 2)

# Function to generate synthetic record
def generate_synthetic_record():
    created = fake.date_time_between(start_date='-12M', end_date='now')
    updated = created + timedelta(minutes=random.randint(1, 60))
    withdrawal_date = created - timedelta(days=random.randint(1, 5))

    return {
        "id": str(uuid.uuid4()),
        "createdDate": created.isoformat() + "Z",
        "lastUpdatedDate": updated.isoformat() + "Z",
        "chargebackDate": None,
        "type": random.choice(["credit", "debit"]),
        "reason": random.choice(["payments_service_fee", "refund", "adjustment"]),
        "amount": generate_amount(), # Use created function
        "currency": "MXN",
        "paymentRequest": str(uuid.uuid4()),
        "paymentRequestReference": f"INV-2025-{random.randint(100,999)}",
        "paymentRequestDisplayReference": f"Payment to {fake.company()}",
        "customerName": fake.name(),
        "customerDocumentType": random.choice(["mx_rfc", "mx_curp"]),
        "customerDocumentNumber": fake.unique.bothify(text="???######???"),
        "paymentMethodType": "bank_account",
        "accountNumber": fake.bban(),
        "withdrawalId": str(uuid.uuid4()),
        "withdrawalCreatedDate": withdrawal_date.isoformat() + "Z",
        "withdrawalExtra": {
            "reference_id": fake.lexify(text="???###"),
            "withdrawal_method": random.choice(["bank_transfer", "card_refund", "cash_pickup"])
        }
    }

# Generate a list of synthetic records
synthetic_data = [generate_synthetic_record() for _ in range(1000)]

# Save data
# with open("synthetic_transactions.json", "w", encoding="utf-8") as f:
#     json.dump(synthetic_data, f, ensure_ascii=False, indent=4)

# Convert to DataFrame
# Empty dict to store movements data
movements_dict = {}

# Desired columns
cols = ["id", "date", "type", "reason", "amount", "currency", "paymentRequestDisplayReference"]

# Loop through all synthetic data and extract desired columns into `movements_dict`
for i in range(len(synthetic_data)):
  for col in cols:
    movements_dict[synthetic_data[i]["id"]] = [synthetic_data[i]["createdDate"],
                                               synthetic_data[i]["type"],
                                               # synthetic_data[i]["reason"],
                                               synthetic_data[i]["amount"],
                                               # synthetic_data[i]["currency"],
                                               synthetic_data[i]["paymentRequestDisplayReference"]
                                               ]
    
# Convert to DataFrame
df = pd.DataFrame.from_dict(movements_dict, orient='index', columns=[
    'timestamp', 'type', 'amount', 'description'
])

# Reset index to make the UUID a column
df = df.reset_index().rename(columns={'index': 'transaction_id'})

# Generate random categories
categories = [
    "Healthcare", "Groceries", "Gasoline", "Entertainment", "Subscriptions",
    "Dining Out", "Housing", "Education", "Travel", "Utilities", "Other"
]

# Assign categories
cats = []
for i in range(len(df)):
  cats.append(random.choice(categories))
df["category"] = pd.Series(cats)

# Assign datatypes
# Ensure proper data types
df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
df["type"] = df["type"].astype("category")
df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
df["description"] = df["description"].astype(str)

# Save as cvs
df.to_csv("movements.csv", index=False)
print(df.head())

