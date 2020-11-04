from ciscoise.session import ISESession
from datetime import datetime
import json
import string
import random


class ISE:
    def __init__(self, session):
        self.ise: ISESession = session

    def getSponsorPortals(self):
        return self.ise.get("sponsorportalall")

    def getSponsorPortal(self, id: str):
        return self.ise.get("sponsorportal")

    def getGuestTypes(self):
        return self.ise.get("guesttypeall")

    def getGuestType(self, id):
        return self.ise.get("guesttypeall", id)["GuestType"]

    def getGuests(self):
        return self.ise.get("guestuserall")

    def getGuest(self, id):
        return self.ise.get("guestuser", id)["GuestUser"]

    def createGuest(self, payload: object):
        """Create a new guest user. This action requires sponsor credentials enabled for the API.

        Expected payload should look like:

        {
            "GuestUser": {
                "name": "Joe Visitor",
                "description": "ERS Example user ",
                "guestType": "Contractor (default)",
                "sponsorUserName": "jdoe",
                "guestInfo": {
                    "userName": "joevisitor",
                    "emailAddress": "joe.visitor@domain.com",
                    "phoneNumber": "5551231234",
                    "password": "Cisco123!@#",
                    "enabled": true,
                    "smsServiceProvider": "Global Default"
                },
                "guestAccessInfo": {
                    "validDays": 90,
                    "fromDate": "10/28/2020 11:06",
                    "toDate": "01/26/2021 10:06",
                    "location": "San Jose"
                },
                "portalId": "b7e7d773-7bb3-442b-a50b-42837c12248a",
                "customFields": {}
            }
        }"""

        return self.ise.post("guestuser", payload)

    def newGuestFromExisting(
        self, payload, guest_type: str = None, portal_id: str = None, test: bool = False
    ):
        if type(payload) != dict:
            payload = json.loads(payload)
        if "GuestUser" not in payload.keys():
            # Ensure payload is nested in a "GuestUser" dict key as expected by ISE API.
            payload = {"GuestUser": payload}
        try:
            # Delete keys from original guest data that creation API does not accept/need.
            del payload["GuestUser"]["link"]
            del payload["GuestUser"]["id"]
            del payload["GuestUser"]["sponsorUserId"]
            del payload["GuestUser"]["status"]
        except TypeError as e:
            pass

        # Overwrite values, if provided.
        if guest_type:
            payload["GuestUser"]["guestType"] = guest_type
        if portal_id:
            payload["GuestUser"]["portalId"] = portal_id

        # If test specified, append random chars to username
        rand_str = "".join(random.choices(string.ascii_uppercase + string.digits, k=3))

        payload["GuestUser"]["guestInfo"]["userName"] = (
            payload["GuestUser"]["guestInfo"]["userName"] + rand_str
        )

        return payload

    def new_guest(
        self,
        username: str,
        email: str,
        password: str,
        valid_days: int,
        from_date: float,
        location: str,
        portal_id: str,
        name: str = None,
        phone: int = None,
        description: str = None,
    ):
        now = datetime.now()
        fromDate = now.strftime("%m/%d/%Y %H:%M")
        toDate = datetime.fromtimestamp(
            now.timestamp() + valid_days * 24 * 60 * 60
        ).strftime("%m/%d/%Y %H:%M")
        print(f"from: {fromDate}, to: {toDate}")
        raise NotImplementedError("Function has not been completed, yet.")
        return {
            "GuestUser": {
                "name": name or username,
                "description": description,
                "guestType": "Contractor (default)",
                "sponsorUserName": "jdoe",
                "guestInfo": {
                    "userName": "joevisitor",
                    "emailAddress": "joe.visitor@domain.com",
                    "phoneNumber": "5551231234",
                    "password": "Cisco123!@#",
                    "enabled": True,
                    "smsServiceProvider": "Global Default",
                },
                "guestAccessInfo": {
                    "validDays": valid_days or 90,
                    "fromDate": now.strftime("%m/%d/%Y %H:%M"),
                    "toDate": "01/26/2021 10:06",
                    "location": "San Jose",
                },
                "portalId": "b7e7d773-7bb3-442b-a50b-42837c12248a",
                "customFields": {},
            }
        }
