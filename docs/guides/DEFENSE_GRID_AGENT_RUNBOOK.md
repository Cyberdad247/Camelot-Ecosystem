# Defense Grid Agent Runbook

## Location
- Agent: `tools/camelot_defense_grid_agent.py`

## Run once (dry-run)
```powershell
python tools\camelot_defense_grid_agent.py
```

## Run once (execute low-risk actions)
```powershell
python tools\camelot_defense_grid_agent.py --execute
```

## Custom paths
```powershell
python tools\camelot_defense_grid_agent.py `
  --execute `
  --report-dir logs\defense_grid `
  --quarantine-dir C:\Users\vizio\CAMELOT_DefenseGrid_Quarantine `
  --max-temp-age-days 7
```

## Schedule hourly (Windows Task Scheduler)
```powershell
schtasks /Create /SC HOURLY /MO 1 /TN "CamelotDefenseGrid" /TR "powershell -NoProfile -ExecutionPolicy Bypass -Command cd C:\Users\vizio\CAMELOT_OS; python tools\camelot_defense_grid_agent.py --execute" /F
```

## Disable scheduled task
```powershell
schtasks /Change /TN "CamelotDefenseGrid" /Disable
```

## Reports
- JSON reports are written to `logs/defense_grid/`.
- Each cycle contains:
  - status
  - bottlenecks
  - executed actions
  - pending approvals
  - metrics
