from imap_tools import MailBox
from discord_webhook import DiscordWebhook
import os
import toml


class cope:
    def __init__(self, do_discord=False):
        self.do_discord = False
        if do_discord:
            self.do_discord = True
            self.discord_url = open(".webhook").read().strip()

        self.annoying = open("annoying").read().strip().split("\n")
        self.annoying_senders = open("annoying_senders").read().strip().split("\n")

    def log(self, text, host):
        print(text)
        with open(f"email-{host}.log", "a+") as f:
            f.write(text + "\n")
        if self.do_discord:
            webhook = DiscordWebhook(
                url=self.discord_url, content=text, rate_limit_retry=True
            )
            webhook.execute()

    def go(self):
        account_fns = []
        for f in os.listdir():
            if ".account_" in f:
                account_fns.append(f)

        grand_total = 0
        grand_msgs_total = 0

        for account_file in account_fns:
            acc = toml.load(account_file)
            print(f"Working on {acc['host']}")
            forwarding_senders = open("forwarding_senders").read().strip().split("\n")
            forwarding_subjects = open("forwarding_subjects").read().strip().split("\n")

            deleted_total = 0
            msgs_total = 0

            with MailBox(host=acc["host"], port=acc["port"]).login(
                acc["email"], acc["password"], acc["mb"]
            ) as mailbox:
                for msg in mailbox.fetch(reverse=True):
                    msgs_total += 1
                    print(msg.subject, msg.date_str, msg.from_, msg.uid)
                    forwarded = False
                    for sender in forwarding_senders:
                        if sender in msg.from_:
                            self.log(
                                f"Forwarding {str(msg.uid)} because it was sent by '{sender}'",
                                acc["host"],
                            )
                            # Add code to forward the email here
                            forwarded = True
                    for phrase in forwarding_subjects:
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
                self.log(f"No messages deleted.", acc["host"])
            self.log(f"Total messages scanned: " + str(msgs_total), acc["host"])

            grand_total += deleted_total
            grand_msgs_total += msgs_total


        return (len(account_fns), grand_total, grand_msgs_total)