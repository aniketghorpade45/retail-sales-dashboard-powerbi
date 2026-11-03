"""
Project: Retail Sales Analysis (Excel + Power BI)
Dataset: "Sample - Superstore" from Kaggle -> save as Sample-Superstore.csv in this folder.
Run:     python superstore_analysis.py
Outputs: superstore_cleaned.csv (load this into Power BI),
         superstore_summary.xlsx (summary tables for Excel), insights.txt
"""
import pandas as pd

# ---------- 1. LOAD ----------
df = pd.read_csv("Sample-Superstore.csv", encoding="latin1")
print("Raw shape:", df.shape)
print("Missing values:\n", df.isnull().sum(), "\n")

# ---------- 2. CLEAN ----------
df = df.drop_duplicates()
df.columns = [c.strip().replace(" ", "_").replace("-", "_") for c in df.columns]
df["Order_Date"] = pd.to_datetime(df["Order_Date"])
df["Ship_Date"] = pd.to_datetime(df["Ship_Date"])
df["Year"] = df["Order_Date"].dt.year
df["Month"] = df["Order_Date"].dt.month
df["Month_Name"] = df["Order_Date"].dt.strftime("%b")
df["Shipping_Days"] = (df["Ship_Date"] - df["Order_Date"]).dt.days
df["Profit_Margin_%"] = (df["Profit"] / df["Sales"] * 100).round(2)
for col in ["Segment", "Region", "Category", "Sub_Category", "Ship_Mode"]:
    df[col] = df[col].str.strip()
df.to_csv("superstore_cleaned.csv", index=False)
print("Clean shape:", df.shape)

# ---------- 3. SUMMARY TABLES ----------
def summary(by):
    t = df.groupby(by).agg(Sales=("Sales", "sum"), Profit=("Profit", "sum"),
                           Orders=("Order_ID", "nunique"), Quantity=("Quantity", "sum")).round(2)
    t["Profit_Margin_%"] = (t["Profit"] / t["Sales"] * 100).round(2)
    return t.sort_values("Sales", ascending=False)

tables = {
    "By Region": summary("Region"),
    "By Category": summary("Category"),
    "By Sub-Category": summary("Sub_Category"),
    "By Segment": summary("Segment"),
    "By Year": summary("Year").sort_index(),
    "By Month": summary(["Year", "Month"]).sort_index(),
    "Top 10 Products": summary("Product_Name").head(10),
    "Top 10 Customers": summary("Customer_ID").head(10),
}
df["Discount_Band"] = pd.cut(df["Discount"], [-0.01, 0, 0.2, 0.4, 1],
                             labels=["No discount", "1-20%", "21-40%", ">40%"])
tables["Discount vs Profit"] = df.groupby("Discount_Band", observed=True).agg(
    Sales=("Sales", "sum"), Profit=("Profit", "sum")).round(2)

with pd.ExcelWriter("superstore_summary.xlsx") as xw:
    for name, t in tables.items():
        t.to_excel(xw, sheet_name=name)

# ---------- 4. INSIGHTS (use these in your resume + interviews) ----------
sub = tables["By Sub-Category"]
loss = sub[sub["Profit"] < 0]
reg = tables["By Region"]
disc = tables["Discount vs Profit"]
lines = [
    f"Total sales: {df['Sales'].sum():,.0f} | Total profit: {df['Profit'].sum():,.0f}",
    f"Best region by sales: {reg.index[0]} ({reg.iloc[0]['Sales']:,.0f})",
    f"Region with highest profit margin: {reg['Profit_Margin_%'].idxmax()}",
    f"Loss-making sub-categories: {', '.join(loss.index) if len(loss) else 'none'}",
    "Profit by discount band:\n" + disc.to_string(),
]
open("insights.txt", "w").write("\n".join(lines))
print("\n".join(lines))
