# import smtplib
# from email.message import EmailMessage

# def send_email_with_map(attachment_path):
#     msg = EmailMessage()
#     msg['Subject'] = 'Walk Tracker Report'
#     msg['From'] = ''
#     msg['To'] = [""]

#     msg.set_content('Please find attached the walk tracker report.')

#     with open(attachment_path, 'rb') as f:
#         file_data = f.read()
#         msg.add_attachment(file_data, maintype='application', subtype='pdf', filename='WalkReport.pdf')

#     # Using TLS (recommended)
#     with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
#         smtp.starttls()
#         smtp.login('', '')
#         smtp.send_message(msg)


import smtplib
from email.message import EmailMessage

def send_email_with_map(attachment_path):
    msg = EmailMessage()
    msg['Subject'] = 'Walk Tracker Report'
    msg['From'] = ''  # Use your email here
    msg['To'] = [""]  # Use the recipient's email

    msg.set_content('Please find attached the walk tracker report.')

    with open(attachment_path, 'rb') as f:
        file_data = f.read()
        msg.add_attachment(file_data, maintype='application', subtype='pdf', filename='WalkReport.pdf')

    # Using TLS (recommended)
    with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
        smtp.starttls()
        smtp.login('', '')  # Use your actual credentials
        smtp.send_message(msg)
