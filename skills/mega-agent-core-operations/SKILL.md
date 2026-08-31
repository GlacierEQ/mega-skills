---
name: mega-agent-core-operations
description: "Consolidated mega skill encompassing 7 sub-skills."
---


# MEGA-AGENT-CORE-OPERATIONS

> [!WARNING]
> **APEX COGNITIVE FIREWALL (INTERCEPTOR GATE)**
> This file contains core operational safety, dependency management, and notebook execution protocols.
DO NOT READ FURTHER unless the current user mandate explicitly requires:
- Data loss safety verification, Python dependency resolution, notebook authoring, or ML best practices.
> If the current task does not specifically target this domain, **STOP READING HERE** to preserve token context.


## Sub-Skill: accidental-data-loss-prevention
# Accidental Data Loss Prevention

> [!CAUTION]
>
> **STOP AND VERIFY**: Before running any command or tool that results in
> irreversible data loss, you **MUST** obtain explicit user consent.

## Mandatory Procedure

1.  **Halt Execution**: Do **not** execute the command.
2.  **Request Consent**: Explain clearly to the user:
    -   The **impact** of this deletion.
    -   **Why** you believe this is necessary.
    -   A request for their **explicit approval** to proceed.
3.  **Wait**: Only proceed if the user provides clear, affirmative consent in
    the conversation.

---

## Sub-Skill: enforcing-resource-attribution
# Resource Attribution Enforcement

To track resources created or manipulated by AI agents, you **MUST** ensure
that standard CLI commands are tagged with appropriate attribution labels
under relevant conditions.

## Applicability

You should apply these attribution labels **ONLY** under the following
conditions:
1.  **DAK Tooling**: You are executing Python scripts, running MCP tools, or
    following workflows provided by the **Data Agent Kit**.
2.  **Domain Relevance**: You are operating on BigQuery datasets, GCS
    buckets, or Analytics infrastructure (including **Spark**,
    **Dataproc**, or Serverless Spark) intended for data preparation,
    deduplication, or analysis.

### 🚫 When to Omit
Do **NOT** apply these labels if you are running generic administrative
commands or working on infrastructure completely unrelated to Data Cloud /
Analytics (e.g., managing Compute Engines for web apps, setting up standard
IAM policies, etc.).

Do **NOT** apply `--label` flags to commands that do not accept labels, as the `--label` flag is unsupported by these specific `bq` subcommands. These include:
- `bq show`
- `bq ls`
- `bq version`
- `bq rm`
- `bq cancel`
- `bq head`

## BigQuery CLI (`bq`)

You **MUST** apply `--label key:value` **ONLY** to subcommands that accept job or resource labels (`bq query`, `bq load`, `bq extract`, `bq mk`, `bq update`, and `bq cp`).

-   **Flag Form**: `--label key:value`
-   **Mandatory Label**: `datacloud:<ide>`
-   **Deduction Rule**: Substitute `<ide>` with your actual environment/client
    (e.g., `vscode`, `jetski`, `antigravity`, `codex`, `cursor`, `cloud-shell`,
    `workstation`, `gemini-cli`, `claude`).
    *   Use `cloud-shell` for GCP Cloud Shell.
    *   Use `workstation` for GCP Cloud Workstations.
    If you cannot determine your environment, use `ai-agent`. Note that
    BigQuery labels **cannot** contain dots or spaces.

### Examples

#### Query Example
**Incorrect**:
```bash
bq query --use_legacy_sql=false "SELECT 1"
```

**Correct** (assuming you are running in VS Code):
```bash
bq query --use_legacy_sql=false --label datacloud:vscode "SELECT 1"
```

#### Copy Example
**Incorrect**:
```bash
bq cp dataset1.table1 dataset2.table1_copy
```

**Correct** (assuming you are running in Jetski):
```bash
bq cp --label datacloud:jetski dataset1.table1 dataset2.table1_copy
```

---

## Google Cloud SDK (`gcloud`)

Whenever you execute any `gcloud` command via `run_command`, you **MUST**
prepend the command with the `CLOUDSDK_METRICS_ENVIRONMENT` environment
variable to ensure proper resource attribution.

-   **Environment Variable**: `CLOUDSDK_METRICS_ENVIRONMENT=datacloud.<ide>`
-   **Deduction Rule**: Substitute `<ide>` with your actual environment/client
    (e.g., `vscode`, `jetski`, `antigravity`, `codex`, `cursor`, `cloud-shell`,
    `workstation`, `gemini-cli`, `claude`).
    *   Use `cloud-shell` for GCP Cloud Shell.
    *   Use `workstation` for GCP Cloud Workstations.
    If you cannot determine your environment, use `ai-agent`. Note that
    values must use dots (e.g., `datacloud.vscode`), not colons.

### Examples

**Incorrect**:
```bash
gcloud compute disks create my-disk --size=10GB
```

**Correct** (assuming you are running in VS Code):
```bash
CLOUDSDK_METRICS_ENVIRONMENT=datacloud.vscode gcloud compute disks create my-disk --size=10GB
```

> [!IMPORTANT]
>
> This applies to **ALL** `gcloud` commands, whether they are read-only
> (`gcloud ... list`) or mutations (`gcloud ... create`).

---

## Sub-Skill: managing-python-dependencies
# Python Dependency Management Rule

> [!CAUTION]
>
> **BEFORE any `pip install`**: You MUST first detect the project's existing
> dependency manager and use it correctly. Do NOT override the project's
> established tooling.

## Dependency Manager Detection

Before installing ANY Python package, check the workspace for these files **in
priority order**:

1.  **Signal:** `uv.lock` or `pyproject.toml` with `[tool.uv]`
    *   **Tool:** **uv**
    *   **Install:** `uv add <package>`
    *   **Setup:** `uv sync`
2.  **Signal:** `pyproject.toml` with `[tool.poetry]`
    *   **Tool:** **Poetry**
    *   **Install:** `poetry add <package>`
    *   **Setup:** `poetry install`
3.  **Signal:** `Pipfile`
    *   **Tool:** **Pipenv**
    *   **Install:** `pipenv install <package>`
    *   **Setup:** `pipenv install`
4.  **Signal:** `environment.yml`
    *   **Tool:** **Conda**
    *   **Install:** `conda install <package>`
    *   **Setup:** `conda env create -f environment.yml`
5.  **Signal:** `requirements.txt` only
    *   **Tool:** **venv + pip**
    *   **Install:** `.venv/bin/pip install <package>`
    *   **Setup:** `.venv/bin/pip install -r requirements.txt`
6.  **Signal:** None of the above
    *   **Tool:** **venv + pip** (default)
    *   **Install:** `.venv/bin/pip install <package>`
    *   **Setup:** `.venv/bin/pip install -r requirements.txt`

## Default: venv + pip

If no dependency manager is detected, use **venv + pip + requirements.txt** as
the default:

```bash
# Initialize environment
python3 -m venv .venv

# Add dependencies
.venv/bin/pip install <package>

# Preserve state
.venv/bin/pip freeze > requirements.txt
```

**Rules for venv + pip workflow:**

-   Always use `.venv/bin/pip` or `.venv/bin/python` (explicit path).
-   After installing, run: `.venv/bin/pip freeze > requirements.txt`.
-   When setting up: `.venv/bin/pip install -r requirements.txt`.

## Prohibited

-   **NEVER** run `pip install` globally
-   **NEVER** override an existing dependency manager with a different one

---

## Sub-Skill: ml-best-practices
# ML Best Practices

I want to read a story about the data, not just run code. Ensure every code cell
is followed by a markdown cell analyzing the results. End the notebook with a
summary comprehensively answering the prompt.

If there is a good match between the user's request and a corresponding example
plan, then adapt the example plan to fully answer the user's request:

## Clustering:

Identify distinct groups based on their features.

-   Understand the schema and field descriptions.
-   Visualize features referenced in the prompt (e.g., with histograms,
    scatterplots).
-   Transform dates into timestamps.
-   Before applying encoders, check if the dataset already contains pre-encoded
    features and prefer existing numerical representations.
-   Prefer to keep data instead of dropping it when possible.
-   Transform ordinal data with an ordinal encoder.
-   Transform nominal data with a one hot encoder.
-   Standardize numerical features.
-   Perform clustering with a range of values, and collect the silhouette score.
-   Choose the optimal number of clusters based on the silhouette score.
-   Use dimensionality reduction (e.g., PCA) to project the data into two
    dimensions.
-   Scatterplot the samples in two dimensions with cluster labels as the hue.
-   Scatterplot the samples in two dimensions with a discrete feature as the
    hue.
-   Describe the clusters in text by feature distributions or typical feature
    values.
-   Conclusion: comprehensively answer the prompt in a final markdown cell.

## Time Series Forecasting:

Develop a predictive model to estimate future values based on historical trends.
How might different modeling approaches impact the prediction accuracy?

-   Understand the schema and field descriptions.
-   Visualize the target feature over time at a reasonable granularity.
-   Always perform a chronological split on the data to create training,
    validation, and test sets.
-   Are there seasonal trends?
-   Test for stationarity.
-   Discuss possible modeling approaches. How might different modeling
    approaches impact the prediction accuracy?
-   Train two time series forecasting models to predict the target feature. Use
    previous seasonality and stationarity information as model hyperparameters.
-   Predict the target feature for the training and validation sets.
-   Optionally, hypertune models with the validation set.
-   Visualize the actual and predicted target feature vs time for each model on
    the training and validation sets.
-   Evaluate the validation performance with error metrics.
-   Select a model.
-   Retrain the selected model on the test and validation sets.
-   Predict the test values with the selected model.
-   Visualize the average target feature and the predicted test values.
-   Conclusion: comprehensively answer the prompt in a final markdown cell.

## Exploratory Data Analysis / Anomaly Detection:

Identify and describe any outliers, unusual patterns, or significant trends
observed in the data. Provide visualizations to support your findings.

-   Understand the schema and field descriptions.
-   Visualize the target feature distribution in a way that shows outliers.
-   Identify and describe any outliers in the target feature.
-   Visualize relationships between the target feature and other features.
-   Identify and describe unusual patterns or significant trends.
-   Visualize patterns and trends.
-   Conclusion: comprehensively answer the prompt in a final markdown cell.

## Classification:

Given the data, can we classify by the target feature?

-   Understand the schema and field descriptions.
-   Identify rows that don't make sense. How many are there and what do they
    contain?
-   Identify rows without a target value. How many are there and what do they
    contain?
-   Drop rows that don't match the schema or don't have the target value (if it
    is reasonable to do so).
-   Split data into training, validation, and test sets.
-   Create features to represent when data are missing, if this is meaningful.
-   Handle missing data. Prefer to keep data instead of dropping it when
    possible.
-   Before applying encoders, check if the dataset already contains pre-encoded
    features and prefer existing numerical representations.
-   Transform ordinal data with an ordinal encoder.
-   Transform nominal data with a one hot encoder.
-   Standardize numerical features.
-   Train multiple models.
-   If there is evidence of overfitting, regularize and retrain the model.
-   If there is evidence of underfitting, consider adding or engineering
    features.
-   Evaluate the models.
-   Create confusion matrices.
-   Conclusion: comprehensively answer the prompt in a final markdown cell.

## Regression:

Predict the continuous valued target feature.

-   Understand the schema and field descriptions.
-   Identify rows that don't make sense. How many are there and what do they
    contain?
-   Identify rows without a target value. How many are there and what do they
    contain?
-   Develop an understanding of the data and determine how to handle missing
    values. This should make sense in the business context.
-   Identify any potential sources of group leakage. Aggregate where appropriate
    to prevent this.
-   Visualize target feature.
-   Split data into training, validation, and test sets.
-   Handle missing data. Prefer to keep data instead of dropping it when
    possible.
-   Before applying encoders, check if the dataset already contains pre-encoded
    features and prefer existing numerical representations.
-   Transform ordinal data with an ordinal encoder.
-   Transform nominal data with a one hot encoder. Restrict high cardinality
    categorical features to a tractable size.
-   Standardize numerical features.
-   Train multiple models.
-   Visualize the actual vs predicted values on training and validation data.
-   If there is evidence of overfitting, regularize and retrain the model.
-   If there is evidence of underfitting, consider adding or engineering
    features.
-   Evaluate the model error.
-   Conclusion: comprehensively answer the prompt in a final markdown cell.

## Comparing ML Models:

Evaluate and compare multiple models to determine which is most suitable for
production based on predictive power, robustness, and viability.

-   Understand the schema and align metrics with business goals (e.g., cost of
    false positives vs. false negatives).
-   Establish baselines: define a naive baseline (majority class/mean) and a
    simple ML baseline (e.g., Logistic/Linear Regression).
-   Ensure rigorous validation: use identical, fixed data splits for all models
    and perform $k$-fold cross-validation.
-   If data is temporal, use chronological splits for validation.
-   Select and report metrics beyond accuracy (e.g., F1-Score, PR-AUC, MAE,
    RMSE) that reflect business impact.
-   Use bootstrapping to calculate 95% confidence intervals for key metrics to
    determine statistical significance.
-   Perform slice-based error analysis: evaluate model performance across key
    subpopulations and demographics to identify bias or specific failure modes.
-   Inspect and compare confusion matrices, residual plots, and calibration
    curves.
-   Evaluate operational trade-offs: consider inference latency, training time,
    compute cost, and model size.
-   Assess interpretability using tools like SHAP or LIME where transparency is
    required.
-   Conclusion: Recommend the optimal model for the specific use case,
    justifying the choice with both performance and production viability.

## No match:

-   Understand the schema and field descriptions.
-   Identify rows that don't make sense. How many are there and what do they
    contain?
-   Identify rows without a target value. How many are there and what do they
    contain?
-   Drop rows that don't match the schema or don't have the target value (if it
    is reasonable to do so).
-   Create features to represent when data are missing, if this is meaningful.
-   Handle missing data. Prefer to keep data instead of dropping it when
    possible.
-   Before applying encoders, check if the dataset already contains pre-encoded
    features and prefer existing numerical representations.
-   Transform ordinal data with an ordinal encoder.
-   Transform nominal data with a one hot encoder.
-   Standardize numerical features.
-   Conclusion: comprehensively answer the prompt in a final markdown cell.

## Essential ML Practices

[!IMPORTANT] ALWAYS follow these ML practices

-   **Strict Featurization Ordering**: For supervised learning **ALWAYS** split
    the dataset into training and test data **BEFORE** fitting preprocessing
    pipelines (e.g. scaling, encoding). Fit the pipelines on the training data
    and test data independently.

-   **Handling Missing or NULL Values**: **ALWAYS** check for and handle missing
    and NULL values. First, analyze their frequency. Then, decide whether to
    keep them, drop them or impute them with a contextually appropriate value,
    and explain your reasoning.

---

## Sub-Skill: notebook-guidance
# Notebook Guidance

## When to Use a Notebook

Before choosing to use a notebook, evaluate the task complexity using these
heuristics.

Use a notebook if you meet at least one of these criteria:

*   📈 **Data Insights & Storytelling**: Use a notebook for any request to "give
    insights", "find trends", "explore data", or "analyze data". These tasks
    benefit from using visualizations to present the data.
*   📊 **Visualizations are requested**: The user explicitly asks for charts or
    plots.
*   🔄 **Stateful / Iterative Exploration**: You need to run a query, inspect
    results, and decide the next query based on those results while keeping
    state in memory.

Do NOT use a notebook ONLY if:

*   📝 **Simple Fact/Status**: The request only requires a single number (e.g.,
    "how many rows") or a status check (e.g., "when was this table updated").
*   🏃‍♂️ **Schema Preview**: The request is only about the schema or field
    types.

**Golden Rule of Data Storytelling:** If any analytical insight, trend, or
comparison is involved, favor a notebook and a visualization. A notebook is the
"standard" environment for our developer workflow; do not avoid it because of
"overhead".

## Notebook Best Practices

> [!IMPORTANT]
>
> **Agent execution rules**: Your behavior MUST depend on whether the
> `notebook_execute_cell` tool is available in your current context: * **If
> notebook `execute_cell` tool is available**: You MUST follow the incremental
> GENERATE CELL -> EXECUTE CELL -> VALIDATE flow. * **If notebook `execute_cell`
> tool is NOT available**: You MUST generate the complete notebook and request
> user execution.

1.  **CONDITIONAL EXECUTION FLOW**:
    *   **If notebook `execute_cell` tool is available**: Follow the **STEP BY
        STEP GENERATE CELL -> EXECUTE CELL -> VALIDATE OUTPUT** flow. Generate
        ONE cell, execute it, then verify the output. If the output is data
        (e.g. a dataframe), you MUST inspect it to confirm the logic is correct
        before generating the next step. Batch generation of an entire notebook
        is strictly prohibited because error propagation in notebooks is
        expensive to fix.
    *   **If notebook `execute_cell` tool is NOT available**:
        *   Create the whole notebook at once.
        *   Tell the user to run the notebook.
        *   Tell the user to let you know once the notebook run is completed so
            you can check the outputs to verify it's correct and fix any errors.
2.  **IDENTIFY DATA EARLY**: Use `@skill:discovering-gcp-data-assets` or
    BigQuery list tools to find the correct `project.dataset.table` before
    writing ANY code. If the table ID is missing, ask the user.
3.  **CLEAN FINAL STATE**: The final notebook MUST NOT have failed cells. If a
    cell fails, you MUST fix it. If you tried several versions, delete the
    failed attempts before you present the notebook to the user.
4.  **LOGICAL CHUNK FIDELITY**: Keep cells small. One logical transformation or
    visualization per cell. Group related cells into logical units (e.g., a
    BigQuery `%%bqsql` magic cell followed immediately by a Python visualization
    cell for those results). Use descriptive **markdown cells** to separate and
    document different logical sections.
5.  **GENERATE VISUALIZATIONS**: Always accompany data insights with
    visualizations; charts are often more effective than raw numbers for
    communicating trends and comparisons.

## Kernel & Environment Management

Notebooks run in specific **Kernels** (execution backends). You MUST ensure the
kernel’s Python environment contains the necessary libraries (`bigframes`,
`ipykernel`, etc.).

### Kernel Types

1.  **Local Python**: Standard Python 3 kernel running on the notebook host
    (Managed instance, local machine).
2.  **Cloud Spark Remote (Dataproc Serverless)**: Transient Spark environment
    managed by GCP. Use for large-scale data processing.
3.  **Cloud Spark Remote (Dataproc Cluster)**: Persistent Spark clusters for
    shared or custom configurations.
4.  **Colab (Managed)**: Ephemeral Google-managed runtimes.

### No Active Kernel / Setup Check

1.  **Infer or Ask about Kernel Preferences**:
    -   **Infer from Context**:
        -   If the task mentions "Spark", "PySpark", or "distributed compute",
            or if the active workspace is already a Spark cluster, lean towards
            **Remote Spark**.
        -   If the task is focused on "BigQuery", "BigFrames", or standard API
            calls, lean towards **Local Python**.
    -   **Ask when Ambiguous**: If multiple options fit, ask if they prefer a
        **Local Python** or a **Cloud/Remote Kernel** (e.g., Colab, Spark).
2.  **For Local Setup**: Use `@skill:managing-python-dependencies` to verify if
    a virtual environment exists. If not, create one. Ensure `ipykernel` is
    installed in that environment. Install any other relevant libraries.
3.  **For Remote Setup**: Advise the user to use the UI to select the
    appropriate remote kernel.

> [!IMPORTANT]
>
> **HARD STOP on kernel failure**: If a cell execution returns "no active
> kernel" or any kernel-not-found error, you MUST **stop immediately**. Do NOT
> scaffold, generate, or insert any further cells. Inform the user which kernel
> is needed (e.g., PySpark / Dataproc Serverless) and wait for explicit
> confirmation that a kernel is active before proceeding with notebook
> execution.

### Proper Library Installation

#### 1. Local Kernels

Before installing any python libraries, you MUST use
`@skill:managing-python-dependencies` to detect how python dependencies are
managed in the project.

#### 2. Remote Kernels (Spark/Colab)

Since these are often ephemeral or managed by GCP:

*   **Check first (REQUIRED)**: Before writing any `%pip install` cell, run
    `%pip list` or `import <package>` to confirm the package is not already
    present. Managed runtimes (Dataproc Serverless, Colab) pre-install many
    common packages. Only install what is confirmed missing.
*   Use `%pip install <package>` in the first cell if a package is confirmed
    missing and it's the only way to modify the runtime.

When in doubt about the kernel type or preferred installation method, ask the
user for clarification.

## Data Analysis & Visualization Rules

Guidelines for performing exploratory data analysis, data cleaning, and
visualization in notebooks.

### Notebook Layout

The notebook should read like a story. While you have flexibility (e.g.,
multiple visualizations for one data cell, or data cells building on each
other), aim for this general flow:

1.  **Title & Objective** (Markdown Cell)
    *   What is this notebook for? (e.g., `# Retention Analysis`)
2.  **Section Header** (Markdown Cell)
    *   What are we looking at now? (e.g., `## Exploring User Retention`)
3.  **Data Acquisition/Transformation** (Python cell, may contain `%%bqsql`
    magics)
    *   Query BigQuery or transform data.
4.  **Verification (Optional but Recommended)** (Python Cell)
    *   `df.head()` or assert sanity checks.
5.  **Visualization (The Goal)** (Python Cell)
    *   Plot the insight (e.g., `df.plot()`).

*Repeat steps 2-5 for each new sub-topic or insight. You can have multiple Data
cells before a Visualization, or multiple Visualizations from one Data cell. The
key is to keep them grouped logically and separated by Markdown headers.*

1.  **Final Summary** (Markdown Cell)

    *   At the end of the notebook, add a markdown cell containing a summary
        paragraph that summarizes the findings to the user. The summary MUST
        follow these guidelines:
    *   MUST NOT add Python code to the summary.
    *   The summary MUST NOT start with a code block.
    *   The summary MUST be strictly grounded in the numerical data verified in
        the notebook.
    *   The summary MUST ONLY contain the following three sections:
        *   ### Q&A If the data analysis task contains questions (implied or
            explicit), you MUST answer them based on the solving process. Skip
            this section if there are no questions to answer.
        *   ### Data Analysis Key Findings Summarize the key analysis findings
            in bullet points, it's a plus to quote the numbers in the previous
            steps. Only report high-value findings, skip the obvious ones.
        *   ### Insights or Next Steps Provide 1-2 concise insights or next
            steps in bullet points.

2.  **Next Steps**: After the notebook has been successfully executed and
    verified, and the summary is complete, notify the user and propose next step
    suggestions.

### Plotting Rules

1.  You MUST use different colors for different features to ensure plots are
    readable for humans.
2.  When creating a plot, you MUST adjust the figure size based on the number of
    features. The labels and legends MUST NOT overlap.
3.  You SHOULD arrange the layout wisely. Using subplots CAN help in placing
    different plots effectively.
4.  You MUST use inline figures to present figures and plots along with code and
    text in the notebook.
5.  For clustering, use PCA to reduce to 2D before scatter plotting.
6.  Use **Line Charts** ONLY for continuous data (e.g. time series) where
    interpolation between points is meaningful.

### Data Cleaning Rules

1.  You MUST be careful about missing values and duplicated values.
2.  You MUST NOT drop columns unless absolutely necessary. Dropping columns is
    irreversible.
3.  You SHOULD focus on columns directly related to accomplishing the task; not
    every column NEEDS to be cleaned.

## Specialized Notebook Guidance

Refer to the following resources for guidance on specific notebook topics:

### 1. BigQuery in Notebooks

Use BigFrames magics `%%bqsql` for BigQuery SQL queries. These cells support
native BigQuery SQL execution and data export to BigFrames dataframes.

> [!IMPORTANT]
>
> *   Unless specified by the user, **always use SQL for querying BigQuery.**
> *   DO NOT use the standard BigQuery Python client library
>     (`google.cloud.bigquery`) or `pandas.read_gbq`.
> *   **Mandatory dataframe export**: Always provide a dataframe name e.g.
>     `%%bqsql <df_name>`. This makes it easy to use results in follow up Python
>     cells.
> *   Verify that `bigframes` version number `2.38.0` and above is installed in
>     the notebook runtime environment. If it is missing, ask the user if they
>     would like you to upgrade for them.

**Example %%bqsql magic usage:**

```python
# Initialize BigFrames and load %%bqsql magics
import bigframes
import bigframes.pandas as bpd
%load_ext bigframes
```

> [!CAUTION]
>
> Always use `%load_ext bigframes` exactly as shown. Do not load submodules —
> for example, `%load_ext bigframes.magics` or `%load_ext bigframes.bigquery`
> are not valid and must not be used.

> [!IMPORTANT]
>
> The `bigframes` library must be installed. Determine if bigframes needs to be
> installed by following @skill:managing-python-dependencies.

```python
%%bqsql df_sample
SELECT * FROM `project.dataset.table` LIMIT 10
```

#### Anti-patterns (NEVER DO THESE)

> [!CAUTION]
>
> 1.  **NO Python SDK for Queries**: Do not switch to
>     `client.query(sql).to_dataframe()` if SQL fails. Fix the SQL syntax
>     instead.
> 2.  **NO Mixing Logic**: Do not put Python code in the same cell as `%%bqsql`
>     magics.

#### Working with SQL Results in Python

Magic cells with `%%bqsql <df_name>` produce a **BigQuery DataFrame**. In
subsequent cells, you can use `<df_name>` directly.

> [!IMPORTANT]
>
> You MUST use BigFrames for data exploration, manipulation, splitting etc. You
> MUST use BQML SQL or bigframes.ml for machine learning tasks. You MUST NOT use
> pandas or Scikit-learn.

##### BigQuery DataFrame Tips

*   **Avoid `.to_pandas()`**: You MUST NOT use `.to_pandas()` to download the
    entire dataset into memory. There are some exceptions:
    *   An error message explicitly requests you to use `to_pandas()`
    *   You are going to visualize the data, **and** the visualization library
        does not accept BigFrames Dataframe/Series instances. In this case,
        reduce the amount of data you are going to download before calling
        `.to_pandas()`
*   **Avoid `read_gbq()` for SQL**: Do not write SQL queries and execute them
    with `read_gbq()`. Use BigFrames Dataframe/Series methods instead.
*   **Use BigFrames ML package for Machine Learning Tasks**: Do not use
    Scikit-learn or other ML libraries with BigFrames dataframes. Import your
    tools/classes from `bigframes.ml`.
*   **Stay in the Cloud**: Perform data cleaning, transformation, and analysis
    via BigFrames methods to leverage BigQuery's scale.
*   **Accessors over UDFs/Lambdas**:
    *   Prefer built-in accessors (e.g., `df.col.str.*`, `df.col.dt.*`) over
        remote UDFs.
    *   **Do not use lambdas** with `Series.map()` or `DataFrame.apply()`.
*   **Schema Verification**: Do not assume schema of intermediate outputs. Check
    `.dtypes` after loading, and use `display()` with `.head()` or `.peek()`.
*   **Visualization**: BigFrames Dataframe mostly works directly with
    Matplotlib, Seaborn, and other plotting libraries. If your attempt didn't
    work, try using the "plot" accessor. If that didn't work either, you MUST
    sample or aggregate your data to make it small enough before calling
    "to_pandas()".
*   **Model Persistence**: To persist a model. use `model.to_gbq()`. To load a
    persisted model, use `bpd.read_gbq_model()`.

### 2. Machine Learning in Notebooks

Integration with machine learning workflows and best practices. - **Guide**: Use
`@skill:ml-best-practices`. - **MUST READ WHEN**: The task involves machine
learning, training a model, clustering, classification, regression, or
time-series forecasting.

If any "MUST READ WHEN" condition is met, you MUST read the corresponding guide
before proceeding.

---

## Sub-Skill: skill-repair
# Skill Repair Assistant

You have been tasked with fixing a broken agent skill. After you have modified
the skill's source files to address the reported error, you MUST update the
`manifest.json` to reflect that the skill is now repaired.

## Skill Context

-   **Skill ID**: The unique identifier for the skill (e.g., `my-skill`).
-   **Source Path**: Where the skill's source files are located.
-   **Installed Path**: Where the skill is installed/replicated.
-   **Manifest Path**: The absolute path to the `manifest.json` file.

## Repair Procedure

1.  **Analyze Error**: Understand the error message provided in the prompt.
2.  **Fix Installed Path**: Fix the issue at the installed path. Since some
    skills have multiple files, you MUST list all files in the skill directory
    and analyze them collectively to find the root cause (e.g., malformed
    `SKILL.md`, missing resources, or incorrect sub-scripts).
3.  **Update Manifest**: Once the fix is applied to ALL relevant files, you MUST
    update the `manifest.json` at the **Manifest Path**.
    -   Find the entry for the skill ID in the `skills` object.
    -   Set `"status": "installed"`.
    -   Clear the `"error"` field (set to `null` or remove it).
4.  **Verification**: The UI will automatically detect this change and refresh.

### Manifest Example

```json
{
  "skills": {
    "my-skill": {
      "status": "installed",
      "disabled": false,
      "error": null
    }
  }
}
```

---

## Sub-Skill: fullstack-firebase-forge
# Fullstack Firebase Forge

Guides the design of real-time web architectures, database schemas, and modern UI performance profiles.

## 1. Firebase Data Structures
- **Firestore (NoSQL):** Model hierarchical collections, subcollections, and write security rules.
- **Data Connect (GraphQL):** Configure relational PostgreSQL backends with generated SDK mappings.

## 2. Modern Web & Styling
- Apply vanilla CSS with strict hierarchical page/component scoping.
- Implement layout best practices: container queries, scroll-driven animations, view transitions.
- Optimize Largest Contentful Paint (LCP) and interaction metrics (INP).

---
