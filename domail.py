import os
import toml

from imap_tools import MailBox
from discord_webhook import DiscordWebhook


class cope:
    def __init__(self, do_discord=False):
        self.do_discord = False
        if do_discord:
            self.do_discord = True
            self.discord_url = open(".webhook").read().strip()
        self.annoying = open("annoying").read().strip().split("\n")
        self.annoying_senders = open("annoying_senders").read().strip().split("\n")

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
    
    def forward_email(self, msg, reason):
        self.log(f"Forwarding {str(msg.uid)} because of '{reason}'", msg.from_)
        # Add code to forward the email here
    
    def delete_email(self, msg, reason):
        self.log(f"Deleting {str(msg.uid)} because of '{reason}'", msg.from_)
        self.log(f"Message info: {msg.subject} {msg.date_str} {msg.from_} {msg.uid}", msg.from_)
        # Add code to delete the email here
    
    def log_message(self, msg, log_msg):
        self.log(log_msg, msg.from_)

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
                            self.forward_email(msg, f"it was sent by '{sender}'")
                            forwarded = True
                    for phrase in forwarding_subjects:
                        if phrase in msg.subject:
                            self.forward_email(msg, f"because of '{phrase}'")
                            forwarded = True
                    for phrase in self.annoying:
                        if phrase in msg.subject and not forwarded:
                            self.delete_email(msg, f"because of '{phrase}'")
                            deleted_total += 1
                    for sender in self.annoying_senders:
                        if sender in msg.from_ and not forwarded:
                            self.delete_email(msg, f"it was sent by '{sender}'")
                            deleted_total += 1
                    if not msg.subject.isascii():
                        self.delete_email(msg, f"it has weird characters.")
                        deleted_total += 1
            if deleted_total != 0:
                self.log(f"Total deleted: {str(deleted_total)}", acc["host"])
            else:
                self.log(f"No messages deleted.", acc["host"])
            self.log(f"Total messages scanned: " + str(msgs_total), acc["host"])

            grand_total += deleted_total
            grand_msgs_total += msgs_total


        return (len(account_fns), grand_total, grand_msgs_total)