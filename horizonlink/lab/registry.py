"""Plugin-style calculation registry.

Every HorizonLink calculation can register a small adapter here. The unified
runner supplies one input object; each compatible calculation returns a named
result. A failing/unsupported calculation is isolated instead of aborting the
whole research run.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass(frozen=True)
class CalculationResult:
    name: str
    category: str
    status: str
    outputs: dict[str, Any] = field(default_factory=dict)
    assumptions: tuple[str, ...] = ()
    notes: tuple[str, ...] = ()
    error: str | None = None


@dataclass(frozen=True)
class Calculation:
    name: str
    category: str
    run: Callable[[Any], CalculationResult]
    description: str = ""
    tags: tuple[str, ...] = ()


class CalculationRegistry:
    def __init__(self) -> None:
        self._items: dict[str, Calculation] = {}

    def register(self, calculation: Calculation) -> Calculation:
        if calculation.name in self._items:
            raise ValueError(f"calculation already registered: {calculation.name}")
        self._items[calculation.name] = calculation
        return calculation

    def all(self) -> tuple[Calculation, ...]:
        return tuple(self._items[k] for k in sorted(self._items))

    def names(self) -> tuple[str, ...]:
        return tuple(sorted(self._items))


registry = CalculationRegistry()


def calculation(name: str, category: str, *, description: str = "", tags: tuple[str, ...] = ()):
    """Decorator for adding a calculation without changing the runner."""
    def decorate(fn: Callable[[Any], CalculationResult]):
        registry.register(Calculation(name, category, fn, description, tags))
        return fn
    return decorate
