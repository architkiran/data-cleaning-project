# =============================================================================
#  DATA CLEANING SCRIPT  |  Employee / Customer Records
#  Covers: missing values, duplicates, data types, formats, outliers
# =============================================================================

import pandas as pd
import numpy as np
import re

# ── Load ──────────────────────────────────────────────────────────────────────
df = pd.read_csv("messy_employees.csv")

print("=" * 60)
print("STEP 0 — RAW DATA OVERVIEW")
print("=" * 60)
print(f"Shape: {df.shape[0]} rows × {df.shape[1]} columns\n")
print(df.dtypes)
print("\nMissing values per column:")
print(df.isnull().sum())
print("\nFirst 5 rows:")
print(df.head())


# =============================================================================
# STEP 1 — REMOVE DUPLICATES
# =============================================================================
print("\n" + "=" * 60)
print("STEP 1 — REMOVE DUPLICATES")
print("=" * 60)

before = len(df)

# Drop exact duplicate rows
df.drop_duplicates(inplace=True)

# Drop rows with the same employee_id (keep first occurrence)
df.drop_duplicates(subset=["employee_id"], keep="first", inplace=True)

df.reset_index(drop=True, inplace=True)
print(f"Removed {before - len(df)} duplicate rows. Remaining: {len(df)}")


# =============================================================================
# STEP 2 — STANDARDIZE TEXT FORMATS
# =============================================================================
print("\n" + "=" * 60)
print("STEP 2 — STANDARDIZE TEXT FORMATS")
print("=" * 60)

# --- Names: Title Case ---
for col in ["first_name", "last_name"]:
    df[col] = df[col].str.strip().str.title()

# --- Department: Title Case (Sales, Hr → HR, Engineering, etc.) ---
dept_map = {
    "sales": "Sales",
    "hr": "HR",
    "engineering": "Engineering",
    "marketing": "Marketing",
    "finance": "Finance",
}
df["department"] = (
    df["department"]
    .str.strip()
    .str.lower()
    .map(dept_map)
)

# --- Gender: normalize to full words ---
gender_map = {
    "male": "Male", "m": "Male",
    "female": "Female", "f": "Female",
    "non-binary": "Non-binary", "nb": "Non-binary",
}
df["gender"] = (
    df["gender"]
    .str.strip()
    .str.lower()
    .map(gender_map)            # unmapped values become NaN automatically
)

# --- City: Title Case ---
df["city"] = df["city"].str.strip().str.title()

# --- Email: lowercase ---
df["email"] = df["email"].str.strip().str.lower()

print("Text columns standardized: first_name, last_name, department, gender, city, email")
print(df[["first_name", "last_name", "department", "gender", "city"]].head(8))


# =============================================================================
# STEP 3 — FIX DATA TYPES
# =============================================================================
print("\n" + "=" * 60)
print("STEP 3 — FIX DATA TYPES")
print("=" * 60)

# --- employee_id → integer ---
df["employee_id"] = pd.to_numeric(df["employee_id"], errors="coerce").astype("Int64")

# --- salary: strip $, commas, convert to float ---
def parse_salary(val):
    if pd.isna(val):
        return np.nan
    s = str(val).replace("$", "").replace(",", "").strip()
    try:
        return float(s)
    except ValueError:
        return np.nan

df["salary"] = df["salary"].apply(parse_salary)

# --- hire_date: parse multiple date formats → datetime ---
def parse_date(val):
    if pd.isna(val):
        return pd.NaT
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%m-%d-%Y", "%d-%m-%Y", "%d/%m/%Y"):
        try:
            return pd.to_datetime(str(val), format=fmt)
        except (ValueError, TypeError):
            pass
    return pd.NaT          # could not parse

df["hire_date"] = df["hire_date"].apply(parse_date)

# --- is_active: normalize to boolean ---
true_vals  = {1, "1", "yes", "true", True}
false_vals = {0, "0", "no", "false", False}

def parse_bool(val):
    if pd.isna(val):
        return np.nan
    if isinstance(val, str):
        val_lower = val.strip().lower()
        if val_lower in {"yes", "true", "1"}:
            return True
        if val_lower in {"no", "false", "0"}:
            return False
        return np.nan
    if val in true_vals:
        return True
    if val in false_vals:
        return False
    return np.nan

df["is_active"] = df["is_active"].apply(parse_bool)

print("Dtypes after fixing:")
print(df.dtypes)


# =============================================================================
# STEP 4 — STANDARDIZE PHONE NUMBERS
# =============================================================================
print("\n" + "=" * 60)
print("STEP 4 — STANDARDIZE PHONE NUMBERS")
print("=" * 60)

def standardize_phone(val):
    """Return a 10-digit US number as (XXX) XXX-XXXX, else NaN."""
    if pd.isna(val):
        return np.nan
    digits = re.sub(r"\D", "", str(val))
    if len(digits) == 11 and digits.startswith("1"):
        digits = digits[1:]
    if len(digits) == 10:
        return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
    return np.nan          # invalid / unrecognizable

df["phone"] = df["phone"].apply(standardize_phone)
print("Sample phone values after standardization:")
print(df["phone"].dropna().head(8).tolist())


# =============================================================================
# STEP 5 — HANDLE MISSING VALUES
# =============================================================================
print("\n" + "=" * 60)
print("STEP 5 — HANDLE MISSING VALUES")
print("=" * 60)

print("Missing values BEFORE:")
print(df.isnull().sum())

# --- salary: fill with median by department ---
df["salary"] = df.groupby("department")["salary"].transform(
    lambda x: x.fillna(x.median())
)
# If still NaN (whole dept was NaN), fill with overall median
df["salary"] = df["salary"].fillna(df["salary"].median())

# --- is_active: assume active if unknown ---
df["is_active"] = df["is_active"].fillna(True)

# --- gender / city: fill with 'Unknown' ---
df["gender"] = df["gender"].fillna("Unknown")
df["city"]   = df["city"].fillna("Unknown")

# --- hire_date: flag but keep as NaT (cannot guess) ---
# --- email / phone: flag but keep as NaN (cannot guess) ---

# --- department: fill with mode ---
mode_dept = df["department"].mode()[0]
df["department"] = df["department"].fillna(mode_dept)

print("\nMissing values AFTER:")
print(df.isnull().sum())


# =============================================================================
# STEP 6 — OUTLIER DETECTION & TREATMENT  (salary)
# =============================================================================
print("\n" + "=" * 60)
print("STEP 6 — OUTLIER DETECTION & TREATMENT")
print("=" * 60)

# IQR method on salary
Q1  = df["salary"].quantile(0.25)
Q3  = df["salary"].quantile(0.75)
IQR = Q3 - Q1
lower_fence = Q1 - 1.5 * IQR
upper_fence = Q3 + 1.5 * IQR

outliers = df[(df["salary"] < lower_fence) | (df["salary"] > upper_fence)]
print(f"Salary — Q1: {Q1:,.0f}  Q3: {Q3:,.0f}  IQR: {IQR:,.0f}")
print(f"Fences  — lower: {lower_fence:,.0f}  upper: {upper_fence:,.0f}")
print(f"Outliers found: {len(outliers)}")
print(outliers[["employee_id", "first_name", "last_name", "department", "salary"]])

# Cap outliers to fence values (Winsorizing)
df["salary"] = df["salary"].clip(lower=lower_fence, upper=upper_fence)
df["salary"] = df["salary"].round(2)
print(f"\nSalary after capping — min: {df['salary'].min():,.2f}  max: {df['salary'].max():,.2f}")


# =============================================================================
# STEP 7 — VALIDATE EMAILS
# =============================================================================
print("\n" + "=" * 60)
print("STEP 7 — VALIDATE EMAILS  (bonus)")
print("=" * 60)

email_pattern = r"^[\w\.\+\-]+@[\w\-]+\.[a-z]{2,}$"
df["email_valid"] = df["email"].apply(
    lambda x: bool(re.match(email_pattern, str(x))) if pd.notna(x) else False
)
invalid_emails = df[~df["email_valid"] & df["email"].notna()]
print(f"Invalid / suspicious emails: {len(invalid_emails)}")
if len(invalid_emails):
    print(invalid_emails[["first_name", "last_name", "email"]].to_string(index=False))
# Drop helper column
df.drop(columns=["email_valid"], inplace=True)


# =============================================================================
# FINAL OUTPUT
# =============================================================================
print("\n" + "=" * 60)
print("FINAL CLEAN DATASET SUMMARY")
print("=" * 60)
print(f"Shape: {df.shape[0]} rows × {df.shape[1]} columns")
print("\nDtypes:")
print(df.dtypes)
print("\nMissing values:")
print(df.isnull().sum())
print("\nSample cleaned rows:")
print(df.head(10).to_string())

df.to_csv("clean_employees.csv", index=False)
print("\n✅  Saved cleaned dataset to: clean_employees.csv")
