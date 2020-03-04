import imaplib, email
import gmailconfig as config

m = imaplib.IMAP4_SSL("imap.gmail.com", 993)
m.login(config.account_email,config.account_passw)

#Get list of folders from gmail box
for i in m.list()[1]:
    l = i.decode().split(' "/" ')
    print(l[0] + " = " + l[1])