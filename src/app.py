import pandas as pd
import numpy as np
import dash
from dash import dcc, html, Input, Output, ctx
import plotly.graph_objects as go

# ── Data ───────────────────────────────────────────────────────
df = pd.read_csv("../data/processed_data.csv")
df["date"] = pd.to_datetime(df["date"])
df = df.sort_values("date")

EVENT_DATE = pd.Timestamp("2021-01-15")

# ── Palette ────────────────────────────────────────────────────
C = {
    "bg":       "#080b10",
    "surface":  "#0f1318",
    "card":     "#13181f",
    "border":   "#1e2530",
    "border2":  "#2a3340",
    "accent":   "#e8c84a",
    "teal":     "#38d9c0",
    "violet":   "#a78bfa",
    "rose":     "#fb7185",
    "orange":   "#fb923c",
    "mint":     "#6ee7b7",
    "text":     "#e2e8f0",
    "muted":    "#64748b",
    "dim":      "#334155",
}

REGION_COLORS = {
    "all":   "#e8c84a",
    "north": "#38d9c0",
    "east":  "#a78bfa",
    "south": "#fb923c",
    "west":  "#6ee7b7",
}

ANIMATIONS_CSS = """
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Mono:wght@300;400;500&display=swap');
* { box-sizing: border-box; }
body { margin:0; background:#080b10; font-family:'DM Mono',monospace; color:#e2e8f0; }

@keyframes slideUp {
    from { opacity:0; transform:translateY(20px); }
    to   { opacity:1; transform:translateY(0); }
}
@keyframes fadeIn {
    from { opacity:0; } to { opacity:1; }
}
@keyframes countUp {
    from { opacity:0; transform:scale(0.85); }
    to   { opacity:1; transform:scale(1); }
}
@keyframes shimmer {
    0%   { background-position:-200% center; }
    100% { background-position: 200% center; }
}

.kpi-card {
    animation: slideUp 0.5s ease both;
    transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
}
.kpi-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 16px 48px rgba(0,0,0,0.6);
    border-color: #2a3340 !important;
}
.kpi-value {
    animation: countUp 0.6s ease both;
}
.chart-card { animation: fadeIn 0.6s ease both; }

.chart-btn {
    transition: all 0.18s ease; cursor:pointer;
    border:1px solid #1e2530; background:#0f1318; color:#64748b;
    font-family:'DM Mono',monospace; font-size:11px; letter-spacing:2px;
    padding:8px 16px; border-radius:6px;
}
.chart-btn:hover { border-color:#2a3340; color:#e2e8f0; background:#13181f; }
.chart-btn.active { background:#e8c84a22; border-color:#e8c84a88; color:#e8c84a; }

.region-btn {
    transition:all 0.18s ease; cursor:pointer;
    border:1px solid #1e2530; background:transparent;
    font-family:'DM Mono',monospace; font-size:11px; letter-spacing:3px;
    padding:8px 18px; border-radius:6px; color:#64748b;
}
.region-btn:hover { color:#e2e8f0; border-color:#2a3340; }

.toggle-row { display:flex; gap:8px; align-items:center; flex-wrap:wrap; }
.divider { width:1px; height:24px; background:#1e2530; margin:0 4px; }

.insight-tag {
    display:inline-flex; align-items:center; gap:6px;
    font-size:11px; letter-spacing:1px; padding:5px 12px;
    border-radius:20px; border:1px solid; animation:fadeIn 0.8s ease both;
}

.topbar-logo {
    background: linear-gradient(90deg,#e8c84a,#38d9c0,#e8c84a);
    background-size:200% auto;
    -webkit-background-clip:text; -webkit-text-fill-color:transparent;
    background-clip:text;
    animation:shimmer 4s linear infinite;
}
"""

# ── App ────────────────────────────────────────────────────────
app = dash.Dash(__name__, suppress_callback_exceptions=True)

app.index_string = f"""<!DOCTYPE html>
<html>
<head>
    {{%metas%}}
    <title>Pink Morsels · Sales Intelligence</title>
    {{%favicon%}}{{%css%}}
    <style>{ANIMATIONS_CSS}</style>
</head>
<body>
    {{%app_entry%}}
    <footer>{{%config%}}{{%scripts%}}{{%renderer%}}</footer>
</body>
</html>"""

# ── Helpers ────────────────────────────────────────────────────
def hex_rgba(h, a=0.10):
    h = h.lstrip("#")
    r,g,b = int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)
    return f"rgba({r},{g},{b},{a})"

def get_filtered(region):
    if region == "all":
        return df.groupby("date")["sales"].sum().reset_index()
    return df[df["region"]==region].groupby("date")["sales"].sum().reset_index()

def fmt_currency(v):
    if v >= 1_000_000: return f"${v/1_000_000:.2f}M"
    if v >= 1_000:     return f"${v/1_000:.1f}K"
    return f"${v:.0f}"

# ── Layout ─────────────────────────────────────────────────────
app.layout = html.Div(style={"minHeight":"100vh","background":C["bg"]}, children=[

    # Top bar
    html.Div(style={
        "borderBottom":f"1px solid {C['border']}","padding":"16px 40px",
        "display":"flex","alignItems":"center","justifyContent":"space-between",
        "background":C["surface"],"position":"sticky","top":"0","zIndex":"100",
    }, children=[
        html.Div(style={"display":"flex","alignItems":"center","gap":"12px"}, children=[
            html.Span("◈", style={"color":C["accent"],"fontSize":"20px"}),
            html.Span("PINK MORSELS", className="topbar-logo",
                      style={"fontWeight":"700","fontSize":"13px","letterSpacing":"6px"}),
            html.Span("/ sales intelligence",
                      style={"fontSize":"11px","color":C["muted"],"letterSpacing":"2px"}),
        ]),
        html.Span(id="last-updated",
                  style={"fontSize":"10px","color":C["muted"],"letterSpacing":"1px"}),
    ]),

    # Body
    html.Div(style={"padding":"36px 40px 60px"}, children=[

        html.Div(style={"marginBottom":"32px"}, children=[
            html.H1("Sales Trend Analysis", style={
                "fontFamily":"'DM Serif Display',Georgia,serif",
                "fontSize":"clamp(26px,4vw,46px)","fontWeight":"400",
                "letterSpacing":"-1px","margin":"0 0 6px","color":C["text"],
            }),
            html.P("Regional performance · Pink Morsels product line · 2020–2021", style={
                "color":C["muted"],"fontSize":"12px","letterSpacing":"1px","margin":"0",
            }),
        ]),

        # KPI row
        html.Div(id="kpi-row", style={
            "display":"grid",
            "gridTemplateColumns":"repeat(auto-fit,minmax(200px,1fr))",
            "gap":"16px","marginBottom":"28px",
        }),

        # Controls
        html.Div(style={
            "background":C["card"],"border":f"1px solid {C['border']}",
            "borderRadius":"12px","padding":"18px 24px","marginBottom":"20px",
            "display":"flex","gap":"20px","flexWrap":"wrap",
            "alignItems":"center","justifyContent":"space-between",
        }, children=[
            html.Div(className="toggle-row", children=[
                html.Span("REGION", style={"fontSize":"10px","letterSpacing":"4px","color":C["muted"],"marginRight":"4px"}),
                *[html.Button(r.upper(), id=f"btn-{r}", className="region-btn", n_clicks=0)
                  for r in ["all","north","east","south","west"]],
            ]),
            html.Div(className="divider"),
            html.Div(className="toggle-row", children=[
                html.Span("CHART", style={"fontSize":"10px","letterSpacing":"4px","color":C["muted"],"marginRight":"4px"}),
                html.Button("LINE",    id="btn-line",    className="chart-btn active", n_clicks=0),
                html.Button("BAR",     id="btn-bar",     className="chart-btn",        n_clicks=0),
                html.Button("SCATTER", id="btn-scatter", className="chart-btn",        n_clicks=0),
            ]),
            html.Div(className="divider"),
            html.Div(className="toggle-row", children=[
                html.Span("OVERLAY", style={"fontSize":"10px","letterSpacing":"4px","color":C["muted"],"marginRight":"4px"}),
                dcc.Checklist(
                    id="overlay-opts",
                    options=[
                        {"label":"  7-day MA ", "value":"ma7"},
                        {"label":"  30-day MA","value":"ma30"},
                        {"label":"  Avg line ", "value":"avg"},
                    ],
                    value=[],
                    inline=True,
                    inputStyle={"marginRight":"5px","accentColor":C["accent"],"cursor":"pointer"},
                    labelStyle={
                        "fontSize":"11px","letterSpacing":"2px","color":C["text"],
                        "marginRight":"16px","cursor":"pointer",
                        "display":"inline-flex","alignItems":"center",
                    },
                ),
            ]),
        ]),

        # Insight bar
        html.Div(id="insight-bar", style={"display":"flex","gap":"10px","flexWrap":"wrap","marginBottom":"20px"}),

        # Main chart
        html.Div(className="chart-card", style={
            "background":C["card"],"border":f"1px solid {C['border']}",
            "borderRadius":"12px","padding":"8px 8px 4px",
            "position":"relative","overflow":"hidden",
        }, children=[
            html.Div(style={
                "position":"absolute","top":"0","left":"0","width":"4px","height":"100%",
                "background":f"linear-gradient(180deg,{C['accent']},{C['teal']})",
                "borderRadius":"12px 0 0 12px",
            }),
            dcc.Graph(id="sales-chart",
                      config={"displayModeBar":True,"displaylogo":False,
                              "modeBarButtonsToRemove":["autoScale2d","lasso2d","select2d"]},
                      style={"height":"460px"}),
        ]),

        # Before / after split
        html.Div(style={"marginTop":"20px"}, children=[
            html.Div(style={"display":"grid","gridTemplateColumns":"1fr 1fr","gap":"16px"}, children=[
                html.Div(id="before-card", style={
                    "background":C["card"],"border":f"1px solid {C['border']}",
                    "borderRadius":"12px","padding":"20px 24px",
                }),
                html.Div(id="after-card", style={
                    "background":C["card"],"border":f"1px solid {C['border']}",
                    "borderRadius":"12px","padding":"20px 24px",
                }),
            ]),
        ]),

        html.Div(style={"marginTop":"20px","display":"flex","gap":"20px","flexWrap":"wrap"}, children=[
            html.Span("▬  Jan 15 2021 event marker", style={"fontSize":"11px","color":C["rose"],"letterSpacing":"1px"}),
            html.Span("Source: processed_data.csv",  style={"fontSize":"11px","color":C["muted"],"letterSpacing":"1px"}),
        ]),
    ]),

    dcc.Store(id="store-region",     data="all"),
    dcc.Store(id="store-chart-type", data="line"),
])


# ── Callbacks ──────────────────────────────────────────────────

@app.callback(
    Output("store-region","data"),
    [Input(f"btn-{r}","n_clicks") for r in ["all","north","east","south","west"]],
    prevent_initial_call=False,
)
def set_region(*args):
    triggered = ctx.triggered_id
    if not triggered: return "all"
    return triggered.replace("btn-","")

@app.callback(
    [Output(f"btn-{r}","className") for r in ["all","north","east","south","west"]],
    Input("store-region","data"),
)
def style_region_btns(region):
    regions = ["all","north","east","south","west"]
    col = REGION_COLORS.get(region, C["accent"])
    styles = []
    for r in regions:
        if r == region:
            styles.append(f"region-btn active")
        else:
            styles.append("region-btn")
    return styles

@app.callback(
    [Output(f"btn-{r}","style") for r in ["all","north","east","south","west"]],
    Input("store-region","data"),
)
def style_region_btn_colors(region):
    regions = ["all","north","east","south","west"]
    result = []
    for r in regions:
        col = REGION_COLORS[r]
        if r == region:
            result.append({
                "color": col,
                "borderColor": col,
                "background": hex_rgba(col, 0.12),
            })
        else:
            result.append({})
    return result

@app.callback(
    Output("store-chart-type","data"),
    Input("btn-line","n_clicks"),
    Input("btn-bar","n_clicks"),
    Input("btn-scatter","n_clicks"),
    prevent_initial_call=False,
)
def set_chart_type(l,b,s):
    triggered = ctx.triggered_id
    mapping = {"btn-line":"line","btn-bar":"bar","btn-scatter":"scatter"}
    return mapping.get(triggered,"line")

@app.callback(
    Output("btn-line","className"),
    Output("btn-bar","className"),
    Output("btn-scatter","className"),
    Input("store-chart-type","data"),
)
def style_chart_btns(ct):
    return ["chart-btn active" if t==ct else "chart-btn" for t in ["line","bar","scatter"]]


@app.callback(
    Output("sales-chart","figure"),
    Output("kpi-row","children"),
    Output("insight-bar","children"),
    Output("before-card","children"),
    Output("after-card","children"),
    Output("last-updated","children"),
    Input("store-region","data"),
    Input("store-chart-type","data"),
    Input("overlay-opts","value"),
)
def render_all(region, chart_type, overlays):
    filtered = get_filtered(region)
    color    = REGION_COLORS[region]
    overlays = overlays or []

    total   = filtered["sales"].sum()
    avg_day = filtered["sales"].mean()
    peak    = filtered["sales"].max()
    peak_dt = filtered.loc[filtered["sales"].idxmax(), "date"]

    before_s = filtered[filtered["date"] <  EVENT_DATE]["sales"]
    after_s  = filtered[filtered["date"] >= EVENT_DATE]["sales"]
    pct_chg  = ((after_s.mean() - before_s.mean()) / before_s.mean() * 100) \
               if len(before_s) and len(after_s) else 0

    # ── KPI cards ────────────────────────────────────────
    kpi_data = [
        ("TOTAL REVENUE",  fmt_currency(total),    C["accent"],                      "0.1s", "all time"),
        ("DAILY AVERAGE",  fmt_currency(avg_day),  C["teal"],                        "0.2s", "per day"),
        ("PEAK SALES",     fmt_currency(peak),     C["violet"],                      "0.3s", peak_dt.strftime("%b %d '%y")),
        ("POST-EVENT Δ",   f"{pct_chg:+.1f}%",    C["rose"] if pct_chg<0 else C["mint"], "0.4s", "vs pre-event avg"),
    ]

    kpi_cards = []
    for label, value, col, delay, sub in kpi_data:
        kpi_cards.append(html.Div(className="kpi-card", style={
            "background":C["card"],"border":f"1px solid {C['border']}",
            "borderRadius":"12px","padding":"20px 22px","animationDelay":delay,
        }, children=[
            html.Div(label, style={"fontSize":"10px","letterSpacing":"3px","color":C["muted"],"marginBottom":"10px"}),
            html.Div(value, className="kpi-value", style={
                "fontSize":"clamp(20px,2.5vw,28px)",
                "fontFamily":"'DM Serif Display',Georgia,serif",
                "color":col,"marginBottom":"6px","animationDelay":delay,
            }),
            html.Div(sub, style={"fontSize":"11px","color":C["dim"],"letterSpacing":"1px"}),
            html.Div(style={
                "marginTop":"14px","height":"2px","borderRadius":"2px",
                "background":f"linear-gradient(90deg,{col},{hex_rgba(col,0.1)})",
            }),
        ]))

    # ── Insights ─────────────────────────────────────────
    insights_data = []
    if pct_chg > 5:
        insights_data.append(("↑ Strong post-event growth",    C["mint"],   C["mint"]))
    elif pct_chg < -5:
        insights_data.append(("↓ Post-event decline detected", C["rose"],   C["rose"]))
    else:
        insights_data.append(("→ Stable around event date",    C["teal"],   C["teal"]))

    if peak_dt > EVENT_DATE:
        insights_data.append(("Peak occurred after event",  C["violet"], C["violet"]))
    else:
        insights_data.append(("Peak occurred before event", C["accent"], C["accent"]))

    insight_els = [html.Span(text, className="insight-tag", style={
        "color":col,"borderColor":hex_rgba(bc,0.4),"background":hex_rgba(bc,0.07),
    }) for text,col,bc in insights_data]

    # ── Before/After split cards ──────────────────────────
    def split_card(title, series, accent_col, icon):
        s_avg = series.mean() if len(series) else 0
        s_tot = series.sum()  if len(series) else 0
        s_max = series.max()  if len(series) else 0
        rows  = [("Total",fmt_currency(s_tot)),("Average",fmt_currency(s_avg)),
                 ("Peak",fmt_currency(s_max)),  ("Days",str(len(series)))]
        return [
            html.Div(style={"display":"flex","alignItems":"center","gap":"8px","marginBottom":"14px"}, children=[
                html.Span(icon, style={"color":accent_col,"fontSize":"16px"}),
                html.Span(title, style={"fontSize":"11px","letterSpacing":"3px","color":accent_col,"fontWeight":"600"}),
            ]),
            *[html.Div(style={
                "display":"flex","justifyContent":"space-between",
                "padding":"7px 0","borderBottom":f"1px solid {C['border']}",
            }, children=[
                html.Span(k, style={"fontSize":"11px","color":C["muted"],"letterSpacing":"1px"}),
                html.Span(v, style={"fontSize":"12px","color":C["text"],"fontFamily":"'DM Serif Display',serif"}),
            ]) for k,v in rows],
        ]

    before_children = split_card("PRE-EVENT",  before_s, C["teal"],   "◐")
    after_children  = split_card("POST-EVENT", after_s,  C["orange"], "◑")

    # ── Figure ───────────────────────────────────────────
    fig = go.Figure()

    if chart_type == "line":
        fig.add_trace(go.Scatter(
            x=filtered["date"], y=filtered["sales"],
            mode="lines", fill="tozeroy",
            fillcolor=hex_rgba(color,0.07),
            line=dict(color=color,width=2.5,shape="spline",smoothing=1.2),
            name="Sales",
            hovertemplate="<b>%{x|%b %d, %Y}</b><br>$%{y:,.0f}<extra></extra>",
        ))
    elif chart_type == "bar":
        fig.add_trace(go.Bar(
            x=filtered["date"], y=filtered["sales"],
            marker_color=hex_rgba(color,0.7),
            marker_line_color=color, marker_line_width=0.5,
            name="Sales",
            hovertemplate="<b>%{x|%b %d, %Y}</b><br>$%{y:,.0f}<extra></extra>",
        ))
    else:
        fig.add_trace(go.Scatter(
            x=filtered["date"], y=filtered["sales"],
            mode="markers",
            marker=dict(color=color,size=5,opacity=0.7,
                        line=dict(color=hex_rgba(color,0.3),width=1)),
            name="Sales",
            hovertemplate="<b>%{x|%b %d, %Y}</b><br>$%{y:,.0f}<extra></extra>",
        ))

    if "ma7" in overlays:
        ma7 = filtered["sales"].rolling(7, min_periods=1).mean()
        fig.add_trace(go.Scatter(
            x=filtered["date"], y=ma7, mode="lines", name="7-day MA",
            line=dict(color=C["teal"],width=1.5),
            hovertemplate="7d MA: $%{y:,.0f}<extra></extra>",
        ))

    if "ma30" in overlays:
        ma30 = filtered["sales"].rolling(30, min_periods=1).mean()
        fig.add_trace(go.Scatter(
            x=filtered["date"], y=ma30, mode="lines", name="30-day MA",
            line=dict(color=C["violet"],width=2),
            hovertemplate="30d MA: $%{y:,.0f}<extra></extra>",
        ))

    if "avg" in overlays:
        avg_val = filtered["sales"].mean()
        fig.add_hline(
            y=avg_val, line_dash="dot", line_color=C["accent"], line_width=1.2,
            annotation_text=f"Avg {fmt_currency(avg_val)}",
            annotation_font_color=C["accent"], annotation_font_size=11,
            annotation_position="right",
        )

    fig.add_vline(
        x=EVENT_DATE.timestamp()*1000,
        line_dash="dot", line_color=C["rose"], line_width=1.5,
        annotation_text="Event · Jan 15",
        annotation_font_color=C["rose"], annotation_font_size=11,
        annotation_position="top right",
    )

    fig.add_vrect(
        x0=EVENT_DATE.timestamp()*1000,
        x1=filtered["date"].max().timestamp()*1000,
        fillcolor=hex_rgba(C["rose"],0.03), line_width=0, layer="below",
    )

    fig.update_layout(
        title=dict(
            text=(f"<b>Sales Over Time</b>  "
                  f"<span style='font-size:12px;color:{C['muted']}'>"
                  f"{'All Regions' if region=='all' else region.capitalize()}</span>"),
            font=dict(family="DM Serif Display,Georgia,serif",size=20,color=C["text"]),
            x=0.02, xanchor="left", pad=dict(t=10,l=12),
        ),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Mono,monospace",color=C["muted"]),
        xaxis=dict(showgrid=False,zeroline=False,tickfont=dict(size=11),
                   tickformat="%b '%y",tickcolor=C["border"],linecolor=C["border"]),
        yaxis=dict(showgrid=True,gridcolor=C["border"],gridwidth=1,
                   zeroline=False,tickfont=dict(size=11),tickformat="$,"),
        margin=dict(l=55,r=40,t=65,b=45),
        hovermode="x unified",
        hoverlabel=dict(bgcolor=C["surface"],bordercolor=C["border"],
                        font=dict(family="DM Mono,monospace",size=12,color=C["text"])),
        legend=dict(bgcolor="rgba(0,0,0,0)",bordercolor=C["border"],borderwidth=1,
                    font=dict(size=11,color=C["muted"]),
                    orientation="h",yanchor="bottom",y=1.02,xanchor="right",x=1),
        transition=dict(duration=400,easing="cubic-in-out"),
    )

    last_date = filtered["date"].max().strftime("%b %d, %Y") if len(filtered) else "—"
    return fig, kpi_cards, insight_els, before_children, after_children, f"Data through {last_date}"


if __name__ == "__main__":
    app.run(debug=True)