import requests
import urllib3
from urllib.parse import urlunsplit, urlsplit, urlparse, urlunparse
import logging
from datetime import datetime
import base64
from .exception import *
import json

urllib3.disable_warnings(category=urllib3.exceptions.InsecureRequestWarning)


class ISESession:
    def __init__(self, hostname, username, password, **kwargs):
        options = kwargs["options"]

        port = options["port"] if "port" in options.keys() else 9060
        sslVerify = False if options["verify"] == False else True
        debug = options["debug"] if "debug" in options.keys() else False

        admin_auth_string = f"{username}:{password}"
        sponsor_auth_string = (
            f"{options['sponsor_api_user']}:{options['sponsor_api_password']}"
            if "sponsor_api_user" in options.keys()
            and "sponsor_api_password" in options.keys()
            else False
        )
        self.config = {
            "hostname": hostname,
            "username": username,
            "password": password,
            "admin_auth": "Basic " + self._b64e(admin_auth_string),
            "sponsor_auth": "Basic " + self._b64e(sponsor_auth_string)
            if sponsor_auth_string
            else False,
            "base_url": f"https://{hostname}:{str(port)}/ers/",
            "debug": debug,
        }

        # Create session using admin credentials
        self.admin = requests.Session()
        self.admin.headers["Authorization"] = self.config["admin_auth"]
        self.admin.headers["Content-Type"] = "application/json"
        self.admin.headers["Accept"] = "application/json"
        self.admin.verify = sslVerify

        if self.config["sponsor_auth"]:
            # Create session using sponsor credentials
            self.sponsor = requests.Session()
            self.sponsor.headers["Authorization"] = self.config["sponsor_auth"]
            self.sponsor.headers["Content-Type"] = "application/json"
            self.sponsor.headers["Accept"] = "application/json"
            self.sponsor.verify = sslVerify

        self.resources = {
            "guestuserall": {
                "target": "guestuser",
                "type": "config",
                "sponsor_auth": True,
                "pagination": True,
            },
            "guestuser": {
                "target": "guestuser",
                "type": "config",
                "sponsor_auth": True,
                "pagination": False,
            },
            "guesttypeall": {
                "target": "guesttype",
                "type": "config",
                "sponsor_auth": False,
                "pagination": True,
            },
            "guesttype": {
                "target": "guesttype",
                "type": "config",
                "sponsor_auth": False,
                "pagination": False,
            },
            "sponsorportalall": {
                "target": "sponsorportal",
                "type": "config",
                "sponsor_auth": False,
                "pagination": True,
            },
            "sponsorportal": {
                "target": "sponsorportal",
                "type": "config",
                "sponsor_auth": False,
                "pagination": False,
            },
        }
        self.logger = self.setup_logging()

    def setup_logging(self):
        log_format = "%(asctime)s - %(levelname)s - %(message)s"
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)

        # Create handlers
        console_handler = logging.StreamHandler()
        # file_handler = logging.FileHandler(
        #     "aciconn." + "{:%Y%m%d_%H-%M-%S}.log".format(datetime.now())
        # )

        # Set logging levels
        console_handler.setLevel(logging.DEBUG)
        # file_handler.setLevel(logging.DEBUG)

        # Create formatters and add it to handlers
        console_format = logging.Formatter("%(levelname)s: %(message)s")
        file_format = logging.Formatter(
            "%(threadName)s: %(asctime)s: %(name)s: %(levelname)s: %(message)s"
        )
        console_handler.setFormatter(console_format)
        # file_handler.setFormatter(file_format)

        # Add handlers to the logger
        logger.addHandler(console_handler)
        # logger.addHandler(file_handler)

        # return logger to class
        return logger

    def url(self, resource: str) -> str:
        api = self.resources[resource]
        return self.config["base_url"] + api["type"] + "/" + api["target"]

    def get(self, resource: str, id: str = None):
        # Find API Endpoint in resources data
        api = self.resources[resource]

        # Because the ISE API is garbo (i.e. does not always return pagination attributes when needed),
        # the most consistent way to handle pagination is by brute force. :)
        current_page = 1
        page_size = 10  # TODO: Set this to 100 for actual packaging.
        next = True
        results = []
        while next:
            url = self.url(resource) + "/" + id if id else self.url(resource)
            if api["pagination"]:
                url = self.paginate_url(url, current_page, page_size)
                # print(urlparse(url))

            # Log if debug flag set
            if self.config["debug"]:
                # TODO: Improve this logging.
                self.logger.debug("GOING TO: " + url)

            # If the API endpoint requires sponsor credentials, check to make sure they were provided. If so, use them instead
            if api["sponsor_auth"]:
                if not self.config["sponsor_auth"]:
                    raise SponsorAuthMissing(
                        "Sponsor credentials required for '"
                        + resource
                        + "'. Please initialise the ISEClient with sponsor_api_user and sponsor_api_password"
                    )
                response = self.sponsor.get(url)
            else:
                response = self.admin.get(url)

            # If response was OK, return data.
            if response.status_code == 200:
                o = json.loads(response.text)
                # If the result was in the form of SearchResults, strip some of the depth out before returning.
                if "SearchResult" in o.keys():
                    # For pagination sake, check if total is 0. If so, jump to return.
                    if o["SearchResult"]["total"] == 0:
                        next = False
                        continue
                    # The contents of o["SearchResult"]["resources"] should be an array when calling get all style
                    # APIs, and so should work with pagination.
                    results.extend(o["SearchResult"]["resources"])

                    # Again, API is garbo, and some endpoints return page 1 results on every page 🙃
                    # So, as additional check if results of page 1 are < page size, we've got them all.
                    if o["SearchResult"]["total"] < page_size:
                        next = False
                else:
                    # Otherwise, return the dict.
                    results = o
                    next = False
            else:
                raise ISEAPIError(response=response)

            if api["pagination"]:
                current_page += 1
        return results

    def paginate_url(self, url: str, page: int = 1, size: int = 100):
        return f"{url}?page={page}&size={size}"

    def _b64e(self, s: str) -> str:
        """Helper function to encode a string to base64"""
        return base64.b64encode(s.encode("ascii")).decode("ascii")

    def post(self, resource: str, payload: object):
        # Find API Endpoint in resources data
        api = self.resources[resource]
        url = self.url(resource)

        # Log if debug flag set
        if self.config["debug"]:
            # TODO: Improve this logging.
            self.logger.debug("GOING TO: " + url)

        # If the API endpoint requires sponsor credentials, check to make sure they were provided. If so, use them instead
        if api["sponsor_auth"]:
            if not self.config["sponsor_auth"]:
                raise SponsorAuthMissing(
                    "Sponsor credentials required for '"
                    + resource
                    + "'. Please initialise the ISEClient with sponsor_api_user and sponsor_api_password"
                )
            response = self.sponsor.post(url, json.dumps(payload))
        else:
            response = self.admin.post(url, json.dumps(payload))

        if response.status_code == 201:
            return True
        else:
            error = response.json()
            raise ISEAPIError(
                error["ERSResponse"]["messages"][0]["title"], response=response
            )
