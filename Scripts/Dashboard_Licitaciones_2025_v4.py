# =============================================================
#  DASHBOARD V4 — LICITACIONES  |  Patrones + Modelo Predictivo
#  Mercado Público Chile · Compra Chile
#  Luego abre: http://127.0.0.1:8053
# =============================================================

import os, sys, warnings
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────────────────────
# RUTAS
# ─────────────────────────────────────────────────────────────
BASE_DIR     = os.path.dirname(os.path.abspath(__file__))
DATA_PATH    = os.path.join(BASE_DIR, "..", "df_final.csv")
ORG_PATH     = os.path.join(BASE_DIR, "..", "organismos_nombres.parquet")
ORG_TOP_PATH = os.path.join(BASE_DIR, "df_organizaciones_top.csv")

# ─────────────────────────────────────────────────────────────
# PALETA
# ─────────────────────────────────────────────────────────────
C = {
    "bg": "#0D0F14", "card": "#141720", "panel": "#1A1E2E",
    "border": "#272C3F", "chart": "#141720",
    "a1": "#4F8EF7", "a2": "#7C5CF7", "a3": "#2DD4BF", "a4": "#F7874F",
    "green": "#22C55E", "yellow": "#F59E0B", "red": "#EF4444",
    "txt": "#E8EAF0", "sub": "#7B85A0",
}
PAL  = ["#4F8EF7","#7C5CF7","#2DD4BF","#F7874F","#F59E0B","#22C55E",
        "#EF4444","#E879F9","#38BDF8","#A3E635"]
FONT = "'Inter','Segoe UI',sans-serif"
GC   = {"background":C["card"],"borderRadius":"12px","border":f"1px solid {C['border']}",
        "padding":"20px","boxShadow":"0 1px 3px rgba(0,0,0,0.2)"}

# ─────────────────────────────────────────────────────────────
# CATÁLOGOS
# ─────────────────────────────────────────────────────────────
ESTADOS = {
    0:"Creada",1:"Publicada",2:"Cerrada",3:"En evaluación",4:"Adjudicada",
    5:"Desierta",6:"Revocada",7:"Cierre administrativo",8:"Adjudicada confirmada",
    9:"Cancelada",10:"Suspendida",11:"En aclaración",12:"En revisión",
    13:"En modificación",14:"Reapertura",15:"Desierta final",16:"Revocada anulada",
}
TIPOS = {
    "LE":"Lic. Pública Menor","LP":"Lic. Pública","LQ":"Lic. Mayor Cuantía",
    "L1":"Lic. Pública Tipo 1","LS":"Lic. Simplificada","CO":"Convenio",
    "CM":"Convenio Marco","SE":"Servicios","SP":"Servicios Prof.",
    "CD":"Compra Directa","TD":"Trato Directo","PR":"Propuesta","CA":"Compra Ágil",
}
MESES = {1:"Ene",2:"Feb",3:"Mar",4:"Abr",5:"May",6:"Jun",
         7:"Jul",8:"Ago",9:"Sep",10:"Oct",11:"Nov",12:"Dic"}

# Nombres cortos de organismos estratégicos
ORG_NOMBRES_CORTOS = {
    "3656":    "Mun. Requinoa",
    "3794":    "Dir. Log. Carabineros",
    "1660":    "S. Salud Coquimbo",
    "3863":    "Mun. Santa Cruz",
    "4809":    "MOP OOPP Araucanía",
    "1247197": "Corp. Mun. Conchalí",
    "3709":    "Mun. Victoria",
    "3510":    "Mun. Calbuco",
    "1509":    "H. Til-Til SS Metro Norte",
    "2196":    "H. Psiq. El Peral",
    "3589":    "Mun. Yungay",
    "3960":    "Mun. Hualane",
    "3928":    "Mun. Pichilemu",
    "4857":    "Mun. Tirua",
    "1057503": "H. Padre A. Hurtado",
    "2564":    "Mun. Chepica",
    "3508":    "Mun. Chonchi",
    "2342":    "Mun. San Bernardo",
    "979":     "MOP Dir. Gral. OOPP",
}

# ─────────────────────────────────────────────────────────────
# CARGA df_organizaciones_top.csv 
# ─────────────────────────────────────────────────────────────
print("Cargando df_organizaciones_top...", end=" ", flush=True)
try:
    df_org_top = pd.read_csv(ORG_TOP_PATH, encoding="utf-8")
    df_org_top["codigo_organismo"] = df_org_top["codigo_organismo"].astype(str)
    # Segmento limpio (sin emoji) para comparaciones de color
    df_org_top["segmento_clean"] = (
        df_org_top["segmento"]
        .str.replace(r"[^\w\s]", "", regex=True)
        .str.strip()
    )
    # Nombre corto: usa ORG_NOMBRES_CORTOS si existe, si no trunca el nombre oficial
    df_org_top["nombre_corto"] = df_org_top.apply(
        lambda r: ORG_NOMBRES_CORTOS.get(
            r["codigo_organismo"],
            str(r["nombre_organismo"])[:25] + "…"
            if len(str(r["nombre_organismo"])) > 25
            else str(r["nombre_organismo"]).title()
        ),
        axis=1,
    )
    N_ESTRATEGICOS = len(df_org_top)
    print(f"OK -> {N_ESTRATEGICOS} organismos")
except FileNotFoundError:
    print(f"\n[ERROR] No se encontró: {ORG_TOP_PATH}")
    sys.exit(1)

# ─────────────────────────────────────────────────────────────
# DATOS DEL MODELO
# ─────────────────────────────────────────────────────────────

# 5 modelos comparados
MODELOS_DF = pd.DataFrame({
    "modelo": ["M1 Reg. Lineal","M2 Random Forest","M3 XGBoost","M4 RF Optimizado","M5 Híbrido ★"],
    "mae":    [18.69, 10.77, 16.94, 12.40, 11.49],
    "rmse":   [21.92, 13.72, 19.04, 14.53, 13.85],
    "mape":   [41.64, 26.32, 38.27, 27.86, 26.23],
    "mejor":  [False, False, False, False, True],
})

# Forecast 2026 Mercado Total — Modelo 5 Híbrido (RF + reglas de negocio)
FORECAST_MKT = pd.DataFrame({
    "mes":    [1,    2,    3,    4,    5,    6,    7,    8,    9,    10,   11,   12],
    "lbl":    ["Ene","Feb","Mar","Abr","May","Jun","Jul","Ago","Sep","Oct","Nov","Dic"],
    "n":      [93.74, 106.61, 74.40, 60.02, 49.75, 51.97, 52.67, 50.89, 42.66, 53.54, 63.09, 80.77],
    "tipo":   ["ESTABLE","ESTABLE","CRITICO","ESTABLE","ESTABLE","ESTABLE",
               "ESTABLE","ESTABLE","CRITICO","ESTABLE","ESTABLE","ESTABLE"],
    "factor": [0.960, 1.114, 0.889, 0.939, 0.905, 1.000, 0.972, 0.984, 0.850, 0.979, 0.925, 1.137],
})

# ─────────────────────────────────────────────────────────────
# RANKING COMERCIAL
# ─────────────────────────────────────────────────────────────
RANKING_COM = df_org_top[["codigo_organismo","score_final","mae","rmse","mape",
                           "segmento","segmento_clean","nombre_corto"]].copy()
RANKING_COM.columns = ["cod","score","mae","rmse","mape","seg","seg_clean","nombre"]

# ─────────────────────────────────────────────────────────────
# FORECAST 2026 POR ORGANISMO 
# ─────────────────────────────────────────────────────────────
FORECAST_ORG = df_org_top[["codigo_organismo","forecast_12m","nombre_corto"]].copy()
FORECAST_ORG.columns = ["cod","n","nombre"]
FORECAST_ORG = FORECAST_ORG.sort_values("n", ascending=False).reset_index(drop=True)

# Forecast mensual 2026 para organismo 1660 (dato completo, ranking #1 comercial)
FORECAST_ORG_1660 = pd.DataFrame({
    "lbl": ["Ene","Feb","Mar","Abr","May","Jun","Jul","Ago","Sep","Oct","Nov","Dic"],
    "n":   [3.30, 2.49, 2.69, 3.98, 1.79, 1.93, 2.15, 2.75, 2.19, 1.55, 2.29, 8.03],
    "tipo":["ESTABLE","ESTABLE","CRITICO","ESTABLE","ESTABLE","ESTABLE",
            "ESTABLE","ESTABLE","CRITICO","ESTABLE","ESTABLE","ESTABLE"],
})

# ─────────────────────────────────────────────────────────────
# CARGA Y PREPARACIÓN DE DATOS HISTÓRICOS
# ─────────────────────────────────────────────────────────────
def load_data(path):
    df = pd.read_csv(path)
    p  = df["CodigoExterno"].str.split("-")
    df["tipo_cod"]         = p.str[2].str[:-2]
    df["tipo_desc"]        = df["tipo_cod"].map(TIPOS).fillna("Otro")
    df["codigo_organismo"] = p.str[0]
    df["estado_desc"]      = df["CodigoEstado"].map(ESTADOS).fillna("Desconocido")
    df["FechaCierre"]      = pd.to_datetime(df["FechaCierre"], errors="coerce")
    df["anio"]   = df["FechaCierre"].dt.year
    df["mes"]    = df["FechaCierre"].dt.month
    df["mes_str"]= df["mes"].map(MESES)
    df["semana"] = df["FechaCierre"].dt.isocalendar().week.astype("Int64")
    df["dia_sem"]= df["FechaCierre"].dt.day_name()
    df["periodo"]= df["FechaCierre"].dt.to_period("M")
    return df

print("Cargando datos históricos...", end=" ", flush=True)
try:
    df_raw = load_data(DATA_PATH)
    print(f"OK -> {len(df_raw):,} registros | anios: {sorted(df_raw['anio'].dropna().unique().astype(int).tolist())}")
except FileNotFoundError:
    print(f"\n[ERROR] No se encontró: {DATA_PATH}")
    sys.exit(1)

try:
    df_org = pd.read_parquet(ORG_PATH)
    org_dict = dict(zip(df_org["prefijo"].astype(str), df_org["nombre_organismo"]))
    print(f"Organismos cargados: {len(org_dict)}")
except Exception as e:
    print(f"[WARN] Organismos: {e}")
    org_dict = {}

f_min = df_raw["FechaCierre"].min()
f_max = df_raw["FechaCierre"].max()
RANGO = f"{f_min.strftime('%d/%m/%Y')} — {f_max.strftime('%d/%m/%Y')}" if pd.notna(f_min) else "--"

# ─────────────────────────────────────────────────────────────
# PRE-CÓMPUTO PATRONES
# ─────────────────────────────────────────────────────────────
def calc_tendencia_global():
    hoy = pd.Period(pd.Timestamp.today(), freq="M")
    d = (df_raw.dropna(subset=["periodo"])
         .groupby("periodo").size().reset_index(name="n").sort_values("periodo"))
    d = d[d["periodo"] < hoy].copy()
    d["t"]     = np.arange(len(d))
    coef       = np.polyfit(d["t"], d["n"], 1)
    d["trend"] = np.polyval(coef, d["t"])
    d["ma3"]   = d["n"].rolling(3, min_periods=1).mean().round(0)
    t_fut  = np.array([len(d), len(d)+1, len(d)+2])
    n_fut  = np.polyval(coef, t_fut).clip(0)
    last_p = d["periodo"].iloc[-1]
    fut_per= [(last_p + i + 1).to_timestamp() for i in range(3)]
    return d, coef, t_fut, n_fut, fut_per

def calc_estacionalidad():
    d = (df_raw.dropna(subset=["anio","mes"])
         .groupby(["anio","mes"]).size().reset_index(name="n"))
    d["anio"] = d["anio"].astype(int)
    ok = d.groupby("anio")["mes"].nunique()
    d  = d[d["anio"].isin(ok[ok >= 3].index)]
    pivot = (d.pivot_table(index="anio", columns="mes", values="n", aggfunc="sum")
               .reindex(columns=list(range(1,13)), fill_value=0))
    pivot.columns = [MESES[c] for c in pivot.columns]
    return pivot

def calc_mom_growth():
    hoy = pd.Period(pd.Timestamp.today(), freq="M")
    d = (df_raw.dropna(subset=["periodo"])
         .groupby("periodo").size().reset_index(name="n").sort_values("periodo"))
    d = d[d["periodo"] < hoy].copy()
    d["mom_pct"] = d["n"].pct_change() * 100
    d["lbl"]     = d["periodo"].apply(lambda p: p.to_timestamp().strftime("%b %Y"))
    return d.dropna(subset=["mom_pct"])

def calc_anomalias():
    d = (df_raw.dropna(subset=["semana","anio"])
         .groupby(["anio","semana"]).size().reset_index(name="n"))
    d["z"]        = (d["n"] - d["n"].mean()) / d["n"].std()
    d["anomalia"] = d["z"].abs() > 2
    d["semana"]   = d["semana"].astype(int)
    d["anio"]     = d["anio"].astype(int)
    return d

print("Calculando patrones...", end=" ", flush=True)
trend_d, trend_coef, t_fut, n_fut, fut_per = calc_tendencia_global()
estac_pivot = calc_estacionalidad()
mom_d       = calc_mom_growth()
anomalias_d = calc_anomalias()
print("OK")

slope         = trend_coef[0]
tendencia_dir = "Crecimiento" if slope > 0 else "Descenso"
tend_color    = C["green"] if slope > 0 else C["red"]
n_anomalias   = int(anomalias_d["anomalia"].sum())
_mes_vol      = df_raw.groupby("mes").size()
mes_pico_lbl  = MESES.get(int(_mes_vol.idxmax()), "--") if len(_mes_vol) else "--"
_sem_vol      = df_raw.dropna(subset=["semana"]).groupby("semana").size()
sem_pico      = int(_sem_vol.idxmax()) if len(_sem_vol) else 0

# ─────────────────────────────────────────────────────────────
# FILTROS
# ─────────────────────────────────────────────────────────────
anios_uniq        = sorted(df_raw["anio"].dropna().unique().astype(int).tolist())
meses_disponibles = sorted([k for k in MESES if k in df_raw["mes"].dropna().unique()])
anios_opts = [{"label":"Todos","value":"ALL"}] + [{"label":str(a),"value":a} for a in anios_uniq]
meses_opts = [{"label":"Todos","value":"ALL"}] + [{"label":f"{MESES[k]} ({k})","value":k} for k in meses_disponibles]

def apply_filters(mes, anio):
    df = df_raw.copy()
    if mes  != "ALL": df = df[df["mes"]  == int(mes)]
    if anio != "ALL": df = df[df["anio"] == int(anio)]
    return df

# ─────────────────────────────────────────────────────────────
# HELPERS UI
# ─────────────────────────────────────────────────────────────
def cb(fig, title="", h=340):
    fig.update_layout(
        title=dict(text=title, font=dict(size=13,color=C["txt"],family=FONT,weight=600),
                   x=0, xref="paper", pad=dict(l=0,t=0,b=12)),
        paper_bgcolor=C["chart"], plot_bgcolor=C["chart"],
        height=h, font=dict(family=FONT,color=C["sub"],size=11),
        margin=dict(l=12,r=12,t=52,b=12),
        legend=dict(bgcolor="rgba(0,0,0,0)",bordercolor=C["border"],font=dict(size=9)),
        hoverlabel=dict(bgcolor=C["panel"],font_size=12,font_family=FONT,bordercolor=C["border"]),
        xaxis=dict(gridcolor=C["border"],zerolinecolor=C["border"],linecolor=C["border"],
                   tickfont=dict(size=9,color=C["sub"])),
        yaxis=dict(gridcolor=C["border"],zerolinecolor=C["border"],linecolor=C["border"],
                   tickfont=dict(size=9,color=C["sub"])),
    )
    return fig

def info(texto):
    return html.Div([html.Div([
        html.I(className="fas fa-info-circle flex-shrink-0",
               style={"color":C["a3"],"fontSize":"14px","marginTop":"2px"}, **{"aria-hidden":"true"}),
        html.P(texto, className="mb-0",
               style={"fontSize":"12px","color":C["sub"],"lineHeight":"1.7"}),
    ], className="d-flex align-items-start gap-2")],
    style={"backgroundColor":"rgba(45,212,191,0.08)","borderLeft":f"3px solid {C['a3']}",
           "borderRadius":"6px","padding":"16px 20px","marginTop":"28px"},
    className="infografia-box")

def kpi(label, value, sub="", color=None, icon="◆"):
    color = color or C["a1"]
    fs = "24px" if len(str(value)) <= 8 else "16px" if len(str(value)) <= 18 else "12px"
    return html.Div(html.Div([
        html.Div(icon, style={"fontSize":"18px","color":color,"marginBottom":"6px"}),
        html.Div(str(value), style={"fontSize":fs,"fontWeight":"700","color":C["txt"],
                                    "lineHeight":"1.2","wordBreak":"break-word"}),
        html.Div(label, style={"fontSize":"10px","fontWeight":"600","letterSpacing":"0.07em",
                               "color":C["sub"],"textTransform":"uppercase","marginTop":"5px"}),
        html.Div(sub, style={"fontSize":"9px","color":color,"marginTop":"2px"}) if sub else None,
    ], style={"padding":"16px 14px","borderRadius":"10px","background":C["card"],
              "border":f"1px solid {C['border']}","borderTop":f"3px solid {color}","height":"100%"}),
    className="h-100", role="status")

def sec(text, sub=""):
    return html.Div([
        html.H2([
            html.Span("┃ ", style={"color":C["a1"],"fontSize":"18px"}),
            html.Span(text, style={"fontSize":"16px","fontWeight":"700","color":C["txt"],"letterSpacing":"-0.3px"}),
        ], style={"margin":"0"}),
        html.Div(sub, style={"fontSize":"11px","color":C["sub"],"marginTop":"4px","marginLeft":"18px"}) if sub else None,
    ], style={"marginBottom":"20px","marginTop":"32px"})

# ─────────────────────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────────────────────
CSS = f"""
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
body{{background:{C['bg']};color:{C['txt']};font-family:{FONT};-webkit-font-smoothing:antialiased;line-height:1.6}}
::-webkit-scrollbar{{width:6px;height:6px}}
::-webkit-scrollbar-track{{background:transparent}}
::-webkit-scrollbar-thumb{{background:{C['border']};border-radius:3px}}
::-webkit-scrollbar-thumb:hover{{background:{C['sub']}}}
*:focus{{outline:2px solid {C['a1']};outline-offset:2px}}
*:focus:not(:focus-visible){{outline:none}}
.infografia-box{{display:block !important;margin-top:28px !important;clear:both}}
.Select-control{{background:{C['panel']} !important;border-color:{C['border']} !important;color:{C['txt']} !important;border-radius:8px !important}}
.Select-menu-outer{{background:{C['panel']} !important;border-color:{C['border']} !important}}
.Select-option{{color:{C['txt']} !important}}
.Select-option.is-focused{{background:{C['bg']} !important}}
.Select-value-label{{color:{C['txt']} !important;font-weight:600 !important}}
.Select-placeholder{{color:{C['sub']} !important;font-weight:500 !important}}
.tab-style{{background:{C['card']};border-bottom:2px solid {C['border']};padding:0 20px}}
.dash-tab{{color:{C['sub']} !important;background:{C['card']} !important;border:none !important;padding:14px 24px !important;font-size:13px;font-weight:500;border-bottom:2px solid transparent !important;transition:all 0.2s ease}}
.dash-tab:hover{{color:{C['txt']} !important}}
.dash-tab--selected{{color:{C['txt']} !important;border-bottom:2px solid {C['a1']} !important}}
"""

# ─────────────────────────────────────────────────────────────
# APP
# ─────────────────────────────────────────────────────────────
app = dash.Dash(__name__,
    external_stylesheets=[dbc.themes.DARKLY,
        "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css"],
    title="Dashboard V4 · Compra Chile",
    suppress_callback_exceptions=True)
app.index_string = f"""<!DOCTYPE html>
<html lang="es"><head>{{%metas%}}<title>{{%title%}}</title>{{%favicon%}}{{%css%}}
<style>{CSS}</style></head>
<body>{{%app_entry%}}<footer>{{%config%}}{{%scripts%}}{{%renderer%}}</footer></body></html>"""

# ─────────────────────────────────────────────────────────────
# LAYOUT
# ─────────────────────────────────────────────────────────────
app.layout = html.Div([

    html.Header([dbc.Container([dbc.Row([
        dbc.Col([
            html.Span("◈ ", style={"fontSize":"20px","color":C["a1"]}),
            html.Span("Compra Chile", style={"fontSize":"16px","fontWeight":"700","color":C["txt"]}),
            html.Span(" · Licitaciones Chile v4", style={"fontSize":"13px","color":C["sub"],"marginLeft":"4px"}),
        ], width="auto", className="d-flex align-items-center"),
        dbc.Col([html.Div([
            html.Span(f"Modelo 5: RF Opt + Factores Nivelación · MAE 11.49 · MAPE 26.23%", style={"fontSize":"11px","color":C["a3"]}),
            html.Span(f"  ·  {RANGO}", style={"fontSize":"11px","color":C["sub"]}),
        ], className="text-end")], className="d-flex align-items-center justify-content-end"),
    ], align="center")], fluid=True, style={"padding":"0 28px"})],
    style={"background":C["card"],"borderBottom":f"1px solid {C['border']}","padding":"13px 0",
           "position":"sticky","top":"0","zIndex":"999"}),

    html.Main([dbc.Container([

        dbc.Row([dbc.Col([
            html.H1("Análisis de Licitaciones & Predicción 2026",
                    style={"fontSize":"26px","fontWeight":"800","color":C["txt"],"letterSpacing":"-0.6px","marginBottom":"2px"}),
            html.P("Patrones históricos · Modelo Híbrido RF · Ranking Comercial Compra Chile",
                   style={"color":C["sub"],"fontSize":"12px"}),
        ], className="mt-4 mb-3")]),

        # FILTROS
        html.Div([dbc.Row([
            dbc.Col([
                html.Label("AÑO", style={"fontSize":"10px","fontWeight":"600","color":C["sub"],"marginBottom":"5px","display":"block","letterSpacing":"0.08em"}),
                dcc.Dropdown(id="f-anio", options=anios_opts, value="ALL", clearable=False,
                             style={"borderRadius":"8px","background":C["panel"]}),
            ], md=3),
            dbc.Col([
                html.Label("MES", style={"fontSize":"10px","fontWeight":"600","color":C["sub"],"marginBottom":"5px","display":"block","letterSpacing":"0.08em"}),
                dcc.Dropdown(id="f-mes", options=meses_opts, value="ALL", clearable=False,
                             style={"borderRadius":"8px","background":C["panel"]}),
            ], md=3),
            dbc.Col([
                html.Label("\u00a0", style={"display":"block","fontSize":"10px","marginBottom":"5px"}),
                dbc.Button([html.I(className="fa fa-rotate-right me-1"), " Limpiar"],
                           id="btn-reset", color="secondary", outline=True, size="sm",
                           style={"borderRadius":"8px","fontSize":"11px","borderColor":C["border"],"color":C["sub"]}),
            ], md=2, className="d-flex align-items-end"),
            dbc.Col([
                html.Div([
                    html.Span("Filtros aplican a ", style={"fontSize":"10px","color":C["sub"]}),
                    html.Span("Visión General", style={"fontSize":"10px","color":C["a1"],"fontWeight":"600"}),
                    html.Span(" y ", style={"fontSize":"10px","color":C["sub"]}),
                    html.Span("Patrones", style={"fontSize":"10px","color":C["a1"],"fontWeight":"600"}),
                    html.Span(" · La pestaña Modelo usa datos del notebook.", style={"fontSize":"10px","color":C["sub"]}),
                ], style={"paddingTop":"22px"}),
            ], md=4),
        ])], className="mb-4 p-3",
        style={"background":C["card"],"borderRadius":"12px","border":f"1px solid {C['border']}"}),

        # TABS
        dcc.Tabs(id="tabs", value="tab-overview", className="tab-style", children=[
            dcc.Tab(label="📊  Visión General",         value="tab-overview",  className="dash-tab", selected_className="dash-tab--selected"),
            dcc.Tab(label="📈  Patrones & Tendencias",  value="tab-patterns",  className="dash-tab", selected_className="dash-tab--selected"),
            dcc.Tab(label="🤖  Modelo & Predicción 2026", value="tab-modelo", className="dash-tab", selected_className="dash-tab--selected"),
        ]),
        html.Div(id="tab-content"),

    ], fluid=True, style={"padding":"0 20px"})]),
], style={"minHeight":"100vh","background":C["bg"]})


# ─────────────────────────────────────────────────────────────
# TAB 1: VISIÓN GENERAL
# ─────────────────────────────────────────────────────────────
def render_overview(df):
    n     = len(df)
    n_org = df["codigo_organismo"].nunique()
    _mv   = df.groupby("mes").size()
    mp_lbl= MESES.get(int(_mv.idxmax()), "--") if len(_mv) else "--"
    _ov   = df["codigo_organismo"].value_counts()
    oc    = str(_ov.idxmax()) if len(_ov) else "--"
    onom  = org_dict.get(oc, ORG_NOMBRES_CORTOS.get(oc, f"Org. {oc}"))[:28]

    kpis = dbc.Row([
        dbc.Col(kpi("Total Licitaciones",   f"{n:,}",    "registros",          C["a1"], "◆"), md=3),
        dbc.Col(kpi("Organismos Activos",   f"{n_org:,}","únicos",             C["a2"], "◈"), md=3),
        dbc.Col(kpi("Mes Pico Histórico",   mp_lbl,      "mayor actividad",    C["a3"], "◉"), md=3),
        dbc.Col(kpi("Organismo Líder",      onom,        "mayor volumen",      C["a4"], "◎"), md=3),
    ], className="mb-4 g-3", style={"marginTop":"20px"})

    return html.Div([kpis,
        sec("Evolución Mensual con Media Móvil", "Serie histórica + MA3"),
        dbc.Row([dbc.Col([
            html.Div(dcc.Graph(id="g-evol", config={"displayModeBar":False}), style=GC),
            info("Azul: volumen mensual real. Naranja: media móvil 3 meses. Revela la tendencia subyacente eliminando ruido estacional."),
        ])], className="mb-5", style={"marginTop":"24px"}),

        sec("Comparativa Año a Año & Top Organismos"),
        dbc.Row([
            dbc.Col([
                html.Div(dcc.Graph(id="g-yoy", config={"displayModeBar":False}), style=GC),
                info("Cada línea es un año. El año más reciente resaltado. Detecta si el comportamiento actual es consistente con años anteriores."),
            ], md=7),
            dbc.Col([
                html.Div(dcc.Graph(id="g-org", config={"displayModeBar":False}), style=GC),
                info("Top 15 organismos por volumen. Identifica los compradores que más impulsan el mercado."),
            ], md=5),
        ], className="mb-5 g-3"),

        sec("Concentración del Mercado", "Top 40 organismos"),
        dbc.Row([dbc.Col([
            html.Div(dcc.Graph(id="g-treemap", config={"displayModeBar":False}), style=GC),
            info("Treemap proporcional. Tamaño = volumen relativo. Revela si el mercado está concentrado en pocos organismos o distribuido."),
        ])], className="mb-5"),
    ])


# ─────────────────────────────────────────────────────────────
# TAB 2: PATRONES & TENDENCIAS
# ─────────────────────────────────────────────────────────────
def render_patterns():
    vol_proy = max(0, int(n_fut[0]))
    kpis = dbc.Row([
        dbc.Col(kpi("Tendencia Global",     tendencia_dir,   f"{abs(slope):.1f} lic/mes", tend_color, "◈"), md=3),
        dbc.Col(kpi("Volumen Proyectado",   f"{vol_proy:,}", "próx. mes (OLS)",           C["a1"],    "◆"), md=3),
        dbc.Col(kpi("Mes Histórico Pico",   mes_pico_lbl,    "mayor actividad",           C["a3"],    "◉"), md=3),
        dbc.Col(kpi("Anomalías Detectadas", f"{n_anomalias}","semanas |z| > 2σ",
                    C["red"] if n_anomalias > 0 else C["sub"], "◍"), md=3),
    ], className="mb-4 g-3", style={"marginTop":"20px"})

    return html.Div([kpis,
        sec("Proyección de Tendencia (OLS)", "Últimos 24 meses + proyección 3 meses · línea de base"),
        dbc.Row([dbc.Col([
            html.Div(dcc.Graph(id="g-forecast", config={"displayModeBar":False}), style=GC),
            info("Regresión lineal OLS sobre serie histórica. Banda ±1.5σ. Diamantes = 3 meses proyectados. Base comparativa para el Modelo 5."),
        ])], className="mb-5", style={"marginTop":"24px"}),

        sec("Estacionalidad & Variación MoM"),
        dbc.Row([
            dbc.Col([
                html.Div(dcc.Graph(id="g-estac", config={"displayModeBar":False}), style=GC),
                info("% del volumen anual por mes. Verde intenso = mes más activo dentro del año. Patrones estacionales recurrentes."),
            ], md=6),
            dbc.Col([
                html.Div(dcc.Graph(id="g-mom", config={"displayModeBar":False}), style=GC),
                info("Variación % mes a mes (MoM). Verde = crecimiento. Rojo = contracción. Detecta aceleraciones en el ritmo de publicaciones."),
            ], md=6),
        ], className="mb-5 g-3"),

        sec("Distribución Semanal & Por Día"),
        dbc.Row([
            dbc.Col([
                html.Div(dcc.Graph(id="g-semana", config={"displayModeBar":False}), style=GC),
                info("Volumen acumulado por semana ISO. Azul = sobre promedio. Detecta semanas de alta/baja actividad estacional."),
            ], md=8),
            dbc.Col([
                html.Div(dcc.Graph(id="g-diasem", config={"displayModeBar":False}), style=GC),
                info("Distribución radial por día de semana. Qué días concentran más publicaciones."),
            ], md=4),
        ], className="mb-5 g-3"),

        sec("Anomalías Semanales", "|z-score| > 2σ"),
        dbc.Row([dbc.Col([
            html.Div(dcc.Graph(id="g-anom", config={"displayModeBar":False}), style=GC),
            info("Rojo = semanas anómalas. Identifica eventos excepcionales o cambios de régimen en el volumen de licitaciones."),
        ])], className="mb-5"),
    ])


# ─────────────────────────────────────────────────────────────
# TAB 3: MODELO PREDICTIVO & RANKING COMERCIAL
# ─────────────────────────────────────────────────────────────
def render_modelo():
    mejor_mape    = MODELOS_DF.loc[MODELOS_DF["mejor"], "mape"].values[0]
    baseline_mape = MODELOS_DF.iloc[0]["mape"]
    mejora_pct    = round((baseline_mape - mejor_mape) / baseline_mape * 100, 1)
    forecast_total = int(FORECAST_MKT["n"].sum())
    n_alto_valor  = int(RANKING_COM["seg_clean"].str.startswith("Alto valor").sum())
    top_org       = RANKING_COM.iloc[0]

    kpis = dbc.Row([
        dbc.Col(kpi("Mejor Modelo",       "Híbrido RF",  "RF Opt + factores nivelación (Iñaki 11/04)", C["a3"], "◈"), md=3),
        dbc.Col(kpi("MAE Modelo 5",       "11.49",       "error promedio lic/mes",          C["a1"],    "◆"), md=3),
        dbc.Col(kpi("Mejora vs Baseline", f"{mejora_pct}%", "vs Regresión Lineal M1",       C["green"], "◉"), md=3),
        dbc.Col(kpi("Organismos Alto Valor", f"{n_alto_valor}", f"de {N_ESTRATEGICOS} evaluados", C["yellow"],"◍"), md=3),
    ], className="mb-4 g-3", style={"marginTop":"20px"})

    return html.Div([kpis,

        # ── Comparación de modelos + Reglas de negocio ────────
        sec("Comparación de 5 Modelos", "MAE y MAPE · menor es mejor · M5 Híbrido es el ganador"),
        dbc.Row([
            dbc.Col([
                html.Div(dcc.Graph(id="g-modelos", config={"displayModeBar":False}), style=GC),
                info("Comparativa directa de los 5 modelos evaluados en el mismo conjunto de test. M5 Híbrido (RF + reglas de negocio) logra el menor MAPE y el menor sesgo (BIAS=6.30)."),
            ], md=7),
            dbc.Col([
                html.Div(dcc.Graph(id="g-reglas", config={"displayModeBar":False}), style=GC),
                info("Clasificación de meses según el error del modelo. CRÍTICO = error > 20%, se aplica factor de corrección. Marzo y Septiembre son los meses más difíciles de predecir."),
            ], md=5),
        ], className="mb-5 g-3", style={"marginTop":"24px"}),

        # ── Forecast 2026 mercado total ───────────────────────
        sec("Forecast 2026 — Mercado Total",
            f"Modelo 5 Híbrido · {N_ESTRATEGICOS} organismos estratégicos · meses CRÍTICO marcados en rojo"),
        dbc.Row([dbc.Col([
            html.Div(dcc.Graph(id="g-forecast2026", config={"displayModeBar":False}), style=GC),
            info(f"Proyección mensual 2026 para el universo de {N_ESTRATEGICOS} organismos estratégicos. Barras rojas = meses CRÍTICO donde se activaron reglas de corrección (Marzo y Septiembre)."),
        ])], className="mb-5"),

        # ── Ranking + Forecast por organismo ─────────────────
        sec("Ranking Comercial & Forecast por Organismo",
            "Score = predictibilidad + volumen + estabilidad · Forecast 12 meses 2026 · Datos: df_organizaciones_top.csv"),
        dbc.Row([
            dbc.Col([
                html.Div(dcc.Graph(id="g-ranking", config={"displayModeBar":False}), style=GC),
                info("Ranking final Compra Chile. Score combina: predictibilidad del modelo (MAE), volumen proyectado y estabilidad histórica. Alto valor = target prioritario."),
            ], md=6),
            dbc.Col([
                html.Div(dcc.Graph(id="g-forecast-org", config={"displayModeBar":False}), style=GC),
                info("Total de licitaciones proyectadas 2026 por organismo. Identifica qué organismos generarán mayor volumen de negocio."),
            ], md=6),
        ], className="mb-5 g-3"),

        # ── Forecast mensual organismo top ────────────────────
        sec(f"Forecast Mensual 2026 — Organismo Top",
            f"{top_org['nombre']} (cod. {top_org['cod']}) · Score más alto · MAE={top_org['mae']:.3f}"),
        dbc.Row([dbc.Col([
            html.Div(dcc.Graph(id="g-forecast-org-mes", config={"displayModeBar":False}), style=GC),
            info(f"Forecast mensual detallado del organismo con mayor score comercial. Diciembre pico proyectado (8.03 lic). Barras rojas = meses CRÍTICO con corrección aplicada."),
        ])], className="mb-5"),
    ])


# ─────────────────────────────────────────────────────────────
# CALLBACKS — TAB ROUTER
# ─────────────────────────────────────────────────────────────
@app.callback(Output("f-anio","value"), Output("f-mes","value"),
              Input("btn-reset","n_clicks"), prevent_initial_call=True)
def reset_f(_): return "ALL", "ALL"

@app.callback(Output("tab-content","children"),
    Input("tabs","value"), Input("f-anio","value"), Input("f-mes","value"))
def render_tab(tab, anio, mes):
    df = apply_filters(mes, anio)
    if tab == "tab-overview":  return render_overview(df)
    if tab == "tab-patterns":  return render_patterns()
    return render_modelo()


# ─────────────────────────────────────────────────────────────
# CALLBACKS — TAB 1 VISIÓN GENERAL
# ─────────────────────────────────────────────────────────────
@app.callback(Output("g-evol","figure"),
    Input("f-anio","value"), Input("f-mes","value"))
def go_evol(anio, mes):
    df = apply_filters(mes, anio)
    d  = (df.dropna(subset=["periodo"]).groupby("periodo").size()
          .reset_index(name="n").sort_values("periodo"))
    d["lbl"] = d["periodo"].apply(lambda p: p.to_timestamp().strftime("%b %Y"))
    d["ma3"] = d["n"].rolling(3, min_periods=1).mean().round(0)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=d["lbl"], y=d["n"], mode="lines",
        line=dict(color=C["a1"], width=2, shape="spline"),
        fill="tozeroy", fillcolor="rgba(79,142,247,0.08)",
        name="Real", hovertemplate="<b>%{x}</b><br>%{y:,}<extra></extra>"))
    fig.add_trace(go.Scatter(x=d["lbl"], y=d["ma3"], mode="lines",
        line=dict(color=C["a4"], width=2.5),
        name="MA3", hovertemplate="<b>%{x}</b><br>MA3: %{y:.0f}<extra></extra>"))
    fig = cb(fig, "Evolución Mensual + Media Móvil 3m", 300)
    fig.update_xaxes(showgrid=False, tickangle=-30)
    fig.update_yaxes(showgrid=True, gridwidth=1)
    fig.update_layout(legend=dict(orientation="h", x=0, y=1.12, font=dict(size=10)))
    return fig

@app.callback(Output("g-yoy","figure"),
    Input("f-anio","value"), Input("f-mes","value"))
def go_yoy(anio, mes):
    df = apply_filters(mes, "ALL")
    d  = (df.dropna(subset=["anio","mes"]).groupby(["anio","mes"]).size().reset_index(name="n"))
    d["anio"] = d["anio"].astype(int)
    ok = d.groupby("anio")["mes"].nunique()
    d  = d[d["anio"].isin(ok[ok >= 3].index)].copy()
    fig = go.Figure()
    anios_s = sorted(d["anio"].unique())
    for i, yr in enumerate(anios_s):
        g = d[d["anio"] == yr].sort_values("mes")
        c = PAL[i % len(PAL)]
        ultimo = (yr == anios_s[-1])
        fig.add_trace(go.Scatter(
            x=[MESES[m] for m in g["mes"]], y=g["n"].tolist(),
            mode="lines+markers", name=str(yr),
            line=dict(color=c, width=3 if ultimo else 1.5, shape="spline"),
            marker=dict(size=6 if ultimo else 3, color=c),
            opacity=1.0 if ultimo else 0.5,
            hovertemplate=f"<b>{yr}</b> — %{{x}}: %{{y:,}}<extra></extra>"))
    fig = cb(fig, "Comparativa Año a Año (YoY)", 360)
    fig.update_xaxes(showgrid=False, categoryorder="array",
                     categoryarray=[MESES[m] for m in range(1,13)])
    fig.update_yaxes(showgrid=True, gridwidth=1)
    fig.update_layout(legend=dict(orientation="h", x=0, y=1.12, font=dict(size=9)))
    return fig

@app.callback(Output("g-org","figure"),
    Input("f-anio","value"), Input("f-mes","value"))
def go_org(anio, mes):
    df = apply_filters(mes, anio)
    d  = (df.groupby("codigo_organismo").size().reset_index(name="n")
          .sort_values("n", ascending=True).tail(15))
    nm = lambda x: org_dict.get(str(x), ORG_NOMBRES_CORTOS.get(str(x), f"Org.{x}"))
    d["lbl"] = d["codigo_organismo"].astype(str).apply(nm)
    d["lbl"] = d["lbl"].apply(lambda x: x[:45]+"…" if len(x)>45 else x)
    grad = [f"rgba(79,142,247,{0.3+0.7*i/max(len(d)-1,1)})" for i in range(len(d))]
    fig = go.Figure(go.Bar(x=d["n"], y=d["lbl"], orientation="h",
        marker=dict(color=grad, line=dict(width=0)),
        text=[f" {v:,}" for v in d["n"]], textposition="outside",
        textfont=dict(size=9,color=C["sub"]),
        hovertemplate="<b>%{y}</b><br>%{x:,}<extra></extra>"))
    fig = cb(fig, "Top 15 Organismos por Volumen", 400)
    fig.update_xaxes(showgrid=True, gridwidth=1)
    fig.update_yaxes(showgrid=False)
    return fig

@app.callback(Output("g-treemap","figure"),
    Input("f-anio","value"), Input("f-mes","value"))
def go_treemap(anio, mes):
    df = apply_filters(mes, anio)
    d  = (df.groupby("codigo_organismo").size().reset_index(name="n")
          .sort_values("n", ascending=False).head(40))
    nm = lambda x: org_dict.get(str(x), ORG_NOMBRES_CORTOS.get(str(x), f"Org.{x}"))
    d["lbl"] = d["codigo_organismo"].astype(str).apply(nm)
    d["lbl"] = d["lbl"].apply(lambda x: x[:32]+"…" if len(x)>32 else x)
    total = d["n"].sum()
    fig = go.Figure(go.Treemap(
        labels=d["lbl"].tolist(), values=d["n"].tolist(), parents=[""]*len(d),
        texttemplate="<b>%{label}</b><br>%{value:,}<br>%{percentRoot:.1%}",
        textfont=dict(size=11, color=C["txt"]),
        marker=dict(colors=d["n"].tolist(),
                    colorscale=[[0,C["panel"]],[0.3,"#1A3A6A"],[0.7,C["a1"]],[1,"#CFDFFF"]],
                    showscale=False),
        hovertemplate="<b>%{label}</b><br>%{value:,} · %{percentRoot:.1%}<extra></extra>"))
    fig = cb(fig, f"Concentración Mercado — Top 40 ({total:,} licitaciones)", 440)
    return fig


# ─────────────────────────────────────────────────────────────
# CALLBACKS — TAB 2 PATRONES
# ─────────────────────────────────────────────────────────────
@app.callback(Output("g-forecast","figure"), Input("tabs","value"))
def go_forecast(tab):
    if tab != "tab-patterns": return go.Figure()
    d = trend_d.tail(24).copy()
    d["lbl"] = d["periodo"].apply(lambda p: p.to_timestamp().strftime("%b %Y"))
    fut_lbl  = [f.strftime("%b %Y") for f in fut_per]
    sigma    = (d["n"] - d["trend"]).std()
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=d["lbl"].tolist()+d["lbl"].tolist()[::-1],
        y=(d["trend"]+1.5*sigma).tolist()+(d["trend"]-1.5*sigma).tolist()[::-1],
        fill="toself", fillcolor="rgba(79,142,247,0.06)", line=dict(width=0),
        hoverinfo="skip", showlegend=False))
    fig.add_trace(go.Scatter(x=d["lbl"], y=d["n"], mode="lines",
        line=dict(color=C["a1"], width=2.5, shape="spline"),
        fill="tozeroy", fillcolor="rgba(79,142,247,0.06)",
        name="Real", hovertemplate="<b>%{x}</b><br>%{y:,}<extra></extra>"))
    fig.add_trace(go.Scatter(x=d["lbl"], y=d["trend"].round().astype(int), mode="lines",
        line=dict(color=C["a2"], width=2, dash="dash"),
        name="Tendencia OLS"))
    fig.add_trace(go.Scatter(
        x=[d["lbl"].iloc[-1]]+fut_lbl,
        y=[int(d["n"].iloc[-1])]+[int(v) for v in n_fut],
        mode="lines+markers", line=dict(color=C["a4"], width=3, dash="dot"),
        marker=dict(size=10, color=C["a4"], symbol="diamond"),
        name="Proyección OLS"))
    for xl, yv in zip(fut_lbl, n_fut):
        fig.add_annotation(x=xl, y=int(yv), text=f"  {int(yv):,}", showarrow=False,
            font=dict(size=11,color=C["a4"],family=FONT), xanchor="left")
    fig = cb(fig, "Tendencia Mensual + Proyección 3 Meses OLS (Últimos 24m)", 380)
    fig.update_xaxes(showgrid=False, tickangle=-45, range=[-0.5, len(d)+3.5])
    fig.update_yaxes(showgrid=True, gridwidth=1)
    fig.add_vrect(x0=d["lbl"].iloc[-1], x1=fut_lbl[-1],
                  fillcolor="rgba(247,135,79,0.04)", line_width=0)
    return fig

@app.callback(Output("g-estac","figure"), Input("tabs","value"))
def go_estac(tab):
    if tab != "tab-patterns": return go.Figure()
    pivot_norm = estac_pivot.div(estac_pivot.sum(axis=1), axis=0) * 100
    fig = go.Figure(go.Heatmap(
        z=pivot_norm.values, x=pivot_norm.columns.tolist(),
        y=[str(yr) for yr in pivot_norm.index.tolist()],
        colorscale=[[0,C["panel"]],[0.3,"#1A2F5A"],[0.7,C["a3"]],[1,"#E0FFF8"]],
        showscale=True,
        colorbar=dict(title=dict(text="%", font=dict(size=9,color=C["sub"])),
                      tickfont=dict(size=8,color=C["sub"]),outlinewidth=0,thickness=8),
        text=[[f"{v:.1f}%" for v in row] for row in pivot_norm.values],
        texttemplate="%{text}", textfont=dict(size=8,color=C["txt"]),
        hovertemplate="Año <b>%{y}</b> · <b>%{x}</b><br>%{z:.1f}%<extra></extra>"))
    fig = cb(fig, "Estacionalidad: % Licitaciones por Mes/Año", 380)
    return fig

@app.callback(Output("g-mom","figure"), Input("tabs","value"))
def go_mom(tab):
    if tab != "tab-patterns": return go.Figure()
    d   = mom_d.tail(24).copy()
    avg = d["mom_pct"].mean()
    fig = go.Figure(go.Bar(
        x=d["lbl"], y=d["mom_pct"],
        marker=dict(color=[C["green"] if v>=0 else C["red"] for v in d["mom_pct"]], opacity=0.85),
        text=[f"{v:+.1f}%" for v in d["mom_pct"]], textposition="outside",
        textfont=dict(size=8,color=C["sub"]),
        hovertemplate="<b>%{x}</b><br>MoM: %{y:+.1f}%<extra></extra>"))
    fig.add_hline(y=0, line_color=C["border"])
    fig.add_hline(y=avg, line_dash="dot", line_color=C["a2"],
        annotation_text=f"Prom: {avg:+.1f}%", annotation_font_color=C["a2"], annotation_font_size=9)
    fig = cb(fig, "Variación MoM % (Últimos 24 Meses)", 380)
    fig.update_xaxes(showgrid=False, tickangle=-45)
    fig.update_yaxes(showgrid=True, gridwidth=1)
    return fig

@app.callback(Output("g-semana","figure"), Input("tabs","value"))
def go_semana(tab):
    if tab != "tab-patterns": return go.Figure()
    d   = (df_raw.dropna(subset=["semana"]).groupby("semana").size()
           .reset_index(name="n").sort_values("semana"))
    d["semana"] = d["semana"].astype(int)
    avg = d["n"].mean()
    fig = go.Figure()
    fig.add_hline(y=avg, line_dash="dot", line_color=C["a2"],
        annotation_text=f"Prom: {avg:.0f}", annotation_font_color=C["a2"], annotation_font_size=9)
    fig.add_trace(go.Bar(x=d["semana"], y=d["n"],
        marker=dict(color=[C["a1"] if v>=avg else C["panel"] for v in d["n"]], opacity=0.85),
        hovertemplate="Semana <b>%{x}</b><br>%{y:,}<extra></extra>"))
    fig = cb(fig, "Distribución por Semana ISO", 280)
    fig.update_xaxes(title_text="Semana ISO", showgrid=False)
    fig.update_yaxes(showgrid=True, gridwidth=1)
    return fig

@app.callback(Output("g-diasem","figure"), Input("tabs","value"))
def go_diasem(tab):
    if tab != "tab-patterns": return go.Figure()
    orden = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    etiq  = ["Lun","Mar","Mié","Jue","Vie","Sáb","Dom"]
    d = (df_raw.dropna(subset=["dia_sem"]).groupby("dia_sem").size()
         .reindex(orden, fill_value=0).reset_index())
    d.columns = ["dia","n"]; d["etiq"] = etiq
    fig = go.Figure(go.Barpolar(r=d["n"], theta=d["etiq"],
        marker=dict(color=d["n"], colorscale=[[0,C["panel"]],[1,C["a3"]]], showscale=False,
                    line=dict(color=C["border"],width=1)),
        hovertemplate="<b>%{theta}</b><br>%{r:,}<extra></extra>"))
    fig = cb(fig, "Actividad por Día de Semana", 280)
    fig.update_layout(polar=dict(bgcolor=C["chart"],
        angularaxis=dict(linecolor=C["border"],gridcolor=C["border"],
                        tickfont=dict(size=10,color=C["sub"]),rotation=90,direction="clockwise"),
        radialaxis=dict(gridcolor=C["border"],linecolor=C["border"],
                       tickfont=dict(size=7,color=C["sub"]),angle=90)))
    return fig

@app.callback(Output("g-anom","figure"), Input("tabs","value"))
def go_anom(tab):
    if tab != "tab-patterns": return go.Figure()
    d   = anomalias_d.copy().sort_values(["anio","semana"])
    d["idx"] = range(len(d))
    d["lbl"] = d["anio"].astype(str)+"-S"+d["semana"].astype(str).str.zfill(2)
    mu  = d["n"].mean(); sig = d["n"].std()
    fig = go.Figure()
    fig.add_trace(go.Bar(x=d["idx"], y=d["n"],
        marker=dict(color=[C["red"] if a else C["a1"] for a in d["anomalia"]],
                    opacity=[1.0 if a else 0.35 for a in d["anomalia"]]),
        customdata=d[["lbl","z"]].values,
        hovertemplate="<b>%{customdata[0]}</b><br>%{y:,} · z=%{customdata[1]:.2f}<extra></extra>"))
    for _, row in d[d["anomalia"]].iterrows():
        fig.add_annotation(x=row["idx"], y=row["n"], text=row["lbl"],
            showarrow=True, arrowhead=1, arrowcolor=C["red"],
            font=dict(size=8,color=C["red"]), ax=0, ay=-28,
            bgcolor="rgba(20,23,32,0.8)", bordercolor=C["red"])
    fig.add_hline(y=mu+2*sig, line_dash="dot", line_color=C["red"],
        annotation_text="+2σ", annotation_font_color=C["red"])
    fig.add_hline(y=max(0,mu-2*sig), line_dash="dot", line_color=C["a2"],
        annotation_text="−2σ", annotation_font_color=C["a2"])
    fig.add_hline(y=mu, line_dash="solid", line_color=C["border"],
        annotation_text=f"μ={mu:.0f}", annotation_font_color=C["sub"])
    au = d.drop_duplicates("anio").copy()
    fig = cb(fig, f"Anomalías Semanales — {n_anomalias} semanas fuera de ±2σ", 380)
    fig.update_xaxes(showgrid=False, tickvals=au["idx"].tolist(),
                     ticktext=au["anio"].astype(str).tolist())
    fig.update_yaxes(showgrid=True, gridwidth=1)
    return fig


# ─────────────────────────────────────────────────────────────
# CALLBACKS — TAB 3 MODELO PREDICTIVO
# ─────────────────────────────────────────────────────────────
@app.callback(Output("g-modelos","figure"), Input("tabs","value"))
def go_modelos(tab):
    if tab != "tab-modelo": return go.Figure()
    d = MODELOS_DF.copy().sort_values("mae", ascending=False)
    colors_mae  = [C["a3"] if b else C["a1"] for b in d["mejor"]]
    colors_mape = [C["a3"] if b else C["a2"] for b in d["mejor"]]
    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=d["modelo"], x=d["mae"], orientation="h", name="MAE",
        marker=dict(color=colors_mae, opacity=0.85, line=dict(width=0)),
        text=[f" {v:.2f}" for v in d["mae"]], textposition="outside",
        textfont=dict(size=9,color=C["sub"]),
        hovertemplate="<b>%{y}</b><br>MAE: %{x:.2f}<extra></extra>"))
    fig.add_trace(go.Bar(
        y=d["modelo"], x=d["mape"]/2, orientation="h", name="MAPE/2 (escala)",
        marker=dict(color=colors_mape, opacity=0.45, line=dict(width=0)),
        hovertemplate="<b>%{y}</b><br>MAPE: %{customdata:.1f}%<extra></extra>",
        customdata=d["mape"]))
    fig = cb(fig, "Comparación de 5 Modelos — MAE y MAPE (menor = mejor)", 360)
    fig.update_layout(barmode="overlay",
                      legend=dict(orientation="h", x=0, y=1.12, font=dict(size=10)))
    fig.update_xaxes(showgrid=True, gridwidth=1, title_text="MAE (licitaciones)")
    fig.update_yaxes(showgrid=False)
    return fig

@app.callback(Output("g-reglas","figure"), Input("tabs","value"))
def go_reglas(tab):
    if tab != "tab-modelo": return go.Figure()
    d = FORECAST_MKT.copy()
    col = [C["red"] if t == "CRITICO" else C["green"] for t in d["tipo"]]
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=d["lbl"], y=d["factor"], name="Factor corrección",
        marker=dict(color=col, opacity=0.85, line=dict(width=0)),
        text=[f"{v:.3f}" for v in d["factor"]], textposition="outside",
        textfont=dict(size=9,color=C["sub"]),
        hovertemplate="<b>%{x}</b><br>Factor: %{y:.3f}<br>Tipo: " +
                      "<extra></extra>"))
    for i, row in d.iterrows():
        fig.add_annotation(x=row["lbl"], y=0.02, text=row["tipo"],
            showarrow=False, font=dict(size=8,
            color=C["red"] if row["tipo"]=="CRITICO" else C["green"]),
            xanchor="center")
    fig.add_hline(y=1.0, line_dash="dot", line_color=C["border"],
        annotation_text="neutro=1.0", annotation_font_color=C["sub"])
    fig = cb(fig, "Reglas de Negocio — Factor de Corrección por Mes", 360)
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=True, gridwidth=1, range=[0.75, 1.20])
    return fig

@app.callback(Output("g-forecast2026","figure"), Input("tabs","value"))
def go_forecast2026(tab):
    if tab != "tab-modelo": return go.Figure()
    d   = FORECAST_MKT.copy()
    col = [C["red"] if t == "CRITICO" else C["a1"] for t in d["tipo"]]
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=d["lbl"], y=d["n"], marker=dict(color=col, opacity=0.88, line=dict(width=0)),
        text=[f"{v:.0f}" for v in d["n"]], textposition="outside",
        textfont=dict(size=11,color=C["txt"],family=FONT),
        hovertemplate="<b>%{x} 2026</b><br>%{y:.1f} licitaciones<extra></extra>",
        name="Forecast M5"))
    avg = d["n"].mean()
    fig.add_hline(y=avg, line_dash="dot", line_color=C["a2"],
        annotation_text=f"Prom: {avg:.0f}", annotation_font_color=C["a2"], annotation_font_size=9)
    for _, row in d[d["tipo"]=="CRITICO"].iterrows():
        fig.add_annotation(x=row["lbl"], y=row["n"]+4, text="CRÍTICO",
            showarrow=False, font=dict(size=9,color=C["red"],family=FONT),
            bgcolor="rgba(239,68,68,0.15)", bordercolor=C["red"], borderwidth=1)
    fig = cb(fig, "Forecast 2026 — Mercado Total · Modelo 5 Híbrido", 340)
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=True, gridwidth=1,
                     title_text="Licitaciones", title_font=dict(size=9,color=C["sub"]))
    return fig

@app.callback(Output("g-ranking","figure"), Input("tabs","value"))
def go_ranking(tab):
    if tab != "tab-modelo": return go.Figure()
    d = RANKING_COM.copy().sort_values("score")
    colors = [C["yellow"] if str(s).startswith("Alto valor") else C["a1"] for s in d["seg_clean"]]
    fig = go.Figure(go.Bar(
        x=d["score"], y=d["nombre"], orientation="h",
        marker=dict(color=colors, opacity=0.88, line=dict(width=0)),
        text=[f" {v:.3f}" for v in d["score"]], textposition="outside",
        textfont=dict(size=9,color=C["sub"]),
        hovertemplate="<b>%{y}</b><br>Score: %{x:.3f}<extra></extra>"))
    fig.add_vline(x=0.55, line_dash="dot", line_color=C["yellow"],
        annotation_text="Alto valor >0.55",
        annotation_font_color=C["yellow"], annotation_font_size=9)
    fig = cb(fig, "Ranking Comercial Compra Chile — Score Final", 380)
    fig.update_xaxes(showgrid=True, gridwidth=1, range=[0, 0.75])
    fig.update_yaxes(showgrid=False)
    return fig

@app.callback(Output("g-forecast-org","figure"), Input("tabs","value"))
def go_forecast_org(tab):
    if tab != "tab-modelo": return go.Figure()
    d = FORECAST_ORG.copy().sort_values("n")
    grad = [f"rgba(79,142,247,{0.3+0.7*i/max(len(d)-1,1)})" for i in range(len(d))]
    fig = go.Figure(go.Bar(
        x=d["n"], y=d["nombre"], orientation="h",
        marker=dict(color=grad, line=dict(width=0)),
        text=[f" {v:.1f}" for v in d["n"]], textposition="outside",
        textfont=dict(size=9,color=C["sub"]),
        hovertemplate="<b>%{y}</b><br>%{x:.1f} licitaciones 2026<extra></extra>"))
    fig = cb(fig, "Forecast Total 2026 por Organismo (12 meses)", 400)
    fig.update_xaxes(showgrid=True, gridwidth=1,
                     title_text="Licitaciones proyectadas", title_font=dict(size=9,color=C["sub"]))
    fig.update_yaxes(showgrid=False)
    return fig

@app.callback(Output("g-forecast-org-mes","figure"), Input("tabs","value"))
def go_forecast_org_mes(tab):
    if tab != "tab-modelo": return go.Figure()
    top = RANKING_COM.iloc[0]
    d   = FORECAST_ORG_1660.copy()
    col = [C["red"] if t == "CRITICO" else C["a3"] for t in d["tipo"]]
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=d["lbl"], y=d["n"], marker=dict(color=col, opacity=0.85, line=dict(width=0)),
        text=[f"{v:.2f}" for v in d["n"]], textposition="outside",
        textfont=dict(size=10,color=C["txt"]),
        hovertemplate="<b>%{x} 2026</b><br>%{y:.2f} licitaciones<extra></extra>",
        name="Forecast"))
    fig.add_trace(go.Scatter(
        x=d["lbl"], y=d["n"], mode="lines",
        line=dict(color=C["a3"], width=1.5, dash="dot"),
        showlegend=False, hoverinfo="skip"))
    fig.add_hline(y=d["n"].mean(), line_dash="dot", line_color=C["a2"],
        annotation_text=f"Prom: {d['n'].mean():.2f}",
        annotation_font_color=C["a2"], annotation_font_size=9)
    fig = cb(fig,
        f"Forecast Mensual 2026 — {top['nombre']} (cod. {top['cod']}) · Score = {top['score']:.3f}",
        320)
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=True, gridwidth=1,
                     title_text="Licitaciones", title_font=dict(size=9,color=C["sub"]))
    return fig


# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("\n" + "-"*55)
    print("  Dashboard V4 — Compra Chile · Licitaciones")
    print(f"  Cobertura histórica: {RANGO}")
    print(f"  Ranking: {N_ESTRATEGICOS} organismos · df_organizaciones_top.csv")
    print("  Modelo: M5 Híbrido RF + Reglas de Negocio")
    print("-"*55)
    print("  -> http://127.0.0.1:8053")
    print("  Detener: Ctrl+C\n")
    app.run(debug=False, host="127.0.0.1", port=8053)
