"""
Where can I afford to live? - an interactive story for newcomers to the Netherlands.

Run from the project root:   streamlit run app/app.py
Works offline: all data is local and the map has no background tiles.
Every rule (distance, thresholds) comes from helpers.py, the same code the notebooks use.
"""
import base64
import io
import json

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection

from helpers import DATA, DEFAULTS, candidates, load_buurten

st.set_page_config(page_title="Where can I afford to live?", page_icon="🏠", layout="wide")

BLUE, BLUE_LIGHT, GREY, MUTED = "#2a78d6", "#cde2fb", "#c3c2b7", "#52514e"
CARD, INK, GRID, ORANGE = "#fcfcfb", "#0b0b0b", "#e1e0d9", "#eb6834"


def card(fig, **layout):
    """
    Every chart sits on its own light card with dark text, whatever the reader's theme.
    Streamlit's dark theme would otherwise paint white text on these light plots
    (legend and labels disappear). Shown with theme=None so Streamlit does not restyle it.
    """
    fig.update_layout(paper_bgcolor=CARD, plot_bgcolor=CARD, font=dict(color=INK, size=13),
                      legend=dict(font=dict(color=INK, size=13), bgcolor="rgba(252,252,251,0.9)"),
                      hoverlabel=dict(bgcolor="white", font=dict(color=INK)), **layout)
    fig.update_xaxes(color=INK, gridcolor=GRID, zerolinecolor=GRID, title_font=dict(color=INK))
    fig.update_yaxes(color=INK, gridcolor=GRID, zerolinecolor=GRID, title_font=dict(color=INK))
    fig.update_xaxes(automargin=True)
    fig.update_yaxes(automargin=True)
    return fig


def show(fig):
    st.plotly_chart(fig, width="stretch", theme=None)
URBANITY = {1: "very strongly urban", 2: "strongly urban", 3: "moderately urban",
            4: "hardly urban", 5: "not urban"}


# ---------------------------------------------------------------- data
@st.cache_data
def get_data():
    return load_buurten()


@st.cache_resource
def get_geometry():
    """
    Outline and centre of every neighbourhood as plain x/y numbers, prepared once.

    x = longitude * cos(52°) keeps the Netherlands in proportion. cache_resource (not
    cache_data) so this large object is never copied on a rerun.
    """
    with open(DATA / "buurten_simplified.geojson", encoding="utf-8") as f:
        gj = json.load(f)
    k = np.cos(np.radians(52.2))
    rings, centres = {}, {}
    for ft in gj["features"]:
        g = ft["geometry"]
        polys = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
        rs = [np.asarray(p[0], dtype=float) * [k, 1.0] for p in polys]   # outer ring only
        code = ft["properties"]["buurtcode"]
        rings[code] = rs
        big = max(rs, key=len)
        centres[code] = (big[:, 0].mean(), big[:, 1].mean())
    return rings, centres


df = get_data()
towns = sorted(df["municipality"].dropna().unique())
default_town = "Utrecht" if "Utrecht" in towns else towns[0]

# ---------------------------------------------------------------- sidebar: the reader's own limits
if "reset" not in st.session_state:
    st.session_state.reset = 0

with st.sidebar:
    st.header("Your situation")
    k = st.session_state.reset   # changing the key resets every widget to its default
    city = st.selectbox("I work in", towns, index=towns.index(default_town), key=f"city{k}")
    st.caption("Distances are measured from where the people of this municipality live, on average.")

    with st.form("needs"):
        st.subheader("What I need")
        max_km = st.slider("Max straight-line distance (km)", 5, 60, DEFAULTS["max_km"], 5, key=f"km{k}")
        min_rent = st.slider("Min. share of homes rented from a private landlord (%)", 0, 50,
                             DEFAULTS["min_private_rent_pct"], 5, key=f"rent{k}")
        max_urb = st.select_slider("At least this urban", options=[1, 2, 3, 4, 5],
                                   value=DEFAULTS["max_urbanity"],
                                   format_func=lambda v: f"{v} · {URBANITY[v]}", key=f"urb{k}")
        max_shop = st.slider("Large supermarket within (km, by road)", 0.5, 3.0,
                             DEFAULTS["max_supermarket_km"], 0.5, key=f"shop{k}")
        with st.expander("More settings"):
            min_homes = st.slider("Ignore neighbourhoods with fewer homes than", 0, 200,
                                  DEFAULTS["min_dwellings"], 10, key=f"homes{k}")
            incl_est = st.checkbox("Include estimated values", DEFAULTS["include_estimated"], key=f"est{k}",
                                   help="1,842 neighbourhoods had a missing value filled with the "
                                        "municipality median. They are left out by default.")
        st.form_submit_button("Apply", type="primary")
    if st.button("Back to the default view"):
        st.session_state.reset += 1
        st.rerun()

settings = dict(max_km=max_km, min_private_rent_pct=min_rent, max_urbanity=max_urb,
                max_supermarket_km=max_shop, min_dwellings=min_homes, include_estimated=incl_est)
d, s, city_woz = candidates(df, city, **settings)
cand = d[d["candidate"]]
is_default = all(s[key] == DEFAULTS[key] for key in DEFAULTS) and city == default_town

# ---------------------------------------------------------------- intro
st.title("Where can I afford to live?")
st.markdown(
    f"You just got a job in **{city}** and need a place to live. Rents are not published per "
    "neighbourhood, but home values are. This story uses the official CBS figures for all 14,729 "
    "Dutch neighbourhoods to find places that are **lower in value than a typical home in the city** "
    "and where you could **actually rent** from a private landlord."
)
if not is_default:
    st.info("You changed the settings. Use *Back to the default view* in the sidebar to return to the "
            "story as written.")

c1, c2, c3 = st.columns(3)
c1.metric(f"Typical home in {city}", f"€{city_woz:,.0f}k",
          help="Median WOZ value, each home counted once (weighted by number of homes). Measured values only.")
c2.metric("Neighbourhoods that fit", f"{len(cand):,}")
c3.metric("…spread over", f"{cand['municipality'].nunique()} towns")

# ---------------------------------------------------------------- step 1: map
st.header(f"1 · Where is it expensive around {city}?")
colour_by = st.radio("Colour the map by", ["home value", "fits my needs"], horizontal=True)
RAMP = ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"]


@st.cache_resource(max_entries=30)
def build_map(city, settings_items, colour_by):
    """
    The map for one combination of settings, rebuilt only when one of them changes.

    Drawing thousands of detailed shapes in the browser is slow, so the shapes are drawn once
    here as an image (matplotlib) and the browser only gets that image plus one invisible
    point per neighbourhood for the hover text. No internet needed: no background map tiles.
    """
    st_ = dict(settings_items)
    d_, _, _ = candidates(get_data(), city, **st_)
    area = d_[d_["dist_to_city_km"] <= max(st_["max_km"], 10) + 5]
    rings, centres = get_geometry()

    if colour_by == "home value":
        shown = area if st_["include_estimated"] else area[~area["woz_estimated"]]
        edges = np.unique(shown["avg_woz_value_k_eur"].quantile(np.linspace(0, 1, len(RAMP) + 1)).round(0))
        cls = pd.cut(shown["avg_woz_value_k_eur"], edges, include_lowest=True, labels=False)
        colour = pd.Series("#ebeae4", index=area.index)
        colour[shown.index] = [RAMP[int(c)] for c in cls]
        legend = [("#ebeae4", "estimated value (not shown)")] + [
            (RAMP[i], f"€{edges[i]:.0f}k – €{edges[i + 1]:.0f}k") for i in range(len(edges) - 1)]
        legend_title = "average WOZ value"
    else:
        colour = pd.Series(np.where(area["candidate"], BLUE, "#ebeae4"), index=area.index)
        legend, legend_title = [("#ebeae4", "does not fit"), (BLUE, "fits my needs")], ""

    polys, cols = [], []
    for code, c in zip(area["WijkenEnBuurten"], colour):
        for r in rings.get(code, []):
            polys.append(r)
            cols.append(c)
    allxy = np.concatenate(polys)
    x0, y0 = allxy.min(axis=0)
    x1, y1 = allxy.max(axis=0)

    w = 9.0
    h = w * (y1 - y0) / (x1 - x0)
    mfig = plt.figure(figsize=(w, h), dpi=130)
    ax = mfig.add_axes([0, 0, 1, 1])
    ax.add_collection(PolyCollection(polys, facecolors=cols, edgecolors="white", linewidths=0.15))
    ax.set_xlim(x0, x1)
    ax.set_ylim(y0, y1)
    ax.axis("off")
    buf = io.BytesIO()
    mfig.savefig(buf, format="png", facecolor=CARD)
    plt.close(mfig)
    img = "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()

    fig = go.Figure()
    fig.add_layout_image(source=img, xref="x", yref="y", x=x0, y=y1, sizex=x1 - x0, sizey=y1 - y0,
                         sizing="stretch", layer="below")
    hover = (area["region_name"].fillna("") + ", " + area["municipality"] + "<br>WOZ €"
             + area["avg_woz_value_k_eur"].round(0).astype(int).astype(str) + "k"
             + np.where(area["woz_estimated"], " (estimated)", "")
             + "<br>private rental " + area["pct_rent_private"].round(0).astype(int).astype(str) + "%"
             + "<br>" + area["dist_to_city_km"].round(1).astype(str) + " km from " + city)
    pts = np.array([centres.get(c, (np.nan, np.nan)) for c in area["WijkenEnBuurten"]])
    fig.add_scattergl(x=pts[:, 0], y=pts[:, 1], mode="markers", marker=dict(size=8, opacity=0),
                      text=hover, hoverinfo="text", showlegend=False)
    for c, name in legend:                       # legend entries only, nothing drawn
        fig.add_scatter(x=[None], y=[None], mode="markers", name=name,
                        marker=dict(symbol="square", size=12, color=c))
    cp = centres[area.loc[area["dist_to_city_km"].idxmin(), "WijkenEnBuurten"]]
    # the city: orange (the only non-blue colour on the map) so it stands out from every value class
    fig.add_scatter(x=[cp[0]], y=[cp[1]], mode="markers", hoverinfo="skip", showlegend=False,
                    marker=dict(symbol="star", size=24, color=ORANGE, line=dict(color="white", width=2)))
    fig.add_annotation(x=cp[0], y=cp[1], text=f"<b>{city}</b>", showarrow=True, arrowhead=0,
                       arrowcolor=INK, arrowwidth=1.5, ax=55, ay=-45, font=dict(color=INK, size=16),
                       bgcolor="white", bordercolor=INK, borderwidth=1.5, borderpad=4)
    fig.update_xaxes(visible=False, range=[x0, x1])
    fig.update_yaxes(visible=False, range=[y0, y1], scaleanchor="x")
    card(fig, height=620, margin=dict(l=0, r=0, t=0, b=0), dragmode="pan")
    fig.update_layout(legend=dict(title=dict(text=legend_title, font=dict(color=INK)), x=0, y=0))
    return fig


fig = build_map(city, tuple(sorted(settings.items())), colour_by)
show(fig)
st.caption("Darker blue = higher average WOZ value. Big rural neighbourhoods fill most of the map but hold "
           "few homes. Hover a neighbourhood for its figures.")

# ---------------------------------------------------------------- step 2: distance
st.header("2 · Does moving further out make it cheaper?")
near = d[(d["dist_to_city_km"] <= 50) & ~d["woz_estimated"]].copy()
near["band"] = pd.cut(near["dist_to_city_km"], bins=range(0, 55, 5), right=False)
b = near.groupby("band", observed=True)["avg_woz_value_k_eur"].quantile([0.25, 0.5, 0.75]).unstack()
x = [i.left + 2.5 for i in b.index]
labels = [f"{i.left}–{i.right} km" for i in b.index]

fig2 = go.Figure()
fig2.add_scatter(x=x + x[::-1], y=list(b[0.75]) + list(b[0.25])[::-1], fill="toself",
                 fillcolor=BLUE_LIGHT, line=dict(width=0), hoverinfo="skip", name="middle half")
fig2.add_scatter(x=x, y=b[0.5], mode="lines+markers", line=dict(color=BLUE, width=2),
                 marker=dict(size=9), name="median", customdata=labels,
                 hovertemplate="%{customdata}<br>median €%{y:.0f}k<extra></extra>")
fig2.add_hline(y=city_woz, line_dash="dash", line_color=MUTED,
               annotation_text=f"typical home in {city}: €{city_woz:.0f}k", annotation_position="top left",
               annotation_font=dict(color=INK, size=13))
card(fig2, height=400, margin=dict(l=10, r=10, t=20, b=10), yaxis_rangemode="tozero",
     xaxis_title=f"straight-line distance to {city} (km)", yaxis_title="average WOZ value (k€)")
fig2.update_layout(legend=dict(orientation="h", y=-0.25))
show(fig2)
if len(b):
    peak = b[0.5].idxmax()
    below = [i for i in b.index if b.loc[i, 0.5] < city_woz]
    st.markdown(
        f"Around {city}, the most expensive ring is **{peak.left}–{peak.right} km** "
        f"(median €{b[0.5].max():.0f}k). "
        + (f"The median first drops below the city at **{below[0].left}–{below[0].right} km**. "
           if below else "The median never drops below the city within 50 km. ")
        + "At every distance the middle half of neighbourhoods is wide, so distance alone is a poor guide."
    )

# ---------------------------------------------------------------- step 3: trade-off
st.header("3 · Can I actually rent there?")
zone = d[(d["dist_to_city_km"] <= max_km) & (d["dwelling_count"] >= min_homes)]
if not incl_est:
    zone = zone[~zone["woz_estimated"] & ~zone["rent_estimated"]]
lower = zone["avg_woz_value_k_eur"] < city_woz
renty = zone["pct_rent_private"] >= min_rent

fig3 = go.Figure()
for part, colour, size, name in [(zone[~zone["candidate"]], GREY, 5, "other neighbourhoods"),
                                 (zone[zone["candidate"]], BLUE, 7, "fits all my needs")]:
    fig3.add_scattergl(x=part["avg_woz_value_k_eur"], y=part["pct_rent_private"], mode="markers",
                       marker=dict(color=colour, size=size, line=dict(color="white", width=0.5)),
                       name=name, text=part["region_name"] + ", " + part["municipality"],
                       hovertemplate="%{text}<br>WOZ €%{x:.0f}k · private rental %{y:.0f}%<extra></extra>")
fig3.add_shape(type="rect", x0=0, x1=city_woz, y0=min_rent, y1=100, fillcolor=BLUE_LIGHT,
               opacity=0.35, line_width=0, layer="below")
card(fig3, height=450, margin=dict(l=10, r=10, t=20, b=10),
     xaxis=dict(title="average WOZ value (k€)", range=[0, zone["avg_woz_value_k_eur"].quantile(0.99)]),
     yaxis=dict(title="homes rented from a private landlord (%)", range=[0, 100]))
fig3.update_layout(legend=dict(orientation="h", y=-0.2))
show(fig3)
if len(zone):
    st.markdown(
        f"Within {max_km} km, **{lower.mean():.0%}** of neighbourhoods are below the city's typical value "
        f"and **{renty.mean():.0%}** have at least {min_rent}% private rentals, but only "
        f"**{(lower & renty).mean():.0%}** have both (the shaded corner). Blue dots also meet the urban "
        "and supermarket conditions."
    )

# ---------------------------------------------------------------- step 4: shortlist
st.header("4 · So where do I start looking?")
if cand.empty:
    st.warning("No neighbourhood meets all your conditions. Try a larger distance or a lower rental share.")
else:
    by_town = (cand.groupby("municipality")
               .agg(neighbourhoods=("candidate", "size"), median_woz=("avg_woz_value_k_eur", "median"),
                    km=("dist_to_city_km", "median"))
               .sort_values("neighbourhoods", ascending=False).head(12).iloc[::-1])
    fig4 = go.Figure(go.Bar(x=by_town["neighbourhoods"], y=by_town.index, orientation="h",
                            marker_color=BLUE, customdata=np.c_[by_town["median_woz"], by_town["km"]],
                            hovertemplate="%{y}: %{x} neighbourhoods<br>median €%{customdata[0]:.0f}k"
                                          " · %{customdata[1]:.0f} km<extra></extra>"))
    card(fig4, height=max(200, 70 + 30 * len(by_town)), margin=dict(l=10, r=10, t=20, b=10),
         xaxis_title="neighbourhoods that fit")
    show(fig4)

    table = (cand.sort_values(["dist_to_city_km"])
             .assign(urban=lambda t: t["urbanity_level"].map(URBANITY))
             [["region_name", "municipality", "dist_to_city_km", "avg_woz_value_k_eur",
               "pct_rent_private", "pct_rent_corporation", "pct_multi_family", "dist_supermarket_km",
               "urban", "dwelling_count"]]
             .rename(columns={"region_name": "neighbourhood", "dist_to_city_km": "km to city",
                              "avg_woz_value_k_eur": "WOZ (k€)", "pct_rent_private": "private rental %",
                              "pct_rent_corporation": "corporation %", "pct_multi_family": "flats %",
                              "dist_supermarket_km": "supermarket km", "dwelling_count": "homes"}))
    st.dataframe(table.round(1), hide_index=True, width="stretch")
    st.caption("A high *flats %* can explain a lower WOZ: WOZ is the value of a whole home, not per m². "
               "Neighbourhoods with 90–100% private rentals may be student or care complexes; check them.")
    st.download_button("Download this list (CSV)", table.to_csv(index=False).encode("utf-8"),
                       file_name=f"neighbourhoods_{city}.csv", mime="text/csv")

# ---------------------------------------------------------------- step 5: limits
st.header("5 · What this cannot tell you")
st.markdown("""
- **Rent.** WOZ is the municipality's valuation of a home for tax, not a rent and not an asking price.
- **Availability.** A high private-rental share means those homes exist, not that one is free today.
- **One home.** These are neighbourhood averages; a single home can be far above or below them.
- **Travel time.** Distance is a straight line, not a train or bike route.
- **Size.** WOZ is per home, not per m²: a neighbourhood of small flats looks cheaper than it is per m².
- **Social housing.** "Corporation-owned" is about the owner, not the rent; CBS did not look at rent levels.
""")
st.caption("Data: CBS *Kerncijfers wijken en buurten 2025* (86165NED) and CBS/Kadaster *Wijk- en buurtkaart 2025*, "
           "CC BY 4.0. Cleaning and analysis: notebooks 01–03 in this repository.")
