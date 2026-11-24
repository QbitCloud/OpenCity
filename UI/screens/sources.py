import streamlit as st

from analysis.court_score import BASELINE, MARGIN, METRICS, format_rate
from analysis.hospital_analysis import DETAIL_THRESHOLD, PEOPLE_PER_UCHC, PEOPLE_PER_UHC, POPULATION


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
        ("Home page map · © OpenStreetMap contributors", "https://www.openstreetmap.org/copyright"),
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
    st.write(
        "Each metric receives its weighted points: Green = 100% of its weight, "
        "Amber = 70%, Orange = 35%, and Red = 0%. "
        "Finance score = sum of the four weighted metric points, out of 100."
    )
    st.caption(
        "A score is not shown when any of the four required Finance values is missing. "
        "The Green/Amber/Orange/Red thresholds are OpenCity project-defined bands, "
        "not official government cut-offs."
    )
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

    st.divider()

    # Court score: Surat's court rates against baselines; the clearance baseline is Gujarat's rate.
    st.subheader("Courts · India Justice Report 2025", anchor=False)
    st.table({
        "Dashboard metric": [label for key, label, unit, better, figure in METRICS],
        "Better when": ["Higher" if better == "higher" else "Lower" for key, label, unit, better, figure in METRICS],
        "Baseline": [
            "Not set · left out of the score" if BASELINE[key] is None else format_rate(BASELINE[key], unit)
            for key, label, unit, better, figure in METRICS
        ],
    })
    st.write("Clearance rate = cases disposed last month ÷ cases filed last month × 100 (civil + criminal).")
    st.write(
        "Metric score = Surat's rate ÷ baseline, capped at 100% (baseline ÷ rate when lower is better). "
        "Court score = average of the metric scores that have a baseline, out of 100."
    )
    st.caption(
        "The clearance baseline is the case clearance rate of Gujarat's subordinate courts. It uses the same formula "
        "on NJDG data, but over a year; Surat's rate uses one month, so it moves more from month to month."
    )
    st.link_button("Baseline source: India Justice Report 2025 · Gujarat profile, judiciary indicator 16, page 3", "https://indiajusticereport.org/files/Gujarat.pdf#page=3")
    st.link_button("Indicator definition: India Justice Report · case clearance rate (sub. court), benchmark 100%", "https://indiajusticereport.org/indicator/315/ijr-4/large-states/map")
    st.subheader("Issue classification rule", anchor=False)
    st.write(f"A metric more than {MARGIN:.0%} behind its baseline, or worse than at the previous reading → Issue.")
    st.caption(f"The {MARGIN:.0%} margin and the comparison with the previous reading are dashboard choices.")

    st.divider()

    # Health score: SMC's urban health centres against the NUHM population norms.
    st.subheader("Hospital · National Urban Health Mission norms", anchor=False)
    st.table({
        "Dashboard metric": ["Urban health centres (UHC)", "Urban community health centres (UCHC)"],
        "Calculation": ["Population ÷ number of UHCs", "Population ÷ number of UCHCs"],
        "Norm used": [f"1 per {PEOPLE_PER_UHC:,} people", f"1 per {PEOPLE_PER_UCHC:,} people"],
    })
    st.write("Metric score = norm ÷ people per centre, capped at 100%. Health score = average of the two metric scores, out of 100.")
    st.write(f"Population = {POPULATION:,}: the Census 2011 count for Surat Municipal Corporation, within the city limits as extended in 2020.")
    st.caption(
        "NUHM sets one U-PHC for every 50,000 people, and one U-CHC for every 2.5 lakh people, or 5 lakh in metros "
        "(cities above 5 lakh only). Surat is a million-plus city, so the dashboard uses the metro norm. "
        "The population is from 2011, so today's shortfall is larger than the score shows."
    )
    st.link_button("Norm source: NUHM Implementation Framework 2013 · facility norms table, PDF page 12", "https://www.nhsrcindia.org/sites/default/files/2021-06/2.Implementation_Framework_NUHM_2013.pdf#page=12")
    st.link_button("Population source: SMC demographics · Census 2011", "https://www.suratmunicipal.gov.in/TheCity/Demographics")
    st.subheader("Issue classification rule", anchor=False)
    st.write(f"Hospital address, phone or pincode reported for fewer than {DETAIL_THRESHOLD}% of listed hospitals → Issue.")
    st.write("A centre type below its NUHM norm → Issue.")
    st.caption(f"The {DETAIL_THRESHOLD}% cutoff is a dashboard choice.")

    st.divider()

    # City score on the Home page.
    st.subheader("City score", anchor=False)
    st.write(
        "City score = average of the School, Hospital, Water Quality, Courts and Finance scores, each for its latest data "
        "and weighted equally. Pages without a score are left out."
    )
    st.write("Star rating = city score ÷ 20, out of 5 stars. The stars are rounded to the nearest whole star; the rating is shown to one decimal.")
    st.caption(
        "Equal weighting follows the India Justice Report, which weights every indicator, theme and pillar equally. "
        "The city score is a dashboard summary, not an official rating."
    )
    st.link_button("Weighting reference: India Justice Report methodology", "https://indiajusticereport.org/methodology")
