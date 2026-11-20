import streamlit as st

from clients.backend import get_officials, generate_rti
from screens.overview import show_overview


# Show any selected metric issue and its related officials.
def issue_details():
    if st.button("Back", icon=":material/arrow_back:"):
        source_page = st.session_state.get("issue_source_page")
        if source_page is None:
            source_page = st.Page(show_overview, title="Home", default=True)
        st.switch_page(source_page)

    issue = st.session_state.get("selected_issue")
    if not issue:
        st.info("Select See issue on a dashboard to view its details.")
        return

    st.title(f"{issue['category']} Issue details", anchor=False)

    # Issue details
    with st.container(border=True):
        st.subheader(issue["metric"], anchor=False)
        st.caption(f"{issue['location']} · {issue['period']} · {issue['source']}")

        st.metric("Reported value", issue["value"])

    st.divider()

    # Responsible office
    st.subheader("Responsible office", anchor=False)
    officials = get_officials()

    if officials is None:
        st.warning("Official details are unavailable.")
    else:
        found = False
        for official in officials:
            if official["category"] != issue["category"]:
                continue

            found = True
            with st.container(border=True):
                st.subheader(official["name"], anchor=False)
                st.text(official["designation"])
                st.text("Mobile: " + (official["mobile"] or ""))
                st.text("Office: " + (official["office_phone"] or ""))
                emails = official["emails"] or [""]
                st.text("Email: " + (emails[0] or ""))

        if not found:
            st.info("No official found for this category.")

    st.divider()

    # RTI section
    st.subheader("RTI generation", anchor=False)
    context = (
        f"For {issue['location']}, {issue['period']}, reported {issue['metric']} "
        f"is {issue['value']}. Category: {issue['category']}. Source: {issue['source']}."
    )

    if st.session_state.get("rti_context") != context:
        st.session_state.rti_context = context
        st.session_state.rti_text = None

    if not st.session_state.get("rti_text"):
        with st.spinner("Generating RTI..."):
            st.session_state.rti_text = generate_rti(context)
        if not st.session_state.rti_text:
            st.error("Could not generate the RTI. Check the backend and Ollama, then try again.")
            if st.button("Try again"):
                st.rerun()
            return

    with st.container(border=True):
        st.text(st.session_state.rti_text)

    if st.button("Generate again"):
        st.session_state.rti_text = None
        st.rerun()
