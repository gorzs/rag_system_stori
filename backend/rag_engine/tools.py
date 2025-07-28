# This module is responsible for sending escalation emails to human agents
import smtplib
from email.message import EmailMessage

email_escalation="gabortzsanz@gmail.com"

def send_escalation_email(user_id, question, conversation_history):
    msg = EmailMessage()
    msg["Subject"] = f"Escalation Needed: User {user_id}"
    msg["From"] = "mexicanrevolution@gmail.com"
    msg["To"] = email_escalation

    msg.set_content(f"""
The following question from user {user_id} requires attention:

"{question}"

Here is the conversation so far:

"{conversation_history}"

Please follow up as soon as possible.
""")

    try:
        #  SMTP server - Gmail
        with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
            smtp.starttls()
            smtp.login(email_escalation, "bxiw nkac yxlo qxox")
            smtp.send_message(msg)
        print("Escalation email sent to a human agent.")
    except Exception as e:
        print("Failed to send email:", str(e))
