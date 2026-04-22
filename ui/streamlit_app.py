from dataclasses import asdict

import pandas as pd
import streamlit as st

from config.scenarios import SCENARIOS
from core.coordinator import MissionCoordinator
from core.exceptions import ValidationError


def apply_custom_css():
    st.markdown(
        """
        <style>
        .block-container {
            padding-top: 1.2rem;
            padding-bottom: 2rem;
            max-width: 1300px;
        }
        .hero {
            padding: 1.25rem 1.4rem;
            border-radius: 18px;
            background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 55%, #0369a1 100%);
            color: white;
            margin-bottom: 1rem;
        }
        .hero h1 {
            margin: 0;
            padding: 0;
            font-size: 2rem;
        }
        .hero p {
            margin-top: 0.5rem;
            color: #dbeafe;
        }
        .section-card {
            border: 1px solid rgba(120,120,120,.15);
            border-radius: 16px;
            padding: 1rem 1rem 0.6rem 1rem;
            background: rgba(250,250,250,.45);
            margin-bottom: 1rem;
        }
        .small-note {
            font-size: 0.92rem;
            opacity: 0.85;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def run_app():
    st.set_page_config(
        page_title="Search & Rescue Multi-Agent System",
        page_icon="🚁",
        layout="wide",
    )

    apply_custom_css()

    st.markdown(
        """
        <div class="hero">
            <h1>🚁 Missing Persons Search & Rescue AI System</h1>
            <p>Multi-agent mission planning with live LLM-backed agent refinement and deterministic fallback for stability.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.sidebar:
        st.header("Mission Controls")
        preset = st.selectbox("Choose a scenario", ["Custom"] + list(SCENARIOS.keys()))
        use_llm = st.toggle("Use LLM Enhancement", value=True)
        st.markdown("---")
        st.markdown(
            """
            **Agent Pipeline**
            1. Case Intake  
            2. Signal Detection  
            3. Zone Prediction  
            4. Drone Coordination  
            5. Volunteer Management  
            """
        )
        st.caption("Each agent can use the LLM. Fallback logic keeps the demo alive if the API misbehaves.")

    default_data = SCENARIOS.get(
        preset,
        {
            "subject_name": "Unknown Subject",
            "age": 30,
            "status_type": "Hiker",
            "hours_missing": 6.0,
            "last_seen_location": "Trail intersection",
            "weather": "Clear",
            "temperature_f": 65,
            "terrain": "Forest",
            "mobility_level": "Medium",
            "medical_risk": "Medium",
            "has_phone": True,
            "phone_battery": 50,
            "wearable_detected": False,
            "stress_level": "Medium",
            "notes": "No additional notes.",
        },
    )

    left, right = st.columns([1.4, 1])

    with left:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.subheader("Case Input")
        with st.form("case_form"):
            col1, col2, col3 = st.columns(3)

            with col1:
                subject_name = st.text_input("Subject Name", value=default_data["subject_name"])
                age = st.number_input("Age", min_value=0, max_value=120, value=int(default_data["age"]))
                status_type = st.selectbox(
                    "Subject Type",
                    ["Hiker", "Child", "Disaster Victim"],
                    index=["Hiker", "Child", "Disaster Victim"].index(default_data["status_type"]),
                )
                hours_missing = st.number_input(
                    "Hours Missing",
                    min_value=0.0,
                    max_value=240.0,
                    value=float(default_data["hours_missing"]),
                    step=0.5,
                )
                last_seen_location = st.text_input("Last Seen Location", value=default_data["last_seen_location"])

            with col2:
                weather = st.selectbox(
                    "Weather",
                    ["Clear", "Rain", "Fog", "Cold Night"],
                    index=["Clear", "Rain", "Fog", "Cold Night"].index(default_data["weather"]),
                )
                temperature_f = st.number_input("Temperature (F)", min_value=-20, max_value=120, value=int(default_data["temperature_f"]))
                terrain = st.selectbox(
                    "Terrain",
                    ["Forest", "Mountain", "Urban Edge", "Lake / Trail"],
                    index=["Forest", "Mountain", "Urban Edge", "Lake / Trail"].index(default_data["terrain"]),
                )
                mobility_level = st.selectbox(
                    "Mobility Level",
                    ["Low", "Medium", "High"],
                    index=["Low", "Medium", "High"].index(default_data["mobility_level"]),
                )
                medical_risk = st.selectbox(
                    "Medical Risk",
                    ["Low", "Medium", "High"],
                    index=["Low", "Medium", "High"].index(default_data["medical_risk"]),
                )

            with col3:
                has_phone = st.checkbox("Has Phone", value=bool(default_data["has_phone"]))
                phone_battery = st.slider("Phone Battery %", min_value=0, max_value=100, value=int(default_data["phone_battery"]))
                wearable_detected = st.checkbox("Wearable Detected", value=bool(default_data["wearable_detected"]))
                stress_level = st.selectbox(
                    "Stress Level",
                    ["Low", "Medium", "High"],
                    index=["Low", "Medium", "High"].index(default_data["stress_level"]),
                )
                notes = st.text_area("Notes", value=default_data["notes"], height=140)

            submitted = st.form_submit_button("Generate Mission Plan", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with right:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.subheader("Demo Notes")
        st.markdown(
            """
            - A visible loading panel shows agent progress during execution.
            - The LLM is applied across all five agents, not just side notes.
            - If the API fails, deterministic logic still produces a usable mission plan.
            """
        )
        st.markdown('<p class="small-note">Because nothing says confidence like watching a UI reassure you while the internet decides whether to cooperate.</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    if submitted:
        try:
            coordinator = MissionCoordinator(use_llm=use_llm)

            status_box = st.status("Starting mission planning...", expanded=True)

            def progress_callback(label: str, state: str = "running"):
                if state == "complete":
                    status_box.update(label=label, state="complete", expanded=False)
                else:
                    status_box.write(f"• {label}")

            with st.spinner("Building mission plan..."):
                results = coordinator.run(
                    {
                        "subject_name": subject_name,
                        "age": age,
                        "status_type": status_type,
                        "hours_missing": hours_missing,
                        "last_seen_location": last_seen_location,
                        "weather": weather,
                        "temperature_f": temperature_f,
                        "terrain": terrain,
                        "mobility_level": mobility_level,
                        "medical_risk": medical_risk,
                        "has_phone": has_phone,
                        "phone_battery": phone_battery if has_phone else 0,
                        "wearable_detected": wearable_detected,
                        "stress_level": stress_level,
                        "notes": notes,
                    },
                    progress_callback=progress_callback,
                )

            case = results["case"]
            signal = results["signal"]
            zones = results["zones"]
            drones = results["drones"]
            volunteers = results["volunteers"]
            intake_analysis = results["intake_analysis"]
            llm_meta = results["llm_meta"]

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Top Zone", zones[0].zone_name)
            c2.metric("Top Confidence", f"{zones[0].probability_score}%")
            c3.metric("Signal Confidence", signal.confidence)
            c4.metric("LLM Mode", "Enabled" if llm_meta.llm_used else "Fallback")

            if llm_meta.llm_error:
                st.warning(f"LLM note: {llm_meta.llm_error}")

            st.markdown(results["summary"])
            st.markdown("---")

            tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
                [
                    "📋 Case Intake",
                    "📡 Signal Detection",
                    "🗺️ Search Zones",
                    "🚁 Drone Tasks",
                    "🧭 Volunteer Teams",
                    "🧠 LLM Notes",
                ]
            )

            with tab1:
                st.markdown("### Structured Case Report")
                st.json(asdict(case))
                st.markdown("### LLM Intake Analysis")
                st.markdown(f"**Urgency Level:** {intake_analysis.get('urgency_level', 'N/A')}")
                risk_flags = intake_analysis.get("risk_flags", [])
                if risk_flags:
                    st.markdown("**Risk Flags:**")
                    for flag in risk_flags:
                        st.markdown(f"- {flag}")
                else:
                    st.markdown("**Risk Flags:** None returned")
                st.info(intake_analysis.get("intake_summary", "No intake summary available."))

            with tab2:
                st.markdown(f"**Signal Type:** {signal.signal_type}")
                st.markdown(f"**Confidence:** {signal.confidence}")
                st.markdown(f"**Recommended Zone:** {signal.recommended_zone}")
                st.info(signal.rationale)

            with tab3:
                zone_df = pd.DataFrame([asdict(z) for z in zones])
                st.dataframe(
                    zone_df[
                        [
                            "zone_name",
                            "probability_score",
                            "terrain_modifier",
                            "behavior_modifier",
                            "signal_modifier",
                            "weather_modifier",
                            "rationale",
                        ]
                    ],
                    use_container_width=True,
                    hide_index=True,
                )
                map_df = pd.DataFrame([{"lat": z.lat, "lon": z.lon} for z in zones[:4]])
                st.map(map_df)

            with tab4:
                drone_df = pd.DataFrame([asdict(d) for d in drones])
                st.dataframe(drone_df, use_container_width=True, hide_index=True)

            with tab5:
                volunteer_df = pd.DataFrame([asdict(v) for v in volunteers])
                st.dataframe(volunteer_df, use_container_width=True, hide_index=True)

            with tab6:
                if llm_meta.agent_notes:
                    for note in llm_meta.agent_notes:
                        st.markdown(f"- {note}")
                else:
                    st.info("No LLM notes recorded.")
                st.caption(f"Model configured: {llm_meta.llm_model}")

        except ValidationError as ve:
            st.error(f"Input validation failed: {ve}")
        except Exception as ex:
            st.error(f"Unexpected error: {ex}")
            st.exception(ex)
