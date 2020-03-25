from typing import Any

try:
    import pkg_resources

    pkg_resources.declare_namespace(__name__)
except ImportError:
    import pkgutil

    __path__: Any = pkgutil.extend_path(__path__, __name__)
