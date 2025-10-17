"""Compatibility shim to allow importing ih_search_service when running tests
from the repository root. This delegates to the real package located under
the `function/ih_search_service` directory.

This avoids needing to change test code or pytest config.
"""
import sys
import os

# Compute path to the actual package inside the function/ directory
PKG_PATH = os.path.join(os.path.dirname(__file__), 'function', 'ih_search_service')
if os.path.isdir(PKG_PATH):
    # Prepend so imports prefer the real package
    if PKG_PATH not in sys.path:
        sys.path.insert(0, PKG_PATH)

# Now import the real package (this will load function/ih_search_service/__init__.py)
try:
    # importlib.import_module would also work, but a simple import ensures module is loaded
    import importlib
    # Import the real package located under function/ih_search_service
    _real = importlib.import_module('ih_search_service')  # type: ignore
    # If the real package has an 'app' module, ensure it's available as a submodule
    try:
        _app = importlib.import_module('app')
        # Register as ih_search_service.app
        sys.modules.setdefault('ih_search_service.app', _app)
        setattr(_real, 'app', _app)
    except Exception:
        # ignore if app not present yet; tests will surface errors
        pass
except Exception:
    # If import fails, allow the error to surface when tests try to import symbols
    pass
