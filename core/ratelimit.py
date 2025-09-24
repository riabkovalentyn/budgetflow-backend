"""Ratelimit shim.

If django-ratelimit is installed we use its decorator. Otherwise we expose a
no-op decorator so the application (and tests) still run without the optional
dependency. This prevents hard failures in environments where the package was
not yet installed.
"""
from __future__ import annotations

try:  # pragma: no cover - trivial import path
    from ratelimit.decorators import ratelimit as _ratelimit
except Exception:  # broad: any ImportError or unexpected issue
    def _ratelimit(*_args, **_kwargs):  # type: ignore
        def decorator(func):
            return func
        return decorator

ratelimit = _ratelimit  # re-export
