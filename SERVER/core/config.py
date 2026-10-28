"""Where the API finds its data, and the limits it puts on requests. Override the database with OPENCITY_DB."""
import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = Path(os.environ.get('OPENCITY_DB', REPO_ROOT / 'data' / 'opencity.db'))
COVERAGE_CSV = REPO_ROOT / 'docs' / 'ftp-coverage.csv'
ADAPTERS_DIR = REPO_ROOT / 'pipeline' / 'opencity' / 'sources'

API_VERSION = '1.0.0'
MAX_LIMIT = 10000          # largest page size any list endpoint returns
MAX_OFFSET = 10 ** 9       # larger offsets overflow SQLite integers
MAX_FILTERS = 20           # dim= or attr= filters per request
MAX_SEARCH = 200           # characters in a q= search
