import json
from urllib.parse import quote
from uuid import uuid4


# Create a portal link carrying the text for the extension
def get_rti_url(text):
    data = {"id": str(uuid4()), "text": text}
    payload = quote(json.dumps(data), safe="")
    return "https://onlinerti.gujarat.gov.in/rti_portal/#opencity_rti=" + payload
