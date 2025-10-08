#!/bin/bash
echo "Start Monitoring"
PID=$(pgrep -f 'jitlab-0.0.1-SNAPSHOT.jar' | head -n1)
python3 tools/monitor.py --pid $PID --interval 1 --duration 800 --out runs/monitor_cpu.csv &

echo "Low intensity starting"

python3 tools/load_py.py \
  --concurrency 8 --warmupSec 30 --runSec 240 --targetRPS 12\
  --out runs/load.csv

echo "Low intensity done"

echo "High intensity starting"
python3 tools/load_py.py \
  --concurrency 32 --warmupSec 0 --runSec 120 --targetRPS 25\
  --out runs/load.csv

echo "High intensity Done"

echo "Low intensity starting"

python3 tools/load_py.py \
  --concurrency 8 --warmupSec 0 --runSec 240 --targetRPS 12\
  --out runs/load.csv

echo "Low intensity done"

echo "High intensity starting"
python3 tools/load_py.py \
  --concurrency 32 --warmupSec 0 --runSec 120 --targetRPS 25\
  --out runs/load.csv

echo "High intensity Done"

echo "Done"

