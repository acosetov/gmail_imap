import imaplib, email
import csv
from bs4 import BeautifulSoup
import gmailconfig as config


#Remove all css and html tags from email body
def cleanMe(html):
    soup = BeautifulSoup(html,  features = "lxml")
    for script in soup(["script", "style"]):
        script.extract()
    # get text
    text = soup.get_text()
    # break into lines and remove leading and trailing space on each
    lines = (line.strip() for line in text.splitlines())
    # break multi-headlines into a line each
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    # drop blank lines
    text = '\n'.join(chunk for chunk in chunks if chunk)
    return text


def read_email():
    m = imaplib.IMAP4_SSL("imap.gmail.com", 993)
    m.login(config.account_email,config.account_passw)
    # grab all emails, if you need just inbox use like this m.select('INBOX')
    m.select('"[Gmail]/All Mail"')

    status, data = m.uid('search', None, "ALL")
    for num in data[0].split():
        try:
            result, data = m.uid('fetch', num, '(RFC822)')
            msg = email.message_from_bytes(data[0][1])
            msg_subject = msg["Subject"]
            if msg_subject:
                body = ""
                if msg.is_multipart():
                    for part in msg.walk():
                        type = part.get_content_type()
                        disp = str(part.get('Content-Disposition'))
                        if type == 'text/plain' and 'attachment' not in disp:
                            charset = part.get_content_charset()
                            body = part.get_payload(decode=True).decode(encoding=charset, errors="ignore")
                            clean_body = body.replace("\r\n", " ")
                            clean_body = body.replace("n", " ")
                            messages.append(
                                {'num': num, 
                                'From': msg["From"], 
                                'To': msg["To"], 
                                'Subject': msg["Subject"],
                                'body': clean_body}
                            )
                else:
                    charset = msg.get_content_charset()
                    body = msg.get_payload(decode=True).decode(encoding=charset, errors="ignore")
                    clean_body = cleanMe(body)
                    clean_body = clean_body.replace("\r\n", " ")
                    clean_body = clean_body.replace("\n", " ")
                    messages.append(
                        {'num': num, 
                        'From': msg["From"], 
                        'To': msg["To"], 
                        'Subject': msg["Subject"],
                        'body': clean_body}
                    )
        except Exception as e:
            print(str(e))

messages = []
read_email()

with open('mails.csv', mode='w') as mail_file:
    mail_writer = csv.writer(mail_file, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)

    for message in messages:
        mail_writer.writerow([message['From'], message['To'], message['Subject'], message['body']])



