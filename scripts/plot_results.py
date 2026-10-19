from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "results" / "graphs"
OUT.mkdir(parents=True, exist_ok=True)

# Values transcribed from the recorded Scenario B result files.
records = []

def add(protocol, condition, repetition, metric, value, unit):
    records.append({
        "protocol": protocol,
        "condition": condition,
        "repetition": repetition,
        "metric": metric,
        "value": value,
        "unit": unit,
    })

# TCP receiver throughput and retransmissions.
for rep, retrans in enumerate([2363, 1647, 2561], start=1):
    add("TCP", "Baseline", rep, "receiver_throughput", 1150, "Mbit/s")
    add("TCP", "Baseline", rep, "retransmissions", retrans, "packets")

add("TCP", "50 ms UE tunnel egress delay", 1,
    "receiver_throughput", 16.4, "Mbit/s")
add("TCP", "50 ms UE tunnel egress delay", 1,
    "retransmissions", 48, "packets")
add("TCP", "1% configured UE tunnel egress loss", 1,
    "receiver_throughput", 470, "Mbit/s")
add("TCP", "1% configured UE tunnel egress loss", 1,
    "retransmissions", 1817, "packets")

# UDP results: three baseline repetitions and one per impairment condition.
udp = [
    ("Baseline", 1, 10.0, 0.028, 0.0),
    ("Baseline", 2, 10.0, 0.070, 0.0),
    ("Baseline", 3, 10.0, 0.046, 0.0),
    ("50 ms UE tunnel egress delay", 1, 9.95, 0.028, 0.0),
    ("1% configured UE tunnel egress loss", 1, 9.90, 0.033, 0.96),
]
for condition, rep, bitrate, jitter, loss in udp:
    add("UDP", condition, rep, "receiver_bitrate", bitrate, "Mbit/s")
    add("UDP", condition, rep, "jitter", jitter, "ms")
    add("UDP", condition, rep, "packet_loss", loss, "%")

# Ten HTTP request timings, converted from seconds to milliseconds.
http_seconds = [
    0.001181, 0.003801, 0.000926, 0.001200, 0.001344,
    0.000808, 0.000908, 0.000785, 0.000959, 0.000831
]
for request, seconds in enumerate(http_seconds, start=1):
    add("HTTP", "Repeated baseline requests", request,
        "response_time", seconds * 1000, "ms")

df = pd.DataFrame(records)
csv_path = ROOT / "results" / "measurement-data.csv"
df.to_csv(csv_path, index=False)

def save_plot(filename):
    plt.tight_layout()
    plt.savefig(OUT / filename, dpi=200, bbox_inches="tight")
    plt.close()

# 1. TCP receiver throughput comparison.
tcp = df[df["metric"] == "receiver_throughput"]
tcp_summary = tcp.groupby("condition", sort=False)["value"].mean()
plt.figure(figsize=(9, 5))
tcp_summary.plot(kind="bar")
plt.title("TCP Receiver Throughput Under Different Conditions")
plt.xlabel("Test condition")
plt.ylabel("Receiver throughput (Mbit/s)")
plt.xticks(rotation=15, ha="right")
plt.grid(axis="y", alpha=0.3)
save_plot("tcp-throughput.png")

# 2. UDP received bitrate for every recorded run.
udp_bitrate = df[df["metric"] == "receiver_bitrate"].copy()
udp_bitrate["run"] = udp_bitrate["condition"] + " — run " + udp_bitrate["repetition"].astype(str)
plt.figure(figsize=(10, 5))
plt.bar(udp_bitrate["run"], udp_bitrate["value"])
plt.title("UDP Receiver Bitrate")
plt.xlabel("Test condition and repetition")
plt.ylabel("Receiver bitrate (Mbit/s)")
plt.xticks(rotation=25, ha="right")
plt.grid(axis="y", alpha=0.3)
save_plot("udp-throughput.png")

# 3. UDP packet loss percentage.
udp_loss = df[df["metric"] == "packet_loss"].copy()
udp_loss["run"] = udp_loss["condition"] + " — run " + udp_loss["repetition"].astype(str)
plt.figure(figsize=(10, 5))
plt.bar(udp_loss["run"], udp_loss["value"])
plt.title("UDP Packet Loss")
plt.xlabel("Test condition and repetition")
plt.ylabel("Lost datagrams (%)")
plt.xticks(rotation=25, ha="right")
plt.grid(axis="y", alpha=0.3)
save_plot("udp-packet-loss.png")

# 4. UDP jitter.
udp_jitter = df[df["metric"] == "jitter"].copy()
udp_jitter["run"] = udp_jitter["condition"] + " — run " + udp_jitter["repetition"].astype(str)
plt.figure(figsize=(10, 5))
plt.bar(udp_jitter["run"], udp_jitter["value"])
plt.title("UDP Receiver Jitter")
plt.xlabel("Test condition and repetition")
plt.ylabel("Jitter (ms)")
plt.xticks(rotation=25, ha="right")
plt.grid(axis="y", alpha=0.3)
save_plot("udp-jitter.png")

# 5. HTTP response time for ten requests.
http = df[df["metric"] == "response_time"]
plt.figure(figsize=(8, 5))
plt.plot(http["repetition"], http["value"], marker="o")
plt.title("HTTP Response Time Across 10 Requests")
plt.xlabel("Request number")
plt.ylabel("Total response time (ms)")
plt.xticks(range(1, 11))
plt.grid(alpha=0.3)
save_plot("http-response-time.png")

print(f"Saved structured measurements: {csv_path}")
print(f"Saved 5 charts in: {OUT}")
print(f"HTTP mean response time: {http['value'].mean():.3f} ms")
print(f"UDP baseline mean jitter: {udp_jitter[udp_jitter['condition'] == 'Baseline']['value'].mean():.3f} ms")
print("\nGenerated files:")
for path in sorted(OUT.glob("*.png")):
    print(f"  {path.name} ({path.stat().st_size:,} bytes)")
