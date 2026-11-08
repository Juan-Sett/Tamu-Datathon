import json
import os
from datetime import datetime

import streamlit as st

from snowflake_client import SnowflakeClient, SnowflakeConfig, SnowflakeError
from decision_engine import build_demo_decision, retrieve_relevant_records


st.set_page_config(
    page_title="Aggie Decision Desk",
    page_icon="🤠",
    layout="wide",
    initial_sidebar_state="expanded",
)


def load_seed_records():
    return [
        {
            "id": "DIN-001", "category": "Dining", "name": "The Commons Dining Hall",
            "description": "All-you-care-to-eat dining hall with vegetarian and vegan stations.",
            "location": "Commons Dining Hall, Northside", "price": 12.50,
            "open_time": "07:00", "close_time": "21:00", "tags": "dining, vegetarian, vegan, meal plan, northside",
            "source_url": "https://dining.tamu.edu/", "updated_at": "2026-11-07",
        },
        {
            "id": "DIN-002", "category": "Dining", "name": "The Grill at MSC",
            "description": "Quick-service burgers, sandwiches, salads, and fries inside the Memorial Student Center.",
            "location": "Memorial Student Center", "price": 10.00,
            "open_time": "10:30", "close_time": "20:00", "tags": "dining, quick, burger, sandwich, central campus",
            "source_url": "https://dining.tamu.edu/", "updated_at": "2026-11-07",
        },
        {
            "id": "DIN-003", "category": "Dining", "name": "Houston Street Cafe",
            "description": "Coffee, smoothies, wraps, and grab-and-go meals with indoor seating.",
            "location": "Zachry Engineering Center", "price": 8.50,
            "open_time": "07:30", "close_time": "17:00", "tags": "dining, coffee, smoothie, wrap, zachry, indoor",
            "source_url": "https://dining.tamu.edu/", "updated_at": "2026-11-07",
        },
        {
            "id": "LOC-001", "category": "Facility", "name": "Zachry Engineering Center",
            "description": "Engineering classrooms, labs, study spaces, and indoor seating.",
            "location": "3167 TAMU", "price": 0,
            "open_time": "06:00", "close_time": "23:00", "tags": "zachry, engineering, study, indoor, classroom",
            "source_url": "https://engineering.tamu.edu/", "updated_at": "2026-11-07",
        },
        {
            "id": "TRN-001", "category": "Transit", "name": "Route 12: Bonfire",
            "description": "Campus shuttle route connecting the MSC, Zachry, and north campus stops.",
            "location": "MSC ↔ Zachry ↔ North Campus", "price": 0,
            "open_time": "07:00", "close_time": "22:00", "tags": "bus, shuttle, transit, msc, zachry, north campus",
            "source_url": "https://transport.tamu.edu/Bus/routes.aspx", "updated_at": "2026-11-07",
        },
        {
            "id": "WTH-001", "category": "Weather", "name": "Campus weather snapshot",
            "description": "Hot afternoon conditions expected. Hydrate, use shade, and prefer indoor routes when possible.",
            "location": "College Station campus", "price": 0,
            "open_time": "12:00", "close_time": "18:00", "tags": "weather, heat, hot, hydration, shade, afternoon",
            "source_url": "https://weather.tamu.edu/", "updated_at": "2026-11-07",
        },
        {
            "id": "RES-001", "category": "Resource", "name": "Student Counseling & Mental Health",
            "description": "Confidential counseling, crisis support, and mental health resources for students.",
            "location": "Student Services Building", "price": 0,
            "open_time": "08:00", "close_time": "17:00", "tags": "wellbeing, counseling, mental health, student support",
            "source_url": "https://caps.tamu.edu/", "updated_at": "2026-11-07",
        },
        {
            "id": "EVT-001", "category": "Event", "name": "Engineering Career Mixer",
            "description": "Employer networking event for engineering students. Business casual recommended.",
            "location": "MSC Bethancourt Ballroom", "price": 0,
            "open_time": "17:30", "close_time": "19:30", "tags": "event, career, engineering, networking, msc",
            "source_url": "https://calendar.tamu.edu/", "updated_at": "2026-11-07",
        },
    ]


def snowflake_client_from_secrets():
    try:
        values = st.secrets["snowflake"]
    except Exception:
        values = {}
    values = dict(values)
    values.setdefault("account", os.getenv("SNOWFLAKE_ACCOUNT", ""))
    values.setdefault("host", os.getenv("SNOWFLAKE_HOST", ""))
    values.setdefault("api_key", os.getenv("SNOWFLAKE_API_KEY", ""))
    values.setdefault("role", os.getenv("SNOWFLAKE_ROLE", "PUBLIC"))
    values.setdefault("warehouse", os.getenv("SNOWFLAKE_WAREHOUSE", "COMPUTE_WH"))
    values.setdefault("database", os.getenv("SNOWFLAKE_DATABASE", "AGGIE_DECISION_DESK"))
    values.setdefault("schema", os.getenv("SNOWFLAKE_SCHEMA", "PUBLIC"))
    required = ["account", "host", "api_key"]
    if not all(values.get(key) for key in required):
        return None
    return SnowflakeClient(SnowflakeConfig(
        account=values.get("account", ""),
        host=values.get("host", ""),
        api_key=values.get("api_key", ""),
        role=values.get("role", "PUBLIC"),
        warehouse=values.get("warehouse", "COMPUTE_WH"),
        database=values.get("database", "AGGIE_DECISION_DESK"),
        schema=values.get("schema", "PUBLIC"),
    ))


def main():
    seed_records = load_seed_records()
    configured_client = snowflake_client_from_secrets()

    with st.sidebar:
        st.markdown("# 🤠 Aggie Decision Desk")
        st.caption("A data-grounded campus copilot powered by Snowflake.")
        st.divider()
        use_snowflake = st.toggle(
            "Use Snowflake live data",
            value=bool(configured_client),
            disabled=not configured_client,
            help="Turn this on after adding Snowflake credentials to Streamlit secrets.",
        )
        if not configured_client:
            st.info("Demo mode is active. Add Snowflake secrets to enable live API calls.")
        st.markdown("### Try asking")
        examples = [
            "I am near Zachry and need lunch under $10.",
            "Help me get from the MSC to an engineering event while avoiding the heat.",
            "What can I do on campus this afternoon with indoor study space?",
        ]
        for example in examples:
            if st.button(example, use_container_width=True):
                st.session_state["question"] = example
        st.divider()
        st.caption("Built for the Best Use of Snowflake API challenge")

    st.markdown("## Plan your next move on campus")
    st.markdown("Ask a practical question. Aggie Decision Desk combines campus facts, constraints, and AI reasoning into an actionable plan.")

    question = st.text_area(
        "What do you need help deciding?",
        value=st.session_state.get("question", ""),
        placeholder="Example: I have 45 minutes between classes near Zachry. Find lunch under $12 and keep me indoors as much as possible.",
        height=100,
        label_visibility="visible",
    )
    submitted = st.button("Make my plan →", type="primary", use_container_width=False)

    if not submitted and not question.strip():
        cols = st.columns(3)
        stats = [("8", "campus facts in demo"), ("3", "decision dimensions"), ("1", "clear next step")]
        for col, (number, label) in zip(cols, stats):
            with col:
                st.metric(label, number)
        st.info("Start with one of the example questions in the sidebar, or describe your own campus decision above.")
        return

    if not question.strip():
        st.warning("Tell me what you are trying to decide first.")
        return

    with st.spinner("Checking campus data and building your plan…"):
        try:
            if use_snowflake and configured_client:
                records = configured_client.fetch_campus_facts()
                relevant = retrieve_relevant_records(question, records)
                decision = configured_client.generate_decision(question, relevant)
                mode_label = "LIVE SNOWFLAKE DATA"
            else:
                relevant = retrieve_relevant_records(question, seed_records)
                decision = build_demo_decision(question, relevant)
                mode_label = "DEMO DATA"
        except SnowflakeError as exc:
            st.error(f"Snowflake request failed: {exc}")
            st.warning("Showing a demo response so the app remains usable during judging.")
            relevant = retrieve_relevant_records(question, seed_records)
            decision = build_demo_decision(question, relevant)
            mode_label = "DEMO FALLBACK"

    st.caption(f"● {mode_label}  ·  Generated {datetime.now().strftime('%b %d, %Y at %I:%M %p')}")
    left, right = st.columns([1.5, 1])
    with left:
        st.markdown("### Your recommended plan")
        st.success(decision.get("recommendation", "Here is a practical next step based on the available campus data."))
        steps = decision.get("steps", [])
        if steps:
            st.markdown("#### Do this next")
            for index, step in enumerate(steps, 1):
                st.markdown(f"**{index}.** {step}")
        tradeoff = decision.get("tradeoff")
        if tradeoff:
            st.markdown("#### Tradeoff")
            st.info(tradeoff)
    with right:
        st.markdown("### Why this plan")
        st.write(decision.get("why", "The plan matches your stated constraints with the strongest available campus options."))
        st.markdown("### Snowflake signal")
        st.write("The recommendation is grounded in records retrieved from the campus data layer, then synthesized by Cortex." if use_snowflake else "This run uses the same retrieval and response flow with seeded demo records. Connect Snowflake to make the data live.")

    st.divider()
    st.markdown("### Evidence used")
    for record in relevant:
        with st.expander(f"{record.get('name', 'Campus fact')} · {record.get('category', 'Source')}"):
            st.write(record.get("description", ""))
            details = []
            if record.get("location"):
                details.append(f"Location: {record['location']}")
            if record.get("price") is not None:
                details.append(f"Typical cost: ${float(record['price']):.2f}")
            if record.get("open_time") and record.get("close_time"):
                details.append(f"Hours: {record['open_time']}–{record['close_time']}")
            st.caption(" · ".join(details))
            st.markdown(f"Source: [{record.get('source_url', 'Campus data')}]({record.get('source_url', '#')})")


if __name__ == "__main__":
    main()
