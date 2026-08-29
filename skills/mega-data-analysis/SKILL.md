---
name: mega-data-analysis
description: Data Analysis Skill — Local File Processing & Analytics
domains: [data-analysis]
token_profile: Lean
---

# MEGA-DATA-ANALYSIS

_Ingested from the opencode skill source. Bundled into the Monolith mega-skills catalog._


# Data Analysis Skill — Local File Processing & Analytics

## Keywords
`data analysis` `csv` `json` `excel` `xlsx` `logs` `parquet` `xml` `pandas` `numpy`
`matplotlib` `seaborn` `plotly` `dataframe` `groupby` `merge` `join` `pivot` `crosstab`
`time series` `statistical analysis` `data cleaning` `data transformation` `outlier detection`
`missing data` `data validation` `schema inference` `correlation` `regression` `hypothesis`
`a/b testing` `cohort analysis` `funnel analysis` `clustering` `feature engineering`
`data profiling` `data summarization` `deduplication` `filtering` `sorting` `aggregation`
`visualization` `histogram` `scatter plot` `box plot` `heatmap` `bar chart` `line chart`
`pie chart` `violin plot` `pair plot` `distribution` `descriptive statistics` `inferential`
`python repl` `node repl` `start process` `interact with process` `read process output`
`local file analysis` `file type detection` `encoding handling` `chunked processing`
`memory efficient` `streaming analysis` `batch processing` `data pipeline` `etl`
`jupyter` `notebook` `exploratory data analysis` `eda` `data science`

## Critical Rule

**ALWAYS use `start_process` + `interact_with_process` for local file analysis.** The analysis tool CANNOT access local files and WILL FAIL.

## Priority Order for File Analysis

1. **Python REPL** (preferred) — `start_process("python3 -i")`
2. **Node.js REPL** — `start_process("node -i")`
3. **Command-line tools** — `cut`, `awk`, `grep` for quick processing

## Python Workflows

### CSV Analysis
```python
# Step 1: Start REPL
start_process("python3 -i")

# Step 2: Import libraries
interact_with_process(pid, "import pandas as pd, numpy as np")

# Step 3: Read file
interact_with_process(pid, "df = pd.read_csv('/path/to/file.csv')")

# Step 4: Analyze
interact_with_process(pid, "print(df.describe())")
interact_with_process(pid, "df.groupby('column').size()")
interact_with_process(pid, "df.head(10)")
```

### JSON Analysis
```python
import json

with open('/path/to/file.json') as f:
    data = json.load(f)

# Explore structure
print(type(data))
print(len(data))
print(data[0].keys() if isinstance(data, list) else data.keys())
```

### Excel Analysis
```python
import pandas as pd

# Read Excel
df = pd.read_excel('/path/to/file.xlsx', sheet_name='Sheet1')

# List sheets
xl = pd.ExcelFile('/path/to/file.xlsx')
print(xl.sheet_names)
```

### Log Analysis
```python
import re
from collections import Counter

with open('/path/to/file.log') as f:
    lines = f.readlines()

# Count patterns
errors = [l for l in lines if 'ERROR' in l]
print(f"Total errors: {len(errors)}")

# Extract timestamps
timestamps = [re.search(r'\d{4}-\d{2}-\d{2}', l) for l in lines]
```

### Parquet Analysis
```python
import pandas as pd

df = pd.read_parquet('/path/to/file.parquet')
print(df.head())
print(df.dtypes)
```

### XML Analysis
```python
import pandas as pd

df = pd.read_xml('/path/to/file.xml')
print(df.head())
```

## Node.js Workflows

### JSON Processing
```javascript
// Step 1: Start REPL
start_process("node -i")

// Step 2: Import modules (ES syntax)
interact_with_process(pid, "import fs from 'fs'")

// Step 3: Read file
interact_with_process(pid, "const data = JSON.parse(fs.readFileSync('/path/to/file.json', 'utf8'))")

// Step 4: Analyze
interact_with_process(pid, "console.log(data.length)")
interact_with_process(pid, "console.log(data[0])")
```

## Command-Line Quick Analysis

### CSV Quick Stats
```bash
# Count rows
wc -l file.csv

# View headers
head -1 file.csv

# Count unique values in column 2
cut -d',' -f2 file.csv | sort | uniq -c | sort -rn

# Filter rows
grep "pattern" file.csv

# Sort by column
sort -t',' -k2 -n file.csv
```

### JSON Quick Stats
```bash
# Pretty print
cat file.json | python3 -m json.tool

# Count items
cat file.json | python3 -c "import json,sys; print(len(json.load(sys.stdin)))"

# Extract field
cat file.json | python3 -c "import json,sys; [print(i['field']) for i in json.load(sys.stdin)]"
```

## Visualization

### Matplotlib
```python
import matplotlib.pyplot as plt

# Line plot
plt.plot(x, y)
plt.savefig('/path/to/plot.png')

# Bar chart
plt.bar(categories, values)
plt.xticks(rotation=45)
plt.savefig('/path/to/bar.png')
```

### Seaborn
```python
import seaborn as sns

# Heatmap
sns.heatmap(df.corr())
plt.savefig('/path/to/heatmap.png')

# Distribution
sns.histplot(df['column'])
plt.savefig('/path/to/dist.png')
```

## Advanced Operations

### DataFrame Operations
```python
# Filter
df[df['column'] > 100]

# Select columns
df[['col1', 'col2']]

# Rename columns
df.rename(columns={'old': 'new'})

# Drop columns
df.drop(columns=['col'])

# Fill missing
df.fillna(0)

# Drop duplicates
df.drop_duplicates()
```

### GroupBy Aggregations
```python
# Simple groupby
df.groupby('category').size()

# Multiple aggregations
df.groupby('category').agg({
    'value': ['mean', 'median', 'std', 'min', 'max']
})

# Pivot table
pd.pivot_table(df, values='value', index='category', columns='date', aggfunc='sum')
```

### Merge/Join
```python
# Inner join
pd.merge(df1, df2, on='key')

# Left join
pd.merge(df1, df2, on='key', how='left')

# Concatenate
pd.concat([df1, df2], axis=0)
```

### Time Series
```python
# Convert to datetime
df['date'] = pd.to_datetime(df['date'])

# Set index
df.set_index('date', inplace=True)

# Resample
df.resample('M').mean()  # Monthly mean

# Rolling average
df['rolling_avg'] = df['value'].rolling(window=7).mean()
```

### Statistical Analysis
```python
from scipy import stats

# Descriptive stats
print(df.describe())

# Correlation
print(df.corr())

# T-test
t_stat, p_value = stats.ttest_ind(group1, group2)

# Chi-square
chi2, p_value, dof, expected = stats.chi2_contingency(contingency_table)
```

## Error Handling

### Common Issues
```python
# File not found
try:
    df = pd.read_csv('file.csv')
except FileNotFoundError:
    print("File not found")

# Encoding issues
df = pd.read_csv('file.csv', encoding='latin-1')

# Large files
df = pd.read_csv('file.csv', chunksize=10000)
for chunk in df:
    process(chunk)
```

## Integration

### With Quantum Nexus
- Analyze case data
- Process evidence lists
- Generate reports

### With Legal Powerhouse
- Analyze court data
- Process filing metadata
- Generate legal analytics

### With Brain
- Analyze threat data
- Process timeline events
- Generate intelligence reports
