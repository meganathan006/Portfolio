from fastapi import FastAPI, Form, Request
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import re
import dns.resolver

app = FastAPI()

# Serve static files (CSS, JS, images, etc.)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set up Jinja2 templates
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    # Serve the index.html file directly
    with open("index.html") as f:
        content = f.read()
    return HTMLResponse(content=content)

# Email validation function
def is_valid_email(email: str) -> bool:
    # Check email format
    email_regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    if not re.match(email_regex, email):
        return False
    
    # Check domain validity
    domain = email.split('@')[-1]
    try:
        # Check for MX records
        mx_records = dns.resolver.resolve(domain, 'MX')
        return bool(mx_records)
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
        return False

    return True

@app.post("/send_email")
async def send_email(request: Request, name: str = Form(...), email: str = Form(...), message: str = Form(...)):
    sender_email = "mp9597000@gmail.com"  # Replace with your email
    receiver_email = "mp9597000@gmail.com"  # Replace with your email (to receive messages)
    app_password = "cerzydbbdutfzrbq"  # Replace with your app password

    # Validate the email address
    if not is_valid_email(email):
        return {"status": "Failed to send message", "error": "Invalid email address"}

    # Create the email content
    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg["Subject"] = "New Contact Form Portfolio"
    
    body = f"Name: {name}\nEmail: {email}\nMessage: {message}"
    msg.attach(MIMEText(body, "plain"))

    try:
        # Connect to the SMTP server
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()  # Secure the connection
            server.login(sender_email, app_password)  # Use app password
            server.sendmail(sender_email, receiver_email, msg.as_string())
        
        # Redirect to success page
        return RedirectResponse(url="/success", status_code=303)
        
    except smtplib.SMTPAuthenticationError:
        return {"status": "Failed to send message", "error": "Authentication failed. Check your email and password."}
    except smtplib.SMTPException as e:
        return {"status": "Failed to send message", "error": str(e)}

@app.get("/success", response_class=HTMLResponse)
async def success_page(request: Request):
    return templates.TemplateResponse("success.html", {"request": request})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
