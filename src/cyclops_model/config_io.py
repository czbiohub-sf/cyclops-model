"""YAML config loading for the cyclops_model entry points.

Configs name their storage locations with environment variables — normally
``$OPS_BASE_PATH`` — so that a config is portable across machines and carries
nobody's personal scratch path. :func:`load_config` expands those references as
the config is read.

An unset variable is an error. ``os.path.expandvars`` leaves an unknown ``$VAR``
untouched, which would otherwise send output to a literal ``./$OPS_BASE_PATH/``
directory; failing loudly matches :mod:`cyclops_model.paths`, where an unset
``OPS_BASE_PATH`` also raises rather than falling back.
"""
import os
import re
from pathlib import Path
from typing import Any, Union

import yaml

# A ``$VAR`` or ``${VAR}`` reference that survived expansion, i.e. was not set.
_UNEXPANDED = re.compile(r"\$\{?([A-Za-z_][A-Za-z0-9_]*)\}?")


def _expand(value: Any, where: str) -> Any:
    """Recursively expand environment variables in every string in ``value``."""
    if isinstance(value, str):
        expanded = os.path.expandvars(value)
        leftover = _UNEXPANDED.search(expanded)
        if leftover:
            var = leftover.group(1)
            raise RuntimeError(
                f"{where}: environment variable ${var} is not set, so {value!r} "
                f"cannot be resolved. Set it first, e.g. "
                f'`export {var}="/path/to/ops_data"`.'
            )
        return expanded
    if isinstance(value, dict):
        return {
            key: _expand(item, f"{where}:{key}" if where else str(key))
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [_expand(item, f"{where}[{i}]") for i, item in enumerate(value)]
    return value


def load_config(config_path: Union[str, Path]) -> Any:
    """Load a YAML config, expanding ``$VAR`` references in every string value.

    Args:
        config_path: Path to the YAML config.

    Returns:
        The parsed config, with environment variables expanded.

    Raises:
        RuntimeError: If a referenced environment variable is unset.
    """
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    return _expand(config, where=str(config_path))
