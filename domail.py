"""
This module contains the code that actually processes the emails in each account, 
and decides wether to delete or forward them.
"""

import os
import toml

from imap_tools import MailBox
from discord_webhook import DiscordWebhook


class Cope:
    """
    Docstring these nuts pylint
    """

    def __init__(self, do_discord=False):
        self.do_discord = False
        if do_discord:
            self.do_discord = True
            with open(".webhook", encoding="utf-8") as durl:
                self.discord_url = durl.read().strip()

        with open("annoying", encoding="utf-8") as ann:
            self.annoying = ann.read().strip().split("\n")

        with open("annoying_senders", encoding="utf-8") as senders:
            self.annoying_senders = senders.read().strip().split("\n")

        with open("forwarding_senders", encoding="utf-8") as frdsndrs:
            self.forwarding_senders = frdsndrs.read().strip().split("\n")

        with open("forwarding_subjects", encoding="utf-8") as fsubjs:
            self.forwarding_subjects = fsubjs.read().strip().split("\n")

    def log(self, text, host):
        """Something worth noting from account <host>, sending to discord if enabled and to file."""
        print(text)
        with open(f"email-{host}.log", "a+", encoding="utf-8") as thefile:
            thefile.write(text + "\n")
        if self.do_discord:
            webhook = DiscordWebhook(
                url=self.discord_url, content=text, rate_limit_retry=True
            )
            webhook.execute()

    def process(self, acc):
        """Operate on one specific account config"""

        deleted_total = 0
        msgs_total = 0

        with MailBox(host=acc["host"], port=acc["port"]).login(
            acc["email"], acc["password"], acc["mb"]
        ) as mailbox:
            for msg in mailbox.fetch(reverse=True):
                msgs_total += 1
                print(msg.subject, msg.date_str, msg.from_, msg.uid)
                forwarded = False
                for sender in self.forwarding_senders:
                    if sender in msg.from_:
                        self.log(
                            f"Forwarding {str(msg.uid)} because it was sent by '{sender}'",
                            acc["host"],
                        )
                        # Add code to forward the email here
                        forwarded = True
                for phrase in self.forwarding_subjects:
                    if phrase in msg.subject:
                        self.log(
                            f"Forwarding {str(msg.uid)} because of '{phrase}'",
                            acc["host"],
                        )
                        # Add code to forward the email here
                        forwarded = True
                for phrase in self.annoying:
                    if phrase in msg.subject and not forwarded:
                        self.log(
                            f"Deleting {str(msg.uid)} because of '{phrase}'",
                            acc["host"],
                        )
                        self.log(
                            f"Message info: {msg.subject} {msg.date_str} {msg.from_} {msg.uid}",
                            acc["host"],
                        )
                        mailbox.delete(msg.uid)
                        deleted_total += 1
                for sender in self.annoying_senders:
                    if sender in msg.from_ and not forwarded:
                        self.log(
                            f"Deleting {str(msg.uid)} b/c it was sent by '{sender}'",
                            acc["host"],
                        )
                        self.log(
                            f"Message info: {msg.subject} {msg.date_str} {msg.from_} {msg.uid}",
                            acc["host"],
                        )
                        mailbox.delete(msg.uid)
                        deleted_total += 1
                if not msg.subject.isascii():
                    self.log(
                        f"Deleting {str(msg.uid)} b/c it has weird characters.",
                        acc["host"],
                    )
                    self.log(
                        f"Message info: {msg.subject} {msg.date_str} {msg.from_} {msg.uid}",
                        acc["host"],
                    )
                    mailbox.delete(msg.uid)
                    deleted_total += 1
        if deleted_total != 0:
            self.log(f"Total deleted: {str(deleted_total)}", acc["host"])
        else:
            self.log("No messages deleted.", acc["host"])
        self.log("Total messages scanned: " + str(msgs_total), acc["host"])

        return (deleted_total, msgs_total)

    def process_all(self):
        """The main function which loops through configured accounts."""
        account_fns = []
        for files in os.listdir():
            if ".account_" in files:
                account_fns.append(files)

        grand_total = 0
        grand_msgs_total = 0

        for account_file in account_fns:
            acc = toml.load(account_file)
            print(f"Working on {acc['host']}")

            deleted_total, msgs_total = self.process(acc)

            grand_total += deleted_total
            grand_msgs_total += msgs_total

        return (len(account_fns), grand_total, grand_msgs_total)
