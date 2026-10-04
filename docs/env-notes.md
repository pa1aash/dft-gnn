# Environment notes

## Local (macOS, osx-arm64)
- `env/environment-local.yml`, environment name `dftgnn`, resolved list in `env/lock-local.txt`.
- torch is taken from conda-forge. The PyPI torch wheel and conda numpy/scikit-learn each ship an OpenMP
  runtime, and importing both in one process aborts with `OMP: Error #15`. Using one torch source avoids it.
- torch_geometric and mace-torch come from PyPI (pure Python on top of the conda torch).

## matgl backend (checked on PyPI, release 4.1.0)
- matgl 4.1.0 requires `torch-geometric` (PyG). It does not list DGL among its requirements.
- Other requirements: torch, torchdata, lightning, pymatgen-core, ase, pydantic, numpy, huggingface_hub, boto3.
- Requires Python >= 3.11. Optional extras: ops, alchmtk, jax.
- Consequence: the MEGNet backbone and torch_geometric share one graph framework (PyG) on the GPU pod.

## GPU (Linux CUDA)
- `env/environment-gpu.yml` and `env/Dockerfile.gpu` add matgl to the local stack.
- No versions are pinned that have not been resolved; the pod resolves them at build time and the lock must be
  recorded after the first build.
- The pod never holds git credentials; results are copied back and committed from the Mac.

## matgl on the Mac (throwaway env, Python 3.11, pip install matgl)
- Installed matgl 4.1.0 and `import matgl` succeeded on osx-arm64 (only a torch.jit.script deprecation warning).
- Not added to the local env; it stays in the GPU specs.
