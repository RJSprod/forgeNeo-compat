import sys
from pathlib import Path
import traceback

# Forge Neo does not keep the extension root on sys.path after load, so importing
# the sibling ``forge_neo_compat`` package fails with ModuleNotFoundError (seen in
# the compat debugger logs). Make the package importable regardless of loader
# behavior before importing anything from it.
EXTENSION_ROOT = Path(__file__).resolve().parents[1]
if str(EXTENSION_ROOT) not in sys.path:
    sys.path.insert(0, str(EXTENSION_ROOT))

from modules import shared, script_callbacks
from modules.options import OptionInfo

from forge_neo_compat.logging import debug, log
from forge_neo_compat.options import compat_enabled, get_try_reproduce, option_exists, register_options as register_extension_options
from forge_neo_compat.patch_manager import PATCH_RESULTS, install_all_patches
from forge_neo_compat.presets import EXT_VERSION, load_presets

PRESETS = load_presets(EXTENSION_ROOT, logger=log)


def apply_preset():
    if not compat_enabled(shared):
        debug(shared, "Preset application skipped because extension is disabled")
        return
    selected = get_try_reproduce(shared)
    preset = PRESETS.get(selected, PRESETS["None"])
    for key, value in preset.get("options", {}).items():
        if not option_exists(shared, key):
            debug(shared, f"Preset {selected}: option does not exist, skipped {key}")
            continue
        try:
            shared.opts.set(key, value, run_callbacks=False)
            debug(shared, f"Preset {selected}: set {key}={value!r}")
        except Exception as exc:
            log(f"Could not set option {key}: {exc}")
    try:
        shared.opts.save(shared.config_filename)
    except Exception as exc:
        log(f"Could not save config after applying preset: {exc}")


def register_options():
    register_extension_options(shared, OptionInfo, apply_preset)


def app_started_callback(*args, **kwargs):
    force = bool(getattr(shared.opts, "forge_neo_compat_force_patch_reinstall", False))
    install_all_patches(shared, PRESETS, force=force)
    # Reconcile option state with the currently selected preset at startup so a
    # saved selection behaves the same as if the user had just picked it. The
    # native Forge Neo radio has no onchange, so without this the cascade only
    # fires after the next manual change.
    apply_preset()
    debug(shared, f"Extension version: {EXT_VERSION}")
    debug(shared, f"Current preset: {get_try_reproduce(shared)}")
    debug(shared, f"Patch report: {PATCH_RESULTS}")


script_callbacks.on_ui_settings(register_options)

try:
    script_callbacks.on_app_started(app_started_callback)
except Exception:
    try:
        app_started_callback()
    except Exception:
        log("Runtime patch installation failed during fallback startup")
        traceback.print_exc()

log(f"Extension loaded; version {EXT_VERSION}")
