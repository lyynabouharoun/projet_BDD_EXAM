import streamlit as st
from backend.database import fetch_all_exams


def render():
    st.header("📊 Faculty Dashboard")

    exams = fetch_all_exams()

    st.metric("Total Exams", len(exams))

    if exams:
        dates = {}
        for e in exams:
            d = e["date_heure"].date()
            dates[d] = dates.get(d, 0) + 1

        st.subheader("📈 Exams per Day")
        st.bar_chart(dates)
    else:
        st.info("No data available.")
