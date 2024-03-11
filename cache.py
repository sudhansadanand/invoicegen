import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

def send_email(pdf_filename, recipient_email):
    # Email configuration
    sender_email = "new.invoice.gen@gmail.com"
    sender_password = "InvoiceGen*187"

    subject = "Invoice"
    body = "Please find attached your Invoice"

    # Create the email message
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    # Attach the PDF file
    with open(pdf_filename, "rb") as pdf_file:
        pdf_attachment = MIMEApplication(pdf_file.read(), _subtype="pdf")
        pdf_attachment.add_header('Content-Disposition', f'attachment; filename={pdf_filename}')
        msg.attach(pdf_attachment)

    # Send the email
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipient_email, msg.as_string())
        server.quit()


send_email("2345__31-01-2024.pdf","sudhansadanand@gmail.com")