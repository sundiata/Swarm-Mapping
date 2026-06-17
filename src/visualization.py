"""Plots focused on visible circles and intersection points (matplotlib.pyplot)."""

from __future__ import annotations

import platform
import subprocess
from pathlib import Path

from data.measurements import MEASUREMENTS
from src.positioning import BaseStationEstimate, build_circles, pairwise_intersections, residual_error


CI_STYLE = {
    12801: {"color": "#D32F2F", "fill": "#FFEBEE", "name": "12801"},
    12802: {"color": "#1565C0", "fill": "#E3F2FD", "name": "12802"},
    12803: {"color": "#2E7D32", "fill": "#E8F5E9", "name": "12803"},
    12804: {"color": "#6A1B9A", "fill": "#F3E5F5", "name": "12804"},
}

INTERSECTION_COLOR = "#F57C00"  # orange — stands out against all tower colors


def _circle_bounds(ci_circles, est) -> tuple[float, float, float, float]:
    xs, ys = [est.x], [est.y]
    for c in ci_circles:
        xs += [c.center_x - c.radius, c.center_x + c.radius]
        ys += [c.center_y - c.radius, c.center_y + c.radius]
    pad = 80
    return min(xs) - pad, max(xs) + pad, min(ys) - pad, max(ys) + pad


def _best_intersection(ci_circles) -> tuple[float, float] | None:
    points = pairwise_intersections(ci_circles)
    if not points:
        return None
    return min(points, key=lambda p: residual_error(p, ci_circles))


def _draw_ci_panel(ax, ci: int, estimates: list[BaseStationEstimate], circles) -> None:
    import matplotlib.pyplot as plt

    style = CI_STYLE[ci]
    color = style["color"]
    fill = style["fill"]
    est = next(e for e in estimates if e.ci == ci)
    measurements = [m for m in MEASUREMENTS if m.ci == ci]
    ci_circles = [c for c in circles if c.ci == ci]
    intersections = pairwise_intersections(ci_circles)

    # --- 1. RSSI circles: filled + border so overlap is visible ---
    for i, c in enumerate(ci_circles):
        m = c.measurement
        # Light fill — darker where circles overlap
        ax.add_patch(
            plt.Circle(
                (c.center_x, c.center_y), c.radius,
                facecolor=fill, edgecolor="none", alpha=0.55, zorder=1,
            )
        )
        # Clear dashed border per circle
        ax.add_patch(
            plt.Circle(
                (c.center_x, c.center_y), c.radius,
                fill=False, edgecolor=color,
                linestyle=(0, (6, 4)), linewidth=1.8, alpha=0.9, zorder=2,
            )
        )
        # Phone at circle centre
        ax.scatter(c.center_x, c.center_y, c=color, marker="^", s=90, zorder=6,
                   edgecolors="white", linewidths=1)
        ax.annotate(
            f"SP{m.smartphone_id}\nRSSI={m.rssi:g}\nr={c.radius:.0f}m",
            (c.center_x, c.center_y),
            textcoords="offset points", xytext=(12, 6),
            fontsize=7, color=color, fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.25", facecolor="white", edgecolor=color, alpha=0.85),
        )

    # --- 2. Intersection points (where circle pairs cross) ---
    if intersections:
        ix, iy = zip(*intersections)
        ax.scatter(ix, iy, c=INTERSECTION_COLOR, marker="x", s=90, linewidths=2.2,
                   zorder=7, label="_intersections")

    # --- 3. Best intersection = chosen tower position ---
    best = _best_intersection(ci_circles)
    if best:
        ax.scatter(best[0], best[1], facecolors="none", edgecolors=INTERSECTION_COLOR,
                   marker="o", s=220, linewidths=2.5, zorder=8)

    # --- 4. Final estimated tower ---
    ax.scatter(est.x, est.y, c=color, marker="*", s=400, zorder=9,
               edgecolors="#212121", linewidths=0.8)
    ax.annotate(
        f"TOWER\n({est.x:.0f}, {est.y:.0f})",
        (est.x, est.y),
        textcoords="offset points", xytext=(0, 22),
        ha="center", fontsize=8, fontweight="bold", color=color,
        bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor=color, alpha=0.95),
    )

    n_inter = len(intersections)
    ax.set_title(
        f"CI {style['name']}  →  ({est.x:.0f}, {est.y:.0f})  |  {len(ci_circles)} circles, {n_inter} intersections",
        fontsize=9.5, fontweight="bold", color=color, pad=10,
    )
    ax.set_xlabel("x (m)", fontsize=8)
    ax.set_ylabel("y (m)", fontsize=8)
    ax.set_facecolor("#FFFFFF")
    ax.grid(True, color="#ECECEC", linewidth=0.7)
    ax.set_aspect("equal")

    xmin, xmax, ymin, ymax = _circle_bounds(ci_circles, est)
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)


def plot_estimation(
    estimates: list[BaseStationEstimate],
    output_path: str | Path = "output/bs_estimation.png",
    show: bool = True,
) -> Path:
    import matplotlib
    if not show:
        matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    circles = build_circles(MEASUREMENTS)
    cis = sorted(e.ci for e in estimates)

    fig, axes = plt.subplots(2, 2, figsize=(14, 12))
    fig.patch.set_facecolor("white")
    fig.suptitle(
        "Base Station Estimation — circles show RSSI distance, ✕ marks show intersections",
        fontsize=12, fontweight="bold", y=0.99,
    )

    for ax, ci in zip(axes.flat, cis):
        _draw_ci_panel(ax, ci, estimates, circles)

    legend_handles = [
        Line2D([0], [0], marker="^", color="gray", linestyle="", markersize=8, label="Smartphone (circle centre)"),
        Line2D([0], [0], color="gray", linestyle=(0, (6, 4)), linewidth=2, label="RSSI distance circle"),
        Line2D([0], [0], marker="x", color=INTERSECTION_COLOR, linestyle="", markersize=9, markeredgewidth=2, label="Circle intersection (✕)"),
        Line2D([0], [0], marker="o", color=INTERSECTION_COLOR, linestyle="", markersize=9,
               markerfacecolor="none", markeredgewidth=2, label="Best intersection (chosen point)"),
        Line2D([0], [0], marker="*", color="gray", linestyle="", markersize=14, label="Estimated tower (★)"),
    ]
    fig.legend(handles=legend_handles, loc="lower center", ncol=3, fontsize=8.5,
               frameon=True, fancybox=True, edgecolor="#CCCCCC", bbox_to_anchor=(0.5, 0.0))

    plt.tight_layout(rect=[0, 0.06, 1, 0.96])
    plt.savefig(output_path, dpi=170, bbox_inches="tight", facecolor="white")
    print(f"Plot saved to: {output_path.resolve()}")

    if show:
        print("Zoom: toolbar magnifier  |  Pan: cross-arrows  |  Reset: home icon")
        plt.show()
    else:
        plt.close()
    return output_path


def _hex_to_rgba(hex_color: str, alpha: float) -> str:
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"


def plot_interactive_html(
    estimates: list[BaseStationEstimate],
    output_path: str | Path = "output/bs_estimation_interactive.html",
    open_browser: bool = True,
) -> Path:
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    circles = build_circles(MEASUREMENTS)
    cis = sorted(e.ci for e in estimates)
    est_map = {e.ci: e for e in estimates}

    titles = [
        f"CI {CI_STYLE[ci]['name']} → ({est_map[ci].x:.0f}, {est_map[ci].y:.0f})"
        for ci in cis
    ]
    fig = make_subplots(rows=2, cols=2, subplot_titles=titles, horizontal_spacing=0.07, vertical_spacing=0.13)

    for ci, (row, col) in zip(cis, [(1, 1), (1, 2), (2, 1), (2, 2)]):
        style = CI_STYLE[ci]
        color = style["color"]
        est = est_map[ci]
        ci_circles = [c for c in circles if c.ci == ci]
        intersections = pairwise_intersections(ci_circles)
        best = _best_intersection(ci_circles)

        # Filled + dashed circles
        for c in ci_circles:
            m = c.measurement
            fig.add_shape(
                dict(type="circle", xref="x", yref="y",
                     x0=c.center_x - c.radius, y0=c.center_y - c.radius,
                     x1=c.center_x + c.radius, y1=c.center_y + c.radius,
                     fillcolor=_hex_to_rgba(color, 0.12),
                     line=dict(color=color, width=2, dash="dash")),
                row=row, col=col,
            )
            fig.add_trace(
                go.Scatter(
                    x=[c.center_x], y=[c.center_y],
                    mode="markers+text",
                    marker=dict(symbol="triangle-up", size=11, color=color, line=dict(color="white", width=1)),
                    text=[f"SP{m.smartphone_id}"],
                    textposition="top center",
                    textfont=dict(size=9, color=color),
                    showlegend=False,
                    hovertemplate=(
                        f"<b>SP{m.smartphone_id}</b><br>"
                        f"RSSI={m.rssi:g}<br>radius={c.radius:.0f} m<br>"
                        f"x=%{{x:.0f}}, y=%{{y:.0f}}<extra></extra>"
                    ),
                ),
                row=row, col=col,
            )

        # All intersection points
        if intersections:
            ix, iy = zip(*intersections)
            fig.add_trace(
                go.Scatter(
                    x=list(ix), y=list(iy),
                    mode="markers",
                    marker=dict(symbol="x", size=11, color=INTERSECTION_COLOR, line=dict(width=3)),
                    name="Intersections",
                    showlegend=False,
                    hovertemplate="Intersection<br>x=%{x:.1f}, y=%{y:.1f}<extra></extra>",
                ),
                row=row, col=col,
            )

        # Best intersection ring
        if best:
            fig.add_trace(
                go.Scatter(
                    x=[best[0]], y=[best[1]],
                    mode="markers",
                    marker=dict(symbol="circle-open", size=18, color=INTERSECTION_COLOR, line=dict(width=3)),
                    showlegend=False,
                    hovertemplate=f"Best intersection<br>x={best[0]:.1f}, y={best[1]:.1f}<extra></extra>",
                ),
                row=row, col=col,
            )

        # Tower
        fig.add_trace(
            go.Scatter(
                x=[est.x], y=[est.y],
                mode="markers+text",
                marker=dict(symbol="star", size=16, color=color, line=dict(color="#212121", width=1)),
                text=["TOWER"],
                textposition="top center",
                textfont=dict(size=10, color=color),
                showlegend=False,
                hovertemplate=f"<b>Tower {ci}</b><br>x=%{{x:.0f}}, y=%{{y:.0f}}<extra></extra>",
            ),
            row=row, col=col,
        )

        xmin, xmax, ymin, ymax = _circle_bounds(ci_circles, est)
        fig.update_xaxes(range=[xmin, xmax], title_text="x (m)", gridcolor="#EEEEEE", row=row, col=col)
        fig.update_yaxes(range=[ymin, ymax], scaleanchor="x", scaleratio=1, title_text="y (m)",
                         gridcolor="#EEEEEE", row=row, col=col)

    fig.update_layout(
        title=dict(
            text="<b>Base Station Estimation</b><br>"
                 "<sup>Dashed circles = RSSI distance  |  ✕ = intersections  |  ★ = tower  |  Scroll to zoom</sup>",
            x=0.5,
        ),
        height=860, width=1200,
        template="plotly_white",
        paper_bgcolor="white",
        plot_bgcolor="white",
        dragmode="zoom",
    )
    fig.update_annotations(font_size=11)

    fig.write_html(str(output_path), config={"scrollZoom": True, "displayModeBar": True})
    print(f"Interactive plot: {output_path.resolve()}")

    if open_browser:
        open_plot(output_path)
    return output_path


def open_plot(path: str | Path) -> None:
    path = Path(path).resolve()
    try:
        if platform.system() == "Darwin":
            subprocess.run(["open", str(path)], check=True)
        elif platform.system() == "Windows":
            subprocess.run(["start", "", str(path)], shell=True, check=True)
        else:
            subprocess.run(["xdg-open", str(path)], check=True)
    except Exception as exc:
        print(f"Could not open automatically: {exc}\n  Open manually: {path}")
