import csv
import os
from pathlib import Path

out = Path(__file__).resolve().parent
os.environ['MPLCONFIGDIR'] = str(out / '.matplotlib')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

source = out.parent / 'ilk_iki_20261025T152612Z_298' / 'ilk_karsilastirma.csv'
with source.open(newline='', encoding='utf-8') as handle:
    rows = {row['condition']: row for row in csv.DictReader(handle)}
labels = ['PRS kapalı', 'PRS açık\n(her 4 slotta)']
colors = ['#2367a7', '#d97723']
rates = [float(rows[k]['dl_mbps']) for k in ['base', 'p4']]
blocks = [float(rows[k]['dl_ok_per_second']) for k in ['base', 'p4']]
plt.rcParams.update({'font.family':'DejaVu Sans', 'font.size':12, 'axes.titlesize':15,
                     'axes.labelsize':12, 'axes.spines.top':False, 'axes.spines.right':False})
fig, axes = plt.subplots(1, 2, figsize=(11.5, 6.2))
fig.patch.set_facecolor('white')
fig.suptitle('OCUDU: PRS kapalı / açık karşılaştırması', fontsize=20, fontweight='bold', y=0.97)
fig.text(0.5, 0.895, 'OCUDU 26.10.0  |  1 sanal kullanıcı  |  20 MHz, n3', ha='center', color='#475569')
for ax, values, title, unit, ymax in [
    (axes[0], rates, 'DL veri hızı', 'Mbps', 68),
    (axes[1], blocks, 'Başarılı blok sayısı', 'blok/s', 1140),
]:
    bars = ax.bar(labels, values, color=colors, width=0.55, zorder=3)
    ax.set_title(title, pad=16)
    ax.set_ylabel(unit)
    ax.set_ylim(0, ymax)
    ax.set_axisbelow(True)
    ax.grid(axis='y', color='#e2e8f0', linewidth=0.8)
    ax.spines['left'].set_color('#cbd5e1')
    ax.spines['bottom'].set_color('#cbd5e1')
    ax.tick_params(axis='x', length=0, pad=10)
    for bar, value in zip(bars, values):
        label = (f'{value:.1f}'.replace('.', ',') if unit == 'Mbps' else f'{value:.0f}')
        ax.text(bar.get_x()+bar.get_width()/2, value+ymax*0.025, label,
                ha='center', va='bottom', fontsize=17, fontweight='bold', color='#172554')
fig.text(0.5, 0.095, 'Radyosuz test modu: ru_dummy / no_core. PRS açık: 12 sembol, 104 PRB.',
         ha='center', fontsize=10, color='#475569')
fig.text(0.5, 0.055, '25.10.2026 • Her koşulda tek koşu; son 15 sayaç örneğinin ortalaması.',
         ha='center', fontsize=10, color='#475569')
fig.subplots_adjust(left=0.09, right=0.97, bottom=0.24, top=0.78, wspace=0.30)
fig.savefig(out / 'ocudu_karsilastirma.png', dpi=160, facecolor='white')
plt.close(fig)
print(out / 'ocudu_karsilastirma.png')
