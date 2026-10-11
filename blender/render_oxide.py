"""Headless Cycles render of an oxide supercell with one oxygen vacancy (M3).

Run inside Blender in background mode (one frame per process):

    /Applications/Blender.app/Contents/MacOS/Blender -b --factory-startup -P blender/render_oxide.py -- \
        --cif <supercell CIF from the universe table> --vacancy <atom index> --out <file.png> \
        [--px 1200 --samples 32] [--width-mm 138.6 --dpi 300] [--camera oblique] [--threads 3]

Normally called through blender/render_host.py, which takes the CIF path from the universe table and checks
memory pressure first. ASE (and SciPy) are imported from .local/blender-site (local only; see blender/README.md).

Scene conventions (identical for every host):
  * the pristine supercell is wrapped periodically so that the vacancy sits just inside the camera-facing
    faces (``--place front``, default) or at the cell centre (``--place centre``); no atom is added, and every
    atom moves by a lattice vector only;
  * ball-and-stick: O red, each cation coloured by its element class (MATERIALS), cation-O bonds only, drawn
    as two half-cylinders in the colours of their atoms; bonds that cross the cell boundary are not drawn;
  * the removed O is not drawn; its site carries a translucent amber shell, and its first cation shell is
    drawn larger, joined into a translucent polyhedron (tetrahedron for four neighbours) with dark edges;
  * orthographic camera on a fixed preset direction, scaled to the projected extent of the cell plus margin;
  * three area lights fixed in the camera frame (key, fill, rim), white world at low strength;
  * Cycles on CPU, OpenImageDenoise, Standard view transform; the transparent render is flattened onto
    white and written as an RGB PNG tagged with the print resolution (dpi).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import bmesh
import bpy
import numpy as np
from mathutils import Matrix, Vector

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT / ".local" / "blender-site"))
from ase.io import read
from ase.neighborlist import neighbor_list

MM_PER_IN = 25.4

# ---------------------------------------------------------------- materials library (fixed for the paper)
CLASS_OF = {}
for _cls, _els in {
    "alkali": "Li Na K Rb Cs",
    "alkaline-earth": "Be Mg Ca Sr Ba",
    "early-d": "Sc Ti V Cr Y Zr Nb Mo Hf Ta W Re",
    "late-d": "Cu Pd Ag Pt Au",
    "d10-post": "Zn Cd Hg Al Ga In Tl Sn Pb Bi",
    "metalloid": "B Si Ge As Sb",
    "lanthanide": "La Ce",
}.items():
    for _e in _els.split():
        CLASS_OF[_e] = _cls

# sRGB hex; oxygen red and the vacancy amber are reserved and used by no cation class
MATERIALS = {
    "O": "#D7301F",
    "alkali": "#8E6BBF",
    "alkaline-earth": "#5AAE61",
    "early-d": "#3F7FBF",
    "late-d": "#B07AA1",
    "d10-post": "#7D8CA3",
    "metalloid": "#C2A060",
    "lanthanide": "#2E9C9A",
    "vacancy": "#F2A900",
    "polyhedron": "#7D8CA3",
    "edge": "#2B2B2B",
}
RADII = {"O": 0.30, "cation": 0.40, "neighbour": 0.50, "vacancy": 0.78, "bond": 0.085, "edge": 0.035}
CAMERA_PRESETS = {
    # direction from the cell centre towards the camera (Cartesian), and the camera up vector
    "oblique": ((-0.46, -0.80, 0.37), (0.0, 0.0, 1.0)),   # azimuth -120 deg, elevation 22 deg
    "along-a": ((1.0, 0.0, 0.0), (0.0, 0.0, 1.0)),
    "along-c": ((0.0, 0.0, 1.0), (0.0, 1.0, 0.0)),
}
LIGHT_RIG = {
    # (right, up, toward-camera) offsets in units of the cell diagonal, energy (W), size (Å)
    "key": ((-0.9, 1.0, 1.4), 4500.0, 8.0),
    "fill": ((1.2, -0.2, 1.0), 1500.0, 12.0),
    "rim": ((0.4, 1.2, -1.4), 2500.0, 8.0),
}
FRONT_DEPTH_A = 2.6
WORLD_STRENGTH = 0.55
MARGIN = 1.06


def hex_rgba(h: str, a: float = 1.0) -> tuple[float, float, float, float]:
    """sRGB hex to linear RGBA (Blender colour sockets are scene-linear)."""
    def lin(c):
        c /= 255.0
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    h = h.lstrip("#")
    return (lin(int(h[0:2], 16)), lin(int(h[2:4], 16)), lin(int(h[4:6], 16)), a)


def colour_of(symbol: str) -> str:
    return MATERIALS["O"] if symbol == "O" else MATERIALS[CLASS_OF.get(symbol, "d10-post")]


# ---------------------------------------------------------------- structure
def vacancy_target(cell: np.ndarray, place: str, camera: str) -> np.ndarray:
    """Fractional position for the vacancy after the periodic wrap. ``centre``: the cell centre. ``front``:
    FRONT_DEPTH_A inside every cell face that faces the camera (0.5 along axes seen nearly edge-on), so that
    at most about one atomic layer lies between the vacancy and the camera."""
    if place == "centre":
        return np.full(3, 0.5)
    d = np.array(CAMERA_PRESETS[camera][0], float)
    d /= np.linalg.norm(d)
    rec = np.linalg.inv(cell).T          # rows: reciprocal vectors (face normals), |rec_i| = 1 / d-spacing
    t = np.full(3, 0.5)
    for k in range(3):
        n = rec[k] / np.linalg.norm(rec[k])
        m = FRONT_DEPTH_A * np.linalg.norm(rec[k])
        if n @ d > 0.3:
            t[k] = 1.0 - m
        elif n @ d < -0.3:
            t[k] = m
    return t


def load(cif: Path, vacancy: int, place: str = "centre", camera: str = "oblique") -> dict:
    atoms = read(str(cif))
    if atoms[vacancy].symbol != "O":
        raise ValueError(f"atom {vacancy} of {cif} is {atoms[vacancy].symbol}, not O")
    f = atoms.get_scaled_positions(wrap=False)
    atoms.set_scaled_positions((f - f[vacancy] + vacancy_target(atoms.cell.array, place, camera)) % 1.0)
    sym = np.array(atoms.get_chemical_symbols())
    pos = atoms.get_positions()
    cat = sym != "O"
    i, j, d, S = neighbor_list("ijdS", atoms, 3.2)
    co = cat[i] & (sym[j] == "O")
    # cation-O cutoff per cation element: 1.2 x its shortest cation-O distance
    cut = {e: 1.2 * d[co & (sym[i] == e)].min() for e in np.unique(sym[cat])}
    keep = co & (d <= np.array([cut.get(e, 0.0) for e in sym[i]])) & (j != vacancy)
    inside = keep & ~S.any(axis=1)
    bonds = sorted({(int(a), int(b)) for a, b in zip(i[inside], j[inside], strict=True)})
    vi = (i == vacancy) & cat[j]
    dv = d[vi]
    shell = vi & (d <= 1.2 * dv.min())
    neigh = [(int(n), float(x)) for n, x in sorted(zip(j[shell], d[shell], strict=True), key=lambda t: t[1])]
    if S[shell].any():
        raise ValueError("a first-shell neighbour is a periodic image after re-centring")
    return {"symbols": sym.tolist(), "pos": pos, "cell": atoms.cell.array.copy(), "vacancy": vacancy,
            "bonds": bonds, "neighbours": neigh, "formula": atoms.get_chemical_formula(mode="metal"),
            "cation_O_cutoff": {k: round(float(v), 4) for k, v in cut.items()}}


# ---------------------------------------------------------------- scene helpers
def material(name: str, rgba, rough: float = 0.38, alpha: float = 1.0, coat: float = 0.15):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    p = m.node_tree.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = rgba
    p.inputs["Roughness"].default_value = rough
    p.inputs["Alpha"].default_value = alpha
    if "Coat Weight" in p.inputs:
        p.inputs["Coat Weight"].default_value = coat
    return m


def shell_material(name: str, rgba, alpha: float = 0.30):
    """Translucent shell: transparent centre, more opaque rim (layer-weight facing)."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    pr = nt.nodes.new("ShaderNodeBsdfPrincipled")
    pr.inputs["Base Color"].default_value = rgba
    pr.inputs["Roughness"].default_value = 0.25
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = rgba
    em.inputs["Strength"].default_value = 0.35
    add = nt.nodes.new("ShaderNodeAddShader")
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    lw = nt.nodes.new("ShaderNodeLayerWeight")
    lw.inputs["Blend"].default_value = 0.45
    ramp = nt.nodes.new("ShaderNodeMapRange")
    ramp.inputs["To Min"].default_value = alpha
    ramp.inputs["To Max"].default_value = min(1.0, alpha + 0.5)
    mix = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(pr.outputs[0], add.inputs[0])
    nt.links.new(em.outputs[0], add.inputs[1])
    nt.links.new(lw.outputs["Facing"], ramp.inputs["Value"])
    nt.links.new(ramp.outputs[0], mix.inputs["Fac"])
    nt.links.new(tr.outputs[0], mix.inputs[1])
    nt.links.new(add.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs["Surface"])
    return m


def _mesh(name: str, build) -> bpy.types.Mesh:
    bm = bmesh.new()
    build(bm)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    for poly in me.polygons:
        poly.use_smooth = True
    return me


def unit_sphere():
    return _mesh("sphere", lambda bm: bmesh.ops.create_uvsphere(bm, u_segments=48, v_segments=24, radius=1.0))


def unit_cylinder():
    return _mesh("cylinder", lambda bm: bmesh.ops.create_cone(
        bm, cap_ends=True, segments=24, radius1=1.0, radius2=1.0, depth=1.0))


def link(name, mesh, mat, loc, scale, rot=None):
    ob = bpy.data.objects.new(name, mesh)
    ob.location = Vector(loc)
    ob.scale = scale
    if rot is not None:
        ob.rotation_mode = "QUATERNION"
        ob.rotation_quaternion = rot
    bpy.context.scene.collection.objects.link(ob)
    ob.material_slots[0].link = "OBJECT"
    ob.material_slots[0].material = mat
    return ob


def cylinder_between(mesh, mat, a, b, r, name):
    a, b = Vector(a), Vector(b)
    v = b - a
    return link(name, mesh, mat, (a + b) / 2, (r, r, v.length), v.to_track_quat("Z", "Y"))


# ---------------------------------------------------------------- scene
def build(s: dict, camera: str) -> dict:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sph, cyl = unit_sphere(), unit_cylinder()
    sph.materials.append(None)
    cyl.materials.append(None)
    mats = {e: material(f"atom-{e}", hex_rgba(colour_of(e))) for e in set(s["symbols"])}
    sym, pos, vac = s["symbols"], s["pos"], s["vacancy"]
    neigh = {n for n, _ in s["neighbours"]}
    for k, (e, p) in enumerate(zip(sym, pos, strict=True)):
        if k == vac:
            continue
        r = RADII["O"] if e == "O" else RADII["neighbour" if k in neigh else "cation"]
        link(f"{e}{k}", sph, mats[e], p, (r, r, r))
    for a, b in s["bonds"]:
        mid = (pos[a] + pos[b]) / 2
        cylinder_between(cyl, mats[sym[a]], pos[a], mid, RADII["bond"], f"bond{a}-{b}a")
        cylinder_between(cyl, mats[sym[b]], mid, pos[b], RADII["bond"], f"bond{a}-{b}b")
    rv = RADII["vacancy"]
    link("vacancy", sph, shell_material("vacancy", hex_rgba(MATERIALS["vacancy"])), pos[vac], (rv, rv, rv))
    npos = np.array([pos[n] for n, _ in s["neighbours"]])
    if len(npos) >= 3:
        poly_rgba = hex_rgba(colour_of(sym[next(iter(neigh))]), 1.0)
        pm = material("polyhedron", poly_rgba, rough=0.5, alpha=0.22, coat=0.0)
        if len(npos) >= 4:
            from scipy.spatial import ConvexHull
            faces = [list(f) for f in ConvexHull(npos).simplices]
        else:
            faces = [[0, 1, 2]]
        me = bpy.data.meshes.new("polyhedron")
        me.from_pydata([tuple(p) for p in npos], [], faces)
        me.materials.append(pm)
        ob = bpy.data.objects.new("polyhedron", me)
        bpy.context.scene.collection.objects.link(ob)
        em = material("edge", hex_rgba(MATERIALS["edge"]), rough=0.6, coat=0.0)
        edges = {tuple(sorted((f[x], f[(x + 1) % 3]))) for f in faces for x in range(3)}
        for a, b in edges:
            cylinder_between(cyl, em, npos[a], npos[b], RADII["edge"], f"edge{a}{b}")
    return frame(s, camera)


def frame(s: dict, camera: str) -> dict:
    """Orthographic camera on the preset direction; three-point rig in the camera frame; white world."""
    sc = bpy.context.scene
    pos = s["pos"]
    centre = Vector(s["cell"].sum(axis=0) / 2)
    d, up0 = (Vector(v).normalized() for v in CAMERA_PRESETS[camera])
    right = up0.cross(d).normalized()     # camera local +X
    upv = d.cross(right).normalized()     # camera local +Y; d is local +Z (the camera looks along -d)
    rel = pos - np.array(centre)
    pad = RADII["vacancy"]
    u = rel @ np.array(right)
    v = rel @ np.array(upv)
    w_ext = (u.max() - u.min()) + 2 * pad
    h_ext = (v.max() - v.min()) + 2 * pad
    shift = Vector(right) * float((u.max() + u.min()) / 2) + Vector(upv) * float((v.max() + v.min()) / 2)
    target = centre + shift
    diag = float(np.linalg.norm(s["cell"].sum(axis=0)))
    cam_data = bpy.data.cameras.new("camera")
    cam_data.type = "ORTHO"
    cam = bpy.data.objects.new("camera", cam_data)
    sc.collection.objects.link(cam)
    cam.location = target + d * (2.0 * diag)
    cam.rotation_mode = "QUATERNION"
    cam.rotation_quaternion = Matrix((right, upv, d)).transposed().to_quaternion()
    cam_data.clip_end = 6.0 * diag
    sc.camera = cam
    for name, ((x, y, z), energy, size) in LIGHT_RIG.items():
        ld = bpy.data.lights.new(name, "AREA")
        ld.energy = energy
        ld.size = size
        lo = bpy.data.objects.new(name, ld)
        lo.location = target + diag * (x * right + y * upv + z * d)
        lo.rotation_mode = "QUATERNION"
        lo.rotation_quaternion = (target - lo.location).to_track_quat("-Z", "Y")
        sc.collection.objects.link(lo)
    world = bpy.data.worlds.new("world")
    world.use_nodes = True
    bg = world.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = (1, 1, 1, 1)
    bg.inputs["Strength"].default_value = WORLD_STRENGTH
    sc.world = world
    return {"w_ext": float(w_ext), "h_ext": float(h_ext), "camera": camera, "direction": list(d), "up": list(upv)}


def render(view: dict, out: Path, px: int, samples: int, threads: int, dpi: int, aspect: float | None) -> dict:
    sc = bpy.context.scene
    r = sc.render
    r.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.samples = samples
    sc.cycles.use_adaptive_sampling = True
    sc.cycles.use_denoising = True
    sc.cycles.denoiser = "OPENIMAGEDENOISE"
    sc.cycles.max_bounces = 8
    sc.cycles.transparent_max_bounces = 16
    r.threads_mode = "FIXED"
    r.threads = threads
    r.film_transparent = True
    sc.view_settings.view_transform = "Standard"
    sc.view_settings.look = "None"
    aspect = aspect or view["h_ext"] / view["w_ext"]
    r.resolution_x = px
    r.resolution_y = round(px * aspect)
    r.resolution_percentage = 100
    cam = sc.camera.data
    cam.sensor_fit = "HORIZONTAL"     # ortho_scale is the image width in Å
    cam.ortho_scale = MARGIN * max(view["w_ext"], view["h_ext"] / aspect)
    r.image_settings.file_format = "PNG"
    r.image_settings.color_mode = "RGBA"
    r.image_settings.color_depth = "8"
    tmp = out.with_name(out.stem + ".rgba.png")
    r.filepath = str(tmp)
    bpy.ops.render.render(write_still=True)
    flatten_white(tmp, out, dpi)
    tmp.unlink()
    return {"px": [r.resolution_x, r.resolution_y], "samples": samples, "ortho_scale": cam.ortho_scale}


def flatten_white(src: Path, dst: Path, dpi: int) -> None:
    """Composite the transparent render over white; write RGB PNG with the dpi tag (pHYs)."""
    import OpenImageIO as oiio
    buf = oiio.ImageBuf(str(src))
    px = buf.get_pixels(oiio.FLOAT)
    a = px[..., 3:4]
    rgb = px[..., :3] * a + (1.0 - a)  # straight alpha over white
    spec = oiio.ImageSpec(px.shape[1], px.shape[0], 3, oiio.UINT8)
    spec.attribute("XResolution", float(dpi))
    spec.attribute("YResolution", float(dpi))
    spec.attribute("ResolutionUnit", "inch")
    o = oiio.ImageOutput.create(str(dst))
    o.open(str(dst), spec)
    o.write_image(np.clip(np.round(rgb * 255.0), 0, 255).astype(np.uint8))
    o.close()


def main(argv: list[str]) -> None:
    ap = argparse.ArgumentParser(prog="render_oxide.py")
    ap.add_argument("--cif", type=Path, required=True)
    ap.add_argument("--cif-label", default=None, help="path recorded in the sidecar (the universe-table path)")
    ap.add_argument("--vacancy", type=int, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--px", type=int, default=None, help="image width in pixels (default: width-mm at dpi)")
    ap.add_argument("--width-mm", type=float, default=138.6)
    ap.add_argument("--dpi", type=int, default=300)
    ap.add_argument("--aspect", type=float, default=None, help="height / width (default: fit the cell)")
    ap.add_argument("--samples", type=int, default=32)
    ap.add_argument("--threads", type=int, default=3)
    ap.add_argument("--camera", choices=sorted(CAMERA_PRESETS), default="oblique")
    ap.add_argument("--place", choices=("centre", "front"), default="front",
                    help="where the periodic wrap puts the vacancy (default: front)")
    a = ap.parse_args(argv)
    if a.samples > 128:
        raise SystemExit("at most 128 samples")
    px = a.px or round(a.width_mm / MM_PER_IN * a.dpi)
    s = load(a.cif, a.vacancy, a.place, a.camera)
    view = build(s, a.camera)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    info = render(view, a.out, px, a.samples, a.threads, a.dpi, a.aspect)
    meta = {
        "cif": a.cif_label or str(a.cif), "cif_sha256": hashlib.sha256(a.cif.read_bytes()).hexdigest(),
        "formula": s["formula"], "n_atoms": len(s["symbols"]), "vacancy_atom_index": s["vacancy"],
        "first_shell": [{"index": n, "element": s["symbols"][n], "distance_A": round(x, 4)} for n, x in s["neighbours"]],
        "cation_O_bond_cutoff_A": s["cation_O_cutoff"], "n_bonds_drawn": len(s["bonds"]),
        "vacancy_place": a.place, "vacancy_cartesian_A": [round(float(x), 4) for x in s["pos"][s["vacancy"]]],
        "dpi": a.dpi, "width_mm": round(info["px"][0] / a.dpi * MM_PER_IN, 2), **info, **view,
        "blender": bpy.app.version_string,
    }
    a.out.with_suffix(".render.json").write_text(json.dumps(meta, indent=1) + "\n")
    print("RENDER_META " + json.dumps(meta))


if __name__ == "__main__":
    main(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else [])
