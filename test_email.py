from mailer import send_email

if __name__ == "__main__":
    send_email(
        "ahmedhamedahmed911@gmail.com",
        "Weather alert test",
        "Hello king 👑, this is a test weather notification from your IoT project."
    )
    print("Email sent (if configuration is correct).")
