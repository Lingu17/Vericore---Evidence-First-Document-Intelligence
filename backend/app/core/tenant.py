"""Request-local workspace selection; no user input can select another workspace."""
from contextvars import ContextVar
from threading import RLock

current_user = ContextVar("vericore_user", default=None)
_services = {}
_lock = RLock()


class ScopedService:
    def __init__(self, default, factory, name):
        object.__setattr__(self, "default", default)
        object.__setattr__(self, "factory", factory)
        object.__setattr__(self, "name", name)

    def selected(self):
        user = current_user.get()
        if not user:
            return self.default
        key = (self.name, user["id"])
        with _lock:
            if key not in _services:
                _services[key] = self.factory(user["id"])
            return _services[key]

    def __getattr__(self, name):
        return getattr(self.selected(), name)

    def __setattr__(self, name, value):
        setattr(self.selected(), name, value)
