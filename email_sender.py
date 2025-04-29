# import smtplib
# from email.message import EmailMessage

# def send_email_with_map(attachment_path):
#     msg = EmailMessage()
#     msg['Subject'] = 'Walk Tracker Report'
#     msg['From'] = 'himanshukumaranand3670@gmail.com'
#     msg['To'] = ["thakuranand2650@gmail.com"]

#     msg.set_content('Please find attached the walk tracker report.')

#     with open(attachment_path, 'rb') as f:
#         file_data = f.read()
#         msg.add_attachment(file_data, maintype='application', subtype='pdf', filename='WalkReport.pdf')

#     # Using TLS (recommended)
#     with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
#         smtp.starttls()
#         smtp.login('himanshukumaranand3670@gmail.com', 'ocki cuvx xlxp phva')
#         smtp.send_message(msg)


import smtplib
from email.message import EmailMessage

def send_email_with_map(attachment_path):
    msg = EmailMessage()
    msg['Subject'] = 'Walk Tracker Report'
    msg['From'] = 'himanshukumaranand3670@gmail.com'  # Use your email here
    msg['To'] = ["thakuranand2650@gmail.com"]  # Use the recipient's email

    msg.set_content('Please find attached the walk tracker report.')

    with open(attachment_path, 'rb') as f:
        file_data = f.read()
        msg.add_attachment(file_data, maintype='application', subtype='pdf', filename='WalkReport.pdf')

    # Using TLS (recommended)
    with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
        smtp.starttls()
        smtp.login('himanshukumaranand3670@gmail.com', 'ocki cuvx xlxp phva')  # Use your actual credentials
        smtp.send_message(msg)
