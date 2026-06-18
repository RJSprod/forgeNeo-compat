import importlib

from .logging import debug, log

PATCHED = False
ORIGINALS = {}
PATCH_RESULTS = []


def result(name, status, detail=""):
    PATCH_RESULTS.append((name, status, detail))
    msg = f"{name} patch {status}"
    if detail:
        msg += f": {detail}"
    log(msg)


def save_original(module, attr):
    key = f"{module.__name__}.{attr}"
    if key not in ORIGINALS:
        ORIGINALS[key] = getattr(module, attr)
    return ORIGINALS[key]


def restore_all_patches():
    for dotted, original in list(ORIGINALS.items()):
        module_name, attr = dotted.rsplit(".", 1)
        module = importlib.import_module(module_name)
        setattr(module, attr, original)


def install_all_patches(shared, presets, force=False):
    global PATCHED
    if PATCHED and not force:
        debug(shared, "Runtime patches already installed")
        return
    if force and PATCHED:
        restore_all_patches()
        PATCHED = False
    if not bool(getattr(shared.opts, "forge_neo_compat_enabled", True)):
        log("Compatibility runtime patches disabled by setting")
        return
    from .patches_rng import patch_rng
    from .patches_samplers import patch_scheduler_sigmas, patch_sampler_alpha_downcast
    from .patches_prompt_scheduling import patch_prompt_scheduling
    from .patches_hires import patch_hires
    from .patches_refiner import patch_refiner

    patch_rng(shared, presets)
    patch_scheduler_sigmas(shared)
    patch_sampler_alpha_downcast(shared)
    patch_prompt_scheduling(shared)
    patch_hires(shared)
    patch_refiner(shared)
    PATCHED = True
