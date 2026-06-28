#!/usr/bin/env python3
"""EServe tutorial helper: model a GPU accelerator's embodied carbon, add the host server it
racks into, and find the embodied-vs-operational grid crossover.

Participant-facing runner for the hands-on tutorial (see TUTORIAL.md). Self-contained in this
repo: it drives EServe's OWN carbon calculators (server_carbon) on the bundled GPU configs.

  ./tutorial.sh --gpu H100HGX                                  one GPU's embodied breakdown
  ./tutorial.sh --gpu H100HGX --host                           + the host server (the reveal)
  ./tutorial.sh --gpu-file exercises/gpu_l4.json               an edited local config
  ./tutorial.sh --gpu H100HGX --host --grid-ci 30 --util 0.5   sweep your region's grid
"""
import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "src"))  # EServe's server_carbon package
from server_carbon import (  # noqa: E402
    GPUCarbonCalculator, CPUCarbonCalculator,
    json_to_gpuspecs, json_to_cpuspecs, MemoryType,
)

# --- config + constants ---
CONFIG = HERE.parent / "config" / "gpuconfigs.json"   # EServe's bundled GPU configs
N_GPUS = 8
UTILIZATION = 0.8
# Paper's three grid intensities (gCO2e/kWh): clean (Sweden) / world-avg / high (California).
GRID_CI = {"clean (Sweden)": 17, "world avg": 261, "high (California)": 501}


def crossover_figure(out_png, *, embodied_rate, power_kw, util, grid_ci, crossover_ci):
    """Operational carbon rate (rising with grid CI) vs the flat amortized embodied rate;
    mark the CI below which embodied wins."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    xmax = 560.0
    ci = np.linspace(0, xmax, 200)
    op = power_kw * util * ci
    fig, ax = plt.subplots(figsize=(7.8, 4.6))
    ax.axvspan(0, crossover_ci, color="#cfe8d6", alpha=0.7,
               label=f"embodied-dominated (CI < ~{crossover_ci:.1f})")
    ax.plot(ci, op, color="#bb5566", lw=2,
            label=f"operational  ({power_kw:.1f} kW node @ {int(util*100)}% util)")
    ax.axhline(embodied_rate, color="#3b7a57", lw=2, ls="--",
               label=f"embodied  ({embodied_rate:.0f} g/hr, 4-yr amortized)")
    ax.axvline(crossover_ci, color="#444", lw=1, ls=":")
    ax.annotate(f"crossover ~{crossover_ci:.1f} gCO2e/kWh",
                xy=(crossover_ci, embodied_rate),
                xytext=(crossover_ci + 70, embodied_rate * 3.0),
                arrowprops=dict(arrowstyle="->", color="#444"), fontsize=9)
    for name, c in grid_ci.items():
        y = power_kw * util * c
        ax.scatter([c], [y], color="#bb5566", zorder=5)
        left = c > 0.6 * xmax
        ax.annotate(f"{name}\n{c} -> {y:,.0f} g/hr", (c, y), textcoords="offset points",
                    xytext=(-8 if left else 8, 8), ha="right" if left else "left", fontsize=8)
    ax.set_xlim(0, xmax)
    ax.set_ylim(0, power_kw * util * xmax * 1.02)
    ax.set_xlabel("grid carbon intensity (gCO2e/kWh)")
    ax.set_ylabel("carbon rate (gCO2e per node-hour)")
    ax.set_title(f"Below ~{crossover_ci:.0f} gCO2e/kWh, embodied outweighs ALL operational (EcoServe Obs 3)")
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.legend(frameon=False, fontsize=8, loc="upper center")
    fig.tight_layout()
    out = Path(out_png)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=130)
    plt.close(fig)
    return out


def _resolve(p):
    p = Path(p)
    return p if p.is_absolute() else HERE / p


def load_gpu(args):
    if args.gpu_file:
        return json.loads(_resolve(args.gpu_file).read_text()), f"file:{args.gpu_file}"
    return json.loads(CONFIG.read_text())[args.gpu], args.gpu


def host_cpu_configs(cfg, args):
    """Return (cpu_configs dict, borrowed_from-or-None). A GPU config may carry its own host
    (cpu_configs); host-less GPUs (e.g. L4) borrow a reference host so the reveal stays honest."""
    if cfg.get("cpu_configs"):
        return cfg["cpu_configs"], None
    src = args.host_source
    p = _resolve(src)
    if p.exists():
        d = json.loads(p.read_text())
        return d.get("cpu_configs", d), src
    return json.loads(CONFIG.read_text())[src]["cpu_configs"], src


def main():
    ap = argparse.ArgumentParser(description="EServe hands-on: GPU + host embodied + grid crossover")
    ap.add_argument("--gpu", default="H100HGX", help="GPU key in EServe/config/gpuconfigs.json")
    ap.add_argument("--gpu-file", help="load a flat single-GPU JSON instead (tutorial-relative ok)")
    ap.add_argument("--host", action="store_true", help="also model the host server")
    ap.add_argument("--host-source", default="H100HGX",
                    help="GPU name or JSON file whose cpu_configs to borrow if the GPU has none")
    ap.add_argument("--n-gpus", type=int, default=N_GPUS)
    ap.add_argument("--util", type=float, default=UTILIZATION)
    ap.add_argument("--grid-ci", type=float, nargs="+", default=None,
                    help="grid carbon intensities gCO2e/kWh (default: the three built-in grids)")
    ap.add_argument("--fig", action="store_true", help="also render the crossover PNG into figures/tutorial/")
    ap.add_argument("--expect", action="append", default=[], metavar="KEY=VAL",
                    help="assert a value: gpu|host|crossover|per_accel|node|embodied_rate (repeatable)")
    args = ap.parse_args()

    cfg, label = load_gpu(args)

    # --- GPU: full-lifetime embodied (ratio = 1 -> the manufactured carbon) ---
    g = json_to_gpuspecs(cfg)
    lt_h = g.lifetime_years * 365 * 24
    gpu_full = GPUCarbonCalculator(g).calculate_total_cf(execution_time_hours=lt_h)
    gpu_total = round(gpu_full["total"], 1)
    results = {"gpu": gpu_total}

    print(f"[EServe tutorial] GPU {label}: embodied {gpu_total} kgCO2e")
    for k in ("SoC", "PDN", "memory", "cooling", "PCB", "connection"):
        if k in gpu_full:
            print(f"    {k:<11} {gpu_full[k]:>8.2f}")

    cspecs = None
    if args.host:
        host_cfg, borrowed = host_cpu_configs(cfg, args)
        cspecs = json_to_cpuspecs(host_cfg)
        host_calc = CPUCarbonCalculator(
            lifetime_years=g.lifetime_years, execution_time=lt_h,
            ssd_capacity_gb=cspecs.storage_size, memory_capacity_gb=cspecs.cpu_memory,
            memory_type=MemoryType.DDR4, die_area_mm2=1600.0, process_node_nm=7,
        )
        host = host_calc.calculate_total_cf()
        host_total = round(host["total_cf"], 1)
        host_ssd = round(host_calc.calculate_ssd_cf(), 1)
        host_dram = round(host_calc.calculate_memory_cf(), 1)
        host_other = round(host_total - host_ssd - host_dram, 1)
        per_accel = round(gpu_total + host_total, 1)
        host_pct = round(100 * host_total / per_accel, 1)
        ratio = round((host_ssd + host_dram) / gpu_total, 1)
        results.update({"host": host_total, "per_accel": per_accel})

        note = f"  (borrowed cpu_configs from {borrowed})" if borrowed else ""
        print(f"  HOST: {host_total} kgCO2e{note}")
        print(f"    SSD {host_ssd}   DRAM {host_dram}   other {host_other}")
        print(f"  -> host = {host_pct}% of one accelerator; storage+DRAM = {ratio}x the GPU")

        # --- crossover: whole-node embodied (amortized) vs operational on the grid ---
        node_embodied = round(args.n_gpus * gpu_total + host_total, 1)
        embodied_rate = round(node_embodied * 1000 / lt_h, 1)
        power_kw = round((args.n_gpus * g.tdp + cspecs.cpu_tdp) / 1000.0, 2)
        crossover_ci = round(embodied_rate / (power_kw * args.util), 1)
        results.update({"node": node_embodied, "embodied_rate": embodied_rate, "crossover": crossover_ci})

        grid = args.grid_ci if args.grid_ci is not None else list(GRID_CI.values())
        print(f"  NODE ({args.n_gpus} GPU + host): embodied {node_embodied} kg "
              f"-> {embodied_rate} g/hr amortized; {power_kw} kW @ {int(args.util * 100)}% util")
        for ci in grid:
            op = round(power_kw * args.util * ci, 1)
            who = "embodied wins" if ci < crossover_ci else "operational wins"
            print(f"    grid CI {ci:>6.0f} g/kWh -> operational {op:>8.1f} g/hr   ({who})")
        print(f"  -> crossover ~{crossover_ci} gCO2e/kWh (below it, building outweighs running)")

        if args.fig:
            crossover_figure(
                HERE / "figures" / "tutorial" / "crossover.png",
                embodied_rate=embodied_rate, power_kw=power_kw, util=args.util,
                grid_ci={f"CI {int(ci)}": ci for ci in grid}, crossover_ci=crossover_ci,
            )

    # --- the real EServe API behind this run (drive it yourself in Python) ---
    print("\n  the EServe API this used (it's a library, not a CLI — call it yourself):")
    print("      from server_carbon import GPUCarbonCalculator, json_to_gpuspecs")
    print(f"      g = json_to_gpuspecs(cfg)                  # cfg = {label}")
    print(f"      GPUCarbonCalculator(g).calculate_total_cf(execution_time_hours={int(lt_h)})")
    if cspecs is not None:
        print("      from server_carbon import CPUCarbonCalculator, MemoryType")
        print(f"      CPUCarbonCalculator(ssd_capacity_gb={int(cspecs.storage_size)}, "
              f"memory_capacity_gb={int(cspecs.cpu_memory)}, memory_type=MemoryType.DDR4,")
        print(f"          die_area_mm2=1600, process_node_nm=7, lifetime_years={int(g.lifetime_years)}, "
              f"execution_time={int(lt_h)}).calculate_total_cf()")
        print("      # crossover_ci = node_embodied_kg * 1000 / lifetime_hours / (power_kw * util)")

    # --- optional CI assertions ---
    failures = []
    for spec in args.expect:
        key, _, raw = spec.partition("=")
        key = key.strip()
        got = results.get(key)
        if got is None:
            failures.append(f"{key}: not computed (need --host?)")
            continue
        want = float(raw)
        tol = max(0.05, 0.001 * abs(want))
        if abs(got - want) > tol:
            failures.append(f"{key}: got {got}, expected {want}")
    if failures:
        for f in failures:
            print(f"  EXPECT FAIL: {f}", file=sys.stderr)
        sys.exit(1)
    if args.expect:
        print("  EXPECT OK")


if __name__ == "__main__":
    main()
