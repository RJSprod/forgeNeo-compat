PREFIX = "[Forge Neo Compatibility]"


def log(message):
    print(f"{PREFIX} {message}")


def debug_enabled(shared):
    try:
        return bool(getattr(shared.opts, "forge_neo_compat_debug_logging", False))
    except Exception:
        return False


def debug(shared, message):
    if debug_enabled(shared):
        log("DEBUG: " + message)
