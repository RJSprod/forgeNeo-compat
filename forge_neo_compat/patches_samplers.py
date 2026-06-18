import functools
import importlib
import inspect

from .options import compat_enabled
from .patch_manager import result, save_original


def _rewrite_sigmas(fn, args, kwargs):
    sig = inspect.signature(fn)
    bound = sig.bind_partial(*args, **kwargs)
    if "sigma_min" in sig.parameters:
        bound.arguments["sigma_min"] = 0.1
    if "sigma_max" in sig.parameters:
        bound.arguments["sigma_max"] = 10.0
    return bound.args, bound.kwargs


def patch_scheduler_sigmas(shared):
    for module_name in ("modules.sd_schedulers", "modules.sd_samplers_kdiffusion", "k_diffusion.sampling"):
        try:
            module = importlib.import_module(module_name)
        except Exception:
            continue
        for attr in dir(module):
            if "karras" not in attr.lower() or "sigma" not in attr.lower():
                continue
            target = getattr(module, attr)
            if not callable(target):
                continue
            original = save_original(module, attr)
            @functools.wraps(original)
            def wrapper(*args, __fn=original, **kwargs):
                if compat_enabled(shared) and getattr(shared.opts, "use_old_karras_scheduler_sigmas", False):
                    try:
                        args, kwargs = _rewrite_sigmas(__fn, args, kwargs)
                    except Exception:
                        kwargs.setdefault("sigma_min", 0.1)
                        kwargs.setdefault("sigma_max", 10.0)
                return __fn(*args, **kwargs)
            setattr(module, attr, wrapper)
            result("Karras sigma", "installed", f"{module_name}.{attr}")
            return
    result("Karras sigma", "skipped", "no compatible target found")


def patch_sampler_alpha_downcast(shared):
    result("Alpha-bar downcast", "skipped", "no stable Forge Neo sampler entry point detected; option is registered for native builds")
