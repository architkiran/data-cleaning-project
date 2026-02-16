# 🧹 Data Cleaning Project — Employee/Customer Records

A data cleaning project using **Python & Pandas**. Includes a realistic messy dataset, a fully commented cleaning script, and a learning guide explaining every concept used.

---

## 📁 Project Structure

```
data-cleaning-project/
│
├── messy_employees.csv            # Raw dataset (130 rows, intentionally dirty)
├── clean_employees.py             # Full data cleaning script
├── Data_Cleaning_Learning_Guide.docx  # Beginner's guide to every concept used
└── README.md
```

---

## 🗂️ Dataset Overview

The raw dataset (`messy_employees.csv`) simulates a real-world employee/customer records export with **11 columns** and **130 rows**, containing the following intentional data quality issues:

| Column | Issues |
|---|---|
| `employee_id` | Missing values, stored as float |
| `first_name` / `last_name` | Mixed casing (`DAVID`, `carol`, `WILLIAMS`) |
| `email` | Missing values, inconsistent casing |
| `phone` | 4 different formats (`(555) 123-4567`, `555-123-4567`, raw digits, `+1...`) |
| `department` | Inconsistent casing (`Sales`, `SALES`, `sales`) |
| `gender` | Mixed representations (`Male`, `M`, `MALE`, `male`) |
| `city` | Mixed casing, missing values |
| `salary` | Dollar signs, commas, negative values, extreme outliers (`$999,999`) |
| `hire_date` | 5 different date formats + missing values |
| `is_active` | Mix of `1/0`, `"Yes"/"No"`, `"TRUE"/"FALSE"`, `True/False`, missing |

---

## 🔧 What the Cleaning Script Does

The script (`clean_employees.py`) walks through **7 steps**:

1. **Inspect** — profile the raw data (shape, dtypes, missing values)
2. **Remove duplicates** — exact row duplicates and duplicate `employee_id`s
3. **Standardize text** — names, departments, gender, city → consistent casing and values
4. **Fix data types** — salary → float, hire_date → datetime, is_active → boolean, employee_id → Int64
5. **Standardize phone numbers** — all formats normalized to `(XXX) XXX-XXXX`
6. **Handle missing values** — salary filled by department median, categoricals filled with `"Unknown"`, booleans assumed `True`
7. **Detect & treat outliers** — IQR method on salary, extreme values capped via Winsorizing

---

## 🚀 Getting Started

### Prerequisites

```bash
pip install pandas numpy
```

### Run the cleaning script

```bash
# Place messy_employees.csv and clean_employees.py in the same folder, then:
python clean_employees.py
```

This will print a step-by-step log to the terminal and save `clean_employees.csv` in the same directory.

---

## 📊 Before vs After

| Metric | Before | After |
|---|---|---|
| Rows | 130 | 120 |
| Duplicate rows | 10 | 0 |
| Missing salary values | 24 | 0 |
| Salary outliers | 32 | 0 (capped) |
| Date formats | 5 different | 1 (datetime) |
| Phone formats | 4 different | 1 (`(XXX) XXX-XXXX`) |
| Gender representations | 8 different | 3 (`Male`, `Female`, `Non-binary`) |

---

## 📚 Learning Guide

The file `Data_Cleaning_Learning_Guide.docx` is a beginner-friendly walkthrough of every concept used in the script, including:

- What data cleaning is and why it matters
- The standard 7-step cleaning pipeline
- Key pandas commands for profiling data
- When to use mean vs median vs mode for missing values
- How the IQR outlier method works
- Concepts explained simply: NaN, lambda functions, method chaining, `inplace=True`
- A full cheat sheet of the 20 most-used pandas commands
- Suggested next steps for continued learning

---

## 🧠 Concepts & Tools Used

| Concept | Used for |
|---|---|
| `pandas` | Core data manipulation library |
| `numpy` | NaN constants and numeric operations |
| `re` (regex) | Phone number parsing and email validation |
| `str.strip() / .lower() / .title()` | Text standardization |
| `.map()` with a dictionary | Normalizing categorical values |
| `pd.to_numeric()` / `pd.to_datetime()` | Type conversion |
| `groupby().transform()` | Filling NaNs using per-group statistics |
| `df.clip()` | Winsorizing outliers |
| IQR method | Outlier detection |
| `Int64` (nullable integer) | Integers that support missing values |

---

## 📌 Notes

- `hire_date` and `email` missing values are **left as NaN** — they cannot be guessed and imputing them would introduce false data.
- The salary outlier treatment uses **Winsorizing** (capping to fence values) rather than deletion, to preserve row count.
- The script is written for **Python 3.8+** and **pandas 2.0+**.

---

## 🗺️ What to Learn Next

- **Exploratory Data Analysis (EDA)** — visualize your clean data with `matplotlib` and `seaborn`
- **Feature Engineering** — create new columns from existing ones (e.g. tenure from `hire_date`)
- **Merging DataFrames** — combine datasets with `pd.merge()` (like SQL JOINs)
- **Automated pipelines** — wrap cleaning into reusable functions or use tools like `dbt` or `Prefect`

---

## 🤝 Contributing

Feel free to open an issue or PR if you'd like to add more data quality scenarios, additional cleaning steps, or support for other file formats.

---

*Built as a learning project for data analysis beginners.*
