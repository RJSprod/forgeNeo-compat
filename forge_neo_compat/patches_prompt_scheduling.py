from .patch_manager import result


def patch_prompt_scheduling(shared):
    result("Prompt scheduling", "skipped", "no stable Forge Neo prompt schedule adapter detected; option is registered for native builds")
