"""Plot base station estimation using matplotlib.pyplot (assignment section 2.2)."""

from __future__ import annotations

import platform
import subprocess
from pathlib import Path

from data.measurements import MEASUREMENTS, TRANSMISSION_RADIUS_M
from src.positioning import BaseStationEstimate, build_circles, pairwise_intersections


def plot_estimation(
    estimates: list[BaseStationEstimate],
    output_path: str | Path = "output/bs_estimation.png",
    show: bool = True,
) -> Path:
    """
    Plot smartphone positions, RSSI circles, intersections, and base stations.

    Uses matplotlib.pyplot as required by the assignment:
        "If you want to plot you should use matplotlib.pyplot."
    """
    import matplotlib

    if not show:
        matplotlib.use("Agg")

    import matplotlib.pyplot as plt

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    circles = build_circles(MEASUREMENTS)
    colors = {12801: "#e41a1c", 12802: "#377eb8", 12803: "#4daf4a", 12804: "#984ea3"}

    plt.figure(figsize=(12, 10))
    ax = plt.gca()

    sp_seen: set[tuple[float, float]] = set()
    sp_xs, sp_ys = [], []
    for m in MEASUREMENTS:
        key = (m.sp_x, m.sp_y)
        if key not in sp_seen:
            sp_xs.append(m.sp_x)
            sp_ys.append(m.sp_y)
            plt.annotate(
                f"SP{m.smartphone_id}",
                (m.sp_x, m.sp_y),
                textcoords="offset points",
                xytext=(4, 4),
                fontsize=8,
            )
            sp_seen.add(key)
    plt.scatter(sp_xs, sp_ys, c="black", marker="^", s=60, zorder=5, label="Smartphone")

    for c in circles:
        color = colors.get(c.ci, "gray")
        ax.add_patch(
            plt.Circle(
                (c.center_x, c.center_y),
                c.radius,
                fill=False,
                linestyle="--",
                linewidth=0.8,
                color=color,
                alpha=0.5,
            )
        )

    for est in estimates:
        ci_circles = [c for c in circles if c.ci == est.ci]
        intersections = pairwise_intersections(ci_circles)
        if intersections:
            ix, iy = zip(*intersections)
            plt.scatter(
                ix, iy,
                c=colors.get(est.ci, "gray"),
                marker="x",
                s=40,
                zorder=4,
                alpha=0.7,
            )

    for est in estimates:
        color = colors.get(est.ci, "gray")
        plt.scatter(est.x, est.y, c=color, marker="*", s=300, zorder=6, edgecolors="black")
        plt.annotate(
            f"BS {est.ci}\n({est.x:.1f}, {est.y:.1f})",
            (est.x, est.y),
            textcoords="offset points",
            xytext=(8, 8),
            fontsize=9,
            fontweight="bold",
        )
        ax.add_patch(
            plt.Circle(
                (est.x, est.y),
                TRANSMISSION_RADIUS_M,
                fill=False,
                linestyle="-",
                linewidth=1.2,
                color=color,
                alpha=0.35,
            )
        )

    plt.xlabel("x-coordinate (m)")
    plt.ylabel("y-coordinate (m)")
    plt.title("Swarm Mapping: Base Station Position Estimation from RSSI")
    plt.axis("equal")
    plt.grid(True, alpha=0.3)
    plt.legend(
        handles=[
            plt.Line2D([0], [0], marker="^", color="black", linestyle="", label="Smartphone"),
            plt.Line2D([0], [0], marker="*", color="gray", linestyle="", label="Estimated BS"),
            plt.Line2D([0], [0], linestyle="--", color="gray", label="RSSI distance circle"),
            plt.Line2D([0], [0], marker="x", color="gray", linestyle="", label="Circle intersection"),
            plt.Line2D(
                [0], [0], linestyle="-", color="gray", alpha=0.5,
                label=f"BS radius r={TRANSMISSION_RADIUS_M} m",
            ),
        ],
        loc="upper right",
    )
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    print(f"Plot saved to: {output_path.resolve()}")

    if show:
        print("Opening plot window... (close the window to continue)")
        plt.show()
    else:
        plt.close()

    return output_path


def open_plot(path: str | Path) -> None:
    """Open the saved plot image in the default viewer (macOS/Linux/Windows)."""
    path = Path(path).resolve()
    system = platform.system()
    try:
        if system == "Darwin":
            subprocess.run(["open", str(path)], check=True)
        elif system == "Windows":
            subprocess.run(["start", "", str(path)], shell=True, check=True)
        else:
            subprocess.run(["xdg-open", str(path)], check=True)
        print(f"Opened plot in default viewer: {path}")
    except Exception as exc:
        print(f"Could not auto-open plot: {exc}")
        print(f"Open manually: {path}")
