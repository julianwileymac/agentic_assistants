"""
PyTorch utility functions.

Provides device detection, GPU information, memory estimation, and
dtype selection for training and inference workloads.

All functions gracefully handle missing torch installation.
"""

from typing import Any, Dict, List, Optional, Tuple

from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)


def is_torch_available() -> bool:
    """Check if PyTorch is installed."""
    try:
        import torch  # noqa: F401
        return True
    except ImportError:
        return False


def is_cuda_available() -> bool:
    """Check if CUDA (NVIDIA GPU) is available."""
    try:
        import torch
        return torch.cuda.is_available()
    except ImportError:
        return False


def is_mps_available() -> bool:
    """Check if MPS (Apple Silicon GPU) is available."""
    try:
        import torch
        return hasattr(torch.backends, "mps") and torch.backends.mps.is_available()
    except (ImportError, AttributeError):
        return False


def get_device(prefer: Optional[str] = None) -> str:
    """
    Auto-detect the best available compute device.

    Args:
        prefer: Preferred device ("cuda", "mps", "cpu"). If available, this
                device is used; otherwise falls back to auto-detection.

    Returns:
        Device string suitable for torch.device()
    """
    if not is_torch_available():
        return "cpu"

    if prefer:
        if prefer == "cuda" and is_cuda_available():
            return "cuda"
        if prefer == "mps" and is_mps_available():
            return "mps"
        if prefer == "cpu":
            return "cpu"

    if is_cuda_available():
        return "cuda"
    if is_mps_available():
        return "mps"
    return "cpu"


def get_gpu_info() -> List[Dict[str, Any]]:
    """
    Get information about available GPUs.

    Returns:
        List of dicts with name, memory_total_mb, memory_free_mb,
        memory_used_mb, and compute_capability per GPU.
    """
    if not is_cuda_available():
        if is_mps_available():
            return [{"index": 0, "name": "Apple Silicon (MPS)", "backend": "mps"}]
        return []

    try:
        import torch

        gpus = []
        for i in range(torch.cuda.device_count()):
            props = torch.cuda.get_device_properties(i)
            mem_total = props.total_mem / (1024 ** 2)
            mem_reserved = torch.cuda.memory_reserved(i) / (1024 ** 2)
            mem_allocated = torch.cuda.memory_allocated(i) / (1024 ** 2)

            gpus.append({
                "index": i,
                "name": props.name,
                "compute_capability": f"{props.major}.{props.minor}",
                "memory_total_mb": round(mem_total, 1),
                "memory_reserved_mb": round(mem_reserved, 1),
                "memory_allocated_mb": round(mem_allocated, 1),
                "memory_free_mb": round(mem_total - mem_reserved, 1),
                "multi_processor_count": props.multi_processor_count,
            })
        return gpus
    except Exception as e:
        logger.error(f"Failed to get GPU info: {e}")
        return []


def get_torch_info() -> Dict[str, Any]:
    """
    Get comprehensive PyTorch environment information.

    Returns:
        Dict with version, CUDA version, device info, etc.
    """
    if not is_torch_available():
        return {"installed": False}

    import torch

    info: Dict[str, Any] = {
        "installed": True,
        "version": torch.__version__,
        "cuda_available": torch.cuda.is_available(),
        "mps_available": is_mps_available(),
        "device": get_device(),
        "gpu_count": torch.cuda.device_count() if torch.cuda.is_available() else 0,
    }

    if torch.cuda.is_available():
        info["cuda_version"] = torch.version.cuda
        info["cudnn_version"] = torch.backends.cudnn.version() if torch.backends.cudnn.is_available() else None
        info["gpus"] = get_gpu_info()

    bf16_support = False
    if torch.cuda.is_available():
        for i in range(torch.cuda.device_count()):
            props = torch.cuda.get_device_properties(i)
            if props.major >= 8:
                bf16_support = True
                break
    info["bf16_supported"] = bf16_support

    return info


def estimate_model_memory(
    num_params: int,
    dtype: str = "float16",
    overhead_factor: float = 1.2,
) -> Dict[str, float]:
    """
    Estimate GPU memory required for a model.

    Args:
        num_params: Number of model parameters
        dtype: Data type (float32, float16, bfloat16, int8, int4)
        overhead_factor: Multiplier for framework overhead

    Returns:
        Dict with estimated memory in MB and GB
    """
    bytes_per_param = {
        "float32": 4,
        "float16": 2,
        "bfloat16": 2,
        "int8": 1,
        "int4": 0.5,
    }

    bpp = bytes_per_param.get(dtype, 2)
    raw_bytes = num_params * bpp
    total_bytes = raw_bytes * overhead_factor

    return {
        "params": num_params,
        "dtype": dtype,
        "raw_memory_mb": round(raw_bytes / (1024 ** 2), 1),
        "estimated_memory_mb": round(total_bytes / (1024 ** 2), 1),
        "estimated_memory_gb": round(total_bytes / (1024 ** 3), 2),
    }


def estimate_training_memory(
    num_params: int,
    method: str = "lora",
    batch_size: int = 4,
    seq_length: int = 2048,
) -> Dict[str, float]:
    """
    Estimate GPU memory for training, accounting for optimizer states
    and activations.

    Args:
        num_params: Number of model parameters
        method: Training method (full, lora, qlora)
        batch_size: Training batch size
        seq_length: Sequence length

    Returns:
        Dict with memory estimates
    """
    if method == "qlora":
        model_mem = num_params * 0.5
        trainable_params = int(num_params * 0.01)
        optimizer_mem = trainable_params * 8
    elif method == "lora":
        model_mem = num_params * 2
        trainable_params = int(num_params * 0.01)
        optimizer_mem = trainable_params * 8
    else:
        model_mem = num_params * 2
        trainable_params = num_params
        optimizer_mem = num_params * 8

    activation_mem = batch_size * seq_length * 4096 * 2

    total = (model_mem + optimizer_mem + activation_mem) * 1.2

    return {
        "model_memory_gb": round(model_mem / (1024 ** 3), 2),
        "optimizer_memory_gb": round(optimizer_mem / (1024 ** 3), 2),
        "activation_memory_gb": round(activation_mem / (1024 ** 3), 2),
        "estimated_total_gb": round(total / (1024 ** 3), 2),
        "trainable_params": trainable_params,
        "method": method,
    }


def clear_gpu_cache() -> None:
    """Clear GPU memory cache."""
    if not is_cuda_available():
        return

    import torch
    torch.cuda.empty_cache()
    import gc
    gc.collect()
    logger.info("GPU cache cleared")


def get_dtype_for_device(device: Optional[str] = None) -> str:
    """
    Get the recommended dtype string for the given device.

    Returns "bfloat16" for Ampere+ GPUs, "float16" for older CUDA,
    "float32" for CPU/MPS.
    """
    device = device or get_device()

    if device == "cpu" or device == "mps":
        return "float32"

    if not is_cuda_available():
        return "float32"

    try:
        import torch
        for i in range(torch.cuda.device_count()):
            props = torch.cuda.get_device_properties(i)
            if props.major >= 8:
                return "bfloat16"
        return "float16"
    except Exception:
        return "float16"


def get_optimal_batch_size(
    model_memory_gb: float,
    available_memory_gb: Optional[float] = None,
    seq_length: int = 2048,
) -> int:
    """
    Suggest an optimal batch size given memory constraints.

    Args:
        model_memory_gb: Model memory footprint
        available_memory_gb: Available GPU memory (auto-detected if None)
        seq_length: Sequence length

    Returns:
        Recommended batch size
    """
    if available_memory_gb is None:
        gpus = get_gpu_info()
        if gpus and "memory_free_mb" in gpus[0]:
            available_memory_gb = gpus[0]["memory_free_mb"] / 1024
        else:
            return 1

    free = available_memory_gb - model_memory_gb
    if free <= 0:
        return 1

    per_sample_gb = (seq_length * 4096 * 2) / (1024 ** 3)
    batch = max(1, int(free / per_sample_gb))
    return min(batch, 32)
