# Expose the SQLAlchemy instance so that `from . import db` returns the db object,
# not the submodule `src.models.db`.
from .db import db

__all__ = ["db"]
