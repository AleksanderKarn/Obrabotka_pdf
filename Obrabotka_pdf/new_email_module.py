import imaplib
import email
from email.header import decode_header

from settings import username, password, email_server, directory


def get_pdf_files_for_mails(part, directory, subject):

    if part.get_content_maintype() == 'multipart':
        for subpart in part.get_payload():

            get_pdf_files_for_mails(subpart, directory, subject)
    elif part.get_content_type() == 'application/pdf':
        try:
            filename = decode_header(part.get_filename())[0][0].decode()
            if filename.split(' ')[0] != 'Калькуляция':
                return

            filename_ = subject
            with open(f"pdf_files/{filename_}.pdf", 'wb') as f:
                print(f"Записали в PDF даныне из {filename_}")
                f.write(part.get_payload(decode=True))
        except Exception as e:
            print(e)


def connector_for_mail(username, password, email_server, directory):
    mail = imaplib.IMAP4_SSL(email_server)
    mail.login(username, password)

    mail.select('INBOX')

    result, data = mail.search(None, 'ALL')
    message_ids = data[0].split()
    subject = ''
    for message_id in message_ids:
        result, data = mail.fetch(message_id, '(RFC822)')
        raw_email = data[0][1]

        for response in data:
            if isinstance(response, tuple):
                msg = email.message_from_bytes(response[1])
                title, encoding = decode_header(msg["Subject"])[0]

                if isinstance(title, bytes):
                    try:
                        subject = title.decode(encoding).split('№')[1].replace(' ', '').replace('-', '_')
                    except Exception:
                        print()

        email_message = email.message_from_bytes(raw_email)
        if email_message.get_content_maintype() == 'multipart':
            for part in email_message.get_payload():
                get_pdf_files_for_mails(part, directory, subject)


    mail.close()
    mail.logout()


connector_for_mail(username, password, email_server, directory)