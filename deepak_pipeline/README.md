# Deepak Pipeline

This pipeline collects public data for the OpenCity dashboard. The first step is to find and store official historic finance documents.

It has two parts:

1. **Finance**  
   It collects Surat Municipal Corporation balance-sheet PDFs and reads important yearly values such as income, expenditure, tax revenue, and surplus.

2. **Drinking Water Quality**  
   It collects monthly Surat Municipal Corporation water-quality reports and reads the number of water samples collected, fit samples, and unfit samples.

## Finance discovery

Run this from the repository root:

```bash
python3 -m pip install -r deepak_pipeline/requirements.txt
bash scripts/run-deepak.sh
```

The command saves the official SMC balance-sheet links in a local SQLite database at `data/deepak_finance.db`. That file is ignored by Git.

## Planned workflow

1. The scraper finds official SMC documents.
2. The parser reads useful values from the documents.
3. The database saves the values without duplicates.
4. The API sends the saved data to the dashboard.
5. The dashboard shows charts and latest values.

## Data sources

- SMC Balance Sheet page  
  https://www.suratmunicipal.gov.in/Departments/Accounts/BalanceSheet

- SMC Water Quality page  
  https://www.suratmunicipal.gov.in/Departments/HydraulicWaterQuality

## Expected dashboard output

- Finance trend: income and expenditure across financial years.
- Latest finance summary: income, expenditure, tax revenue, and surplus.
- Water-quality trend: monthly compliance and unfit-sample count.
- Source links for every value shown.

This pipeline uses only official public SMC data. Local database files and downloaded documents are not committed to Git.
