from imap_tools import MailBox

host = "tar.black"
port = 993
# assumes SSL/TLS

email = "matt@tar.black"
password = open(".password").read().strip()

mb_name = "INBOX"

data = []

if __name__ == "__main__":
    with MailBox(host).login(email, password, mb_name) as mailbox:
        for msg in mailbox.fetch(reverse=True):
            if msg.to != email:
                print(msg.from_ + " sent an email to " + str(msg.to))
                data.append(msg.from_ + " sent an email to " + str(msg.to))
    with open("data.txt","w") as f:
        f.write("\n".join(data))