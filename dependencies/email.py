from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import random
from dependencies import mongo
from models.opportunities import Job
from datetime import datetime, timedelta
from fastapi.responses import JSONResponse
import key

def generate_otp():
    return str(random.randint(100000, 999999))

def send_otp(email: str):
    with open("dependencies/mail-content/verify-mail.html", "r") as file:
        html_content = file.read()
    otp = generate_otp()
    html_content = html_content.replace("123456", f"{otp}")
    expiration_time = datetime.utcnow() + timedelta(minutes=5)
    mongo.db.pendingusers.update_one({"email": email},{"$set": {"otp": otp, "expiration_time": expiration_time}},upsert=True)
    subject = 'OTP for Account Verification'
    email_user = key.EMAIL_LOGIN
    email_password = key.EMAIL_PASS
    msg = MIMEMultipart()
    msg['From'] = key.EMAIL_USER
    msg['To'] = email
    msg['Subject'] = subject
    msg.attach(MIMEText(html_content,'html'))
    try:
        with smtplib.SMTP(key.EMAIL_SERVER, 587) as server:
            server.starttls()
            server.login(email_user, email_password)

            # Sending the email
            server.sendmail(key.EMAIL_USER, [email], msg.as_string())

        return JSONResponse(content={"message": "Email sent successfully"}, status_code=200)
    except Exception as e:
        print(f"Error sending OTP to {email}: {e}")
        return JSONResponse(content={"message": "Error occurred in sending email"}, status_code=404)
    
def send_opportunity(email: str, job : Job):
    with open("dependencies/mail-content/opportunity.html", "r") as file:
        html_content = file.read()
    html_content = html_content.replace("*|companyname|*", job.companyName)
    html_content = html_content.replace("*|role|*", job.role)
    html_content = html_content.replace("*|link|*", job.applicationLink)
    html_content = html_content.replace("*|date|*", job.date)
    html_content = html_content.replace("*|contributor|*", job.contributor)
    html_content = html_content.replace("*|econtributor|*", job.contributorEmail)
    subject = '[Placement News] New Opportunity for you'
    email_user = key.EMAIL_LOGIN
    email_password = key.EMAIL_PASS
    msg = MIMEMultipart()
    msg['From'] = key.EMAIL_USER
    msg['To'] = email
    msg['Subject'] = subject
    msg.attach(MIMEText(html_content,'html'))
    try:
        with smtplib.SMTP(key.EMAIL_SERVER, 587) as server:
            server.starttls()
            server.login(email_user, email_password)

            # Sending the email
            server.sendmail(key.EMAIL_USER, [email], msg.as_string())

        return JSONResponse(content={"message": "Email sent successfully"}, status_code=200)
    except Exception as e:
        print(f"Error sending OTP to {email}: {e}")
        return JSONResponse(content={"message": "Error occurred in sending email"}, status_code=404)