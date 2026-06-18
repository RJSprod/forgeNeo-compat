import copy
import json
from pathlib import Path

EXT_VERSION = "0.2.0"

PRESET_CHOICES = [
    "None",
    "Diffusers",
    "ComfyUI",
    "WebUI 1.5",
    "InvokeAI",
    "EasyDiffusion",
    "DrawThings",
]

DEFAULT_PRESETS = {
    "None": {"runtime_force_noise_source": None, "options": {}},
    "ComfyUI": {
        "runtime_force_noise_source": "CPU",
        "options": {"randn_source": "CPU", "emphasis": "Original", "sdxl_crop_top": 0, "sdxl_crop_left": 0},
    },
    "DrawThings": {"runtime_force_noise_source": "CPU", "options": {"randn_source": "CPU", "emphasis": "Original"}},
    "Diffusers": {
        "runtime_force_noise_source": "CPU",
        "options": {"randn_source": "CPU", "emphasis": "Original", "sdxl_crop_top": 0, "sdxl_crop_left": 0},
    },
    "WebUI 1.5": {
        "runtime_force_noise_source": None,
        "options": {
            "emphasis": "Original",
            "use_old_hires_fix_width_height": True,
            "hires_fix_use_firstpass_conds": True,
            "use_old_scheduling": True,
            "use_downcasted_alpha_bar": True,
        },
    },
    "InvokeAI": {
        "runtime_force_noise_source": "CPU",
        "options": {"randn_source": "CPU", "emphasis": "Original", "sdxl_crop_top": 0, "sdxl_crop_left": 0},
    },
    "EasyDiffusion": {"runtime_force_noise_source": "CPU", "options": {"randn_source": "CPU", "emphasis": "Original"}},
}


def load_presets(extension_root=None, logger=None):
    presets = copy.deepcopy(DEFAULT_PRESETS)
    if not extension_root:
        return presets
    path = Path(extension_root) / "presets.json"
    if not path.exists():
        return presets
    try:
        user_presets = json.loads(path.read_text(encoding="utf8"))
        for name, preset in user_presets.items():
            base = presets.setdefault(name, {"runtime_force_noise_source": None, "options": {}})
            base.update({k: v for k, v in preset.items() if k != "options"})
            base.setdefault("options", {}).update(preset.get("options", {}))
    except Exception as exc:
        if logger:
            logger(f"Could not load presets.json: {exc}")
    return presets
