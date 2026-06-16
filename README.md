# Real Estate & Demographics

A data-driven static web site that explores the intersection of US housing markets and demographic trends. It ingests raw data from the **US Census Bureau** and **Zillow**, transforms and cleans it with Pandas, generates 20+ interactive Plotly visualizations, and uses a TensorFlow/Keras neural network to predict home values across all 50 states and DC.

**Live site:** [data.saadyaldram.com](https://data.saadyaldram.com)

---

## Architecture

![architecture diagram](docs/architecture.svg)

| Layer | Technology |
|---|---|
| CDN / HTTPS | CloudFront (custom domain, ACM cert) |
| Origin | Private S3 bucket via Origin Access Control |
| Build | Flask 3.x + Frozen-Flask (pre-renders every page to HTML) |
| Data & Viz | Pandas 3.x, Plotly 6.x (server-side at build time) |
| ML | TensorFlow / Keras (offline training, predictions baked into the build) |
| Infrastructure | AWS S3, CloudFront, Route 53, ACM, IAM (OIDC) |
| IaC | Terraform (S3 + DynamoDB remote state) |
| Deploy | GitHub Actions on push to `main` |
| Frontend | Bootstrap 5, jQuery, custom CSS/JS |

---

## Features

- **National overview** — choropleth maps and bar charts covering home affordability, median prices, income, tax burden, mortgage payments, housing units, household size, and birth rates across the US.
- **State-level drill-down** — select any state to view its population pyramid, birth trends, income distribution, home values, property characteristics, bedroom breakdown, and taxes.
- **ML predictions** — a dedicated page documenting the deep learning model, training process, evaluation metrics, and predicted home values per state.
- **Interactive charts** — all visualizations are Plotly-powered with hover tooltips, zoom, and pan.
- **Dark / light theme toggle** — user-selectable color scheme with a persistent toggle.
- **Responsive design** — mobile-friendly layout using Bootstrap 5.

---

## Data Sources

All data comes from public sources. The 2020 survey year is excluded because the ACS did not publish estimates that year due to the pandemic.

| Dataset | Source | Format |
|---|---|---|
| Sex by Age (2022) | ACS | CSV |
| Average Household Size (2012, 2022) | ACS | CSV |
| Financial & Mortgage Data (2019, 2022) | ACS | CSV |
| Physical Housing Occupancy | ACS | CSV |
| Household Income (2022) | ACS | CSV |
| Income in Past 12 Months | ACS | CSV |
| Fertility / Birth Rates (2010–2022) | ACS | Excel |
| Home Value Index | Zillow | Pre-computed charts |

Source: [American Community Survey (ACS)](https://www.census.gov/programs-surveys/acs/data.html)

---

## Machine Learning Model

The predictions page uses a Keras `Sequential` neural network trained on demographic and housing features to forecast home values.

**Features used:**
- Total births per year
- Average household size
- Median mortgage loan financed per state
- Median household income per state
- Median monthly housing cost per state
- Median real estate taxes per state
- Number of occupied housing units per state
- Zillow Home Value Index per state

**Model architecture:**
- 5 hidden layers (10 neurons each, ReLU activation, 20% dropout)
- Adam optimizer, MSE loss
- Early stopping on validation loss (patience = 25)
- 75/25 train-test split with MinMaxScaler normalization

**Evaluation results:**

| Metric | Value |
|---|---|
| RMSE | $66,474 |
| MAE | $45,797 |
| Explained Variance | 85.4% |

---

## Project Structure

```
RealEstate-vs-Demographics/
├── app/
│   ├── app.py                 # Flask routes and entry point
│   ├── freeze.py              # Frozen-Flask build script (renders site to ../build/)
│   ├── graphs.py              # Choropleth maps, housing, and birth charts
│   ├── graph_generator.py     # Population pyramids, mortgage, income, and tax charts
│   ├── constants.py           # State abbreviations, theme config, Plotly options
│   ├── requirements.txt       # Python dependencies (build-time)
│   ├── data/                  # Raw CSV/Excel datasets from ACS
│   ├── templates/
│   │   ├── index.html         # Main dashboard (US overview + state drill-down)
│   │   ├── predictions.html   # ML model documentation and results
│   │   └── 404.html           # Custom not-found page
│   └── static/
│       ├── assets/            # CSS, JS, fonts, images
│       └── charts/            # Pre-rendered Plotly HTML (ML charts)
├── Terraform/
│   ├── main.tf                # Provider config, S3 backend
│   ├── s3.tf                  # Private site bucket + OAC bucket policy
│   ├── cloudfront.tf          # Distribution, OAC, alias, ACM cert, 404 mapping
│   ├── route53.tf             # A/AAAA ALIAS records → CloudFront
│   ├── iam.tf                 # GitHub Actions OIDC provider + deploy role
│   ├── variables.tf           # Input variables
│   └── outputs.tf             # Bucket name, distribution ID, role ARN, etc.
├── .github/workflows/
│   └── deploy.yml             # Build + sync to S3 + CloudFront invalidation
├── Makefile                   # build / serve / clean targets
└── docs/
    └── flask-app.png          # Architecture diagram
```

---

## Getting Started

### Prerequisites

- Python 3.10+
- pip

### Local Development

```bash
# Clone the repository
git clone https://github.com/syaldram/RealEstate-vs-Demographics.git
cd RealEstate-vs-Demographics

# Create a virtual environment and install dependencies
python -m venv .venv
source .venv/bin/activate
pip install -r app/requirements.txt

# Option A: run the Flask dev server (live reload, dynamic routes)
cd app && python app.py
#   -> http://127.0.0.1:5001

# Option B: build the static site and serve it locally
make build && make serve
#   -> http://127.0.0.1:8000
```

---

## Deployment

The site is a fully static bundle hosted on **S3** behind a **CloudFront** distribution. There is no application server, no SSH, and no long-lived AWS credentials in GitHub.

### Infrastructure (Terraform)

All AWS resources are provisioned with Terraform. State is stored remotely in S3 with DynamoDB locking.

**Resources created:**
- Private S3 bucket (origin) with OAC-only bucket policy
- CloudFront distribution (HTTPS, custom domain, `/404.html` error mapping)
- Route 53 A + AAAA ALIAS records for `data.saadyaldram.com`
- IAM OIDC provider + deploy role for GitHub Actions

```bash
cd Terraform
terraform init
terraform plan
terraform apply
```

Required variables (pass via `terraform.tfvars` or `-var`):

| Variable | Example |
|---|---|
| `bucket_name` | `data-saadyaldram-com-site` |
| `domain_name` | `data.saadyaldram.com` |
| `hosted_zone_name` | `saadyaldram.com` |
| `certificate_arn` | ACM cert ARN in `us-east-1` covering the domain |
| `github_repo` | `syaldram/RealEstate-vs-Demographics` |

### GitHub Actions deploy

`.github/workflows/deploy.yml` runs on every push to `main` that touches `app/`. It builds the static site with `make build`, assumes the deploy role via OIDC, syncs `build/` to S3, and invalidates the CloudFront cache.

Configure these **repository variables** (Settings → Secrets and variables → Actions → Variables) using the Terraform outputs:

| Variable | Source |
|---|---|
| `AWS_DEPLOY_ROLE_ARN` | `terraform output github_actions_role_arn` |
| `S3_BUCKET` | `terraform output bucket_name` |
| `CLOUDFRONT_DISTRIBUTION_ID` | `terraform output cloudfront_distribution_id` |

### DNS & SSL

- **Route 53** records are managed by Terraform (`route53.tf`).
- **AWS ACM** provides the SSL certificate (must already exist in `us-east-1`); CloudFront enforces HTTPS via `redirect-to-https`.

---

## Dependencies

| Package | Version | Purpose |
|---|---|---|
| Flask | 3.1.2 | URL routing + template rendering (build time only) |
| Frozen-Flask | 1.0.2 | Walks every route and writes static HTML to `build/` |
| Pandas | 3.0.0 | Data manipulation and cleaning |
| Plotly | 6.5.2 | Interactive chart generation |
| openpyxl | 3.1.5 | Excel file reading (fertility data) |