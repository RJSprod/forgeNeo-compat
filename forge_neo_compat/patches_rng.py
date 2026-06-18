import traceback

from .options import compat_enabled, get_try_reproduce
from .patch_manager import result, save_original


def effective_noise_source(shared, presets):
    if not compat_enabled(shared):
        return shared.opts.randn_source
    forced = presets.get(get_try_reproduce(shared), {}).get("runtime_force_noise_source")
    return forced or shared.opts.randn_source


def patch_rng(shared, presets):
    try:
        import torch
        from modules import devices, rng_philox
        import modules.rng as rng_mod

        def compat_get_noise_source_type():
            return effective_noise_source(shared, presets)

        def randn(seed, shape, generator=None):
            manual_seed((seed + 100000) % 65536 if generator is not None else seed)
            source = compat_get_noise_source_type()
            if source == "NV":
                return torch.asarray((generator or rng_mod.nv_rng).randn(shape), device=devices.device)
            if source == "CPU" or devices.device.type == "mps":
                return torch.randn(shape, device=devices.cpu, generator=generator).to(devices.device)
            return torch.randn(shape, device=devices.device, generator=generator)

        def randn_local(seed, shape):
            source = compat_get_noise_source_type()
            if source == "NV":
                return torch.asarray(rng_philox.Generator(seed).randn(shape), device=devices.device)
            local_device = devices.cpu if source == "CPU" or devices.device.type == "mps" else devices.device
            return torch.randn(shape, device=local_device, generator=torch.Generator(local_device).manual_seed(int(seed))).to(devices.device)

        def randn_like(x):
            source = compat_get_noise_source_type()
            if source == "NV":
                return torch.asarray(rng_mod.nv_rng.randn(x.shape), device=x.device, dtype=x.dtype)
            if source == "CPU" or x.device.type == "mps":
                return torch.randn_like(x, device=devices.cpu).to(x.device)
            return torch.randn_like(x)

        def randn_without_seed(shape, generator=None):
            source = compat_get_noise_source_type()
            if source == "NV":
                return torch.asarray((generator or rng_mod.nv_rng).randn(shape), device=devices.device)
            if source == "CPU" or devices.device.type == "mps":
                return torch.randn(shape, device=devices.cpu, generator=generator).to(devices.device)
            return torch.randn(shape, device=devices.device, generator=generator)

        def manual_seed(seed):
            if compat_get_noise_source_type() == "NV":
                rng_mod.nv_rng = rng_philox.Generator(seed)
            else:
                torch.manual_seed(seed)

        def create_generator(seed):
            source = compat_get_noise_source_type()
            if source == "NV":
                return rng_philox.Generator(seed)
            device = devices.cpu if source == "CPU" or devices.device.type == "mps" else devices.device
            return torch.Generator(device).manual_seed(int(seed))

        for name, fn in {"get_noise_source_type": compat_get_noise_source_type, "randn": randn, "randn_local": randn_local, "randn_like": randn_like, "randn_without_seed": randn_without_seed, "manual_seed": manual_seed, "create_generator": create_generator}.items():
            if hasattr(rng_mod, name):
                save_original(rng_mod, name)
            setattr(rng_mod, name, fn)
        result("RNG", "installed")
    except Exception as exc:
        result("RNG", "failed", str(exc))
        traceback.print_exc()
