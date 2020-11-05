# Overview
This command-line python tool pulls all the guests from an ISE instance and pushes those guests to another ISE server. This is to facilitate large guest populations that must be maintained during an ISE migration where a standard upgrade or backup/restore is not being performed. 

# ISE Requirements
This was tested on ISE 2.7, but should work up to ISE 3.0 and back to ISE 2.2 or previous based on API release notes.

The ISE ERS API must be enabled, and a sponsor account must have API access. [Please see here for more information](https://community.cisco.com/t5/security-documents/ise-guest-sponsor-api-tips-amp-tricks/ta-p/3636773).

Should be run using Python 3.6+.

**Warning**: There is no confirmation or rollback options, use at your own risk.

# Install
Clone (or download):  

`git clone https://github.com/ironbow/ise-guest-migrator.git`

Install requirements: 

`pip install -r requirements.txt`
**Note**: Depending on the system, you may need to specify `pip3` for Python3's PIP instance.

Configure: 

Edit the `config.template.ini` to use appropriate values, and rename to `config.ini`.

Run:

* Run with defaults: `python migrate-guests.py`
* Run with a sponsor username filter: `python migrate-guests.py -f john.doe`
* Run with custom config file: `python migrate-guests.py -c /path/to/my/config.ini`

**Note**: Depending on the system, you may need to specify `python3`, `python3.7`, etc. for Python3.

# Caveats

* If only one sponsor portal is configured on the target system, it will be used to create the guests. If more than one exists, the user will be prompted to select the portal to use.
* If a guest account with the same username already exists (or other conflicts), the guest account will not be migrated. An error will be displayed, but the script will continue.
* The same Guest Type (by name) must exist on the target system for all guest users. Ideally, the guest types should have identical configurations to prevent errors.
* Any errors aside from the username already existing will cause the script to exit.

# Usage
```
usage: migrate-guests.py [-h] [-c CONFIG_FILE] [-f FILTER_SPONSOR]

Migrate guest users from one ISE instance to another.

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIG_FILE, --config-file CONFIG_FILE
                        The path to the config file (default: config.ini).
  -f FILTER_SPONSOR, --filter-sponsor FILTER_SPONSOR
                        Only migrate accounts created by this sponsor username (default: no filter).
```
# Example Output
```
python migrate-guests.py -f admin
Getting data from source ISE server...
        Found 205 total guest accounts.
Getting data from target ISE server...
        Found 1 sponsor portal.
        Proceeding with Sponsor Portal (default)
Pushing configs into target ISE server...
        Only migrating accounts created by sponsor 'admin'.
        Creating new guest contractor_2m59tt704... SUCCEEDED.
        Creating new guest contractor_2m59ttlm8NCT... SUCCEEDED.
        <output truncated>
        Creating new guest gonee1lIET... SUCCEEDED.
        Creating new guest gonee1lduq4UF... SUCCEEDED.
FINAL REPORT:
        Only accounts created by admin were migrated.
        Created a total of 88 guest accounts on target ISE server.
        There were 0 failures. Please see above output for more information.
```

# License
Licensed under the [MIT License](https://choosealicense.com/licenses/mit/).