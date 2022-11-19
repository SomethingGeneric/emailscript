#!/usr/bin/env python3

import toml
from getpass import getpass

while True:
    action = input("Add a new account? (y or n): ")
    if action == "n":
        break
    else:
        data = {
            "host": input("Server hostname (sometimes imap.yourhost.com): "),
            "port": int(input("IMAP Port (check with your host): ")),
            "email": input("User login (sometimes your full address, check w/ host): "),
            "password": getpass(prompt="Password: "),
            "mb": input("Mailbox name (typically INBOX): "),
        }
        datastr = toml.dumps(data)
        with open(f".account_{data['host']}", "w") as f:
            f.write(datastr)
