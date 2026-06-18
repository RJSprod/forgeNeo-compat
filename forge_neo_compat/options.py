import gradio as gr

from .presets import PRESET_CHOICES
from .logging import debug, log

SECTION = ("compatibility", "Compatibility")


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


def ensure_try_reproduce_choices(shared, name="forge_try_reproduce"):
    """Make sure every preset we know about is selectable on the native radio.

    Newer Forge Neo already exposes the full choice list, but if a build ships a
    narrower set we extend it rather than replace it, so native choices are
    never lost.
    """
    try:
        info = shared.opts.data_labels[name]
        args = getattr(info, "component_args", None)
        if not isinstance(args, dict):
            return
        choices = args.get("choices")
        if not isinstance(choices, list):
            return
        for choice in PRESET_CHOICES:
            if choice not in choices:
                choices.append(choice)
    except Exception as exc:  # never break startup over a cosmetic merge
        debug(shared, f"Could not reconcile forge_try_reproduce choices: {exc}")


def attach_try_reproduce_onchange(shared, apply_preset, name="forge_try_reproduce"):
    """Wire the preset cascade onto an already-existing forge_try_reproduce.

    Newer Forge Neo ships forge_try_reproduce natively but with no onchange
    callback, so selecting a preset never cascades to randn_source / the
    compatibility flags the way old Forge did natively. Chain apply_preset onto
    whatever callback already exists instead of skipping because the option is
    present (the bug that made the extension a no-op on Forge Neo).
    """
    if not option_exists(shared, name):
        return False
    info = shared.opts.data_labels[name]
    existing = getattr(info, "onchange", None)
    if existing is apply_preset or getattr(existing, "_fnc_wrapped", False):
        debug(shared, "forge_try_reproduce onchange already wired")
        return True
    if existing is None:
        info.onchange = apply_preset
    else:
        def chained(*args, _orig=existing, **kwargs):
            _orig()
            apply_preset()
        chained._fnc_wrapped = True
        info.onchange = chained
    debug(shared, "Attached apply_preset onchange to existing forge_try_reproduce")
    return True


def compat_enabled(shared):
    return bool(getattr(shared.opts, "forge_neo_compat_enabled", True))


def register_options(shared, OptionInfo, apply_preset):
    add_option_if_missing(shared, "forge_neo_compat_enabled", OptionInfo(True, "Enable Forge Neo Compatibility Restorer", section=SECTION).needs_reload_ui())
    add_option_if_missing(shared, "forge_neo_compat_debug_logging", OptionInfo(False, "Compatibility Restorer debug logging", section=SECTION))
    add_option_if_missing(shared, "forge_neo_compat_force_patch_reinstall", OptionInfo(False, "Force Compatibility Restorer patch reinstall on app start", section=SECTION).needs_reload_ui())
    if option_exists(shared, "forge_try_reproduce"):
        ensure_try_reproduce_choices(shared)
        attach_try_reproduce_onchange(shared, apply_preset)
    else:
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
