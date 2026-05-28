"""
Qyro-Acne environment checker.

Lightweight diagnostics for local YOLOv11 / PyTorch CUDA readiness.
This script does not install or change anything.
"""

from __future__ import annotations

import importlib
import importlib.metadata as importlib_metadata
import os
import platform
import sys
from dataclasses import dataclass
from typing import Optional


REQUIRED_PACKAGES = [
    ("torch", "torch", "torch"),
    ("torchvision", "torchvision", "torchvision"),
    ("ultralytics", "ultralytics", "ultralytics"),
    ("opencv-python", "cv2", "opencv-python"),
    ("numpy", "numpy", "numpy"),
    ("matplotlib", "matplotlib", "matplotlib"),
    ("pandas", "pandas", "pandas"),
    ("pyyaml", "yaml", "PyYAML"),
]


@dataclass
class CheckResult:
    name: str
    status: str
    detail: str
    hint: Optional[str] = None


def supports_color() -> bool:
    """Return True when ANSI colors are likely to render cleanly."""
    if os.environ.get("NO_COLOR"):
        return False
    if not sys.stdout.isatty():
        return False

    if os.name == "nt":
        # Enables ANSI escape handling in most modern Windows terminals.
        os.system("")

    return True


USE_COLOR = supports_color()


def color(text: str, ansi_code: str) -> str:
    if not USE_COLOR:
        return text
    return f"\033[{ansi_code}m{text}\033[0m"


def status_label(status: str) -> str:
    colors = {
        "PASS": "32;1",
        "WARNING": "33;1",
        "FAIL": "31;1",
        "INFO": "36;1",
    }
    return color(f"[{status}]", colors.get(status, "0"))


def bytes_to_gb(value: int) -> float:
    return value / (1024**3)


def version_for_distribution(distribution_name: str) -> Optional[str]:
    try:
        return importlib_metadata.version(distribution_name)
    except importlib_metadata.PackageNotFoundError:
        return None


def version_for_import(import_name: str) -> Optional[str]:
    try:
        module = importlib.import_module(import_name)
    except Exception:
        return None
    return getattr(module, "__version__", None)


def package_result(display_name: str, import_name: str, distribution_name: str) -> CheckResult:
    if importlib.util.find_spec(import_name) is None:
        return CheckResult(
            display_name,
            "FAIL",
            "Not installed or not visible to this Python environment.",
            f"python -m pip install {display_name}",
        )

    version = version_for_distribution(distribution_name) or version_for_import(import_name)
    version_text = f"version {version}" if version else "installed, version unknown"
    return CheckResult(display_name, "PASS", version_text)


def check_python_version() -> CheckResult:
    version = sys.version_info
    version_text = f"{platform.python_version()} ({platform.architecture()[0]})"

    if version < (3, 8):
        return CheckResult(
            "Python version",
            "FAIL",
            f"{version_text}. Python 3.8+ is required for current Ultralytics-style training workflows.",
            "Install Python 3.10 or 3.11, then recreate the virtual environment.",
        )

    if version >= (3, 13):
        return CheckResult(
            "Python version",
            "WARNING",
            f"{version_text}. Very new Python versions can lag behind PyTorch/Ultralytics wheel support.",
            "If installs fail, use Python 3.10 or 3.11 for the training environment.",
        )

    return CheckResult("Python version", "PASS", f"{version_text}. Suitable for training setup.")


def get_torch_module():
    try:
        return importlib.import_module("torch")
    except Exception as exc:
        return exc


def check_torch_version(torch_obj) -> CheckResult:
    if isinstance(torch_obj, Exception):
        return CheckResult(
            "PyTorch version",
            "FAIL",
            f"Could not import torch: {torch_obj}",
            "Install PyTorch with the CUDA command from https://pytorch.org/get-started/locally/",
        )

    return CheckResult("PyTorch version", "PASS", torch_obj.__version__)


def check_cuda_available(torch_obj) -> CheckResult:
    if isinstance(torch_obj, Exception):
        return CheckResult("CUDA availability", "FAIL", "torch is not importable.")

    if torch_obj.cuda.is_available():
        return CheckResult("CUDA availability", "PASS", "CUDA GPU is visible to PyTorch.")

    return CheckResult(
        "CUDA availability",
        "FAIL",
        "PyTorch cannot see a CUDA-capable GPU.",
        "Check NVIDIA driver, CUDA-enabled PyTorch install, and whether the laptop is using the NVIDIA GPU.",
    )


def check_cuda_version(torch_obj) -> CheckResult:
    if isinstance(torch_obj, Exception):
        return CheckResult("CUDA version", "FAIL", "torch is not importable.")

    cuda_version = getattr(torch_obj.version, "cuda", None)
    if cuda_version:
        return CheckResult("CUDA version", "PASS", f"PyTorch was built with CUDA {cuda_version}.")

    return CheckResult(
        "CUDA version",
        "FAIL",
        "This looks like a CPU-only PyTorch build.",
        "Install a CUDA-enabled PyTorch build from https://pytorch.org/get-started/locally/",
    )


def check_gpu_name(torch_obj) -> CheckResult:
    if isinstance(torch_obj, Exception) or not torch_obj.cuda.is_available():
        return CheckResult("GPU name", "FAIL", "No CUDA GPU available through PyTorch.")

    gpu_name = torch_obj.cuda.get_device_name(0)
    if "5050" in gpu_name:
        return CheckResult("GPU name", "PASS", gpu_name)

    return CheckResult(
        "GPU name",
        "WARNING",
        f"{gpu_name}. This is usable if it is the intended NVIDIA training GPU.",
        "Expected project hardware is an RTX 5050 Laptop GPU.",
    )


def check_vram(torch_obj) -> CheckResult:
    if isinstance(torch_obj, Exception) or not torch_obj.cuda.is_available():
        return CheckResult("Available VRAM", "FAIL", "No CUDA GPU available through PyTorch.")

    try:
        free_bytes, total_bytes = torch_obj.cuda.mem_get_info(0)
        free_gb = bytes_to_gb(free_bytes)
        total_gb = bytes_to_gb(total_bytes)
    except Exception as exc:
        return CheckResult(
            "Available VRAM",
            "WARNING",
            f"Could not read VRAM through PyTorch: {exc}",
            "Try nvidia-smi in a terminal for a second opinion.",
        )

    detail = f"{free_gb:.2f} GB free / {total_gb:.2f} GB total"
    if total_gb >= 7.0 and free_gb >= 3.0:
        return CheckResult("Available VRAM", "PASS", detail)

    if total_gb >= 7.0:
        return CheckResult(
            "Available VRAM",
            "WARNING",
            detail,
            "Close browsers, games, editors with GPU acceleration, or other CUDA jobs before training.",
        )

    return CheckResult(
        "Available VRAM",
        "WARNING",
        detail,
        "Training can still work, but use smaller YOLO model size, lower image size, and smaller batch size.",
    )


def check_cudnn(torch_obj) -> CheckResult:
    if isinstance(torch_obj, Exception):
        return CheckResult("cuDNN availability", "FAIL", "torch is not importable.")

    try:
        available = torch_obj.backends.cudnn.is_available()
        enabled = torch_obj.backends.cudnn.enabled
        version = torch_obj.backends.cudnn.version()
    except Exception as exc:
        return CheckResult("cuDNN availability", "WARNING", f"Could not inspect cuDNN: {exc}")

    if available and enabled:
        return CheckResult("cuDNN availability", "PASS", f"Available and enabled. Version: {version}")

    if available:
        return CheckResult(
            "cuDNN availability",
            "WARNING",
            f"Available but disabled. Version: {version}",
            "Usually this should be enabled for faster CNN training.",
        )

    return CheckResult(
        "cuDNN availability",
        "FAIL",
        "cuDNN is not available in this PyTorch build.",
        "Install a CUDA-enabled PyTorch build that includes cuDNN support.",
    )


def check_mixed_precision(torch_obj) -> CheckResult:
    if isinstance(torch_obj, Exception) or not torch_obj.cuda.is_available():
        return CheckResult("Mixed precision support", "FAIL", "No CUDA GPU available through PyTorch.")

    try:
        device_name = torch_obj.cuda.get_device_name(0)
        major, minor = torch_obj.cuda.get_device_capability(0)
        has_tensor_cores = major >= 7

        x = torch_obj.randn((64, 64), device="cuda")
        if hasattr(torch_obj, "amp") and hasattr(torch_obj.amp, "autocast"):
            autocast_context = torch_obj.amp.autocast("cuda", enabled=True)
        else:
            autocast_context = torch_obj.cuda.amp.autocast(enabled=True)

        with autocast_context:
            y = x @ x
        torch_obj.cuda.synchronize()
        del x, y
        torch_obj.cuda.empty_cache()
    except Exception as exc:
        return CheckResult(
            "Mixed precision support",
            "WARNING",
            f"AMP probe failed: {exc}",
            "Training may still run in full precision, but CUDA/PyTorch should be checked before YOLO training.",
        )

    tensor_core_text = "Tensor Core capable" if has_tensor_cores else "AMP available, Tensor Core support uncertain"
    return CheckResult(
        "Mixed precision support",
        "PASS",
        f"AMP test passed on {device_name} (compute capability {major}.{minor}, {tensor_core_text}).",
    )


def check_training_device(torch_obj) -> CheckResult:
    if isinstance(torch_obj, Exception) or not torch_obj.cuda.is_available():
        return CheckResult(
            "Recommended training device",
            "FAIL",
            "Use CPU only for smoke tests; YOLOv11 training should wait until CUDA is working.",
        )

    try:
        free_bytes, total_bytes = torch_obj.cuda.mem_get_info(0)
        free_gb = bytes_to_gb(free_bytes)
        total_gb = bytes_to_gb(total_bytes)
    except Exception:
        free_gb = 0.0
        total_gb = 0.0

    device_name = torch_obj.cuda.get_device_name(0)
    if total_gb >= 7.0:
        detail = f"Use device=0 ({device_name}). Good starting point: imgsz=640, batch=4, amp=True."
        if free_gb < 3.0:
            return CheckResult(
                "Recommended training device",
                "WARNING",
                detail,
                "Free VRAM is currently low; close GPU-heavy apps or start with batch=2.",
            )
        return CheckResult("Recommended training device", "PASS", detail)

    return CheckResult(
        "Recommended training device",
        "WARNING",
        f"Use device=0 ({device_name}), but start conservatively: imgsz=512, batch=2, amp=True.",
        "Increase image size or batch only after the first training run is stable.",
    )


def print_header() -> None:
    print()
    print(color("Qyro-Acne CUDA / PyTorch Environment Check", "36;1"))
    print("=" * 48)
    print(f"OS: {platform.platform()}")
    print(f"Python executable: {sys.executable}")
    print()


def print_results(title: str, results: list[CheckResult]) -> None:
    print(color(title, "36;1"))
    print("-" * len(title))
    for result in results:
        print(f"{status_label(result.status):>12} {result.name}: {result.detail}")
        if result.hint:
            print(f"{'':>12} Hint: {result.hint}")
    print()


def summarize(results: list[CheckResult]) -> int:
    fail_count = sum(1 for result in results if result.status == "FAIL")
    warning_count = sum(1 for result in results if result.status == "WARNING")

    print(color("Summary", "36;1"))
    print("-------")
    if fail_count:
        print(status_label("FAIL"), f"{fail_count} blocking issue(s) found. Fix these before YOLOv11 training.")
        return 1

    if warning_count:
        print(status_label("WARNING"), f"{warning_count} warning(s) found. Training may work, but read the hints first.")
        return 0

    print(status_label("PASS"), "Environment looks ready for YOLOv11 training.")
    return 0


def print_missing_package_commands(package_results: list[CheckResult]) -> None:
    missing = [result.name for result in package_results if result.status == "FAIL"]
    if not missing:
        return

    print()
    print(color("Suggested install commands", "36;1"))
    print("--------------------------")
    print("No packages were installed automatically. To install the missing packages, run:")
    print()
    print(f"python -m pip install {' '.join(missing)}")
    print()
    if "torch" in missing or "torchvision" in missing:
        print("For CUDA-enabled PyTorch, prefer the official command from:")
        print("https://pytorch.org/get-started/locally/")


def main() -> int:
    print_header()

    torch_obj = get_torch_module()

    system_results = [
        check_python_version(),
        check_torch_version(torch_obj),
        check_cuda_available(torch_obj),
        check_cuda_version(torch_obj),
        check_gpu_name(torch_obj),
        check_vram(torch_obj),
        check_cudnn(torch_obj),
        check_mixed_precision(torch_obj),
        check_training_device(torch_obj),
    ]
    package_results = [
        package_result(display_name, import_name, distribution_name)
        for display_name, import_name, distribution_name in REQUIRED_PACKAGES
    ]

    print_results("System checks", system_results)
    print_results("Required package checks", package_results)

    all_results = system_results + package_results
    exit_code = summarize(all_results)
    print_missing_package_commands(package_results)

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
