import numpy as np
import pandas as pd

# 1. random number generator: reproducibility for 2026 revlotion
np.random.seed(2026)

# 2. Columns: data sources
num_rows = 10000
counterparties = [
    f"CP{str(i).zfill(3)}" for i in range(1, 101)
]  # 100 couter parties for CDS product
tickers = [
    "BARC",
    "HSBA",
    "VOD",
    "BP",
    "TSCO",
    "GLEN",
    "LLOY",
    "AZN",
    "GSK",
    "SHEL",
    "DBK",
    "BNP",
]
sectors = {
    "BARC": "Financials",
    "HSBA": "Financials",
    "LLOY": "Financials",
    "DBK": "Financials",
    "BNP": "Financials",
    "VOD": "Telecoms",
    "BP": "Energy",
    "SHEL": "Energy",
    "TSCO": "Consumer",
    "GLEN": "Mining",
    "AZN": "Healthcare",
    "GSK": "Healthcare",
}
ratings = ["AAA", "AA", "A", "BBB", "BB", "B", "CCC"]

# 3. 5 Columns: data frame
df = pd.DataFrame(
    {
        "Trade_ID": range(100001, 100001 + num_rows),
        "Counterparty_ID": np.random.choice(counterparties, num_rows),
        "Ticker": np.random.choice(tickers, num_rows),
        "Notional_GBP_M": np.round(np.random.uniform(5, 100, num_rows), 2),  # Notional Amt: 5M - 100M
        "Credit_Rating": np.random.choice(
            ratings, num_rows, p=[0.05, 0.15, 0.25, 0.30, 0.15, 0.08, 0.02]
        ),
    }
)

# Mapping sector to tickers in dic
df["Sector"] = df["Ticker"].map(sectors)

# Financial Logic: Counterparty Risk measured in "Notional_GBP_M" has different risk level in different sectors.
# Banks & Energy have big counterparty risk exposure (more sensitive to Geopolitical risk shock - tail event); 
# Consumer has  small risk.
sector_multipler = {
    "Financials": 5.0,
    "Energy": 3.0,
    "Telecoms": 1.5,
    "Mining": 1.3,
    "Healthcare": 0.8,
    "Consumer": 0.3
}

df["Multiplier"] = df["Sector"].map(sector_multipler)
df["Notional_GBP_M"] = np.round(df["Notional_GBP_M"]*df["Multiplier"], 2)
df = df.drop(columns=["Multiplier"])

# 4. Financial Logic: Credit Rating is lower when base spread is higher
base_spread_map = {
    "AAA": 20,
    "AA": 45,
    "A": 75,
    "BBB": 130,
    "BB": 280,
    "B": 550,
    "CCC": 1200,
}
df["Base_Spread"] = df["Credit_Rating"].map(base_spread_map)

# 5. Time line (monthly date) in horizontal view (Jan - Jun) ->  Unpivot practice
months = ["Jan_26", "Feb_26", "Mar_26", "Apr_26", "May_26", "Jun_26"]

# ==============================================================================
# RISK SPILLOVER & CREDIT CONTAGION MODELING
# Source: FT Lex - Capital Requirement Regulation & Systemic Risk
#
# Financial Logic (Vickers & Aikman):
# It is intuitive to think that a bank's health only affects financial companies.
# However, if a bank has a smaller safety cushion (lower capital ratio), international
# markets view it as riskier. Consequently, the bank's own borrowing costs increase.
# Instead of absorbing these costs, banks pass them on, meaning they won't lower
# rates for commercial borrowers.
#
# Impact: This triggers a macroeconomic chain reaction. The cost of capital rises
# across the board, driving up CDS spreads for ALL sectors in a modern economy,
# including non-finance sectors like Healthcare and Mining.
# ==============================================================================

# The initial shock: Simulate a sudden drop in bank capital ratios
bank_spread_spike = 50

for month in months:
    # 1. Base market condition: Apply to every sector,
    # normal distrution (mean = 0 , std = 15)
    volatility = np.random.normal(0, 15, num_rows)
    # Market trend simulation：assume market is downgrading,
    # each month's Spreads increase across all sectors.
    market_drift = months.index(month) * 5

    # Everyone receives their base + normal market noise (daily market noise plus monthly trend)
    df[f"Spread_{month}"] = df["Base_Spread"] + volatility + market_drift
    # 2. The credit contagion event = marco-eco chain reation
    # Non-Financials (Health, Mining, Consumer, etc.) suffer a 40% spillover effect,
    # as borrowing costs rise globally due to the bank's lack of a safety cushion
    # (less stable).
    df.loc[df["Sector"] != "Financials", f"Spread_{month}"] += bank_spread_spike * 0.4

    # Financials take the direct 100% hit from the capital ratio drop
    df.loc[df["Sector"] == "Financials", f"Spread_{month}"] += bank_spread_spike * 1.0

    # Make sure spread is not negative
    df[f"Spread_{month}"] = df[f"Spread_{month}"].apply(lambda x: max(x, 10))

# 6. Injection null data  (Data Quality Issues) -> practice for Power Query (Fabric)
# 6.1  3% Rows = Nulls
#      3% occurance of total rows = random value less than 0.03, based on uniform disutrion
mask_null = np.random.rand(num_rows) < 0.03
df.loc[mask_null, "Spread_Mar_26"] = np.nan

# 6.2 Data type error (Strings in Numeric columns)
# 1% Rows = Nulls
# 1% occurance of total rows = random value less than 0.01, based on uniform disutrion
mask_error = np.random.rand(num_rows) < 0.01

# Explicitly convert the column to 'object' data type for mix numbers & string
# New version of Pandas requirement for calc of "Spred_Month" columns above
df["Spread_Jan_26"] = df["Spread_Jan_26"].astype(object)

df.loc[mask_error, "Spread_Jan_26"] = "System_Error"

# 6.3 Duplication error  (Duplicates)
df = pd.concat([df, df.iloc[:200]], ignore_index=True)  # duplicate frist 200 rows

# 7. Clean data frame
df = df.drop(columns=["Base_Spread"])
# Load into Files under CDS_Data_Lake (default one)
#output_filename = "/lakehouse/default/Files/Mizuho_Mock_CDS_Data_Large.csv"
#df.to_csv(output_filename, index=False)
# print(f" Data generation is done! Saved to Lakehouse: {output_filename}")
# print(f"Total Rows: {len(df)}")

# 7.1 Convert Panda DataFrame into Spark Frame (a native big-data engine for Fabric Tables, Delta Tables)
# Convert everything into string firstly to avoid Spark crashing on "System-Error" dirty data.
spark_df = spark.createDataFrame(df.astype(str))

# 7.2 Save directly into Lakehouse > Table folder
table_name = "CDS_Dataset"

# Writes high-optimized Delta Table in Fabric
# mode("overwrite") ensures it deletes yesterday's data and replaces it with today's run.
spark_df.write.format("delta").mode("overwrite").saveAsTable(table_name)

print(f"Success! Data generated & saved in Delta Table in Fabric {table_name}")
print(f"Total Rows: {len(df)}")
