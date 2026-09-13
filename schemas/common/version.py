from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class VersionInfo:
    """
    Canonical version metadata for ROBOMLM components.
    """

    major: int
    minor: int
    patch: int
    label: str | None = None

    def __post_init__(self) -> None:
        if self.major < 0:
            raise ValueError("major version cannot be negative")

        if self.minor < 0:
            raise ValueError("minor version cannot be negative")

        if self.patch < 0:
            raise ValueError("patch version cannot be negative")

    @property
    def value(self) -> str:
        base = f"{self.major}.{self.minor}.{self.patch}"

        if self.label:
            return f"{base}-{self.label}"

        return base

    def __str__(self) -> str:
        return self.value

    def to_dict(self) -> dict[str, int | str | None]:
        return {
            "major": self.major,
            "minor": self.minor,
            "patch": self.patch,
            "label": self.label,
            "version": self.value,
        }

    def is_at_least(self, other: "VersionInfo") -> bool:
        if not isinstance(other, VersionInfo):
            raise TypeError("other must be a VersionInfo")

        return (
            self.major,
            self.minor,
            self.patch,
        ) >= (
            other.major,
            other.minor,
            other.patch,
        )


ROBOMLM_VERSION = VersionInfo(1, 0, 0)