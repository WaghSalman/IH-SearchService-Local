"""Package initializer for ih_search_service.

This module exposes convenient top-level aliases for internal subpackages
(`model`, `enums`, `schema`, `controllers`) so older tests and code that
import them as top-level modules (for example `import model.influencer`)
continue to work when `ih_search_service` is imported as a package.

This preserves backwards compatibility without requiring test changes.
"""
import sys

# Import subpackages so they are initialized as package modules
from . import model as _model
from . import enums as _enums
from . import schema as _schema
from . import controllers as _controllers

# Register top-level aliases if not already present in sys.modules
sys.modules.setdefault('model', _model)
sys.modules.setdefault('enums', _enums)
sys.modules.setdefault('schema', _schema)
sys.modules.setdefault('controllers', _controllers)
