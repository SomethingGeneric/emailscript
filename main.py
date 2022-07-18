from imap_tools import MailBox
import os,shutil
from random import randint
from discord_webhook import DiscordWebhook

host = "tar.black"
port = 993
# assumes SSL/TLS

email = "matt@tar.black"
password = open(".password").read().strip()

mb_name = "INBOX"

discord_url = open(".webhook").read().strip()

annoying = [
    "Price alert",
    "Cron",
    "Google Alert",
    "ACM TechNews",
    "Postmates",
    "Dreamstime",
    "DoorDash",
    "Private_photos",
    "Private_photo",
    "Profile_with_photo",
    "Direct_message",
    "Private_profile",
]
annoying_senders = [
    "donotreply@speedydock.com",
    "no-reply@email.alltrails.com",
    "info@i.drop.com",
    "diagnosis@mail.codealchemi.com",
    "news@georgetowncupcake.com"
]


def do_log(text):
    print(text)
    with open("program.log", "a+") as f:
        f.write(text + "\n")
    webhook = DiscordWebhook(url=discord_url, content=text, rate_limit_retry=True)
    webhook.execute()


if __name__ == "__main__":
    if os.path.exists("program.log"):
        shutil.move("program.log", "program.log." + str(randint(1,10000)))
    deleted_total = 0
    msgs_total = 0
    with MailBox(host).login(email, password, mb_name) as mailbox:
        for msg in mailbox.fetch(reverse=True):
            msgs_total += 1
            print(msg.subject, msg.date_str, msg.from_, msg.uid)
            for phrase in annoying:
                if phrase in msg.subject:
                    do_log("Deleting " + str(msg.uid) + " because of '" + phrase + "'")
                    do_log("Message info: " + msg.subject + " " + msg.date_str + " " + msg.from_ + " " + msg.uid)
                    mailbox.delete(msg.uid)
                    deleted_total += 1
            for sender in annoying_senders:
                if sender in msg.from_:
                    do_log("Deleting " + str(msg.uid) + " b/c it was sent by " + sender)
                    do_log("Message info: " + msg.subject + " " + msg.date_str + " " + msg.from_ + " " + msg.uid)
                    mailbox.delete(msg.uid)
                    deleted_total += 1
            if not msg.subject.isascii():
                do_log("Deleting " + str(msg.uid) + " b/c it has weird characters.")
                do_log("Message info: " + msg.subject + " " + msg.date_str + " " + msg.from_ + " " + msg.uid)
                mailbox.delete(msg.uid)
                deleted_total += 1
    if deleted_total != 0:
        do_log("Total deleted: " + str(deleted_total))
    else:
        do_log("No messages deleted.")
    do_log("Total messages scanned: " + str(msgs_total))
