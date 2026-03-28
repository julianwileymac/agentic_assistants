"""
DTO boundary layer with configurable include/exclude/rename/partial semantics.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, ClassVar, Generic, Optional, TypeVar, get_args, get_origin

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


@dataclass
class DTOConfig:
    """Configuration options for a DTO class."""

    exclude: set[str] = field(default_factory=set)
    include: Optional[set[str]] = None
    rename_fields: dict[str, str] = field(default_factory=dict)
    rename_strategy: Optional[str] = None
    max_nested_depth: int = 1
    partial: bool = False
    forbid_unknown_fields: bool = False
    drop_none: bool = False


def _to_camel(name: str) -> str:
    parts = name.split("_")
    return parts[0] + "".join(p.capitalize() for p in parts[1:])


def _to_pascal(name: str) -> str:
    return "".join(p.capitalize() for p in name.split("_"))


_RENAME_STRATEGIES: dict[str, Any] = {
    "camel": _to_camel,
    "lower_camel": _to_camel,
    "pascal": _to_pascal,
}


class BaseDTO(Generic[T]):
    """Generic DTO converter for model -> dict and dict -> model boundaries."""

    Config: ClassVar[DTOConfig] = DTOConfig()

    @classmethod
    def _get_config(cls) -> DTOConfig:
        cfg: Any = getattr(cls, "Config", DTOConfig())
        if isinstance(cfg, DTOConfig):
            return DTOConfig(
                exclude=set(cfg.exclude),
                include=set(cfg.include) if cfg.include is not None else None,
                rename_fields=dict(cfg.rename_fields),
                rename_strategy=cfg.rename_strategy,
                max_nested_depth=cfg.max_nested_depth,
                partial=cfg.partial,
                forbid_unknown_fields=cfg.forbid_unknown_fields,
                drop_none=cfg.drop_none,
            )

        if isinstance(cfg, type) and issubclass(cfg, DTOConfig):
            return DTOConfig(
                exclude=set(getattr(cfg, "exclude", set())),
                include=(
                    set(getattr(cfg, "include"))
                    if getattr(cfg, "include", None) is not None
                    else None
                ),
                rename_fields=dict(getattr(cfg, "rename_fields", {})),
                rename_strategy=getattr(cfg, "rename_strategy", None),
                max_nested_depth=int(getattr(cfg, "max_nested_depth", 1)),
                partial=bool(getattr(cfg, "partial", False)),
                forbid_unknown_fields=bool(getattr(cfg, "forbid_unknown_fields", False)),
                drop_none=bool(getattr(cfg, "drop_none", False)),
            )

        return DTOConfig()

    @classmethod
    def _get_model_type(cls) -> type[BaseModel]:
        for base in getattr(cls, "__orig_bases__", []):
            origin = get_origin(base)
            if origin is BaseDTO or (origin is not None and issubclass(origin, BaseDTO)):
                args = get_args(base)
                if args:
                    return args[0]  # type: ignore[return-value]
        raise TypeError(f"{cls.__name__} must specify a model type parameter, e.g. BaseDTO[User]")

    @classmethod
    def _apply_rename(cls, key: str, cfg: DTOConfig) -> str:
        if key in cfg.rename_fields:
            return cfg.rename_fields[key]
        if cfg.rename_strategy and cfg.rename_strategy in _RENAME_STRATEGIES:
            return _RENAME_STRATEGIES[cfg.rename_strategy](key)
        return key

    @classmethod
    def _reverse_rename_map(cls, model_fields: set[str], cfg: DTOConfig) -> dict[str, str]:
        reverse = {v: k for k, v in cfg.rename_fields.items()}
        if cfg.rename_strategy:
            for field_name in model_fields:
                reverse.setdefault(cls._apply_rename(field_name, cfg), field_name)
        return reverse

    @classmethod
    def _serialize_value(
        cls,
        value: Any,
        *,
        depth: int,
        max_depth: int,
        drop_none: bool,
    ) -> Any:
        if isinstance(value, BaseModel):
            raw = value.model_dump(mode="python")
            if depth >= max_depth:
                return value.model_dump(mode="json")
            return {
                k: cls._serialize_value(v, depth=depth + 1, max_depth=max_depth, drop_none=drop_none)
                for k, v in raw.items()
                if not (drop_none and v is None)
            }

        if isinstance(value, dict):
            return {
                k: cls._serialize_value(v, depth=depth + 1, max_depth=max_depth, drop_none=drop_none)
                for k, v in value.items()
                if not (drop_none and v is None)
            }

        if isinstance(value, (list, tuple, set)):
            return [
                cls._serialize_value(v, depth=depth + 1, max_depth=max_depth, drop_none=drop_none)
                for v in value
                if not (drop_none and v is None)
            ]

        return value

    @classmethod
    def _filter_fields(cls, data: dict[str, Any], cfg: DTOConfig) -> dict[str, Any]:
        if cfg.include is not None:
            data = {k: v for k, v in data.items() if k in cfg.include}
        if cfg.exclude:
            data = {k: v for k, v in data.items() if k not in cfg.exclude}
        if cfg.drop_none:
            data = {k: v for k, v in data.items() if v is not None}
        return data

    @classmethod
    def from_model(cls, model: T, **overrides: Any) -> dict[str, Any]:
        """Convert a model instance into a DTO-safe dictionary."""
        cfg = cls._get_config()
        raw = model.model_dump(mode="python")
        serialized = {
            k: cls._serialize_value(
                v,
                depth=0,
                max_depth=max(0, cfg.max_nested_depth),
                drop_none=cfg.drop_none,
            )
            for k, v in raw.items()
        }
        filtered = cls._filter_fields(serialized, cfg)
        renamed = {cls._apply_rename(k, cfg): v for k, v in filtered.items()}
        renamed.update(overrides)
        return renamed

    @classmethod
    def from_model_list(cls, models: list[T], **overrides: Any) -> list[dict[str, Any]]:
        return [cls.from_model(item, **overrides) for item in models]

    @classmethod
    def to_model(cls, data: dict[str, Any]) -> T:
        """Convert DTO data back into the configured model type."""
        cfg = cls._get_config()
        model_cls = cls._get_model_type()
        model_fields = set(model_cls.model_fields.keys())
        reverse = cls._reverse_rename_map(model_fields, cfg)
        mapped = {reverse.get(k, k): v for k, v in data.items()}

        if cfg.forbid_unknown_fields:
            extra = set(mapped.keys()) - model_fields
            if extra:
                raise ValueError(f"Unknown fields: {sorted(extra)}")

        if cfg.partial:
            return cls._partial_validate(model_cls, mapped)
        return model_cls.model_validate(mapped)

    @classmethod
    def to_model_list(cls, rows: list[dict[str, Any]]) -> list[T]:
        return [cls.to_model(item) for item in rows]

    @classmethod
    def round_trip(cls, model: T) -> T:
        """Serialize then validate back into the model type."""
        payload = cls.from_model(model)
        cfg = cls._get_config()
        model_cls = cls._get_model_type()
        reverse = cls._reverse_rename_map(set(model_cls.model_fields.keys()), cfg)
        mapped = {reverse.get(k, k): v for k, v in payload.items()}

        # Preserve omitted required fields when DTO config intentionally excludes them.
        original = model.model_dump(mode="python")
        for field_name in model_cls.model_fields:
            if field_name not in mapped and field_name in original:
                mapped[field_name] = original[field_name]

        if cfg.partial:
            return cls._partial_validate(model_cls, mapped)
        return model_cls.model_validate(mapped)

    @classmethod
    def _partial_validate(cls, model_cls: type[T], data: dict[str, Any]) -> T:
        merged = dict(data)
        for name, field_info in model_cls.model_fields.items():
            if name in merged:
                continue
            if field_info.default_factory is not None:
                merged[name] = field_info.default_factory()
            elif not field_info.is_required():
                merged[name] = field_info.default
            else:
                merged[name] = None
        return model_cls.model_validate(merged)


class CreateDTO(BaseDTO[T]):
    """DTO for create endpoints."""

    class Config(DTOConfig):
        exclude = {"id", "created_at", "updated_at", "deleted_at"}


class ReadDTO(BaseDTO[T]):
    """DTO for read endpoints."""

    class Config(DTOConfig):
        exclude: set[str] = set()


class UpdateDTO(BaseDTO[T]):
    """DTO for update endpoints (partial by default)."""

    class Config(DTOConfig):
        exclude = {"id", "created_at"}
        partial = True


__all__ = [
    "DTOConfig",
    "BaseDTO",
    "CreateDTO",
    "ReadDTO",
    "UpdateDTO",
]

