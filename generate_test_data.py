import pandas as pd
import numpy as np
from datetime import datetime, timedelta

print("Generating Noctisedge AI Stress-Test Dataset (5,000 rows)...")

# 1. Base Setup
np.random.seed(42)
num_rows = 5000
start_date = datetime(2025, 1, 1)

# 2. Generate Normal Data
data = {
    "OrderID": [f"NCT-{10000 + i}" for i in range(num_rows)],
    "Date": [(start_date + timedelta(days=np.random.randint(0, 365))).strftime("%Y-%m-%d") for _ in range(num_rows)],
    "ClientID": [f"AGENCY-CLIENT-{np.random.randint(1, 15)}" for _ in range(num_rows)],
    "Category": np.random.choice(["Apparel", "Electronics", "Home & Garden", "Beauty", "Fitness"], num_rows),
    "Region": np.random.choice(["North America", "Europe", "Asia", "South America"], num_rows),
    "Units_Sold": np.random.randint(1, 20, num_rows),
    "Revenue": np.round(np.random.normal(loc=150.0, scale=50.0, size=num_rows), 2),
    "Ad_Spend": np.round(np.random.normal(loc=40.0, scale=10.0, size=num_rows), 2)
}

df = pd.DataFrame(data)

# Ensure no accidental negative revenue in the normal distribution
df['Revenue'] = df['Revenue'].clip(lower=10.0)

# Calculate Profit Margin (Revenue - Ad_Spend - Base Cost)
df['Profit'] = np.round(df['Revenue'] - df['Ad_Spend'] - (df['Revenue'] * 0.4), 2)

# --- INJECTING EXACT ANOMALIES FOR THE SWARM TO CATCH ---

# Anomaly 1: The "Rogue Ad Campaign" (Massive negative profit)
df.loc[1250, 'Ad_Spend'] = 8500.00
df.loc[1250, 'Profit'] = -8400.00
df.loc[1250, 'Category'] = 'Electronics'

# Anomaly 2: The "Bot Purchase" (Extreme outlier in Units Sold)
df.loc[3421, 'Units_Sold'] = 1500
df.loc[3421, 'Revenue'] = 45000.00

# Anomaly 3: The "Pricing Glitch" (Negative Revenue)
df.loc[4111, 'Revenue'] = -500.00
df.loc[4111, 'Profit'] = -500.00

# 4. Save to CSV
file_name = "noctisedge_agency_data.csv"
df.to_csv(file_name, index=False)
print(f"✅ Success! {file_name} created with {num_rows} records.")
print("Hidden Anomalies at rows: 1250, 3421, and 4111.")