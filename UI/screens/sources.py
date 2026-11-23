import streamlit as st


def sources():
    st.title("Sources", anchor=False)

    # Original websites and API used by the pipelines.
    st.subheader("Data sources", anchor=False)
    data_sources = [
        ("School · UDISE+ education highlights API", "https://api.udiseplus.gov.in/open-services/v1.1/kpi/edu-highlights"),
        ("Courts · NJDG Surat district dashboard", "https://njdg.ecourts.gov.in/njdg_v3/?p=home/index&state_code=24~17&dist_code=14"),
        ("Health · Surat district hospital directory", "https://surat.nic.in/public-utility-category/hospitals/"),
        ("Health · SMC urban health centres", "https://www.suratmunicipal.gov.in/Departments/PMJAYUHC"),
        ("Finance · SMC balance sheets", "https://www.suratmunicipal.gov.in/Departments/Accounts/BalanceSheet"),
        ("Water · SMC water quality reports", "https://www.suratmunicipal.gov.in/Departments/HydraulicWaterQuality"),
        ("Officials · SMC officials directory", "https://www.suratmunicipal.gov.in/Home/SMCOfficials"),
    ]

    for name, url in data_sources:
        st.link_button(name, url, width="stretch")

    st.divider()
    st.subheader("Benchmarks and scoring", anchor=False)

    # School metrics across LEA, Infrastructure and Digital Learning.
    st.subheader("Schools · PGI-D 2025–26", anchor=False)
    st.table({
        "Dashboard / API metric": [
            "Drinking water", "Toilets (girls + boys)",
            "Accessible toilets", "Handwashing", "Rainwater harvesting", "Playgrounds",
            "Library / reading corner", "Ramps with handrails", "Internet access",
            "Computers", "Functional smart classrooms",
        ],
        "PGI-D indicator": [
            "2.2.4 · Clean and potable drinking water facility",
            "2.2.1 + 2.2.2 · Functional girls’ and boys’ toilets",
            "2.2.3 · CWSN friendly toilet",
            "2.2.5 · Hand wash area/s",
            "2.2.6 · Rainwater harvesting structures in school",
            "2.2.7 · Playground",
            "3.4 · Library and/or Reading Corner",
            "3.5 · Ramp with railing",
            "5.1 · Internet facility for pedagogical purposes",
            "5.2 · Computer/laptop used for pedagogical purposes",
            "5.3 · Computer-assisted teaching learning facility (e.g. smart classrooms)",
        ],
        "Maximum points": ["2", "4", "2", "2", "2", "4", "4", "4", "10", "10", "10"],
    })
    st.write("Indicator score = (coverage (%) / 100) × weight")
    st.write("Selected-metric score (%) = (sum of indicator scores / sum of their weights) × 100.")
    st.link_button("Source: MoE PGI-D 2025–26 · Methodology 3.5; Annexure 2, pages 36–37", "https://dpgi.udiseplus.gov.in/")
    st.subheader("Issue classification rule", anchor=False)
    st.write("School facility coverage below 70% → Issue.")
    st.caption("Derived from government score-based classification and extended to individual metrics. The 70% issue cutoff is a dashboard choice.")
    st.link_button("Classification source: MoE PGI-D 2024–25 · Section 3.6, page 6", "https://ssa.assam.gov.in/sites/default/files/swf_utility_folder/departments/ssam_medhassu_in_oid_5/do_u_want_2_know/pgi-district-2024-25-brochure.pdf#page=6")

    st.divider()

    # Finance score built from the same SMC balance-sheet fields shown on the dashboard.
    st.subheader("Finance · SMC balance-sheet trend score", anchor=False)
    st.table({
        "Dashboard metric": [
            "Operating balance margin",
            "Expenditure growth above income growth",
            "Own-source revenue proxy",
            "Three-year balance stability",
        ],
        "Calculation": [
            "(Income − expenditure) ÷ income × 100",
            "Expenditure year-on-year change − income year-on-year change",
            "(Tax revenue + non-tax revenue) ÷ income × 100",
            "Number of non-negative operating balances in the latest three years",
        ],
        "Score weight": ["35", "25", "25", "15"],
    })
    st.link_button(
        "Data source: SMC balance sheets",
        "https://www.suratmunicipal.gov.in/Departments/Accounts/BalanceSheet",
    )
    st.link_button(
        "Indicator reference: NUDM Urban Analytics Standard",
        "https://www.nudm.mohua.gov.in/wp-content/uploads/2025/05/UA-Standard-NUDM.pdf",
    )
    st.link_button(
        "Reporting context: 16th Finance Commission",
        "https://www.indiabudget.gov.in/doc/16fcvol1.pdf",
    )

    st.divider()

    # Water quality percentage mapped to the PJS scoring bands.
    st.subheader("Water · AMRUT 2.0 / Pey Jal Survekshan 2022", anchor=False)
    st.table({
        "Samples passing consumer-end quality tests": ["≥95%", "75% to <95%", "50% to <75%", "25% to <50%", "5% to <25%", "<5%"],
        "Points out of 50": ["50", "40", "30", "20", "10", "0"],
    })
    st.write("Formula: compliance rate = passed samples / total tested samples × 100. Assign points using the bands above.")
    st.write("Dashboard score = band points / 50 × 100. The below-5% band is a custom dashboard rule.")
    st.link_button("Source: MoHUA Pey Jal Survekshan Toolkit · 1.4B, printed pages 24–26", "https://amrut.mohua.gov.in/uploads/PeyJal_Survekshan_ToolKit.pdf#page=13")
    st.subheader("Issue classification rule", anchor=False)
    st.table({
        "Samples passing (%)": ["≥95%", "75% to <95%", "50% to <75%", "<50%"],
        "Classification": ["Good", "Needs improvement", "Poor", "Very poor"],
    })
    st.write("Water compliance below 95% → Issue.")
    st.caption("Derived from PJS scoring bands, in the absence of a verified government issue-classification rule directly applicable to our data.")
