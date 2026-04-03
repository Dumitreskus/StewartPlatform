"""
Stewart Platform с линейными приводами — интерактивная визуализация.
Запуск: python app.py
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.widgets import Slider, Button
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
from stewart_controller import Stewart_Platform_Linear

# ── Параметры платформы ────────────────────────────────────────────────────────
R_B     = 132 / 2   # радиус основания (мм)
R_P     = 100 / 2   # радиус платформы (мм)
GAMMA_B = 0.2269    # полуугол между точками крепления на основании (рад, ~13°)
GAMMA_P = 0.82      # полуугол между точками крепления на платформе (рад, ~47°)
HOME_Z  = 2 * R_B   # высота платформы в нейтральном положении (мм)
REF_ROT = 5 * np.pi / 6

platform = Stewart_Platform_Linear(R_B, R_P, GAMMA_B, GAMMA_P, HOME_Z, REF_ROT)

# Начальные длины ног (нейтраль) — для отображения отклонения
_home_lengths = platform.calculate(np.zeros(3), np.zeros(3)).copy()
L_MIN = _home_lengths.min() * 0.75
L_MAX = _home_lengths.max() * 1.25

# Пределы ползунков
TRANS_LIM = 20      # мм
ROT_LIM   = 0.35    # рад (~20°)

# ── Цветовая схема ─────────────────────────────────────────────────────────────
BG_DARK   = '#1e1e2e'
BG_PANEL  = '#181825'
TEXT      = '#cdd6f4'
ACCENT    = '#89b4fa'
GREEN     = '#a6e3a1'
RED       = '#f38ba8'
ORANGE    = '#fab387'
YELLOW    = '#f9e2af'
PURPLE    = '#cba6f7'
GREY      = '#45475a'
SLIDER_BG = '#313244'

LEG_COLORS = [RED, ORANGE, YELLOW, GREEN, ACCENT, PURPLE]

# ── Компоновка окна ────────────────────────────────────────────────────────────
fig = plt.figure(figsize=(15, 9), facecolor=BG_DARK)
fig.canvas.manager.set_window_title('Stewart Platform — Линейные приводы')

gs = gridspec.GridSpec(
    2, 2,
    left=0.04, right=0.98,
    top=0.96, bottom=0.36,
    wspace=0.28, hspace=0.38,
)

ax3d     = fig.add_subplot(gs[:, 0], projection='3d')
ax_top   = fig.add_subplot(gs[0, 1])
ax_legs  = fig.add_subplot(gs[1, 1])

for ax in (ax_top, ax_legs):
    ax.set_facecolor(BG_PANEL)
ax3d.set_facecolor(BG_PANEL)


def _style(ax, title):
    ax.set_title(title, color=TEXT, fontsize=10, pad=6)
    ax.tick_params(colors=TEXT, labelsize=8)
    for sp in ax.spines.values():
        sp.set_edgecolor(GREY)


# ── Ползунки ──────────────────────────────────────────────────────────────────
slider_defs = [
    ('Tx (мм)',         -TRANS_LIM, TRANS_LIM, 0.0),
    ('Ty (мм)',         -TRANS_LIM, TRANS_LIM, 0.0),
    ('Tz (мм)',         -TRANS_LIM, TRANS_LIM, 0.0),
    ('Крен (рад)',      -ROT_LIM,   ROT_LIM,   0.0),
    ('Тангаж (рад)',    -ROT_LIM,   ROT_LIM,   0.0),
    ('Рыскание (рад)',  -ROT_LIM,   ROT_LIM,   0.0),
]

sliders = []
SL_H   = 0.025
SL_GAP = 0.038
SL_Y0  = 0.28

for i, (label, vmin, vmax, vinit) in enumerate(slider_defs):
    col  = i // 3
    row  = i % 3
    left = 0.07 + col * 0.50
    bot  = SL_Y0 - row * SL_GAP
    ax_s = fig.add_axes([left, bot, 0.39, SL_H], facecolor=SLIDER_BG)
    sl   = Slider(ax_s, label, vmin, vmax, valinit=vinit, color=ACCENT)
    sl.label.set_color(TEXT)
    sl.valtext.set_color(TEXT)
    sliders.append(sl)

sl_tx, sl_ty, sl_tz, sl_rx, sl_ry, sl_rz = sliders

ax_btn = fig.add_axes([0.45, 0.03, 0.10, 0.04])
btn_reset = Button(ax_btn, 'Сброс', color=SLIDER_BG, hovercolor=GREY)
btn_reset.label.set_color(TEXT)

# ── Обновление ────────────────────────────────────────────────────────────────
def update(_=None):
    trans    = np.array([sl_tx.val, sl_ty.val, sl_tz.val])
    rotation = np.array([sl_rx.val, sl_ry.val, sl_rz.val])

    try:
        lengths = platform.calculate(trans, rotation)
    except Exception:
        return

    B = platform.B
    L = platform.L

    # ── 3D ────────────────────────────────────────────────────────────────────
    ax3d.cla()
    ax3d.set_facecolor(BG_PANEL)

    lim = R_B * 1.9
    ax3d.set_xlim3d(-lim, lim)
    ax3d.set_ylim3d(-lim, lim)
    ax3d.set_zlim3d(0, lim * 2.4)
    ax3d.set_xlabel('X', color=TEXT, fontsize=8)
    ax3d.set_ylabel('Y', color=TEXT, fontsize=8)
    ax3d.set_zlabel('Z', color=TEXT, fontsize=8)
    ax3d.tick_params(colors=TEXT, labelsize=7)
    ax3d.set_title('3D-вид  (линейные приводы)', color=TEXT, fontsize=10, pad=8)
    for pane in (ax3d.xaxis.pane, ax3d.yaxis.pane, ax3d.zaxis.pane):
        pane.fill = False
        pane.set_edgecolor(GREY)
    ax3d.grid(True, color=GREY, linewidth=0.4)

    # Основание
    ax3d.add_collection3d(Poly3DCollection(
        [list(np.transpose(B))],
        facecolors=GREEN, alpha=0.20, edgecolors=GREEN, linewidths=1.2))

    # Платформа
    ax3d.add_collection3d(Poly3DCollection(
        [list(np.transpose(L))],
        facecolors=ACCENT, alpha=0.30, edgecolors=ACCENT, linewidths=1.2))

    # Линейные актуаторы — сплошные цветные линии от B до L
    for i in range(6):
        color = LEG_COLORS[i]
        ax3d.plot(
            [B[0, i], L[0, i]],
            [B[1, i], L[1, i]],
            [B[2, i], L[2, i]],
            color=color, linewidth=2.5)

        # Точки шарниров
        ax3d.scatter(*B[:, i], color=GREEN,  s=18, zorder=5)
        ax3d.scatter(*L[:, i], color=ACCENT, s=18, zorder=5)

    # Длина ног как текст рядом с серединой привода
    for i in range(6):
        mid = (B[:, i] + L[:, i]) / 2
        delta = lengths[i] - _home_lengths[i]
        sign  = '+' if delta >= 0 else ''
        ax3d.text(mid[0], mid[1], mid[2],
                  f' {lengths[i]:.1f}\n({sign}{delta:.1f})',
                  color=LEG_COLORS[i], fontsize=6.5, ha='left')

    # ── Вид сверху ────────────────────────────────────────────────────────────
    ax_top.cla()
    ax_top.set_facecolor(BG_PANEL)
    _style(ax_top, 'Вид сверху')
    ax_top.set_aspect('equal')
    ax_top.set_xlim(-lim, lim)
    ax_top.set_ylim(-lim, lim)
    ax_top.grid(True, color=GREY, linewidth=0.4)

    bx = list(B[0]) + [B[0, 0]]
    by = list(B[1]) + [B[1, 0]]
    ax_top.fill(B[0], B[1], color=GREEN,  alpha=0.12)
    ax_top.plot(bx, by, color=GREEN,  linewidth=1.5, label='Основание')
    ax_top.scatter(B[0], B[1], color=GREEN, s=22, zorder=5)

    lx2 = list(L[0]) + [L[0, 0]]
    ly2 = list(L[1]) + [L[1, 0]]
    ax_top.fill(L[0], L[1], color=ACCENT, alpha=0.15)
    ax_top.plot(lx2, ly2, color=ACCENT, linewidth=1.5, label='Платформа')
    ax_top.scatter(L[0], L[1], color=ACCENT, s=22, zorder=5)

    for i in range(6):
        ax_top.plot([B[0, i], L[0, i]], [B[1, i], L[1, i]],
                    color=LEG_COLORS[i], linewidth=1.0, linestyle='--', alpha=0.7)

    ax_top.legend(fontsize=7, facecolor=SLIDER_BG, labelcolor=TEXT,
                  edgecolor=GREY, loc='upper right')

    # ── Длины приводов ────────────────────────────────────────────────────────
    ax_legs.cla()
    ax_legs.set_facecolor(BG_PANEL)
    _style(ax_legs, 'Длины линейных приводов (мм)')
    ax_legs.set_xlim(-0.5, 5.5)
    ax_legs.grid(True, color=GREY, linewidth=0.4, axis='y')

    bars = ax_legs.bar(range(6), lengths, color=LEG_COLORS, alpha=0.85, width=0.6)

    # Линия нейтрального положения
    ax_legs.axhline(_home_lengths[0], color=TEXT, linewidth=0.9,
                    linestyle='--', alpha=0.5, label=f'Нейтраль {_home_lengths[0]:.1f} мм')

    y_min = min(L_MIN, lengths.min() * 0.97)
    y_max = max(L_MAX, lengths.max() * 1.03)
    ax_legs.set_ylim(y_min, y_max)
    ax_legs.set_xticks(range(6))
    ax_legs.set_xticklabels([f'A{i+1}' for i in range(6)], color=TEXT)
    ax_legs.legend(fontsize=7, facecolor=SLIDER_BG, labelcolor=TEXT,
                   edgecolor=GREY, loc='upper right')

    for i, (bar, length) in enumerate(zip(bars, lengths)):
        delta = length - _home_lengths[i]
        sign  = '+' if delta >= 0 else ''
        ax_legs.text(
            bar.get_x() + bar.get_width() / 2,
            length + (y_max - y_min) * 0.01,
            f'{length:.1f}\n({sign}{delta:.1f})',
            ha='center', va='bottom', color=TEXT, fontsize=7.5)

    fig.canvas.draw_idle()


def reset(_):
    for sl in sliders:
        sl.reset()


for sl in sliders:
    sl.on_changed(update)
btn_reset.on_clicked(reset)

# ── Пояснение под графиком ────────────────────────────────────────────────────
fig.text(0.50, 0.01,
         'Линейный привод: длина меняется непрерывно  •  '
         'Нейтраль: %.1f мм  •  '
         'Ползунки управляют положением верхней платформы' % _home_lengths[0],
         ha='center', color='#6c7086', fontsize=8)

update()
plt.show()
