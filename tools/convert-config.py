# VIBECODED SCRIPT PLEASE TAKE A BACKUP BEFORE RUNNING THIS
# TODO: update to latest schema
from pathlib import Path

import yaml


# --- custom string type that will be dumped WITH quotes ---
class QuotedString(str):
    pass


def quoted_presenter(dumper, data):
    # represent as a YAML string scalar and force double quotes
    return dumper.represent_scalar("tag:yaml.org,2002:str", str(data), style='"')


# Register the representer only for QuotedString (NOT for all `str`)
yaml.SafeDumper.add_representer(QuotedString, quoted_presenter)


# Recursively wrap string *values* with QuotedString; keep keys unchanged
def wrap_strings(obj):
    if isinstance(obj, str):
        return QuotedString(obj)
    if isinstance(obj, dict):
        return {k: wrap_strings(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [wrap_strings(i) for i in obj]
    return obj


# --- load original cfg ---
cfg_path = Path("user/cfg.yml")
cfg = yaml.safe_load(cfg_path.read_text())

# --- prepare output dir ---
out_dir = Path("config")
out_dir.mkdir(exist_ok=True)

# --- build output dicts (keys are plain strings) ---
account_cfg = {
    "email": cfg.get("email", ""),
    "password": cfg.get("password", ""),
    "newPassword": cfg.get("newPassword", ""),
    "resetToken": cfg.get("resetToken", ""),
    "authToken": cfg.get("authToken", ""),
}

program_cfg = {
    "programMode": cfg.get("programMode", ""),
    "codeMode": cfg.get("codeMode", ""),
    "browser": cfg.get("browser", ""),
}

# wrap values only
account_cfg = wrap_strings(account_cfg)
program_cfg = wrap_strings(program_cfg)

# dump using SafeDumper (our representer is registered on SafeDumper)
with (out_dir / "account.yml").open("w", encoding="utf-8") as f:
    yaml.safe_dump(account_cfg, f, sort_keys=False, default_flow_style=False)

with (out_dir / "program.yml").open("w", encoding="utf-8") as f:
    yaml.safe_dump(program_cfg, f, sort_keys=False, default_flow_style=False)
