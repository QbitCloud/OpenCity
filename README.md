# OpenCity

*All are accountable to all*

OpenCity is a dashboard for Surat city. It collects public data about schools, courts, hospitals, money and water, and shows it in one place. When something looks wrong, it helps you write an RTI (Right to Information) request about it.

## Why we made this

Information about government progress/work is not easy to access, the citizens need a clearer view of public services and a way to ask for information when they find gaps. 


OpenCity tries to fix both:

- It puts public data together, so problems are easy to see.
- It helps you ask the government about a problem by writing a draft RTI for you.

## What it covers

- **Area:** Surat city or Surat district, depending on the data source.
- **Topics:** schools, courts, health, finance and water quality, plus a list of the officials responsible for them.

| Page | Where the data comes from |
|---|---|
| Schools | UDISE+ (students, teachers and buildings) |
| Courts | NJDG cases and IJR (3rd party) |
| Health | Surat NIC official site |
| Finance | Surat Municipal Corporation official site |
| Water | Surat Municipal Corporation official site |
| Officials | SMC contacts, grouped by department |

## What you can do with it

- See a score for Surat on the Home page.
- Open a page for each topic and look at charts and numbers.
- See a list of problems. For example, a school facility that less than 70% of schools have.
- Click a problem to see its value, the time period, and the officials in charge.
- Get a draft RTI written for that problem.
- Read the Sources page to see where every number and score comes from.

## How we score things

- **Schools:** we use some of the government's PGI-D weights for the data we have.
- **Water:** the share of water samples that passed, put into score bands.
- **Finance, courts and health:** each has its own simple baseline.

These scores are our own estimates. They are not official scores.

## How the RTI helper works

1. Open a problem and look at its details.
2. A small AI model running on your own computer (through Ollama) writes a draft RTI.
3. Our browser extension keeps the draft while you log in to the Gujarat RTI portal, then fills in the form for you.
4. You read the draft, fix anything you want, and submit it yourself.

Courts use a different RTI portal, so the extension does not fill in court requests.

## Tools we used

| Part | Tools |
|---|---|
| Getting and reading data | Python, requests, BeautifulSoup, pdftotext, regex |
| Database | MongoDB Atlas, PyMongo |
| API server | FastAPI, Uvicorn |
| Dashboard and charts | Streamlit, pandas, Matplotlib |
| RTI drafts | CrewAI, Ollama (qwen3:0.6b) |
| Automation | Bash, a JavaScript browser extension |

## Folders

```
OpenCity
├── PIPELINE/            one folder per topic, each downloads and saves its data
├── SERVER/              the API server (FastAPI)
│   ├── api/routes.py    the API addresses the dashboard calls
│   └── services/        code that reads data for each topic and writes RTI drafts
├── UI/                  the dashboard (Streamlit)
│   ├── app.py           start here
│   ├── screens/         one file per page
│   ├── analysis/        numbers, scores and baselines for each page
│   └── components/      chart code
├── browser-extension/   fills in the RTI form on the Gujarat portal
├── scripts/             scripts to start the app and run the pipelines
└── opencity_settings.py reads settings from the .env file
```

## How to run it

### What you need

- Python 3
- A MongoDB database (we used MongoDB Atlas)
- `pdftotext` (from poppler-utils), for the water and finance data
- [Ollama](https://ollama.com) with the `qwen3:0.6b` model, for RTI drafts
- Google Chrome (or another Chromium browser), for the RTI extension

### 1. Install

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r SERVER/requirments.txt -r UI/requirements.txt
pip install -r PIPELINE/court_pipeline/requirements.txt \
            -r PIPELINE/health_pipeline/requirements.txt \
            -r PIPELINE/hospital_pipeline/requirements.txt \
            -r PIPELINE/officials_pipeline/requirements.txt \
            -r PIPELINE/school_pipeline/requirements.txt \
            -r PIPELINE/water_and_finance_pipeline/requirements.txt

ollama pull qwen3:0.6b
```

### 2. Add your settings

Make a file called `.env` in the main folder:

```
API_PORT=8000
UI_PORT=8501
MONGODB_URI=<your MongoDB connection string>
MONGODB_DB=opencity
FINANCE_CSV_PATH=data/export/observations/smc_balance_sheet.csv
```

### 3. Load the data

Run each pipeline once to fill the database:

```bash
bash scripts/run-school.sh
bash scripts/run-health.sh
bash scripts/run-hospital.sh
bash scripts/run-court.sh
bash scripts/run-officials.sh
bash scripts/run-water-and-finance.sh
```

### 4. Start the app

```bash
bash scripts/run-app.sh
```

This starts the API server and the dashboard. Open the link it prints (for example `http://localhost:8501`). Press Ctrl+C to stop everything.

While it is running, it also refreshes all the data on the 1st of every month. The log is saved in `data/logs/pipelines.log`.

Make sure Ollama is running if you want RTI drafts.

### 5. Add the browser extension (for RTI)

1. Open `chrome://extensions` in Chrome.
2. Turn on **Developer mode**.
3. Click **Load unpacked** and pick the `browser-extension` folder.

## Limitations

- Different sources cover different time periods and areas (city or district).
- Not every number has a baseline to compare it with.
- You must read and check every RTI draft before you send it.
- The extension does not work with the court RTI portal.
- If a government website changes, its pipeline may stop working.

## Team

| Name | Roll no. | Work |
|---|---|---|
| Deva Narayana Babu | 26M0797 | Court and hospital pipelines, APIs, dashboards and baselines. Overview (Home) page. |
| Parthsinh Thakor | 26M0796 | School, health and officials pipelines, APIs, dashboards and baselines. RTI module. |
| Deepak Sharma | 26M0741 | Finance and water pipelines, APIs and dashboards. Finance baseline. |

Made for the CS699 course project.

## Use of AI

We used AI tools to help with:

- the RTI browser extension
- finding data sources and scoring references
- code that turns Gujarati numbers into normal numbers
- the Surat map on the Home page
- the system diagram
- some of the harder charts

## License

MIT. See [LICENSE](LICENSE).
