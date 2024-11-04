def generate_email_template(otp):
    return f"""
    <html>
        <body>
            <h2>Your OTP for Registration</h2>
            <p>Use the following One-Time Password (OTP) to complete your registration:</p>
            <h3>{otp}</h3>
            <p>This OTP is valid for a limited time only. Do not share it with anyone.</p>
            <br>
            <p>Thank you,</p>
            <p>The Team</p>
        </body>
    </html>
    """
