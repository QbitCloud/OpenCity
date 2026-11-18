# Which post is responsible for each court figure the pipeline saves.
#
# The post is what matters. It stays the same when judges are transferred.
# The name of the judge holding the post is extra: it was checked on 18-11-2026, and it
# changes with transfers. Set "name" to None if it is not known or no longer correct.
#
# Where the posts and names come from (the official Surat district court website):
#   Home page:      https://surat.dcourts.gov.in/
#                   (the panel of three photos: Acting Chief Justice, Administrative Judge,
#                   Principal District & Sessions Judge)
#   List of Judges: https://surat.dcourts.gov.in/list-of-judges/
#
# Above every post named here, the High Court of Gujarat controls the district courts
# (Constitution of India, Article 235). The High Court names one of its judges as the
# "Administrative Judge" who supervises Surat district; the home page above lists him
# (Hon'ble Mr. Justice A. S. Supehia on 18-11-2026).
#
# The laws below were read on bare-act websites, not the official gazette:
#   Gujarat Civil Courts Act, 2005:                  https://indiankanoon.org/doc/95540367/
#   Bharatiya Nagarik Suraksha Sanhita, 2023 (BNSS): https://lawgist.in/bharatiya-nagarik-suraksha-sanhita-2023/13
#   Legal Services Authorities Act, 1987:            https://www.advocatekhoj.com/library/bareacts/legalservicesauthorities/9.php


# Principal District and Sessions Judge: the head of every court in Surat district,
# both the city courts and the taluka courts.
#   The post's control over the civil courts: Gujarat Civil Courts Act, 2005, sections 12(3) and 23(1)
#   The post's control over the criminal courts: BNSS 2023, section 13(1)
#   Name: https://surat.dcourts.gov.in/list-of-judges/
#         (first row of the "District And Sessions Court, Surat" table)
DISTRICT_JUDGE = {
    "post": "Principal District and Sessions Judge, Surat",
    "name": "Mr. R. A. Trivedi",
}

# Chief Judicial Magistrate: supervises the magistrate courts, where most criminal cases are heard,
# and decides how cases are shared out among the magistrates.
#   The post's role: BNSS 2023, section 13 (this replaced section 15 of the old CrPC)
#   Name: https://surat.dcourts.gov.in/list-of-judges/
#         ("Civil Court, Surat" table, "Chief Judicial Magistrate & Addl. Sr. Civil Judge")
CHIEF_JUDICIAL_MAGISTRATE = {
    "post": "Chief Judicial Magistrate, Surat",
    "name": "Mr. Y. I. Shaikh",
}


# One post for each figure. The keys match the saved record: its top-level keys,
# and the "name" of each row in "particulars" (written exactly as NJDG shows it).
RESPONSIBLE = {
    # All pending cases, civil and criminal, across every court in the district.
    "total_pending": DISTRICT_JUDGE,

    # Every civil court in the district is under the District Judge
    # (Gujarat Civil Courts Act, 2005, sections 12(3) and 23(1)).
    # The Principal Senior Civil Judge (same List of Judges page) runs the civil court in Surat city,
    # but the taluka civil courts are not under that post, so it is not used here.
    "civil_pending": DISTRICT_JUDGE,

    # Most criminal cases are in the magistrate courts, which the CJM supervises (BNSS 2023, section 13).
    # Sessions cases (the most serious crimes) are with the Principal District and Sessions Judge instead.
    # Note: NJDG's "Pending Dashboard" for Surat showed about half of all pending cases at the
    # "Process Issue" stage on 18-11-2026, meaning summons or warrants not yet served. In criminal
    # cases these are often served by the police (Surat City Police and Surat Rural Police).
    "criminal_pending": CHIEF_JUDICIAL_MAGISTRATE,

    # NJDG does not explain this figure. A hidden table in the page's HTML splits it into
    # "Pre-Litigation" (0) and "Pre-Trial" (1,350, all criminal), so these look like criminal
    # matters that have not reached trial yet. The CJM post is used on that basis.
    # Confirm with the court before showing this one in the UI.
    #   Source: https://njdg.ecourts.gov.in/njdg_v3/?p=home/index&state_code=24~17&dist_code=14
    #           (HTML comment next to the "Pre-Litigation / Pre-Trial" card), checked 18-11-2026
    "pre_litigation": CHIEF_JUDICIAL_MAGISTRATE,

    # Cases are filed by people and, in criminal cases, by the police (charge sheets and challans),
    # so no judge decides how many come in. The District Judge is used as the head of the courts
    # that register them.
    "Cases Instituted in Last Month": DISTRICT_JUDGE,

    # Cases decided across every court in the district.
    "Cases Disposed in Last Month": DISTRICT_JUDGE,

    # The District Judge also chairs the District Legal Services Authority, Surat, which gives
    # free legal aid (Legal Services Authorities Act, 1987, section 9(2)(a)).
    # Every woman is entitled to free legal aid under section 12(c) of the same Act:
    #   https://www.advocatekhoj.com/library/bareacts/legalservicesauthorities/12.php
    "Filed Cases By Woman": DISTRICT_JUDGE,

    # Same as above: head of the district's courts and chair of the District Legal Services Authority.
    "Filed Cases By Senior Citizen": DISTRICT_JUDGE,

    # Old cases across every court in the district.
    "pending_by_age": DISTRICT_JUDGE,
}
