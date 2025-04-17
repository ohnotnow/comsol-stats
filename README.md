# comsol-stats

Parses and analyzes COMSOL license server log files, extracting usage statistics and generating visualizations and an Excel report.

## Features
- Parses timestamped log events with date context
- Outputs an Excel file with:
  - Raw log events with full datetime
  - Aggregated usage statistics by feature and user
  - Hourly usage counts
  - Daily unique user counts
  - Summary statistics
- Generates plots using Seaborn:
  - Feature usage bar chart
  - Hourly usage line chart
  - Top 10 user bar chart

## Repository
GitHub: [https://github.com/ohnotnow/comsol-stats](https://github.com/ohnotnow/comsol-stats)

## Requirements
- Python 3.8+
- Dependencies listed in `pyproject.toml`
- Uses [`uv`](https://docs.astral.sh/uv/) for dependency management and execution

## Installation

### macOS / Ubuntu / Windows
```bash
git clone https://github.com/ohnotnow/comsol-stats.git
cd comsol-stats
uv sync
```

## Usage

```bash
uv run main.py <log_file>
```

Replace `<log_file>` with the path to your COMSOL license log file (e.g., `comsol62.log`).

### Output
- Excel file: `comsol_license_analysis.xlsx`
- PNG plots:
  - `feature_usage.png`
  - `usage_by_hour.png`
  - `user_usage.png`

## License
MIT License. See below for attribution.


