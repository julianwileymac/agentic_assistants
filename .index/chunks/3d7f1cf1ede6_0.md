# Chunk: 3d7f1cf1ede6_0

- source: `.venv-lab/Lib/site-packages/jedi/third_party/django-stubs/django-stubs/utils/dateparse.pyi`
- lines: 1-15
- chunk: 1/1

```
from datetime import date, datetime, time, timedelta
from typing import Any, Optional

date_re: Any
time_re: Any
datetime_re: Any
standard_duration_re: Any
iso8601_duration_re: Any
postgres_interval_re: Any

def parse_date(value: str) -> Optional[date]: ...
def parse_time(value: str) -> Optional[time]: ...
def parse_datetime(value: str) -> Optional[datetime]: ...
def parse_duration(value: str) -> Optional[timedelta]: ...
```
