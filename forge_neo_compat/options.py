import gradio as gr

from .presets import PRESET_CHOICES
from .logging import debug, log

SECTION = ("compatibility", "Compatibility", "sd")


def option_exists(shared, name):
    return hasattr(shared, "opts") and name in getattr(shared.opts, "data_labels", {})


def add_option_if_missing(shared, name, option_info):
    if option_exists(shared, name):
        debug(shared, f"Option already exists; not re-adding: {name}")
        return False
    shared.opts.add_option(name, option_info)
    debug(shared, f"Option added: {name}")
    return True


def get_try_reproduce(shared):
    if hasattr(shared.opts, "forge_try_reproduce"):
        return shared.opts.forge_try_reproduce
    if hasattr(shared.opts, "neo_forge_try_reproduce"):
        return shared.opts.neo_forge_try_reproduce
    return "None"


def compat_enabled(shared):
    return bool(getattr(shared.opts, "forge_neo_compat_enabled", True))


def register_options(shared, OptionInfo, apply_preset):
    add_option_if_missing(shared, "forge_neo_compat_enabled", OptionInfo(True, "Enable Forge Neo Compatibility Restorer", section=SECTION).needs_reload_ui())
    add_option_if_missing(shared, "forge_neo_compat_debug_logging", OptionInfo(False, "Compatibility Restorer debug logging", section=SECTION))
    add_option_if_missing(shared, "forge_neo_compat_force_patch_reinstall", OptionInfo(False, "Force Compatibility Restorer patch reinstall on app start", section=SECTION).needs_reload_ui())
    add_option_if_missing(shared, "forge_try_reproduce", OptionInfo("None", "Try to reproduce the results from external software", gr.Radio, {"choices": PRESET_CHOICES}, onchange=apply_preset, section=SECTION))
    add_option_if_missing(shared, "auto_backcompat", OptionInfo(True, "Automatic backward compatibility", section=SECTION))
    add_option_if_missing(shared, "use_old_emphasis_implementation", OptionInfo(False, "Use old emphasis implementation. Can be useful to reproduce old seeds.", section=SECTION))
    add_option_if_missing(shared, "use_old_karras_scheduler_sigmas", OptionInfo(False, "Use old karras scheduler sigmas (0.1 to 10).", section=SECTION))
    add_option_if_missing(shared, "no_dpmpp_sde_batch_determinism", OptionInfo(False, "Do not make DPM++ SDE deterministic across different batch sizes.", section=SECTION))
    add_option_if_missing(shared, "use_old_hires_fix_width_height", OptionInfo(False, "For Hires. Fix, use Width/Height sliders to set final resolution.", section=SECTION))
    add_option_if_missing(shared, "hires_fix_use_firstpass_conds", OptionInfo(False, "For Hires. Fix, calculate Hires pass conds using first pass Extra Networks.", section=SECTION))
    add_option_if_missing(shared, "use_old_scheduling", OptionInfo(False, "Use old prompt editing timelines.", section=SECTION))
    add_option_if_missing(shared, "use_downcasted_alpha_bar", OptionInfo(False, "Downcast model alphas_cumprod to fp16 before sampling.", section=SECTION))
    add_option_if_missing(shared, "refiner_switch_by_sample_steps", OptionInfo(False, "Switch to refiner by sampling steps instead of model timesteps.", section=SECTION))
    log("Options registered")
