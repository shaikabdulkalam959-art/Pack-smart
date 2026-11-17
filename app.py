"""Streamlit interface for Pack Smart's knapsack algorithms.

Run locally with: streamlit run app.py
"""
from __future__ import annotations

import matplotlib.pyplot as plt
import streamlit as st

from App import ALGOS, DEPOT, Item, load_sample, pickup_trip, run, total, validate_item

st.set_page_config(page_title="Pack Smart", page_icon="🎒", layout="wide")
st.title("🎒 Pack Smart")
st.caption("Compare five approaches to the 0/1 knapsack problem and plan a pickup route.")

if "items" not in st.session_state:
    st.session_state.items = load_sample()
if "capacity" not in st.session_state:
    st.session_state.capacity = 15

with st.sidebar:
    st.header("Bag settings")
    st.session_state.capacity = st.number_input(
        "Weight capacity", min_value=1, max_value=1000,
        value=int(st.session_state.capacity), step=1,
    )

    st.header("Manage items")
    with st.form("add_item_form", clear_on_submit=True):
        item_name = st.text_input("Name", max_chars=20)
        item_weight = st.number_input("Weight", min_value=1, max_value=999, value=1, step=1)
        item_value = st.number_input("Value", min_value=1, max_value=999, value=1, step=1)
        submitted = st.form_submit_button("Add item")
        if submitted:
            item, error = validate_item(
                st.session_state.items, item_name, str(item_weight), str(item_value)
            )
            if error:
                st.error(error)
            else:
                st.session_state.items.append(item)
                st.success(f"Added {item.name}.")

    if st.session_state.items:
        remove_name = st.selectbox("Remove an item", [item.name for item in st.session_state.items])
        if st.button("Remove selected item", use_container_width=True):
            st.session_state.items = [
                item for item in st.session_state.items if item.name != remove_name
            ]
            st.rerun()

    left, right = st.columns(2)
    if left.button("Load sample", use_container_width=True):
        st.session_state.items = load_sample()
        st.session_state.capacity = 15
        st.rerun()
    if right.button("Clear", use_container_width=True):
        st.session_state.items = []
        st.rerun()

items = st.session_state.items
capacity = int(st.session_state.capacity)
st.subheader("Your items")
if items:
    st.dataframe(
        [
            {"Item": item.name, "Weight": item.weight, "Value": item.value,
             "Value / weight": round(item.ratio, 2),
             "Location (km)": f"({item.x:.1f}, {item.y:.1f})"}
            for item in items
        ],
        hide_index=True,
        use_container_width=True,
    )
else:
    st.info("Add an item or load the sample data to get started.")

st.subheader("Choose algorithms")
algorithm_names = {key: data[0] for key, data in ALGOS.items()}
selected_keys = st.multiselect(
    "Algorithms to compare",
    options=list(ALGOS),
    default=list(ALGOS),
    format_func=lambda key: algorithm_names[key],
)

if st.button("Solve knapsack", type="primary", disabled=not items or not selected_keys):
    results = [run(key, items, capacity) for key in selected_keys]
    best_value = max(result["v"] for result in results)
    st.subheader("Comparison")
    st.dataframe(
        [
            {
                "Algorithm": result["name"],
                "Value": result["v"],
                "Weight": f"{result['w']} / {capacity}",
                "Optimal among selected": result["v"] == best_value,
                "Runtime (ms)": round(result["ms"], 3),
                "Work": result["work"],
            }
            for result in results
        ],
        hide_index=True,
        use_container_width=True,
    )

    for result in results:
        with st.expander(f"{result['name']} — value {result['v']}"):
            st.write(f"**Complexity:** time {result['time']}; space {result['space']}.")
            st.write("**How it works**")
            for step in result["steps"]:
                st.markdown(f"- {step}")

            chosen = [items[index] for index in result["ids"]]
            weight, value = total(items, result["ids"])
            metric_cols = st.columns(3)
            metric_cols[0].metric("Total value", value)
            metric_cols[1].metric("Total weight", f"{weight} / {capacity}")
            order, distance = pickup_trip(items, result["ids"])
            metric_cols[2].metric("Pickup trip", f"{distance:.2f} km")
            if chosen:
                st.write("**Packed:** " + ", ".join(item.name for item in chosen))
                route = " → ".join(["Depot"] + [items[index].name for index in order] + ["Depot"])
                st.write(f"**Route:** {route}")
            else:
                st.write("No items fit within this capacity.")

            fig, ax = plt.subplots(figsize=(8, 4.5))
            packed = set(result["ids"])
            for index, item in enumerate(items):
                ax.scatter(item.x, item.y, color="#c2410c" if index in packed else "#888888", s=70)
                ax.annotate(item.name, (item.x, item.y), xytext=(0, 7),
                            textcoords="offset points", ha="center", fontsize=8)
            route_points = [DEPOT] + [(items[index].x, items[index].y) for index in order]
            if order:
                route_points.append(DEPOT)
                ax.plot([point[0] for point in route_points],
                        [point[1] for point in route_points], color="#c2410c", alpha=0.7)
            ax.scatter(*DEPOT, marker="s", color="black", s=90, label="Depot")
            ax.set(xlim=(0, 10), ylim=(7, 0), xlabel="km", ylabel="km",
                   title="Pickup map (packed items in orange)")
            ax.grid(True, alpha=0.3)
            ax.legend()
            st.pyplot(fig, clear_figure=True)
            plt.close(fig)

st.caption("Exact algorithms should agree on the optimal value; greedy is a fast heuristic and may differ.")
