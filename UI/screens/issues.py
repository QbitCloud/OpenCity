import streamlit as st

from clients.backend import get_court_officials, get_officials, generate_rti
from screens.overview import show_overview
from clients.rti import get_rti_url


# Show the officials responsible for an issue, read from MongoDB through the backend.
def show_officials(issue):
    # Court issues name the figure they are about, and read the posts responsible for it
    if issue.get("figure"):
        officials = get_court_officials()

        def matches(official):
            return issue["figure"] in official["figures"]
    else:
        officials = get_officials()

        def matches(official):
            return official["category"] == issue["category"]

    if officials is None:
        st.warning("Official details are unavailable.")
        return

    found = False
    for official in officials:
        if not matches(official):
            continue

        found = True
        with st.container(border=True):
            st.subheader(official["name"] or official["designation"], anchor=False)
            st.text(official["designation"])
            if official["mobile"]:
                st.text("Mobile: " + official["mobile"])
            if official["office_phone"]:
                st.text("Office: " + official["office_phone"])
            emails = official["emails"] or [""]
            if emails[0]:
                st.text("Email: " + emails[0])
            if official.get("checked_on"):
                st.caption(f"Checked on {official['checked_on']} · {official['source_url']}")

    if not found:
        st.info("No official found for this category.")


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
        if issue.get("baseline"):
            st.caption("Baseline: " + issue["baseline"])

    st.divider()

    # Responsible office
    st.subheader(f"Related Officials to {issue['category']}", anchor=False)
    show_officials(issue)

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

    if issue["category"] == "Courts":
        st.link_button("Open RTI portal", "https://gujarathc-casestatus.nic.in/rtiportal/", type="primary", width="stretch")
    else:
        st.link_button("File RTI", get_rti_url(st.session_state.rti_text), type="primary", width="stretch")
        
    if st.button("Generate again"):
        st.session_state.rti_text = None
        st.rerun()
