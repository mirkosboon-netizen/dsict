# To run
Start the Spring Boot server with the desired JIT configuration. I.E:
java -jar target/jitlab-0.0.1-SNAPSHOT.jar

Then start the bash script experiment.sh

Wait for the monitor process to die before starting a new run.

Place the resulting load.csv and monitor_cpu.csv from the runs folder in the corresponding JIT-type folder.

Then run the following command to create the graphs:
python3 tools/graph_dsict.py --baselineL baseline/load.csv --baselineM baseline/monitor_cpu.csv --noJITL no-jit/load.csv --noJITM no-jit/monitor_cpu.csv --C1L c1/load.csv --C1M c1/monitor_cpu.csv --C2L c2/load.csv --C2M c2/monitor_cpu.csv 
