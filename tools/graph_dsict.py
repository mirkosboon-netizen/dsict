import argparse, pandas as pd, matplotlib.pyplot as plt
import os

"""Launch command:
python3 tools/graph_dsict.py --baselineL baseline/load.csv --baselineM baseline/monitor_cpu.csv --noJITL no-jit/load.csv --noJITM no-jit/monitor_cpu.csv --C1L c1/load.csv --C1M c1/monitor_cpu.csv --C2L c2/load.csv --C2M c2/monitor_cpu.csv 


"""

ap = argparse.ArgumentParser()
ap.add_argument("--baselineL", required=True, help="load.csv from baseline run")
ap.add_argument("--baselineM", required=True, help="monitor.csv from baseline run")
ap.add_argument("--noJITL", required=True, help="load.csv from no-jit run")
ap.add_argument("--noJITM", required=True, help="monitor.csv from no-jit run")
ap.add_argument("--C1L", required=True, help="load.csv from C1 run")
ap.add_argument("--C1M", required=True, help="monitor.csv from C1 run")
ap.add_argument("--C2L", required=True, help="load.csv from C2 run")
ap.add_argument("--C2M", required=True, help="monitor.csv from C2 run")

os.makedirs("graphs", exist_ok=True)

args = ap.parse_args()
load_baseline = pd.read_csv(args.baselineL)
monitor_baseline = pd.read_csv(args.baselineM)[29:751]

load_no_jit = pd.read_csv(args.noJITL)
monitor_no_jit = pd.read_csv(args.noJITM)[29:751]

load_c1 = pd.read_csv(args.C1L)
monitor_c1 = pd.read_csv(args.C1M)[29:751]

load_c2 = pd.read_csv(args.C2L)
monitor_c2 = pd.read_csv(args.C2M)[29:751]

monitor_baseline["t"] = round(monitor_baseline["ts"] - monitor_baseline["ts"].min() + 1)
monitor_no_jit["t"] = round(monitor_no_jit["ts"] - monitor_no_jit["ts"].min() + 1)
monitor_c1["t"] = round(monitor_c1["ts"] - monitor_c1["ts"].min() + 1)
monitor_c2["t"] = round(monitor_c2["ts"] - monitor_c2["ts"].min() + 1)

load_baseline["t"] = round(load_baseline["ts"] - load_baseline["ts"].min() + 1)
load_no_jit["t"] = round(load_no_jit["ts"] - load_no_jit["ts"].min() + 1)
load_c1["t"] = round(load_c1["ts"] - load_c1["ts"].min() + 1)   
load_c2["t"] = round(load_c2["ts"] - load_c2["ts"].min() + 1)

monitor_baseline['power_smooth'] = monitor_baseline['power_w'].rolling(window=10, center=True).mean()
monitor_no_jit['power_smooth'] = monitor_no_jit['power_w'].rolling(window=10, center=True).mean()
monitor_c1['power_smooth'] = monitor_c1['power_w'].rolling(window=10, center=True).mean()
monitor_c2['power_smooth'] = monitor_c2['power_w'].rolling(window=10, center=True).mean()

# Figure 1: Power(W) over time
plt.figure()
plt.plot(monitor_baseline["t"], monitor_baseline["power_smooth"], label="Baseline (W)")
plt.plot(monitor_no_jit["t"], monitor_no_jit["power_smooth"], label="No-JIT (W)")
plt.plot(monitor_c1["t"], monitor_c1["power_smooth"], label="C1 (W)")
plt.plot(monitor_c2["t"], monitor_c2["power_smooth"], label="C2 (W)")
plt.axvline(x=240, color='red', linestyle='--', label='start high intensity')
plt.axvline(x=360, color='blue', linestyle='--', label='end high intensity')
plt.axvline(x=600, color='red', linestyle='--', label='start high intensity')
plt.axvline(x=720, color='blue', linestyle='--', label='end high intensity')
plt.xlabel("Time (s)"); plt.ylabel("Watts"); plt.title("Power usage over time (Rolling average 10s)")
plt.legend(
    loc='upper center',          # put it at the center horizontally
    bbox_to_anchor=(0.5, -0.2),  # move it below the axes
    ncol=2                       # make it spread out horizontally
)

plt.tight_layout()
plt.savefig("graphs/plot_power.png")

load_baseline['rps_smooth'] = load_baseline['rps'].rolling(window=10, center=True).mean()
load_no_jit['rps_smooth'] = load_no_jit['rps'].rolling(window=10, center=True).mean()
load_c1['rps_smooth'] = load_c1['rps'].rolling(window=10, center=True).mean()
load_c2['rps_smooth'] = load_c2['rps'].rolling(window=10, center=True).mean()

# Figure 2: RPS over time
plt.figure()
plt.plot(load_baseline["t"], load_baseline["rps_smooth"], label="Baseline")
plt.plot(load_no_jit["t"], load_no_jit["rps_smooth"], label="No-JIT")
plt.plot(load_c1["t"], load_c1["rps_smooth"], label="C1")
plt.plot(load_c2["t"], load_c2["rps_smooth"], label="C2")
plt.axvline(x=240, color='red', linestyle='--', label='start high intensity')
plt.axvline(x=360, color='blue', linestyle='--', label='end high intensity')
plt.axvline(x=600, color='red', linestyle='--', label='start high intensity')
plt.axvline(x=720, color='blue', linestyle='--', label='end high intensity')
plt.xlabel("Time (s)"); plt.ylabel("Watts"); plt.title("RPS over time (Rolling average 10s)")
plt.legend(
    loc='upper center',          # put it at the center horizontally
    bbox_to_anchor=(0.5, -0.2),  # move it below the axes
    ncol=2                       # make it spread out horizontally
)
plt.tight_layout()
plt.savefig("graphs/plot_rps.png")

# Figure 3: Latency p95 (ms)
plt.figure()
plt.scatter(load_baseline["t"], load_baseline["p95_ms"], label = "Baseline", s=10)
plt.scatter(load_no_jit["t"], load_no_jit["p95_ms"], label = "No-JIT", s=10)
plt.scatter(load_c1["t"], load_c1["p95_ms"], label = "C1", s=10)
plt.scatter(load_c2["t"], load_c2["p95_ms"], label = "C2", s=10)
plt.axvline(x=240, color='red', linestyle='--', label='start high intensity')
plt.axvline(x=360, color='blue', linestyle='--', label='end high intensity')
plt.axvline(x=600, color='red', linestyle='--', label='start high intensity')
plt.axvline(x=720, color='blue', linestyle='--', label='end high intensity')

plt.xlabel("Time (s)"); plt.ylabel("Latency p95 (ms)"); plt.title("Latency p95")
plt.legend(
    loc='upper center',          # put it at the center horizontally
    bbox_to_anchor=(0.5, -0.2),  # move it below the axes
    ncol=2                       # make it spread out horizontally
)
plt.tight_layout(); 
plt.savefig("graphs/plot_latency_p95.png")

# Figure 4: Total enery (J) bar chart
plt.figure()
names = ["C2","C1","Baseline", "No-JIT"]
values = [
    monitor_c2["energy_j_total"].iloc[-1],
    monitor_c1["energy_j_total"].iloc[-1],
    monitor_baseline["energy_j_total"].iloc[-1],
    monitor_no_jit["energy_j_total"].iloc[-1],    
]

plt.bar(names, values, color=["green", "yellow", "orange", "red"])
plt.ylim(0, max(values) * 1.25)
bar_width = 0.8

for i in range(len(names)-1):
    x1 = i          # left bar
    x2 = i + 1      # right bar
    y1 = values[i]
    y2 = values[i+1]

    # Compute x positions at 75% of left bar and 25% of right bar
    x1 = x1 + (0.75 - 0.5) * bar_width   # 0.75 of left bar
    x2 = x2 + (0.25 - 0.5) * bar_width   # 0.25 of right bar

    # y position of bracket (just above taller bar)
    y_bracket = max(y1, y2) + 0.05 * max(values)
    
    # Draw the bracket
    plt.plot([x1, x1, x2, x2],
             [y1, y_bracket, y_bracket, y2],
             color='black', linewidth=1, alpha=0.7, linestyle='dashed')

    # Place difference label above bracket
    diff = y2 - y1
    plt.text(
        (x1 + x2) / 2,             # midpoint between bars
        y_bracket + 0.02 * max(values),
        f'{diff:.1f}',
        ha='center', va='bottom', fontsize=10, color='black', alpha=0.7
    )
plt.savefig("graphs/plot_total_energy.png")

# Figure 5: Energy per Request
load_baseline['energy_per_req'] = monitor_baseline["power_w"]/load_baseline['rps_smooth']
load_no_jit['energy_per_req'] = monitor_no_jit["power_w"]/load_no_jit['rps_smooth']
load_c1['energy_per_req'] = monitor_c1["power_w"]/load_c1['rps_smooth']
load_c2['energy_per_req'] = monitor_c2["power_w"]/load_c2['rps_smooth']

plt.figure()
plt.scatter(load_baseline["t"], load_baseline["energy_per_req"], label = "Baseline", s=10)
plt.scatter(load_no_jit["t"], load_no_jit["energy_per_req"], label = "No-JIT", s=10)
plt.scatter(load_c1["t"], load_c1["energy_per_req"], label = "C1", s=10)
plt.scatter(load_c2["t"], load_c2["energy_per_req"], label = "C2", s=10)
plt.axvline(x=240, color='red', linestyle='--', label='start high intensity')
plt.axvline(x=360, color='blue', linestyle='--', label='end high intensity')
plt.axvline(x=600, color='red', linestyle='--', label='start high intensity')
plt.axvline(x=720, color='blue', linestyle='--', label='end high intensity')

plt.xlabel("Time (s)"); plt.ylabel("W/req"); plt.title("Energy per request")
plt.legend(
    loc='upper center',          # put it at the center horizontally
    bbox_to_anchor=(0.5, -0.2),  # move it below the axes
    ncol=2                       # make it spread out horizontally
)
plt.tight_layout(); 
plt.savefig("graphs/plot_energy_per_request.png")
print("done")