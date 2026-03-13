# Real Estate & Demographics

A data-driven Flask web application that explores the intersection of US housing markets and demographic trends. It ingests raw data from the **US Census Bureau** and **Zillow**, transforms and cleans it with Pandas, generates 20+ interactive Plotly visualizations, and uses a TensorFlow/Keras neural network to predict home values across all 50 states and DC.

**Live site:** [data.saadyaldram.com](https://data.saadyaldram.com)

---

## Architecture

![architecture diagram](docs/architecture.svg)

| Layer | Technology |
|---|---|
| Web Server | Nginx (reverse proxy, port 80/443) |
| App Server | Gunicorn (WSGI, binds to localhost:8000) |
| Application | Flask 3.x, Jinja2 templates |
| Data & Viz | Pandas 3.x, Plotly 6.x |
| ML | TensorFlow / Keras (deep neural network) |
| Infrastructure | AWS EC2, CloudFront, Route 53, ACM |
| IaC | Terraform (S3 + DynamoDB remote state) |
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
│   ├── graphs.py              # Choropleth maps, housing, and birth charts
│   ├── graph_generator.py     # Population pyramids, mortgage, income, and tax charts
│   ├── constants.py           # State abbreviations, theme config, Plotly options
│   ├── requirements.txt       # Python dependencies
│   ├── data/                  # Raw CSV/Excel datasets from ACS
│   ├── templates/
│   │   ├── index.html         # Main dashboard (US overview + state drill-down)
│   │   └── predictions.html   # ML model documentation and results
│   └── static/
│       ├── assets/            # CSS, JS, fonts, images
│       └── charts/            # Pre-rendered Plotly HTML (ML charts)
├── Terraform/
│   ├── main.tf                # Provider config, S3 backend
│   ├── server.tf              # EC2, security group, IAM, CloudFront
│   ├── variables.tf           # Input variables
│   └── outputs.tf             # EC2 public IP, SSH command
├── scripts/
│   └── gunicorn.service.sh    # systemd service file for Gunicorn
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

# Run the development server
cd app
python app.py
```

The app will be available at `http://127.0.0.1:5001`.

---

## Deployment

The application runs on an **AWS EC2** instance behind **Nginx** (reverse proxy) and **Gunicorn** (WSGI server), with **CloudFront** providing CDN and HTTPS termination.

### Infrastructure (Terraform)

All AWS resources are provisioned with Terraform. State is stored remotely in S3 with DynamoDB locking.

**Resources created:**
- EC2 instance (Ubuntu) with SSH key pair
- Security group (ports 22, 80, 443)
- IAM role and instance profile (CloudWatch Logs access)
- CloudFront distribution with a custom domain and ACM certificate

```bash
cd Terraform
terraform init
terraform plan
terraform apply
```

### Server Setup

Once the EC2 instance is running:

1. **SSH into the instance** using the output from `terraform output ssh_command`.
2. **Clone the repo** and create a Python virtual environment inside `app/`.
3. **Install dependencies** with `pip install -r requirements.txt` and additionally install `gunicorn`.
4. **Configure Gunicorn** as a systemd service (see `scripts/gunicorn.service.sh`).
5. **Configure Nginx** as a reverse proxy forwarding traffic to `localhost:8000`.
6. **Enable and start** both services:
   ```bash
   sudo systemctl enable gunicorn
   sudo systemctl start gunicorn
   sudo systemctl restart nginx
   ```

### DNS & SSL

- **Route 53** manages the `data.saadyaldram.com` DNS record, pointing to the CloudFront distribution.
- **AWS ACM** provides the SSL certificate, and CloudFront enforces HTTPS via `redirect-to-https`.

---

## Dependencies

| Package | Version | Purpose |
|---|---|---|
| Flask | 3.1.2 | Web framework |
| Pandas | 3.0.0 | Data manipulation and cleaning |
| Plotly | 6.5.2 | Interactive chart generation |
| openpyxl | 3.1.5 | Excel file reading (fertility data) |