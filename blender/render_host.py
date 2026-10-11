"""Render one host with one oxygen vacancy: the reusable entry point for structure figures (M3).

Runs in the project Python (not inside Blender). It resolves the supercell CIF from the universe table
(``supercell_cif_path`` of data/processed/universe_v1.parquet; never globbed), checks that the vacancy index
is one of that host's vacancy sites, waits until macOS reports no memory pressure, then launches one
background Blender process (nice 15, OMP_NUM_THREADS=3) on blender/render_oxide.py. One frame per call.

    python blender/render_host.py mp-2133 150 figures/main/fig1_zno_vacancy.png --px 1200 --samples 32
    python blender/render_host.py mp-856 24 figures/si/structure_sno2.png --samples 128

data/processed and data/raw are not tracked; --data-root points at the checkout that holds them
(default: this repository).
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
import time
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
BLENDER = "/Applications/Blender.app/Contents/MacOS/Blender"
UNIVERSE = Path("data/processed/universe_v1.parquet")
NORMAL_PRESSURE = 1        # kern.memorystatus_vm_pressure_level: 1 normal, 2 warn, 4 critical


def resolve(host_id: str, vacancy: int, data_root: Path) -> tuple[Path, pd.Series, str]:
    u = pd.read_parquet(data_root / UNIVERSE)
    rows = u[u.host_id == host_id]
    if rows.empty:
        raise SystemExit(f"{host_id} is not in the universe table")
    site = rows[rows.vacancy_atom_index == vacancy]
    if len(site) != 1:
        raise SystemExit(f"atom {vacancy} is not a vacancy site of {host_id}: "
                         f"{sorted(rows.vacancy_atom_index.tolist())}")
    cifs = rows.supercell_cif_path.unique()
    if len(cifs) != 1:
        raise SystemExit(f"{host_id} has {len(cifs)} supercell paths")
    cif = data_root / cifs[0]
    if not cif.is_file():
        raise SystemExit(f"missing {cif}")
    return cif, site.iloc[0], cifs[0]


def pressure_level() -> int:
    out = subprocess.run(["sysctl", "-n", "kern.memorystatus_vm_pressure_level"], capture_output=True, text=True, check=False)
    return int(out.stdout.strip())


def wait_for_memory(max_wait_s: int, poll_s: int = 30) -> None:
    """Log vm_stat and memory_pressure (report only), and wait until the pressure level is normal."""
    t0 = time.time()
    while True:
        vm = subprocess.run(["vm_stat"], capture_output=True, text=True, check=False).stdout
        free = re.search(r"Pages free:\s+(\d+)", vm)
        mp = subprocess.run(["memory_pressure"], capture_output=True, text=True, check=False).stdout
        pct = re.search(r"free percentage:\s*(\d+)%", mp)
        lvl = pressure_level()
        print(f"[memory] level={lvl} free_pages={free.group(1) if free else '?'} "
              f"free_pct={pct.group(1) if pct else '?'}%", flush=True)
        if lvl == NORMAL_PRESSURE:
            return
        if time.time() - t0 > max_wait_s:
            raise SystemExit(f"memory still under pressure after {max_wait_s} s; not starting Blender")
        time.sleep(poll_s)


def render(host_id: str, vacancy: int, out: Path, px: int | None, samples: int, camera: str = "oblique",
           place: str = "front",
           data_root: Path = ROOT, width_mm: float = 138.6, dpi: int = 300, aspect: float | None = None,
           threads: int = 3, max_wait_s: int = 3600) -> Path:
    cif, site, label = resolve(host_id, vacancy, data_root)
    print(f"[render_host] {host_id} {site.site_id} atom {vacancy} <- {cif}", flush=True)
    wait_for_memory(max_wait_s)
    args = ["--cif", str(cif), "--cif-label", label, "--vacancy", str(vacancy), "--out", str(out), "--samples", str(samples),
            "--threads", str(threads), "--camera", camera, "--place", place, "--width-mm", str(width_mm), "--dpi", str(dpi)]
    if px:
        args += ["--px", str(px)]
    if aspect:
        args += ["--aspect", str(aspect)]
    env = {**os.environ, "OMP_NUM_THREADS": "3"}
    cmd = ["nice", "-n", "15", BLENDER, "-b", "--factory-startup", "-noaudio",
           "-P", str(ROOT / "blender" / "render_oxide.py"), "--", *args]
    t0 = time.time()
    p = subprocess.run(cmd, env=env, capture_output=True, text=True, check=False)
    log = out.with_suffix(".blender.log")
    keep = [ln for ln in p.stdout.splitlines() if not ln.startswith("Fra:")]
    print("\n".join(keep[-12:]))
    if p.returncode != 0 or not out.is_file():
        log.write_text(p.stdout + p.stderr)
        raise SystemExit(f"Blender failed ({p.returncode}); log in {log}")
    print(f"[render_host] wrote {out} in {time.time() - t0:.0f} s", flush=True)
    return out


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("host_id")
    ap.add_argument("vacancy", type=int)
    ap.add_argument("out", type=Path)
    ap.add_argument("--px", type=int, default=None, help="width in pixels (default: width-mm at dpi)")
    ap.add_argument("--samples", type=int, default=32)
    ap.add_argument("--camera", default="oblique")
    ap.add_argument("--place", choices=("centre", "front"), default="front")
    ap.add_argument("--width-mm", type=float, default=138.6)
    ap.add_argument("--dpi", type=int, default=300)
    ap.add_argument("--aspect", type=float, default=None)
    ap.add_argument("--data-root", type=Path, default=ROOT)
    ap.add_argument("--max-wait", type=int, default=3600)
    a = ap.parse_args(argv)
    render(a.host_id, a.vacancy, a.out.resolve(), a.px, a.samples, a.camera, a.place, a.data_root.resolve(),
           a.width_mm, a.dpi, a.aspect, max_wait_s=a.max_wait)


if __name__ == "__main__":
    sys.exit(main())
