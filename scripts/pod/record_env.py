"""Record the GPU pod environment in results/pod_env.json (runs ON the pod, S07 step 1).

Runs a small matgl MEGNet forward/backward on the GPU first, so the record also proves the stack works.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))


def sh(cmd: str) -> str:
    return subprocess.run(cmd, shell=True, capture_output=True, text=True).stdout.strip()


def main() -> None:
    import torch

    import matgl
    from dftgnn.io.results import write_result
    from dftgnn.models import HParams, build_model

    assert torch.cuda.is_available(), "CUDA unavailable"
    dev = torch.device("cuda")
    net = build_model("S", HParams(), n_host=12, n_site=10, cutoff=5.0).to(dev)
    from dftgnn.graphs import collate_sites
    from dftgnn.train import Store

    st = Store()
    b = collate_sites(st.graphs, st.sites, [0, 1, 2, 3], y=st.sites["target"].float()).to(dev)
    out = net(b)
    out.sum().backward()
    no_grad = [n for n, p in net.named_parameters() if p.grad is None]
    ok = bool(all(torch.isfinite(p.grad).all() for p in net.parameters() if p.grad is not None))
    props = torch.cuda.get_device_properties(0)
    payload = {
        "gpu": {"name": props.name, "total_memory_bytes": props.total_memory, "n_gpus": torch.cuda.device_count(),
                "compute_capability": f"{props.major}.{props.minor}",
                "query": sh("nvidia-smi --query-gpu=name,driver_version,memory.total,pstate,power.limit --format=csv"),
                "nvidia_smi": sh("nvidia-smi")},
        "driver_cuda_version": sh("nvidia-smi | grep -o 'CUDA Version: [0-9.]*'"),
        "torch": {"version": torch.__version__, "cuda_runtime": torch.version.cuda,
                  "cudnn": torch.backends.cudnn.version(), "cuda_available": True},
        "matgl_version": matgl.__version__,
        "matgl_megnet_gpu_forward_backward": {"device": str(dev), "output_shape": list(out.shape),
                                              "all_gradients_finite": ok,
                                              "parameters_without_gradient": no_grad, "model": "S default hparams"},
        "host": {"cpu_count": os.cpu_count(), "affinity": len(os.sched_getaffinity(0)),
                 "mem_total_kib": sh("grep MemTotal /proc/meminfo"), "os": sh("grep PRETTY /etc/os-release"),
                 "cpu_quota_vcpu": sh("echo $(cat /sys/fs/cgroup/cpu/cpu.cfs_quota_us) / $(cat /sys/fs/cgroup/cpu/cpu.cfs_period_us) | bc -l 2>/dev/null"),
                 "cgroup_memory_max": sh("cat /sys/fs/cgroup/memory.max 2>/dev/null || cat /sys/fs/cgroup/memory/memory.limit_in_bytes 2>/dev/null")},
        "storage": {"df_workspace": sh("df -h /workspace"), "mount_workspace": sh("mount | grep workspace"),
                    "df_root": sh("df -h /"),
                    "workspace_is_separate_volume": "fuse" in sh("mount | grep ' /workspace '")},
    }
    print(write_result("pod_env", payload, allow_dirty=False))


if __name__ == "__main__":
    main()
