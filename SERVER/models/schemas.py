"""Response shapes. FastAPI publishes them in the OpenAPI schema at /docs and /openapi.json."""
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class Root(BaseModel):
    message: str
    status: str = Field(..., description='ok, or no_database when data/opencity.db is missing')
    version: str
    docs: str


class Place(BaseModel):
    geo_level: str
    geo_code: str
    name: Optional[str] = None
    parent_level: Optional[str] = None
    parent_code: Optional[str] = None
    note: Optional[str] = None


class GeoLevel(BaseModel):
    geo_level: str
    places: int


class MetricSummary(BaseModel):
    metric_id: str
    label: Optional[str] = None
    unit: Optional[str] = None
    module: Optional[str] = None
    source_id: str
    description: Optional[str] = None
    observations: int = 0
    reported: int = Field(0, description='observations with a value (status reported)')
    first_period: Optional[str] = Field(None, description='earliest period_start')
    last_period: Optional[str] = Field(None, description='latest period_end')
    geo_levels: List[str] = []


class SourceRef(BaseModel):
    source_id: str
    name: Optional[str] = None
    publisher: Optional[str] = None
    url: Optional[str] = None


class MetricDetail(MetricSummary):
    source: SourceRef
    dims: Dict[str, List[str]] = Field({}, description='each breakdown key with every value it takes')
    places: List[Place] = []


class SourceSummary(BaseModel):
    source_id: str
    name: Optional[str] = None
    publisher: Optional[str] = None
    url: Optional[str] = None
    module: Optional[str] = None
    cadence: Optional[str] = None
    enabled: bool
    status: str = Field(..., description='ok, error, disabled or not_run')
    last_success: Optional[str] = None
    last_status: Optional[str] = None
    errors_last_run: int = 0
    observations: int = 0
    records: int = 0
    metrics: int = 0
    latest_period: Optional[str] = None
    notes: Optional[str] = Field(None, description="maintainers' notes, e.g. why a source is disabled")


class RecordTypeSummary(BaseModel):
    record_type: str
    source_id: str
    module: Optional[str] = None
    count: int
    fields: List[str] = []


class Fetch(BaseModel):
    url: str
    fetched_at: str
    status: str
    http_status: Optional[int] = None
    changed: Optional[int] = None
    error: Optional[str] = None


class SourceDetail(SourceSummary):
    interval_hours: Optional[float] = None
    parser_version: Optional[str] = None
    geo_note: Optional[str] = None
    licence_note: Optional[str] = None
    notes: Optional[str] = None
    last_error: Optional[str] = None
    documentation: Optional[str] = Field(None, description="the adapter's docstring: URLs, fields, caveats")
    metric_list: List[MetricSummary] = []
    record_types: List[RecordTypeSummary] = []
    recent_fetches: List[Fetch] = []


class ModuleSummary(BaseModel):
    module: str
    label: str
    sources: int
    enabled_sources: int
    metrics: int
    metrics_with_data: int
    observations: int
    records: int


class Observation(BaseModel):
    metric_id: str
    geo_level: str
    geo_code: str
    geo_name: Optional[str] = None
    period_start: str
    period_end: str
    dims: Dict[str, Any] = {}
    value: Optional[float] = None
    value_text: Optional[str] = None
    status: str = Field(..., description='reported, not_reported (blank at the source) or withheld')
    period_label: Optional[str] = Field(None, description='e.g. "Sep 2026", "FY 2025-26", "Apr-Jun 2026"')
    publisher_as_of: Optional[str] = None
    source_id: str
    source_page: Optional[str] = Field(None, description='the source page a person can open')
    source_url: Optional[str] = Field(None, description='the exact document or API call the value came from')
    retrieved_at: Optional[str] = None


class ObservationPage(BaseModel):
    metric: MetricSummary
    total: int
    limit: int
    offset: int
    items: List[Observation]


class SeriesPoint(BaseModel):
    period_start: str
    period_end: str
    label: str = Field(..., description='readable period, e.g. "Sep 2026"')
    value: Optional[float] = None
    value_text: Optional[str] = Field(None, description='the value when it is text, e.g. an AQI category')
    status: str


class Series(BaseModel):
    geo_level: str
    geo_code: str
    geo_name: Optional[str] = None
    dims: Dict[str, Any] = {}
    points: List[SeriesPoint]


class SeriesResponse(BaseModel):
    metric: MetricSummary
    series: List[Series]


class LatestResponse(BaseModel):
    metric: MetricSummary
    items: List[Observation]


class ModuleDetail(ModuleSummary):
    source_list: List[SourceSummary] = []
    metric_list: List[MetricSummary] = []
    record_types: List[RecordTypeSummary] = []


class Record(BaseModel):
    record_type: str
    record_key: str
    attrs: Dict[str, Any]
    valid_from: str
    valid_to: Optional[str] = None
    source_id: str
    source_page: Optional[str] = None
    source_url: Optional[str] = None


class RecordPage(BaseModel):
    record_type: str
    total: int
    limit: int
    offset: int
    items: List[Record]


class RecordDetail(BaseModel):
    current: Optional[Record] = None
    history: List[Record] = Field([], description='every stored version, newest first')


class Breakdown(BaseModel):
    label: str
    value: Optional[float] = None
    display: Optional[str] = None


class Card(BaseModel):
    id: str
    title: str
    value: Optional[float] = None
    unit: Optional[str] = None
    display: Optional[str] = Field(None, description='value formatted for people, e.g. "Rs 9,140 crore"')
    period_label: Optional[str] = None
    period_start: Optional[str] = None
    period_end: Optional[str] = None
    geo_level: Optional[str] = None
    geo_code: Optional[str] = None
    note: Optional[str] = None
    breakdown: List[Breakdown] = []
    metric_ids: List[str] = []
    source_ids: List[str] = []
    source_pages: List[str] = []


class ChartPoint(BaseModel):
    x: str
    value: Optional[float] = None
    period_start: Optional[str] = None
    period_end: Optional[str] = None


class ChartSeries(BaseModel):
    name: str
    points: List[ChartPoint]


class Chart(BaseModel):
    id: str
    title: str
    kind: str = Field(..., description='line or bar')
    unit: Optional[str] = None
    note: Optional[str] = None
    series: List[ChartSeries]
    metric_ids: List[str] = []
    source_ids: List[str] = []
    source_pages: List[str] = []


class Overview(BaseModel):
    as_of: Optional[str] = Field(None, description='finish time of the last pipeline run')
    cards: List[Card]
    charts: List[Chart]


class CoverageCounts(BaseModel):
    covered: int = 0
    partial: int = 0
    missing: int = 0
    not_applicable: int = 0


class CoverageModule(BaseModel):
    module: str
    metrics: int
    before: CoverageCounts
    after: CoverageCounts


class CoverageRow(BaseModel):
    n: int
    ftp_module: str
    ftp_metric: str
    before: str
    after: str
    backed_by: List[str] = Field([], description='metric:<id> or record:<type> (linkable through the API); '
                                                 'geo:<level>, table:<name> or view:<name> for pipeline internals')
    note: str


class Coverage(BaseModel):
    before: CoverageCounts
    after: CoverageCounts
    modules: List[CoverageModule]
    items: List[CoverageRow]


class Run(BaseModel):
    run_id: int
    started_at: str
    finished_at: Optional[str] = None
    command: Optional[str] = None
    status: Optional[str] = None


class Status(BaseModel):
    schema_version: Optional[str] = None
    database_bytes: int
    sources: int
    enabled_sources: int
    sources_with_errors: int
    metrics: int
    metrics_with_data: int
    observations: int
    records: int
    last_run: Optional[Run] = None
    recent_runs: List[Run] = []
