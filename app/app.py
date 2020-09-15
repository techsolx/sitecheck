#!/usr/bin/env python3

import urllib.request
import json
import hashlib
import logging
import sys

logging.basicConfig(stream=sys.stderr, level=logging.CRITICAL)

# stuff to fake
headers = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:80.0) Gecko/20100101 Firefox/80.0"
    )
}


def load_json_data(filename):
    """ load named json file """
    with open(filename) as f:
        return json.loads(f.read())


def save_json_data(data, filename):
    """ save named json file """
    with open(filename, "w") as outfile:
        json.dump(data, outfile)


def check_site(site, needle, headers):
    """given site, needle, and headers,
    check site for needle, pass headers
    to not run afoul of those that check."""
    try:
        req = urllib.request.Request(site, headers=headers)
        with urllib.request.urlopen(req) as response:
            b_needle = needle.encode("utf-8")
            haystack = response.read()
            fresh_hash = hashlib.sha256(haystack).hexdigest()
            if b_needle in haystack:
                return True, fresh_hash
            else:
                return False, fresh_hash
    except urllib.error.URLError as e:
        return e.reason


def get_new_hash(site, headers):
    """Get hash of site, for sites that
    change with every request, this will change."""
    req = urllib.request.Request(site, headers=headers)
    with urllib.request.urlopen(req) as response:
        haystack = response.read()
        return hashlib.sha256(haystack).hexdigest()


def call_forhelp(site, needle):
    """stub out for process to contact help,
    either send email or sns or some other process."""
    if not needle:
        print(f"call_forhelp {site} hash has changed")
    else:
        print(f"call_forhelp {site} has changed,")
        print(f'check this line: "{needle}" for changes')


test = {
    "https://packages.ubuntu.com/xenial/ubuntu-minimal": ["ubuntu-minimal (1.351)", ""],
    "https://google.com": ["", ""],
}


def main():
    """
    Using site data from json file check site
    to see if needle exists on site, or to see if site
    hash has changed, if it has contact help as action
    may be needed.
    """
    # data = test
    data = load_json_data("sites.json")

    logging.debug(data)

    for site, value in data.items():
        print("\n")
        needle = value[0]
        site_hash = value[1]

        if not site_hash:
            value[1] = get_new_hash(site, headers)
            site_hash = value[1]
            logging.info("Adding new site hash for: {}".format(site))

        if needle:
            print(
                (
                    f"site is {site} needle to check is {needle},"
                    f"hash to check is {site_hash}"
                )
            )
        else:
            print(f"site is {site} hash to check is {site_hash}")

        status, fresh_site_hash = check_site(site, needle, headers)
        if fresh_site_hash != site_hash:
            value[1] = fresh_site_hash
            call_forhelp(site, "")
        elif status and not needle:
            print(f"No changes on {site}")
        elif status and (fresh_site_hash == site_hash):
            print(f"No changes on {site} for {needle}")
        else:
            value[1] = fresh_site_hash
            call_forhelp(site, needle)

    save_json_data(data, "sites.json")


if __name__ == "__main__":
    main()
