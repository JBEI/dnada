from typing import Any, Dict

from sqlalchemy.ext.declarative import as_declarative, declared_attr


@as_declarative()
class Base(object):
    id: Any
    __name__: str

    # Generate __tablename__ automatically
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

    def __repr__(cls) -> str:
        params = ", ".join(f"{k}={v}" for k, v in todict(cls).items())
        return f"{cls.__class__.__name__}({params})"


def todict(obj: Base) -> Dict[str, Any]:
    """Return the object's dict excluding private attributes,
    sqlalchemy state and relationship attributes.
    """
    excl = ("_sa_adapter", "_sa_instance_state")
    return {
        k: v
        for k, v in vars(obj).items()
        if not k.startswith("_") and not any(hasattr(v, a) for a in excl)
    }
