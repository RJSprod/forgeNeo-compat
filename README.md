# Forge Neo Compatibility Restorer

A Forge Neo WebUI extension that restores the legacy **Settings → Stable Diffusion → Compatibility** controls from old Forge and wires the most stable compatibility behaviors back into current Forge Neo builds.

## Features

- Restores the `forge_try_reproduce` radio option with the old choices: `None`, `Diffusers`, `ComfyUI`, `WebUI 1.5`, `InvokeAI`, `EasyDiffusion`, and `DrawThings`.
- Adds the legacy compatibility toggles, including Karras sigma, prompt scheduling, hires-fix, alpha-bar, and refiner compatibility flags.
- Applies preset option mappings from a single preset table.
- Forces the runtime RNG source to CPU for ComfyUI, Diffusers, InvokeAI, EasyDiffusion, and DrawThings compatibility presets while leaving `None` controlled by `randn_source`.
- Avoids duplicate option registration when Forge Neo already exposes a native option.
- Logs installed and skipped patches so Forge Neo code drift is visible without breaking startup.

## Installation

Place this repository or extension folder under:

```text
extensions/sd-forge-neo-compatibility/
```

Restart Forge Neo, then open **Settings → Stable Diffusion → Compatibility**.

## Optional preset override

Create `presets.json` in the extension root to override or extend built-in presets:

```json
{
  "ComfyUI": {
    "runtime_force_noise_source": "CPU",
    "options": {
      "randn_source": "CPU",
      "emphasis": "Original"
    }
  }
}
```

## Compatibility notes

Some behaviors depend on exact Forge Neo internals and are intentionally capability-based. If a stable adapter is not detected, the extension registers the option and logs a skipped patch rather than guessing destructively. The RNG and Karras sigma patches are implemented directly; prompt scheduling, alpha-bar downcast, hires-fix, and refiner hooks are left for native support or future adapters when stable targets are available.
