"""
generate_report.py
Génère un rapport HTML interactif style Power BI depuis le CSV des prédictions.
Usage: python generate_report.py
Output: reports/fraud_report.html
"""

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import os
from datetime import datetime

# ─────────────────────────────────────────────
# Chargement des données
# ─────────────────────────────────────────────
CSV_PATH = 'data/predictions_log.csv'
OUTPUT_DIR = 'reports'
OUTPUT_FILE = os.path.join(OUTPUT_DIR, 'fraud_report.html')

os.makedirs(OUTPUT_DIR, exist_ok=True)

if not os.path.exists(CSV_PATH):
    print("❌ Aucune donnée trouvée. Lance l'app et fais des prédictions d'abord.")
    exit()

df = pd.read_csv(CSV_PATH)

if df.empty:
    print("❌ Le fichier CSV est vide.")
    exit()

print(f"✓ {len(df)} transactions chargées")

# ─────────────────────────────────────────────
# Calcul des KPIs
# ─────────────────────────────────────────────
total = len(df)
fraudulent = int(df['prediction'].sum())
legitimate = total - fraudulent
fraud_rate = round((fraudulent / total) * 100, 1)
avg_amount = round(df['amount'].mean(), 2)
avg_fraud_amount = round(df[df['prediction'] == 1]['amount'].mean(), 2) if fraudulent > 0 else 0

# ─────────────────────────────────────────────
# Couleurs
# ─────────────────────────────────────────────
COLOR_FRAUD = '#e74c3c'
COLOR_LEGIT = '#2ecc71'
COLOR_BG = '#0f1117'
COLOR_CARD = '#1a1d2e'
COLOR_TEXT = '#ffffff'
COLOR_SUBTEXT = '#a0aec0'
COLOR_ACCENT = '#667eea'

# ─────────────────────────────────────────────
# Figure 1 — Donut Chart
# ─────────────────────────────────────────────
fig_donut = go.Figure(go.Pie(
    labels=['Légitime', 'Frauduleuse'],
    values=[legitimate, fraudulent],
    hole=0.65,
    marker=dict(colors=[COLOR_LEGIT, COLOR_FRAUD]),
    textinfo='percent',
    textfont=dict(size=14, color='white'),
    hovertemplate='%{label}: %{value} transactions<extra></extra>'
))
fig_donut.update_layout(
    title=dict(text='Répartition Fraude / Légitime', font=dict(color=COLOR_TEXT, size=16), x=0.5),
    paper_bgcolor=COLOR_CARD,
    plot_bgcolor=COLOR_CARD,
    font=dict(color=COLOR_TEXT),
    legend=dict(orientation='h', y=-0.1, font=dict(color=COLOR_SUBTEXT)),
    margin=dict(t=50, b=20, l=20, r=20),
    annotations=[dict(
        text=f'<b>{fraud_rate}%</b><br>fraude',
        x=0.5, y=0.5,
        font=dict(size=18, color=COLOR_FRAUD),
        showarrow=False
    )]
)

# ─────────────────────────────────────────────
# Figure 2 — Barres empilées par type
# ─────────────────────────────────────────────
by_type = df.groupby(['type', 'result']).size().reset_index(name='count')
types = df['type'].unique().tolist()

legit_counts = []
fraud_counts = []
for t in types:
    subset = by_type[by_type['type'] == t]
    l = subset[subset['result'] == 'Not Fraudulent']['count'].sum()
    f = subset[subset['result'] == 'Fraudulent']['count'].sum()
    legit_counts.append(l)
    fraud_counts.append(f)

fig_bar = go.Figure()
fig_bar.add_trace(go.Bar(
    name='Légitime',
    x=types,
    y=legit_counts,
    marker_color=COLOR_LEGIT,
    hovertemplate='%{x}: %{y} légitimes<extra></extra>'
))
fig_bar.add_trace(go.Bar(
    name='Frauduleuse',
    x=types,
    y=fraud_counts,
    marker_color=COLOR_FRAUD,
    hovertemplate='%{x}: %{y} fraudes<extra></extra>'
))
fig_bar.update_layout(
    barmode='stack',
    title=dict(text='Fraudes par Type de Transaction', font=dict(color=COLOR_TEXT, size=16), x=0.5),
    paper_bgcolor=COLOR_CARD,
    plot_bgcolor=COLOR_CARD,
    font=dict(color=COLOR_TEXT),
    xaxis=dict(gridcolor='rgba(255,255,255,0.05)', color=COLOR_SUBTEXT),
    yaxis=dict(gridcolor='rgba(255,255,255,0.05)', color=COLOR_SUBTEXT),
    legend=dict(orientation='h', y=-0.2, font=dict(color=COLOR_SUBTEXT)),
    margin=dict(t=50, b=20, l=20, r=20)
)

# ─────────────────────────────────────────────
# Figure 3 — Scatter montant vs solde (fraude en rouge)
# ─────────────────────────────────────────────
fig_scatter = px.scatter(
    df,
    x='amount',
    y='oldbalanceOrg',
    color='result',
    color_discrete_map={'Fraudulent': COLOR_FRAUD, 'Not Fraudulent': COLOR_LEGIT},
    hover_data=['type', 'amount', 'result'],
    labels={'amount': 'Montant', 'oldbalanceOrg': 'Solde Avant (Orig)'}
)
fig_scatter.update_layout(
    title=dict(text='Montant vs Solde Origine (par résultat)', font=dict(color=COLOR_TEXT, size=16), x=0.5),
    paper_bgcolor=COLOR_CARD,
    plot_bgcolor=COLOR_CARD,
    font=dict(color=COLOR_TEXT),
    xaxis=dict(gridcolor='rgba(255,255,255,0.05)', color=COLOR_SUBTEXT),
    yaxis=dict(gridcolor='rgba(255,255,255,0.05)', color=COLOR_SUBTEXT),
    legend=dict(title='', font=dict(color=COLOR_SUBTEXT)),
    margin=dict(t=50, b=20, l=20, r=20)
)

# ─────────────────────────────────────────────
# Figure 4 — Timeline des prédictions
# ─────────────────────────────────────────────
df['timestamp'] = pd.to_datetime(df['timestamp'])
df_sorted = df.sort_values('timestamp')
df_sorted['cumulative'] = range(1, len(df_sorted) + 1)
df_sorted['cumulative_fraud'] = df_sorted['prediction'].cumsum()

fig_line = go.Figure()
fig_line.add_trace(go.Scatter(
    x=df_sorted['timestamp'],
    y=df_sorted['cumulative'],
    name='Total',
    line=dict(color=COLOR_ACCENT, width=2),
    hovertemplate='%{x}<br>Total: %{y}<extra></extra>'
))
fig_line.add_trace(go.Scatter(
    x=df_sorted['timestamp'],
    y=df_sorted['cumulative_fraud'],
    name='Fraudes',
    line=dict(color=COLOR_FRAUD, width=2, dash='dot'),
    hovertemplate='%{x}<br>Fraudes: %{y}<extra></extra>'
))
fig_line.update_layout(
    title=dict(text='Évolution Cumulative des Transactions', font=dict(color=COLOR_TEXT, size=16), x=0.5),
    paper_bgcolor=COLOR_CARD,
    plot_bgcolor=COLOR_CARD,
    font=dict(color=COLOR_TEXT),
    xaxis=dict(gridcolor='rgba(255,255,255,0.05)', color=COLOR_SUBTEXT),
    yaxis=dict(gridcolor='rgba(255,255,255,0.05)', color=COLOR_SUBTEXT),
    legend=dict(orientation='h', y=-0.2, font=dict(color=COLOR_SUBTEXT)),
    margin=dict(t=50, b=20, l=20, r=20)
)

# ─────────────────────────────────────────────
# Export HTML
# ─────────────────────────────────────────────
donut_html   = fig_donut.to_html(full_html=False, include_plotlyjs=False)
bar_html     = fig_bar.to_html(full_html=False, include_plotlyjs=False)
scatter_html = fig_scatter.to_html(full_html=False, include_plotlyjs=False)
line_html    = fig_line.to_html(full_html=False, include_plotlyjs=False)

generated_at = datetime.now().strftime('%d/%m/%Y à %H:%M')

html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Fraud Detection — Rapport BI</title>
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            background: #0f1117;
            font-family: 'Segoe UI', sans-serif;
            color: #ffffff;
            padding: 30px;
        }}
        .header {{
            margin-bottom: 30px;
            border-bottom: 1px solid rgba(255,255,255,0.1);
            padding-bottom: 20px;
            display: flex;
            justify-content: space-between;
            align-items: flex-end;
        }}
        .header h1 {{ font-size: 1.8rem; color: #667eea; }}
        .header p {{ color: #a0aec0; font-size: 0.85rem; margin-top: 4px; }}
        .header .generated {{ color: #4a5568; font-size: 0.8rem; }}

        /* KPI Cards */
        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(5, 1fr);
            gap: 16px;
            margin-bottom: 24px;
        }}
        .kpi-card {{
            background: #1a1d2e;
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            border: 1px solid rgba(255,255,255,0.07);
        }}
        .kpi-value {{
            font-size: 2rem;
            font-weight: 800;
            line-height: 1;
        }}
        .kpi-label {{
            font-size: 0.75rem;
            color: #a0aec0;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            margin-top: 8px;
        }}

        /* Charts Grid */
        .charts-grid-2 {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 16px;
            margin-bottom: 16px;
        }}
        .charts-grid-full {{
            display: grid;
            grid-template-columns: 1fr;
            gap: 16px;
            margin-bottom: 16px;
        }}
        .chart-card {{
            background: #1a1d2e;
            border-radius: 12px;
            padding: 10px;
            border: 1px solid rgba(255,255,255,0.07);
        }}

        /* Table */
        .table-card {{
            background: #1a1d2e;
            border-radius: 12px;
            padding: 20px;
            border: 1px solid rgba(255,255,255,0.07);
            margin-bottom: 16px;
            overflow-x: auto;
        }}
        .table-card h3 {{
            color: #a0aec0;
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            margin-bottom: 15px;
        }}
        table {{ width: 100%; border-collapse: collapse; font-size: 0.88rem; }}
        th {{ color: #a0aec0; font-weight: 600; padding: 10px 12px; text-align: left;
              border-bottom: 1px solid rgba(255,255,255,0.1); font-size: 0.78rem; text-transform: uppercase; }}
        td {{ padding: 10px 12px; border-bottom: 1px solid rgba(255,255,255,0.04); }}
        tr:hover td {{ background: rgba(255,255,255,0.03); }}
        .badge-fraud {{ background: #e74c3c22; color: #e74c3c; padding: 3px 10px;
                        border-radius: 20px; font-size: 0.75rem; font-weight: 600; }}
        .badge-legit {{ background: #2ecc7122; color: #2ecc71; padding: 3px 10px;
                        border-radius: 20px; font-size: 0.75rem; font-weight: 600; }}

        .footer {{ text-align: center; color: #4a5568; font-size: 0.8rem; margin-top: 30px; }}

        @media (max-width: 768px) {{
            .kpi-grid {{ grid-template-columns: repeat(2, 1fr); }}
            .charts-grid-2 {{ grid-template-columns: 1fr; }}
        }}
    </style>
</head>
<body>

<div class="header">
    <div>
        <h1>📊 Fraud Detection — Rapport BI</h1>
        <p>Analyse des transactions financières · Modèle Random Forest</p>
    </div>
    <div class="generated">Généré le {generated_at}</div>
</div>

<!-- KPI Cards -->
<div class="kpi-grid">
    <div class="kpi-card">
        <div class="kpi-value" style="color:#667eea">{total}</div>
        <div class="kpi-label">Total Transactions</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-value" style="color:#e74c3c">{fraudulent}</div>
        <div class="kpi-label">Frauduleuses</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-value" style="color:#2ecc71">{legitimate}</div>
        <div class="kpi-label">Légitimes</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-value" style="color:{'#e74c3c' if fraud_rate > 30 else '#f39c12'}">{fraud_rate}%</div>
        <div class="kpi-label">Taux de Fraude</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-value" style="color:#4facfe">${avg_fraud_amount:,.0f}</div>
        <div class="kpi-label">Montant Moy. Fraude</div>
    </div>
</div>

<!-- Charts Row 1 -->
<div class="charts-grid-2">
    <div class="chart-card">{donut_html}</div>
    <div class="chart-card">{bar_html}</div>
</div>

<!-- Charts Row 2 -->
<div class="charts-grid-2">
    <div class="chart-card">{scatter_html}</div>
    <div class="chart-card">{line_html}</div>
</div>

<!-- Transactions Table -->
<div class="table-card">
    <h3>🕐 Dernières Transactions Analysées</h3>
    <table>
        <thead>
            <tr>
                <th>Horodatage</th>
                <th>Type</th>
                <th>Montant</th>
                <th>Solde Avant</th>
                <th>Solde Après</th>
                <th>Résultat</th>
            </tr>
        </thead>
        <tbody>
            {''.join([f"""
            <tr>
                <td>{row['timestamp']}</td>
                <td>{row['type']}</td>
                <td>${float(row['amount']):,.2f}</td>
                <td>${float(row['oldbalanceOrg']):,.2f}</td>
                <td>${float(row['newbalanceOrig']):,.2f}</td>
                <td><span class="{'badge-fraud' if row['prediction'] == 1 else 'badge-legit'}">
                    {'⚠️ Frauduleuse' if row['prediction'] == 1 else '✅ Légitime'}
                </span></td>
            </tr>""" for _, row in df.sort_values('timestamp', ascending=False).head(15).iterrows()])}
        </tbody>
    </table>
</div>

<div class="footer">
    Credit Card Fraud Detection · Machine Learning + OCR · 
    <a href="https://github.com/KodsLamouchi322/credit-card-fraud-detection-ml" 
       style="color:#667eea">GitHub</a>
</div>

</body>
</html>"""

with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    f.write(html)

print(f"✅ Rapport généré : {OUTPUT_FILE}")
print(f"   → Ouvre le fichier dans ton navigateur")
print(f"\n📊 Résumé :")
print(f"   Total transactions : {total}")
print(f"   Frauduleuses       : {fraudulent}")
print(f"   Légitimes          : {legitimate}")
print(f"   Taux de fraude     : {fraud_rate}%")
print(f"   Montant moy fraude : ${avg_fraud_amount:,.2f}")
