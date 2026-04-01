"""Generate uml_final.png — PawPal+ class diagram using matplotlib."""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch

# ── Layout constants ───────────────────────────────────────────────────────────
FIG_W, FIG_H = 20, 14
BOX_W = 3.6          # class box width
HEADER_H = 0.45      # title band height
ROW_H = 0.28         # per-row height
PAD = 0.12           # internal left pad

BG       = "#1e1e2e"
HDR_CLR  = "#313244"
TXT_CLR  = "#cdd6f4"
ATT_CLR  = "#89b4fa"   # blue  – attributes
MTH_CLR  = "#a6e3a1"   # green – methods
DIV_CLR  = "#45475a"   # separator line color
ARROW_CLR = "#f38ba8"  # arrows


def draw_class(ax, cx, cy, name, attributes, methods):
    """Draw a UML class box centred at (cx, cy). Returns the box height."""
    n_rows = len(attributes) + len(methods) + (1 if (attributes and methods) else 0)
    box_h = HEADER_H + n_rows * ROW_H + PAD

    x0 = cx - BOX_W / 2
    y0 = cy - box_h / 2

    # outer rect
    rect = mpatches.FancyBboxPatch(
        (x0, y0), BOX_W, box_h,
        boxstyle="round,pad=0.04",
        linewidth=1.5, edgecolor=ATT_CLR, facecolor=HDR_CLR,
    )
    ax.add_patch(rect)

    # header band
    hdr = mpatches.FancyBboxPatch(
        (x0, y0 + box_h - HEADER_H), BOX_W, HEADER_H,
        boxstyle="round,pad=0.04",
        linewidth=0, facecolor="#45475a",
    )
    ax.add_patch(hdr)

    ax.text(cx, y0 + box_h - HEADER_H / 2, f"«class»\n{name}",
            ha="center", va="center", fontsize=8.5, fontweight="bold",
            color=TXT_CLR, linespacing=1.2)

    y_cursor = y0 + box_h - HEADER_H - PAD / 2

    for attr in attributes:
        y_cursor -= ROW_H
        ax.text(x0 + PAD, y_cursor + ROW_H * 0.35, attr,
                ha="left", va="center", fontsize=7.2, color=ATT_CLR,
                fontfamily="monospace")

    if attributes and methods:
        y_cursor -= ROW_H * 0.5
        ax.plot([x0 + 0.1, x0 + BOX_W - 0.1], [y_cursor + ROW_H * 0.3] * 2,
                color=DIV_CLR, linewidth=0.8)
        y_cursor -= ROW_H * 0.5

    for mth in methods:
        y_cursor -= ROW_H
        ax.text(x0 + PAD, y_cursor + ROW_H * 0.35, mth,
                ha="left", va="center", fontsize=7.2, color=MTH_CLR,
                fontfamily="monospace")

    return box_h


def arrow(ax, x1, y1, x2, y2, label="", style="->", color=ARROW_CLR):
    arrowprops = dict(
        arrowstyle=style,
        color=color,
        lw=1.4,
        connectionstyle="arc3,rad=0.0",
    )
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1), arrowprops=arrowprops)
    if label:
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        ax.text(mx + 0.05, my, label, fontsize=6.8, color="#fab387",
                va="center", style="italic")


# ── Figure setup ───────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(FIG_W, FIG_H))
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)
ax.set_xlim(0, FIG_W)
ax.set_ylim(0, FIG_H)
ax.axis("off")

ax.text(FIG_W / 2, FIG_H - 0.4, "PawPal+ — Class Diagram (Final)",
        ha="center", va="top", fontsize=14, fontweight="bold", color=TXT_CLR)

# ── Class definitions ──────────────────────────────────────────────────────────
#  Positions: (cx, cy)
classes = {
    "Owner": (3.0, 10.5,
        ["+name: str", "+available_minutes: int", "+pet_time_budgets: dict"],
        ["+budget_for(pet_name: str): int"]),

    "Pet": (3.0, 6.5,
        ["+name: str", "+species: str", "+tasks: List[Task]"],
        ["+add_task(task: Task): void",
         "+get_default_tasks(): List[Task]"]),

    "Task": (9.0, 10.5,
        ["+title: str", "+duration_minutes: int", "+priority: str",
         "+status: str", "+required: bool", "+earliest_start: int",
         "+depends_on: Optional[str]", "+frequency: str",
         "+due_date: Optional[date]"],
        ["+mark_complete(): Optional[Task]",
         "+priority_value(): int",
         "+value_density(): float"]),

    "Scheduler": (3.0, 2.8,
        ["+owner: Owner", "+pet: Pet",
         "+tasks: List[Task]", "+buffer_minutes: int"],
        ["+generate_plan(): DailyPlan",
         "+filter_tasks(...): tuple",
         "+detect_conflicts(plan): List[str]"]),

    "DailyPlan": (15.0, 7.0,
        ["+owner_name: str", "+pet_name: str",
         "+scheduled_items: List[dict]",
         "+dropped_tasks: List[Task]",
         "+total_duration: int"],
        ["+add_item(task, start_time): void",
         "+sort_by_time(): List",
         "+filter_tasks(...): List",
         "+detect_conflicts(): List",
         "+explain(): str",
         "+display(): List"]),
}

box_heights = {}
for name, (cx, cy, attrs, meths) in classes.items():
    h = draw_class(ax, cx, cy, name, attrs, meths)
    box_heights[name] = (cx, cy, h)

# ── Relationships ──────────────────────────────────────────────────────────────
def top(name):
    cx, cy, h = box_heights[name]; return cx, cy + h / 2

def bottom(name):
    cx, cy, h = box_heights[name]; return cx, cy - h / 2

def left(name):
    cx, cy, h = box_heights[name]; return cx - BOX_W / 2, cy

def right(name):
    cx, cy, h = box_heights[name]; return cx + BOX_W / 2, cy

# Owner → Pet  (owns)
arrow(ax, *bottom("Owner"), *top("Pet"), label="  owns")

# Pet → Task  (has many)
arrow(ax, *right("Pet"), 9.0 - BOX_W / 2, 9.0, label="  has *")

# Scheduler → Owner
arrow(ax, *top("Scheduler"), *bottom("Owner"), label="  uses")

# Scheduler → Pet
sx, sy, sh = box_heights["Scheduler"]
arrow(ax, sx + BOX_W / 2, sy + 0.3, *left("Pet"), label="uses  ")

# Scheduler → DailyPlan  (produces)
arrow(ax, sx + BOX_W / 2, sy - 0.1,
      15.0 - BOX_W / 2, box_heights["DailyPlan"][1] - 1.0,
      label="produces  ")

# DailyPlan → Task  (references)
arrow(ax, 15.0 - BOX_W / 2, box_heights["DailyPlan"][1] + 0.8,
      9.0 + BOX_W / 2, 10.0, label="references  ")

# Task self-ref  (spawns via mark_complete)
tx, ty, th = box_heights["Task"]
ax.annotate("", xy=(tx + BOX_W / 2, ty + 0.6),
            xytext=(tx + BOX_W / 2, ty - 0.6),
            arrowprops=dict(arrowstyle="->", color=ARROW_CLR, lw=1.2,
                            connectionstyle="arc3,rad=-0.7"))
ax.text(tx + BOX_W / 2 + 1.0, ty, "spawns\n(recurrence)",
        fontsize=6.5, color="#fab387", va="center", style="italic")

# ── Legend ─────────────────────────────────────────────────────────────────────
lx, ly = 0.3, 1.1
ax.text(lx, ly, "Attribute", fontsize=7.5, color=ATT_CLR, fontfamily="monospace")
ax.text(lx + 2.0, ly, "Method", fontsize=7.5, color=MTH_CLR, fontfamily="monospace")
ax.text(lx + 4.0, ly, "→ relationship", fontsize=7.5, color=ARROW_CLR)

plt.tight_layout(pad=0.3)
out = "uml_final.png"
plt.savefig(out, dpi=150, bbox_inches="tight", facecolor=BG)
print(f"Saved {out}")
