from datetime import datetime

import streamlit as st

from clients.backend import get_officials


# Show SMC officials by category.
def officials():
    title_column, filter_column = st.columns([3, 1], vertical_alignment="bottom")

    with title_column:
        st.title("SMC Officials", anchor=False)
        st.caption("Surat Municipal Corporation officials and their listed contact details. Categories are based on their designations.")

    official_records = get_officials()
    if official_records is None:
        st.error("Officials data is unavailable. Check the backend and MongoDB connection.")
        return

    if not official_records:
        st.info("No officials found. Run the officials pipeline first.")
        return

    categories = []
    for official in official_records:
        if official["category"] not in categories:
            categories.append(official["category"])
    categories.sort()

    with filter_column:
        selected_category = st.selectbox("Category", ["All"] + categories)

    if selected_category != "All":
        categories = [selected_category]

    st.divider()

    # Each category has a row of three cards.
    for category in categories:
        category_officials = []
        for official in official_records:
            if official["category"] == category:
                category_officials.append(official)

        st.subheader(f"{category} · {len(category_officials)}", anchor=False)
        columns = st.columns(3)

        for index, official in enumerate(category_officials):
            with columns[index % 3]:
                with st.container(border=True):
                    st.subheader(official["name"], anchor=False)
                    st.text(official["designation"])

                    if official["zone"]:
                        st.caption(official["zone"])
                    if official["mobile"]:
                        st.text("Mobile: " + official["mobile"])
                    if official["office_phone"]:
                        st.text("Office: " + official["office_phone"])
                    emails = official.get("emails") or []
                    email = (emails[0] or "") if emails else ""
                    st.text("Email: " + email)

        st.divider()
        
    # Footer
    updated_column, source_column = st.columns([3, 1], vertical_alignment="center")

    with updated_column:
        st.text("Last fetched")
        fetched_at = datetime.fromisoformat(official_records[0]["scraped_at"])
        st.caption(str(fetched_at))

    with source_column:
        st.link_button("View SMC source", "https://www.suratmunicipal.gov.in/Home/SMCOfficials", width="stretch")
