from ciscoise.exception import ISEAPIError
from ciscoise import *
from pprint import pprint
from datetime import datetime

source_ise_session = ISESession(
    "ise27api.ironbowlab.com",
    "admin",
    "Ir0n1234!@#$",
    options={
        "verify": False,
        "sponsor_api_user": "sponsorapisvc",
        "sponsor_api_password": "Ir0n1234!@#$",
        "debug": False,
    },
)
source = ISE(source_ise_session)

target_ise_session = ISESession(
    "ise27api.ironbowlab.com",
    "admin",
    "Ir0n1234!@#$",
    options={
        "verify": False,
        "sponsor_api_user": "sponsorapisvc",
        "sponsor_api_password": "Ir0n1234!@#$",
        "debug": False,
    },
)
target = ISE(target_ise_session)

new_guest = {
    "GuestUser": {
        "name": "Joe Visitor",
        "description": "ERS Example user ",
        "guestType": "Contractor (default)",
        "sponsorUserName": "rwolfe",
        "guestInfo": {
            "userName": "joevisitor",
            "emailAddress": "joe.visitor@domain.com",
            "phoneNumber": "5551231234",
            "password": "6053",
            "enabled": True,
            "smsServiceProvider": "Global Default",
        },
        "guestAccessInfo": {
            "validDays": 90,
            "fromDate": "10/28/2020 11:06",
            "toDate": "01/26/2021 10:06",
            "location": "San Jose",
        },
        "portalId": "b7e7d773-7bb3-442b-a50b-42837c12248a",
        "customFields": {},
    }
}


try:
    print(f"Getting data from source ISE server...")
    guests = source.getGuests()
    print(f"\tFound {len(guests)} total guest accounts.")

    # May not need to actually get this data, just assume same guest type (by name) exists on target system
    types = source.getGuestTypes()
    # pprint(types)
    print(f"\tFound {len(types)} different guest types.")

    print(f"Getting data from target ISE server...")
    sponsor_portals = target.getSponsorPortals()
    sponsor_portals_count = len(sponsor_portals)
    if sponsor_portals_count == 1:
        print(f"\tFound {sponsor_portals_count} sponsor portal.")
        selected_portal = sponsor_portals[0]
        selected_portal_id = selected_portal["id"]
    else:
        print(
            f"\tFound {sponsor_portals_count} sponsor portals. Please select which one to continue with:"
        )
        i = 0
        for portal in sponsor_portals:
            print(f"\t\t#{i} - {sponsor_portals[i]['name']}")

        entered_portal_id = int(
            input(
                f"\tEnter number of portal to proceed with [0-{sponsor_portals_count-1}]: "
            )
        )
        selected_portal = sponsor_portals[entered_portal_id]
        selected_portal_id = selected_portal["id"]
    print(f"\tProceeding with {selected_portal['name']}")

    print(f"Pushing configs into target ISE server...")
    sponsor_filter = "admin"
    if sponsor_filter:
        print(f"\tOnly migrating accounts created by sponsor '{sponsor_filter}'.")
    total_created = 0
    total_failed = 0
    for guest in guests:
        guest = source.getGuest(guest["id"])
        if sponsor_filter:
            if guest["sponsorUserName"] == sponsor_filter:
                print(
                    f"\t{guest['guestInfo']['userName']} was created by {sponsor_filter} and will be migrated."
                )
            else:
                # print(
                #     f"Guest {guest['guestInfo']['userName']} was created by {guest['sponsorUserName']} and not {sponsor_filter}. Skipping.."
                # )
                continue

        # pprint(guest)
        new_guest = target.newGuestFromExisting(
            guest, guest["guestType"], selected_portal_id, True
        )
        print(
            f'\tCreating new guest {new_guest["GuestUser"]["guestInfo"]["userName"]}... ',
            end="",
        )
        created = target.createGuest(new_guest)
        if created:
            print(f"SUCCEEDED.")
            total_created += 1
        else:
            print(f"FAILED.")
            total_failed += 1

    print(f"FINAL REPORT:")
    if sponsor_filter:
        print(f"\tOnly accounts created by {sponsor_filter} were migrated.")
    print(f"\tCreated a total of {total_created} guest accounts on target ISE server.")
    print(
        f"\tThere were {total_failed} failures. Please see above output for more information."
    )

except ISEAPIError as e:
    print(e.response.text)
    pprint(e.response.request.headers)

