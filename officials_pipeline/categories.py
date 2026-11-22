# Find the category from the designation.
def get_category(designation, source_category):
    category_keywords = {
        "Education": ["school board", "suman shala"],
        "Finance": ["accountant", "auditor", "tax", "recovery"],
        "Food": ["food", "market superintendent"],
        "Health": ["health", "medical", "smimer", "rcho", "tb officer", "pathologist"],
        "Water": ["hydraulic", "drainage", "water", "barrage", "tertiary treatment", "recycle"],
        "Environment": ["environment", "garden", "riverfront", "tapi", "creek", "khadi canal"],
        "Council": ["municipal secretary", "election", "census"],
        "Transport": ["sitilink", "traffic", "brts"],
        "Housing": ["housing"],
        "Town Planning": ["town planner", "town development"],
        "Infrastructure": ["city engineer", "public infrastructure", "bridge"],
        "Energy": ["energy", "ele. & mech."],
        "Fire Safety": ["fire officer"],
        "Culture": ["science center", "auditorium", "performing art", "gandhi smruti", "rang upvan"],
        "Sports": ["sports", "stadium", "swimming pool"],
        "Library": ["librarian", "library"],
        "Social Welfare": ["ucd", "c.d.p.o"],
        "RTI": ["rti cell"],
        "Law": ["law officer"],
        "Security": ["security officer"],
        "Vigilance": ["vigilance", "departmental inquiry"],
    }
    designation = designation.lower()

    for category, keywords in category_keywords.items():
        for keyword in keywords:
            if keyword in designation:
                return category

    return source_category
