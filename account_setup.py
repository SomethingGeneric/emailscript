#!/usr/bin/env python3

"""
Utility to set up the accounts
"""

from getpass import getpass
import toml

while True:
    action = input("Add a new account? (y or n): ")
    if action == "y":
        data = {
            "host": input("Server hostname (sometimes imap.yourhost.com): "),
            "port": int(input("IMAP Port (check with your host): ")),
            "email": input("User login (sometimes your full address, check w/ host): "),
            "password": getpass(prompt="Password: "),
            "mb": input("Mailbox name (typically INBOX): "),
            "forwarding_address": input(
                "Forwarding email address (optional, leave blank if not needed): "
            ),
        }
        datastr = toml.dumps(data)
        with open(f".account_{data['host']}", "w", encoding="utf-8") as f:
            f.write(datastr)
