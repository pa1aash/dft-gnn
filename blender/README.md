# Structure renders (Blender, headless)

Ball-and-stick Cycles renders of a host supercell with one oxygen vacancy, in one fixed visual language for
every structure figure in the paper.

| File | Runs in | Role |
|---|---|---|
| `render_host.py` | project Python | Entry point. Host id + vacancy atom index -> supercell CIF from the universe table (`supercell_cif_path`), memory-pressure gate, one background Blender process. |
| `render_oxide.py` | Blender (`-b -P`) | Reads the CIF with ASE, builds the scene (materials library, vacancy shell, first-shell polyhedron, camera and light presets), renders with Cycles on CPU + OpenImageDenoise, writes an RGB PNG on white with the dpi tag and a `.render.json` sidecar. |

## One-time setup (local only)

Blender's bundled Python has no ASE. Install ASE and SciPy into the git-excluded `.local/` directory:

```bash
/Applications/Blender.app/Contents/Resources/5.2/python/bin/python3.13 -m pip install \
    --target .local/blender-site --no-deps "ase==3.26.0" "scipy==1.16.3"
```

`data/processed/` and `data/raw/` are untracked; in a worktree pass `--data-root` pointing at the checkout
that holds them.

## Usage

```bash
# preview (1200 px, 32 samples), then the print version (138.6 mm at 300 dpi = 1637 px, <= 128 samples)
python blender/render_host.py mp-2133 150 /tmp/zno_preview.png --px 1200 --samples 32 --data-root ~/Desktop/dft-gnn
python blender/render_host.py mp-2133 150 figures/main/fig1_zno_vacancy.png --samples 128 --data-root ~/Desktop/dft-gnn
```

Politeness: `render_host.py` logs `vm_stat` and `memory_pressure` (report mode only) and waits until
`kern.memorystatus_vm_pressure_level` is 1 (normal) before starting Blender under `nice -n 15` with
`OMP_NUM_THREADS=3` and 3 Cycles threads. One frame per process; run hosts one after another.

## Visual conventions

- O red; each cation coloured by its element class (`MATERIALS` / `CLASS_OF` in `render_oxide.py`):
  alkali violet, alkaline earth green, early d blue, late d mauve, d10 and post-transition slate grey-blue,
  metalloid tan, lanthanide teal. Amber is reserved for the vacancy.
- The removed O is not drawn. Its site carries a translucent amber shell; its first cation shell
  (cations within 1.2 x the shortest vacancy-cation distance) is drawn larger and joined into a translucent
  polyhedron with dark edges (tetrahedron in wurtzite ZnO, triangle in rutile SnO2).
- The supercell is wrapped so that the vacancy sits at the cell centre. Cation-O bonds (cutoff 1.2 x the
  shortest cation-O distance per cation element) are drawn as two half-cylinders; bonds crossing the cell
  boundary are omitted.
- Orthographic camera on a preset direction (`oblique`, `along-a`, `along-c`), scaled to the projected cell
  plus a 6% margin; key, fill and rim area lights fixed in the camera frame; Standard view transform.
- No text in the image. Element colours, the vacancy marker and distances go in the caption file.
