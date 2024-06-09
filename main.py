from fastapi import FastAPI, File, UploadFile, HTTPException ,Request ,Form , Query
import mysql.connector
import uvicorn
import json
from pathlib import Path
from datetime import datetime
import hashlib
import os
import base64
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from fastapi.responses import FileResponse
from itsdangerous import URLSafeTimedSerializer


mydb = mysql.connector.connect(
    host = "localhost",
    user = "root",
    password = "4321"
)

cursor = mydb.cursor()
cursor.execute("use Users") 

UPLOAD_DIRECTORY = "uploaded_files"
SECRET_KEY = "7Hl5 i5 4 S3CR3T K3Y" # A better approach is to rotate the secret key periodically (eg: every 1hr).
SIGNER = URLSafeTimedSerializer(SECRET_KEY)
EXPIRATION_TIME = 3600  # URL valid for 1 hour


# Ensure the upload directory exists
if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)


# Generate a random salt
def generate_salt():
    return base64.b64encode(os.urandom(16)).decode('utf-8')[:15]
     

# Generate email verification token
def generate_verification_token():
    random_bytes = os.urandom(32)
    token = base64.urlsafe_b64encode(random_bytes)
    return token.decode('utf-8')

# Hash the password with salt
def hash_password(password, salt):
    pwdhash = hashlib.sha256(password.encode() + salt.encode()).hexdigest()
    return pwdhash

# Verify the password
def verify_password(stored_password, provided_password, salt):
    return stored_password == hash_password(provided_password, salt)


def send_verification_email(user_name,user_email,token):
    try:
        subject = 'Email Verification'
        YOUR_GOOGLE_EMAIL = 'balajim06082003@gmail.com'
        YOUR_GOOGLE_EMAIL_APP_PASSWORD = 'rewm svwp pkug wvac'  
        smtpserver = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        smtpserver.ehlo()
        smtpserver.login(YOUR_GOOGLE_EMAIL, YOUR_GOOGLE_EMAIL_APP_PASSWORD)
        sent_from = YOUR_GOOGLE_EMAIL
        sent_to = user_email

        msg = MIMEMultipart()
        msg['From'] = sent_from
        msg['To'] = sent_to
        msg['Subject'] = subject
        # the html of the email being sent 
        email_body = f"""
        <html>
            <body style="height: 30%;padding: 15px 32px" >
                <p>Click here to verify your email.</p>
                <div style="height: 30%;padding: 15px 32px"><a href="http://127.0.0.1:8000/emailVerification?user_name={user_name}&token={token}" style="background-color: #549bff; color: white; padding: 15px 32px; text-decoration: none;  font-size: 16px; border-radius: 3px; cursor: pointer;">Verify </div>
            </body>
        </html>
        """
        msg.attach(MIMEText(email_body, 'html'))
        smtpserver.send_message(msg)
        smtpserver.quit()
        return "successful"
    except:
        return "failed"


# Checks if the user belongs to the particular type 
def checkUser(user_name,requiredType):
    try:
        sql = "SELECT user_type from user WHERE user_name = (%s) "
        val = (user_name,)
        cursor.execute(sql,val)
        userTypeFetched = cursor.fetchone()
        print(userTypeFetched,requiredType)
        if userTypeFetched[0] != requiredType:
            return HTTPException(status_code=403, detail="Operation not allowed")
    except:
        return HTTPException(status_code=404, detail="Username doesn't exist")



app = FastAPI()


@app.get("/emailVerification")
async def verifyEmail(user_name: str = Query(...), token: str = Query(...)):
    print(user_name, token)
    sql = "SELECT verification_token from user WHERE user_name = (%s) "
    val = (user_name,)
    cursor.execute(sql,val)
    tokenFetched = cursor.fetchone()[0]
    if token != tokenFetched:
        return {"error" : "verification failed"}
    
    query = "UPDATE user SET email_verified = 1 WHERE user_name = (%s)"
    cursor.execute(query, (user_name,))
    mydb.commit()
    
    return {"message": "Email verified successfully"}

@app.get("/login")
async def user_login(request: Request):
    body = await request.json()
    user_name = body["user_name"]
    
    sql = "SELECT * from user WHERE user_name = (%s) "
    val = (user_name,)
    cursor.execute(sql,val)
    if not cursor.fetchone():
        raise HTTPException(status_code=409, detail="No user found")
    
    user_passowrd = body["password"]
    
    
    sql = "SELECT hashed_password,salt from user WHERE user_name = (%s) "
    val = (user_name,)
    # This query format is SQL injection resistant.
    cursor.execute(sql,val)
    detailsFetched = cursor.fetchone()
    passwordFetched = detailsFetched[0]
    saltFetched = detailsFetched[1]
    if not verify_password(passwordFetched, user_passowrd,saltFetched):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    return {"message": "login successful"}


@app.get("/allUploadedFiles")
async def getAllfiles():
    sql = "SELECT file_name from files"
    cursor.execute(sql)
    filesFetched = cursor.fetchall()
    return filesFetched


@app.post("/signUp/")
async def signUp(request: Request):
    body = await request.json()
    user_name = body["user_name"] 
    user_email = body["user_email"]
    verification_token = generate_verification_token()
    salt = generate_salt()
    hashed_password = hash_password(password=body["password"],salt=salt)
    user_type = 0
    
    # Check if username already exists
    sql = "SELECT * from user WHERE user_name = (%s) "
    val = (user_name,)
    cursor.execute(sql,val)
    if cursor.fetchone():
        raise HTTPException(status_code=409, detail="Username already exists")
    
    # Creates a new user
    sql = "INSERT INTO user (user_name, user_email,verification_token,salt,hashed_password,user_type) VALUES (%s, %s, %s, %s, %s, %s)"
    val = (user_name, user_email, verification_token, salt, hashed_password, user_type)
    cursor.execute(sql,val)
    mydb.commit()
    
    
    send_verification_email(user_name,user_email,verification_token)
    return {"encrypted_url" : verification_token}

@app.get("/generate-download-url")
async def generate_download_url(user_name: str = Query(...), file_name: str = Query(...)):
    
    file_path = os.path.join(UPLOAD_DIRECTORY, file_name)
    print(file_path)
    if os.path.exists(file_path):
        data = json.dumps({"file_name":file_name,"user_name":user_name})
        token = SIGNER.dumps(data)
        download_url = f"http://127.0.0.1:8000/download/{token}"
        return {"download_url": download_url,"message" : "Success"}
    else:
        raise HTTPException(status_code=404, detail="File not found")


@app.get("/download/{token}")
async def download_file(token ):
    try:
        data = json.loads(SIGNER.loads(token, max_age=EXPIRATION_TIME))
        file_name = data["file_name"]
        user_name = data["user_name"]
        # checks if the user belongs to client users
        error = checkUser(user_name,1)
        if error:
            return error
        file_path = os.path.join(UPLOAD_DIRECTORY, file_name)
        print(file_path,file_name)
        print(os.path.exists(file_path))
        if os.path.exists(file_path):
            return FileResponse(file_path, media_type='application/octet-stream', filename=file_name)
        else:
            raise HTTPException(status_code=404, detail="File not found")
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid or expired token")



@app.post("/upload")
async def upload_file(user_name: str = Form(...),file: UploadFile = File(...)):
    
    # checks if the user belongs to operation users
    error = checkUser(user_name,1)
    if error:
        return error
    
    # checking with extenstions can be vulnerable
    if file.content_type not in ["application/vnd.openxmlformats-officedocument.wordprocessingml.document", 
                                 "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", 
                                 "application/vnd.openxmlformats-officedocument.presentationml.presentation"]:
        raise HTTPException(status_code=400, detail="Invalid file type")
    
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    original_filename = file.filename
    file_extension = Path(original_filename).suffix
    new_filename = f"{original_filename}_{timestamp}{file_extension}"
    file_location = "./Uploaded_Files"
    
    sql = "INSERT INTO files (user_name,file_name) VALUES (%s, %s)"
    val = (user_name,new_filename)
    cursor.execute(sql,val)
    mydb.commit()    

    file_location = os.path.join(UPLOAD_DIRECTORY, new_filename)
    with open(file_location, "wb") as file_object:
        file_object.write(await file.read())
    return {"info": f"file '{new_filename}' uploaded"}



if __name__ == '__main__':
    uvicorn.run("main:app",host="127.0.0.1",reload=True)