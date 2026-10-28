# sys-metric-daemon

Zero-dependency system metrics exporter in Prometheus text exposition format.

## Overview

Monitoring host systems often involves heavy agent daemons. `sys-metric-daemon` is a minimal, pure-standard-library metric collector that gathers CPU load averages and disk space utilization, formatting them in Prometheus text exposition format.

## Features

- Prometheus Format: Directly consumable by Prometheus scrapers, VictoriaMetrics, or Telegraf.
- Metric Collection: Gathers 1-minute, 5-minute, and 15-minute load averages alongside total, used, and free disk bytes.
- Standard Library Implementation: Uses `os.getloadavg()` and `shutil.disk_usage()`, eliminating C-extension prerequisites.

## Installation

```bash
git clone https://gitlab.com/jk9576/sys-metric-daemon.git
cd sys-metric-daemon
pip install -e .
```

## CLI Usage

```bash
sys-metrics
```

Sample Output:

```
# TYPE node_disk_bytes_total gauge
node_disk_bytes_total 494384128000.0000
# TYPE node_disk_bytes_used gauge
node_disk_bytes_used 284120934400.0000
# TYPE node_disk_bytes_free gauge
node_disk_bytes_free 210263193600.0000
# TYPE node_disk_utilization_ratio gauge
node_disk_utilization_ratio 0.5747
# TYPE node_load1 gauge
node_load1 1.8200
# TYPE node_load5 gauge
node_load5 1.9500
# TYPE node_load15 gauge
node_load15 2.1000
```

## Python API Usage

```python
from sys_metrics.collector import MetricCollector

collector = MetricCollector()
metrics = collector.get_disk_metrics("/")
print(f"Disk Free: {metrics['node_disk_bytes_free'] / (1024**3):.2f} GB")
```

## Running Tests

```bash
python -m unittest discover tests
```

## License

MIT License. See LICENSE for details.
