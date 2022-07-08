from imap_tools import MailBox
import os

host = "tar.black"
port = 993
# assumes SSL/TLS

email = "matt@tar.black"
password = open(".password").read().strip()

mb_name = "INBOX"

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
]

if __name__ == "__main__":
    break_uid = None
    if os.path.exists("last_uid"):
        break_uid = int(open("last_uid").read())
    this_uid = 0
    with MailBox(host).login(email, password, mb_name) as mailbox:
        for msg in mailbox.fetch(reverse=True):
            this_uid = msg.uid
            if break_uid != None and msg.uid == break_uid:
                break
            print(msg.subject, msg.date_str, msg.from_, msg.uid)
            for phrase in annoying:
                if phrase in msg.subject:
                    print("Deleting because of " + phrase)
                    mailbox.delete(msg.uid)
            for sender in annoying_senders:
                if sender in msg.from_:
                    print("Deleting b/c sent by " + sender)
                    mailbox.delete(msg.uid)
    with open("last_uid", "w") as f:
        f.write(str(this_uid))
