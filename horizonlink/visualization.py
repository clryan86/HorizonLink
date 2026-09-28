"""Optional plotting helpers for HorizonLink experiment outputs."""

from __future__ import annotations

from collections.abc import Iterable


def plot_horizon_profile(
    radius_rs: Iterable[float],
    received_frequency_hz: Iterable[float],
    received_power_fraction: Iterable[float],
):
    """Create two standalone matplotlib figures for a horizon profile.

    Matplotlib is an optional dependency. Install with ``pip install -e .[viz]``.
    The function returns the two figure objects and does not call ``show()``.
    """
    try:
        import matplotlib.pyplot as plt
    except ImportError as exc:  # pragma: no cover - environment dependent
        raise RuntimeError("Install HorizonLink with the 'viz' extra to plot results") from exc

    x = list(radius_rs)
    frequency = list(received_frequency_hz)
    power = list(received_power_fraction)
    if not (len(x) == len(frequency) == len(power)):
        raise ValueError("all profile series must have equal length")

    fig_frequency, ax_frequency = plt.subplots()
    ax_frequency.plot(x, frequency)
    ax_frequency.set_xscale("log")
    ax_frequency.set_xlabel("Emitter radius (Schwarzschild radii)")
    ax_frequency.set_ylabel("Received frequency (Hz)")
    ax_frequency.set_title("Gravitational redshift profile")
    ax_frequency.grid(True, alpha=0.25)

    fig_power, ax_power = plt.subplots()
    ax_power.plot(x, power)
    ax_power.set_xscale("log")
    ax_power.set_yscale("log")
    ax_power.set_xlabel("Emitter radius (Schwarzschild radii)")
    ax_power.set_ylabel("Received / emitted power")
    ax_power.set_title("Toy exterior-horizon link profile")
    ax_power.grid(True, alpha=0.25)

    return fig_frequency, fig_power
