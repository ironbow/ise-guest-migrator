#!/usr/bin/env python
from ciscoise.exception import ISEAPIError
from ciscoise import *
from pprint import pprint
from datetime import datetime
import argparse
import configparser


def main(source, target, sponsor_filter):
    print(f"Getting data from source ISE server...")
    guests = source.getGuests()
    print(f"\tFound {len(guests)} total guest accounts.")

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
    if sponsor_filter:
        print(f"\tOnly migrating accounts created by sponsor '{sponsor_filter}'.")
    total_created = 0
    total_failed = 0
    for guest in guests:
        guest = source.getGuest(guest["id"])
        if sponsor_filter and guest["sponsorUserName"] != sponsor_filter:
            # Skip accounts not created by the supplied sponsor account
            continue

        # pprint(guest)
        new_guest = target.newGuestFromExisting(
            guest, guest["guestType"], selected_portal_id
        )
        print(
            f'\tCreating new guest {new_guest["GuestUser"]["guestInfo"]["userName"]}... ',
            end="",
        )
        try:
            created = target.createGuest(new_guest)
            if created:
                print(f"SUCCEEDED.")
        except ISEAPIError as e:
            print(f"FAILED. {e}")
            total_failed += 1

    print(f"FINAL REPORT:")
    if sponsor_filter:
        print(f"\tOnly accounts created by {sponsor_filter} were migrated.")
    print(f"\tCreated a total of {total_created} guest accounts on target ISE server.")
    print(
        f"\tThere were {total_failed} failures. Please see above output for more information."
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Migrate guest users from one ISE instance to another.",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "-c",
        "--config-file",
        type=str,
        required=False,
        default="config.ini",
        help="The path to the config file (default: config.ini).",
    )

    parser.add_argument(
        "-f",
        "--filter-sponsor",
        type=str,
        required=False,
        help="Only migrate accounts created by this sponsor username (default: no filter).",
    )

    args = parser.parse_args()

    config = configparser.ConfigParser()
    config.read(args.config_file)
    if (
        config["global"]["verify_ssl"] == "false"
        or config["global"]["verify_ssl"] == False
    ):
        verify_ssl = False
    else:
        verify_ssl = True

    source_ise_session = ISESession(
        config["source"]["server"],
        config["source"]["admin_user"],
        config["source"]["admin_user_password"],
        options={
            "verify": verify_ssl,
            "sponsor_api_user": config["source"]["sponsor_user"],
            "sponsor_api_password": config["source"]["sponsor_user_password"],
            "debug": False,
        },
    )
    source = ISE(source_ise_session)

    target_ise_session = ISESession(
        config["target"]["server"],
        config["target"]["admin_user"],
        config["target"]["admin_user_password"],
        options={
            "verify": verify_ssl,
            "sponsor_api_user": config["target"]["sponsor_user"],
            "sponsor_api_password": config["target"]["sponsor_user_password"],
            "debug": False,
        },
    )
    target = ISE(target_ise_session)

    main(source, target, args.filter_sponsor)
