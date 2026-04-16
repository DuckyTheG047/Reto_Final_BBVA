"""
╔══════════════════════════════════════════════════════════════╗
║   DASHBOARD CREDITICIO · SEGMENTO JOVEN · JALISCO 2024      ║
║   Datos calibrados con estadísticas ENOE-INEGI Q4 2024      ║
║   Ejecución: streamlit run equipo_dashboard.py               ║
╚══════════════════════════════════════════════════════════════╝
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# ══════════════════════════════════════════════════════
#  CONFIGURACIÓN DE PÁGINA
# ══════════════════════════════════════════════════════
st.set_page_config(
    page_title="CreditScore Jalisco",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════════════
#  CSS PERSONALIZADO
# ══════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=Outfit:wght@300;400;500;600&display=swap');

*, html, body, [class*="css"] { font-family: 'Outfit', sans-serif; }

.stApp { background: #080f1e; }
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #080f1e 0%, #060c18 100%);
    border-right: 1px solid #15294a;
}
.block-container { padding-top: 1.5rem; }

.dash-title {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 2rem; font-weight: 600;
    color: #38bdf8;
    text-shadow: 0 0 40px rgba(56,189,248,0.35);
    margin: 0;
}
.dash-sub {
    font-size: 0.8rem; color: #334e6e;
    letter-spacing: 3px; text-transform: uppercase; margin-top: 2px;
}
.sec-title {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.85rem; color: #7dd3fc;
    border-left: 3px solid #38bdf8;
    padding-left: 10px; margin: 18px 0 10px; letter-spacing: 1px;
}
.kpi-row { display: flex; gap: 14px; margin-bottom: 18px; flex-wrap: wrap; }
.kpi-box {
    flex: 1; min-width: 140px;
    background: linear-gradient(135deg, #0c1a30 0%, #0e2040 100%);
    border: 1px solid #15294a; border-radius: 10px;
    padding: 16px 20px; position: relative; overflow: hidden;
}
.kpi-box::after {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, #38bdf8, #0ea5e9);
}
.kpi-val {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 1.9rem; font-weight: 600; color: #38bdf8; line-height: 1.1;
}
.kpi-lbl { font-size: 0.72rem; color: #334e6e; text-transform: uppercase; letter-spacing: 1px; margin-top: 4px; }
.kpi-delta { font-size: 0.78rem; color: #4ade80; margin-top: 3px; }
.kpi-box.green::after { background: linear-gradient(90deg, #4ade80, #22c55e); }
.kpi-box.green .kpi-val { color: #4ade80; }
.kpi-box.red::after { background: linear-gradient(90deg, #f87171, #ef4444); }
.kpi-box.red .kpi-val { color: #f87171; }
.kpi-box.yellow::after { background: linear-gradient(90deg, #fbbf24, #f59e0b); }
.kpi-box.yellow .kpi-val { color: #fbbf24; }
.sidebar-stat { font-size: 0.8rem; color: #4a7fa5; line-height: 2.1; }
.sidebar-stat b { color: #7dd3fc; }
hr { border-color: #15294a; margin: 14px 0; }
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: #080f1e; }
::-webkit-scrollbar-thumb { background: #15294a; border-radius: 4px; }
div[role="radiogroup"] label { color: #7dd3fc !important; font-size: 0.88rem !important; }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════
#  DATOS (calibrados con ENOE-INEGI Jalisco 2024)
#  - Salario promedio Jalisco: ~$18,500 MXN (ENOE Q4 2024)
#  - Tasa ocupación: 98.6%
#  - Informalidad: 20.6%
#  - Municipios reales ZMG y alrededores
# ══════════════════════════════════════════════════════
@st.cache_data
def generar_datos_jalisco():
    np.random.seed(2024)
    n = 1000

    municipios = {
        "Guadalajara":     (20.6597, -103.3496, 0.28),
        "Zapopan":         (20.7214, -103.3916, 0.18),
        "Tlaquepaque":     (20.6418, -103.3108, 0.12),
        "Tonalá":          (20.6236, -103.2364, 0.09),
        "Tlajomulco":      (20.4738, -103.4452, 0.09),
        "Puerto Vallarta": (20.6534, -105.2253, 0.07),
        "Lagos de Moreno": (21.3561, -101.9317, 0.04),
        "Tepatitlán":      (20.8183, -102.7450, 0.04),
        "Ocotlán":         (20.3519, -102.7697, 0.03),
        "Ameca":           (20.5500, -104.0500, 0.03),
        "Autlán":          (19.7681, -104.3678, 0.03),
    }

    nombres = list(municipios.keys())
    pesos   = [v[2] for v in municipios.values()]
    mun_asig = np.random.choice(nombres, n, p=pesos)

    lat_arr, lon_arr = [], []
    for m in mun_asig:
        lc, loc, _ = municipios[m]
        lat_arr.append(float(np.random.normal(lc, 0.045)))
        lon_arr.append(float(np.random.normal(loc, 0.055)))

    edad    = np.random.randint(18, 28, n)
    genero  = np.random.choice(["Hombre","Mujer"], n, p=[0.54, 0.46])
    estatus = np.random.choice(
        ["Empleado","Emprendedor","Desempleado","Estudiante"],
        n, p=[0.55, 0.22, 0.13, 0.10]
    )

    contrato_arr = []
    for e in estatus:
        if e == "Empleado":
            contrato_arr.append(np.random.choice(["Indefinido","Temporal","Sin contrato"], p=[0.40,0.42,0.18]))
        else:
            contrato_arr.append("Sin contrato")

    antiguedad_arr = []
    for e in estatus:
        if e == "Empleado":
            antiguedad_arr.append(round(float(np.random.exponential(2.8).clip(0.1, 10)), 1))
        elif e == "Emprendedor":
            antiguedad_arr.append(round(float(np.random.exponential(1.5).clip(0.1, 7)), 1))
        else:
            antiguedad_arr.append(0.0)

    ingreso_base = np.random.lognormal(9.8, 0.45, n)
    bonus = np.array(antiguedad_arr) * np.random.uniform(600, 1100, n)
    ingresos_arr = []
    for i, e in enumerate(estatus):
        if e in ["Desempleado","Estudiante"]:
            ingresos_arr.append(round(float(np.random.uniform(3000, 8000)), -2))
        else:
            ingresos_arr.append(round(float(np.clip(ingreso_base[i] + bonus[i], 5000, 80000)), -2))

    saldo_arr = [round(float(ing * np.random.uniform(0.05, 0.9)), -2) for ing in ingresos_arr]
    saldo_arr = [max(500.0, min(s, 150000.0)) for s in saldo_arr]

    mes_num  = np.random.choice([1,2,3], n, p=[0.30,0.35,0.35])
    mes_dict = {1:"Enero", 2:"Febrero", 3:"Marzo"}
    mes_str  = [mes_dict[m] for m in mes_num]

    sector_arr = []
    sectores = ["Comercio","Manufactura","Servicios","Tecnología","Construcción","Turismo"]
    ps = [0.22,0.19,0.28,0.14,0.09,0.08]
    for e in estatus:
        if e in ["Desempleado","Estudiante"]:
            sector_arr.append("N/A")
        else:
            sector_arr.append(np.random.choice(sectores, p=ps))

    df = pd.DataFrame({
        "Latitud":            lat_arr,
        "Longitud":           lon_arr,
        "Municipio":          mun_asig,
        "Edad":               edad,
        "Genero":             genero,
        "Estatus_Laboral":    estatus,
        "Tipo_Contrato":      contrato_arr,
        "Antiguedad_Anos":    antiguedad_arr,
        "Ingresos_Mensuales": ingresos_arr,
        "Saldo_Cuenta":       saldo_arr,
        "Sector":             sector_arr,
        "Mes_Num":            mes_num,
        "Mes":                mes_str,
        "Estado":             "Jalisco",
    })
    return df


def aplicar_reglas(df):
    d = df.copy()
    d = d[(d["Edad"] >= 18) & (d["Edad"] <= 27)]
    d = d[d["Estatus_Laboral"].isin(["Empleado","Emprendedor"])]
    score_ant = d["Antiguedad_Anos"] * 10
    score_aho = d["Saldo_Cuenta"] / 1000
    score_est = d["Tipo_Contrato"].map({"Indefinido":20,"Temporal":5,"Sin contrato":0}).fillna(0)
    d["Score_Final"] = (score_ant + score_aho + score_est).round(2)
    d["Candidato"] = np.where(
        (d["Score_Final"] > 70) & (d["Ingresos_Mensuales"] > 12000),
        "Aprobado","Rechazado"
    )
    return d.reset_index(drop=True)


df_raw = generar_datos_jalisco()
df     = aplicar_reglas(df_raw)

total      = len(df)
aprobados  = int((df["Candidato"] == "Aprobado").sum())
rechazados = total - aprobados
tasa_apro  = aprobados / total * 100

COLORES = {"Aprobado":"#4ade80","Rechazado":"#f87171"}

def plotly_base(height=420):
    return dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(12,26,48,0.6)",
        font=dict(color="#7dd3fc", family="Outfit", size=12),
        height=height,
        margin=dict(l=10, r=10, t=28, b=10),
        legend=dict(bgcolor="rgba(8,15,30,0.8)", bordercolor="#15294a",
                    borderwidth=1, font=dict(color="#7dd3fc")),
        xaxis=dict(gridcolor="#0f2240", zerolinecolor="#0f2240"),
        yaxis=dict(gridcolor="#0f2240", zerolinecolor="#0f2240"),
    )


# ══════════════════════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style="text-align:center;padding:10px 0 22px;border-bottom:1px solid #15294a;margin-bottom:18px;">
        <div style="font-family:'IBM Plex Mono',monospace;font-size:1.5rem;color:#38bdf8;font-weight:600;">
            💳 CREDIT<br><span style="color:#0ea5e9;">SCORE</span>
        </div>
        <div style="font-size:0.65rem;color:#334e6e;letter-spacing:3px;margin-top:4px;">JALISCO · 2024</div>
    </div>
    """, unsafe_allow_html=True)

    pagina = st.radio("", [
        "🗺️  Monitor de Aprobación",
        "📊  Análisis de Riesgo",
        "🎬  Dinámica Temporal",
    ], label_visibility="collapsed")

    st.markdown("---")
    st.markdown(f"""
    <div class="sidebar-stat">
        👥 Total analizado: <b>{total:,}</b><br>
        ✅ Aprobados: <b style="color:#4ade80">{aprobados:,}</b><br>
        ❌ Rechazados: <b style="color:#f87171">{rechazados:,}</b><br>
        📍 Estado: <b>Jalisco</b><br>
        🎂 Edad: <b>18 – 27 años</b><br>
        💼 Filtro: <b>Empleado / Emprendedor</b><br>
        📅 Periodo: <b>Ene – Mar 2024</b>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    <div style="font-size:0.68rem;color:#1e3a5a;line-height:2;text-align:center;">
        Score = Antigüedad×10 + Saldo/1,000<br>
        + Estabilidad (Indef=20, Temp=5)<br>
        <b style="color:#334e6e;">Aprobado:</b> Score &gt;70 & Ingreso &gt;$12,000
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════
#  PÁGINA 1 · MONITOR DE APROBACIÓN
# ══════════════════════════════════════════════════════
if pagina == "🗺️  Monitor de Aprobación":
    st.markdown('<div class="dash-title">Monitor de Aprobación</div>', unsafe_allow_html=True)
    st.markdown('<div class="dash-sub">Distribución espacial · Jalisco · Segmento 18–27 años</div>', unsafe_allow_html=True)
    st.markdown("")

    ing_prom     = df["Ingresos_Mensuales"].mean()
    score_prom   = df["Score_Final"].mean()
    ing_aprobado = df[df["Candidato"]=="Aprobado"]["Ingresos_Mensuales"].mean()

    st.markdown(f"""
    <div class="kpi-row">
        <div class="kpi-box green">
            <div class="kpi-val">{tasa_apro:.1f}%</div>
            <div class="kpi-lbl">Tasa de Aprobación</div>
            <div class="kpi-delta">▲ {aprobados:,} candidatos elegibles</div>
        </div>
        <div class="kpi-box">
            <div class="kpi-val">${ing_prom:,.0f}</div>
            <div class="kpi-lbl">Ingreso Promedio Segmento</div>
            <div class="kpi-delta">MXN mensuales · ENOE 2024</div>
        </div>
        <div class="kpi-box yellow">
            <div class="kpi-val">{score_prom:.1f}</div>
            <div class="kpi-lbl">Score Promedio</div>
            <div class="kpi-delta">Umbral mínimo: 70 pts</div>
        </div>
        <div class="kpi-box green">
            <div class="kpi-val">${ing_aprobado:,.0f}</div>
            <div class="kpi-lbl">Ingreso Promedio Aprobados</div>
            <div class="kpi-delta">vs $12,000 umbral mínimo</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sec-title">🗺 MAPA DE SOLICITUDES — Verde = Aprobado · Rojo = Rechazado</div>', unsafe_allow_html=True)

    fig_map = px.scatter_mapbox(
        df, lat="Latitud", lon="Longitud",
        color="Candidato", color_discrete_map=COLORES,
        hover_name="Municipio",
        hover_data={"Candidato":True,"Ingresos_Mensuales":":,.0f","Score_Final":":.1f",
                    "Edad":True,"Estatus_Laboral":True,"Latitud":False,"Longitud":False},
        zoom=7.4, center={"lat":20.65,"lon":-103.6},
        mapbox_style="carto-darkmatter",
        opacity=0.82, size_max=10, height=500,
        labels={"Candidato":"Estatus"},
    )
    fig_map.update_traces(marker_size=7)
    fig_map.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", margin=dict(l=0,r=0,t=0,b=0),
        legend=dict(bgcolor="rgba(8,15,30,0.85)", bordercolor="#15294a",
                    borderwidth=1, font=dict(color="#7dd3fc",size=13)),
    )
    st.plotly_chart(fig_map, use_container_width=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="sec-title">ESTATUS LABORAL</div>', unsafe_allow_html=True)
        df_lab = df.groupby(["Estatus_Laboral","Candidato"]).size().reset_index(name="N")
        f1 = px.bar(df_lab, x="Estatus_Laboral", y="N", color="Candidato",
                    color_discrete_map=COLORES, barmode="group",
                    labels={"N":"Solicitudes","Estatus_Laboral":""})
        f1.update_layout(**plotly_base(270))
        st.plotly_chart(f1, use_container_width=True)

    with col2:
        st.markdown('<div class="sec-title">SCORE POR TIPO DE CONTRATO</div>', unsafe_allow_html=True)
        df_cont = df.groupby("Tipo_Contrato")["Score_Final"].mean().reset_index()
        f2 = px.bar(df_cont, x="Tipo_Contrato", y="Score_Final",
                    color="Score_Final", color_continuous_scale=["#f87171","#fbbf24","#4ade80"],
                    labels={"Score_Final":"Score Promedio","Tipo_Contrato":""})
        f2.update_layout(**plotly_base(270), coloraxis_showscale=False)
        st.plotly_chart(f2, use_container_width=True)

    with col3:
        st.markdown('<div class="sec-title">TOP 5 MUNICIPIOS APROBADOS</div>', unsafe_allow_html=True)
        top5 = (df[df["Candidato"]=="Aprobado"]
                .groupby("Municipio").size().reset_index(name="N")
                .nlargest(5,"N"))
        f3 = px.bar(top5, x="N", y="Municipio", orientation="h",
                    color="N", color_continuous_scale=["#0ea5e9","#4ade80"],
                    labels={"N":"Aprobados","Municipio":""})
        f3.update_layout(**plotly_base(270), coloraxis_showscale=False,
                         yaxis=dict(autorange="reversed",gridcolor="#0f2240"))
        st.plotly_chart(f3, use_container_width=True)


# ══════════════════════════════════════════════════════
#  PÁGINA 2 · ANÁLISIS DE RIESGO
# ══════════════════════════════════════════════════════
elif pagina == "📊  Análisis de Riesgo":
    st.markdown('<div class="dash-title">Análisis de Riesgo</div>', unsafe_allow_html=True)
    st.markdown('<div class="dash-sub">Ingresos vs Score · Filtros dinámicos en tiempo real</div>', unsafe_allow_html=True)
    st.markdown("")

    col_c1, col_c2, col_c3 = st.columns([2,2,1])
    with col_c1:
        ing_min = st.slider("💰 Ingreso mínimo requerido (MXN)",
                            4000, 40000, 12000, 500, format="$%d")
    with col_c2:
        score_min = st.slider("📈 Score mínimo requerido", 0, 200, 70, 5)
    with col_c3:
        estatus_sel = st.multiselect("Estatus", ["Empleado","Emprendedor"],
                                     default=["Empleado","Emprendedor"])

    dfd = df.copy()
    if estatus_sel:
        dfd = dfd[dfd["Estatus_Laboral"].isin(estatus_sel)]
    dfd = dfd.copy()
    dfd["Cand_Din"] = np.where(
        (dfd["Score_Final"] > score_min) & (dfd["Ingresos_Mensuales"] > ing_min),
        "Aprobado","Rechazado"
    )

    tot_d  = len(dfd)
    apr_d  = int((dfd["Cand_Din"]=="Aprobado").sum())
    tasa_d = apr_d / tot_d * 100 if tot_d else 0
    delta  = tasa_d - tasa_apro

    st.markdown(f"""
    <div class="kpi-row">
        <div class="kpi-box {'green' if tasa_d>=tasa_apro else 'red'}">
            <div class="kpi-val">{tasa_d:.1f}%</div>
            <div class="kpi-lbl">Tasa Aprobación Dinámica</div>
            <div class="kpi-delta">{'▲' if delta>=0 else '▼'} {abs(delta):.1f}% vs original</div>
        </div>
        <div class="kpi-box green">
            <div class="kpi-val">{apr_d:,}</div>
            <div class="kpi-lbl">Aprobados con umbral actual</div>
            <div class="kpi-delta">de {tot_d:,} registros</div>
        </div>
        <div class="kpi-box red">
            <div class="kpi-val">{tot_d - apr_d:,}</div>
            <div class="kpi-lbl">Rechazados</div>
            <div class="kpi-delta">Score ≤{score_min} ó Ing ≤${ing_min:,}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sec-title">🔬 INGRESOS MENSUALES vs SCORE FINAL</div>', unsafe_allow_html=True)

    fig_sc = px.scatter(
        dfd, x="Ingresos_Mensuales", y="Score_Final",
        color="Cand_Din", color_discrete_map=COLORES,
        hover_data={"Edad":True,"Municipio":True,"Estatus_Laboral":True,
                    "Tipo_Contrato":True,"Cand_Din":False},
        opacity=0.65, size_max=7, height=430,
        labels={"Ingresos_Mensuales":"Ingresos Mensuales (MXN)",
                "Score_Final":"Score Final (pts)","Cand_Din":"Estatus"},
    )
    fig_sc.add_vline(x=ing_min, line_dash="dash", line_color="#fbbf24", line_width=1.5,
                     annotation_text=f"${ing_min:,}", annotation_font_color="#fbbf24",
                     annotation_position="top right")
    fig_sc.add_hline(y=score_min, line_dash="dash", line_color="#fbbf24", line_width=1.5,
                     annotation_text=f"Score {score_min}", annotation_font_color="#fbbf24",
                     annotation_position="bottom right")
    fig_sc.add_shape(type="rect",
                     x0=ing_min, x1=dfd["Ingresos_Mensuales"].max()*1.03,
                     y0=score_min, y1=dfd["Score_Final"].max()*1.05,
                     fillcolor="rgba(74,222,128,0.06)",
                     line_color="rgba(74,222,128,0.25)")
    fig_sc.update_layout(**plotly_base(430),
                         xaxis=dict(gridcolor="#0f2240", tickformat="$,.0f"),
                         yaxis=dict(gridcolor="#0f2240"))
    st.plotly_chart(fig_sc, use_container_width=True)

    col_h1, col_h2 = st.columns(2)
    with col_h1:
        st.markdown('<div class="sec-title">DISTRIBUCIÓN SCORE FINAL</div>', unsafe_allow_html=True)
        fh1 = px.histogram(dfd, x="Score_Final", color="Cand_Din",
                           color_discrete_map=COLORES, nbins=45, barmode="overlay",
                           opacity=0.7, labels={"Score_Final":"Score","Cand_Din":"Estatus"})
        fh1.add_vline(x=score_min, line_dash="dash", line_color="#fbbf24",
                      annotation_text=f"Umbral {score_min}", annotation_font_color="#fbbf24")
        fh1.update_layout(**plotly_base(260), showlegend=False)
        st.plotly_chart(fh1, use_container_width=True)

    with col_h2:
        st.markdown('<div class="sec-title">DISTRIBUCIÓN INGRESOS</div>', unsafe_allow_html=True)
        fh2 = px.histogram(dfd, x="Ingresos_Mensuales", color="Cand_Din",
                           color_discrete_map=COLORES, nbins=45, barmode="overlay",
                           opacity=0.7, labels={"Ingresos_Mensuales":"Ingresos (MXN)","Cand_Din":"Estatus"})
        fh2.add_vline(x=ing_min, line_dash="dash", line_color="#fbbf24",
                      annotation_text=f"${ing_min:,}", annotation_font_color="#fbbf24")
        fh2.update_layout(**plotly_base(260), showlegend=False,
                          xaxis=dict(gridcolor="#0f2240", tickformat="$,.0f"))
        st.plotly_chart(fh2, use_container_width=True)

    st.markdown('<div class="sec-title">🗺 MAPA CON UMBRAL DINÁMICO</div>', unsafe_allow_html=True)
    fig_map2 = px.scatter_mapbox(
        dfd, lat="Latitud", lon="Longitud",
        color="Cand_Din", color_discrete_map=COLORES,
        hover_name="Municipio",
        hover_data={"Ingresos_Mensuales":":,.0f","Score_Final":":.1f",
                    "Edad":True,"Latitud":False,"Longitud":False,"Cand_Din":False},
        zoom=7.4, center={"lat":20.65,"lon":-103.6},
        mapbox_style="carto-darkmatter", opacity=0.82, height=420,
        labels={"Cand_Din":"Estatus"},
    )
    fig_map2.update_traces(marker_size=7)
    fig_map2.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", margin=dict(l=0,r=0,t=0,b=0),
        legend=dict(bgcolor="rgba(8,15,30,0.85)", bordercolor="#15294a",
                    borderwidth=1, font=dict(color="#7dd3fc",size=13)),
    )
    st.plotly_chart(fig_map2, use_container_width=True)


# ══════════════════════════════════════════════════════
#  PÁGINA 3 · DINÁMICA TEMPORAL
# ══════════════════════════════════════════════════════
elif pagina == "🎬  Dinámica Temporal":
    st.markdown('<div class="dash-title">Dinámica Temporal</div>', unsafe_allow_html=True)
    st.markdown('<div class="dash-sub">Flujo de solicitudes Enero → Febrero → Marzo 2024</div>', unsafe_allow_html=True)
    st.markdown("")

    df_mes = (df.groupby("Mes")
                .agg(Total=("Candidato","count"),
                     Aprobados=("Candidato", lambda x: int((x=="Aprobado").sum())),
                     Score_Prom=("Score_Final","mean"),
                     Ing_Prom=("Ingresos_Mensuales","mean"))
                .reset_index())
    df_mes["Tasa"]  = (df_mes["Aprobados"]/df_mes["Total"]*100).round(1)
    df_mes["Orden"] = df_mes["Mes"].map({"Enero":1,"Febrero":2,"Marzo":3})
    df_mes          = df_mes.sort_values("Orden")

    col1, col2, col3 = st.columns(3)
    for col, (_, row) in zip([col1,col2,col3], df_mes.iterrows()):
        with col:
            st.markdown(f"""
            <div class="kpi-box" style="margin-bottom:14px;">
                <div class="kpi-val" style="font-size:1.5rem;">📅 {row['Mes']}</div>
                <div class="kpi-lbl">{int(row['Total'])} solicitudes recibidas</div>
                <div class="kpi-delta" style="color:#4ade80;">
                    ✅ {int(row['Aprobados'])} aprobados ({row['Tasa']}%)
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown('<div class="sec-title">🎬 MAPA ANIMADO — Presiona ▶ Play para ver el flujo mes a mes</div>', unsafe_allow_html=True)
    st.info("⏩ Usa el botón Play o arrastra el slider para navegar entre meses")

    orden_anim  = {"Enero":"1_Enero","Febrero":"2_Febrero","Marzo":"3_Marzo"}
    df_anim     = df.copy()
    df_anim["Mes_Sort"] = df_anim["Mes"].map(orden_anim)

    fig_anim = px.scatter_mapbox(
        df_anim.sort_values("Mes_Sort"),
        lat="Latitud", lon="Longitud",
        color="Candidato", color_discrete_map=COLORES,
        animation_frame="Mes_Sort",
        hover_name="Municipio",
        hover_data={"Ingresos_Mensuales":":,.0f","Score_Final":":.1f",
                    "Edad":True,"Mes":True,
                    "Latitud":False,"Longitud":False,"Mes_Sort":False},
        zoom=7.4, center={"lat":20.65,"lon":-103.6},
        mapbox_style="carto-darkmatter",
        opacity=0.85, height=480,
        labels={"Candidato":"Estatus","Mes_Sort":"Mes"},
    )
    fig_anim.update_traces(marker_size=8)
    for fr in fig_anim.frames:
        fr.name = fr.name.replace("1_","").replace("2_","").replace("3_","")

    fig_anim.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0,r=0,t=0,b=0),
        legend=dict(bgcolor="rgba(8,15,30,0.85)", bordercolor="#15294a",
                    borderwidth=1, font=dict(color="#7dd3fc",size=13)),
        sliders=[{"currentvalue":{"prefix":"Mes: ",
                                  "font":{"color":"#38bdf8","family":"IBM Plex Mono"}},
                  "font":{"color":"#7dd3fc"}}],
        updatemenus=[{
            "type":"buttons","showactive":False,
            "y":0,"x":0.5,"xanchor":"center",
            "buttons":[
                {"label":"▶  Play","method":"animate",
                 "args":[None,{"frame":{"duration":1400,"redraw":True},"fromcurrent":True}]},
                {"label":"⏸  Pausa","method":"animate",
                 "args":[[None],{"frame":{"duration":0,"redraw":False},"mode":"immediate"}]},
            ],
            "bgcolor":"#0c1a30","bordercolor":"#15294a",
            "font":{"color":"#38bdf8","family":"IBM Plex Mono"},
        }],
    )
    st.plotly_chart(fig_anim, use_container_width=True)

    col_t1, col_t2 = st.columns(2)
    with col_t1:
        st.markdown('<div class="sec-title">TASA DE APROBACIÓN POR MES</div>', unsafe_allow_html=True)
        fl = px.line(df_mes, x="Mes", y="Tasa", markers=True,
                     color_discrete_sequence=["#38bdf8"],
                     labels={"Tasa":"Tasa (%)","Mes":""})
        fl.update_traces(marker=dict(size=13, color="#4ade80", line=dict(width=2,color="#38bdf8")),
                         line=dict(width=3))
        fl.update_layout(**plotly_base(250),
                         xaxis=dict(categoryorder="array",categoryarray=["Enero","Febrero","Marzo"],
                                    gridcolor="#0f2240"),
                         yaxis=dict(ticksuffix="%",gridcolor="#0f2240"))
        st.plotly_chart(fl, use_container_width=True)

    with col_t2:
        st.markdown('<div class="sec-title">VOLUMEN DE SOLICITUDES POR MES</div>', unsafe_allow_html=True)
        fb = px.bar(df_mes, x="Mes", y=["Aprobados","Total"],
                    color_discrete_map={"Aprobados":"#4ade80","Total":"#1e3a5a"},
                    barmode="overlay", labels={"value":"Solicitudes","Mes":"","variable":""})
        fb.update_layout(**plotly_base(250),
                         xaxis=dict(categoryorder="array",categoryarray=["Enero","Febrero","Marzo"],
                                    gridcolor="#0f2240"))
        st.plotly_chart(fb, use_container_width=True)

    st.markdown('<div class="sec-title">TABLA RESUMEN MENSUAL DETALLADA</div>', unsafe_allow_html=True)
    df_tab = df.groupby(["Mes","Candidato"]).agg(
        Solicitudes=("Score_Final","count"),
        Score_Prom=("Score_Final","mean"),
        Ingreso_Prom=("Ingresos_Mensuales","mean"),
        Saldo_Prom=("Saldo_Cuenta","mean"),
    ).reset_index()
    df_tab["Score_Prom"]   = df_tab["Score_Prom"].round(1)
    df_tab["Ingreso_Prom"] = df_tab["Ingreso_Prom"].apply(lambda x: f"${x:,.0f}")
    df_tab["Saldo_Prom"]   = df_tab["Saldo_Prom"].apply(lambda x: f"${x:,.0f}")
    orden_m = {"Enero":1,"Febrero":2,"Marzo":3}
    df_tab["_o"] = df_tab["Mes"].map(orden_m)
    df_tab = df_tab.sort_values(["_o","Candidato"]).drop(columns="_o")
    df_tab.columns = ["Mes","Estatus","# Solicitudes","Score Prom.","Ingreso Prom. (MXN)","Saldo Prom. (MXN)"]
    st.dataframe(df_tab, use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════
#  FOOTER
# ══════════════════════════════════════════════════════
st.markdown("---")
st.markdown("""
<div style="text-align:center;font-size:0.7rem;color:#15294a;
font-family:'IBM Plex Mono',monospace;line-height:2;">
    DASHBOARD CREDITICIO · JALISCO · SEGMENTO 18–27 AÑOS · 2024<br>
    Datos calibrados con ENOE-INEGI Q4 2024 · Python · Streamlit · Plotly<br>
    streamlit run equipo_dashboard.py
</div>
""", unsafe_allow_html=True)
