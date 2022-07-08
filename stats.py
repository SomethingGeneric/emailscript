from imap_tools import MailBox

host = "tar.black"
port = 993
# assumes SSL/TLS

email = "matt@tar.black"
password = open(".password").read().strip()

mb_name = "INBOX"

data = {}

if __name__ == "__main__":
    with MailBox(host).login(email, password, mb_name) as mailbox:
        for msg in mailbox.fetch(reverse=True):
            if msg.from_ in data:
                data[msg.from_] += 1
                print(msg.from_ + " incremented to " + str(data[msg.from_]))
            else:
                data[msg.from_] = 1
                print(msg.from_ + " added for the first time.")
    new = sorted((value,key) for (key,value) in data.items())
    print(new)
    with open("stats.txt", "w") as f:
        for k,v in data.items():
            f.write(k + ": " + str(v) + "\n")