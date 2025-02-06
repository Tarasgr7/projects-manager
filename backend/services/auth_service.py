import os
import smtplib
from datetime import datetime,timedelta
from typing import Annotated


from ..models.users_models import Users

from ..dependencies import SECRET_KEY,ALGORITHM,EMAIL_PASSWORD,EMAIL_ADDRESS,logger

from fastapi import Depends,HTTPException,status
from fastapi.security import OAuth2PasswordRequestForm,OAuth2PasswordBearer

from passlib.context import CryptContext
from jose import jwt,JWTError
from dotenv import load_dotenv

from email.message import EmailMessage

from jinja2 import Environment, FileSystemLoader


email_templates_env = Environment(loader=FileSystemLoader("backend/templates"))

oauth2_bearer=OAuth2PasswordBearer(tokenUrl='auth/token')

bcrypt_context=CryptContext(schemes=['bcrypt'],deprecated='auto')


def authenticate_user(email:str,password:str,db):
   user=db.query(Users).filter(Users.email==email).first()
   if not user or not bcrypt_context.verify(password, user.hashed_password):
     return False
   return user


def create_access_token(email: str, id: str,role:str,is_active:bool,projects:bool, expires_delta: timedelta):
   encode={
      'sub': email,
      'id': id,
      'role':role,
      'projects':projects,
      'status':is_active
      }
   expires=datetime.utcnow() + expires_delta
   encode.update({'exp':expires})
   return jwt.encode(encode,SECRET_KEY,algorithm=ALGORITHM)


async def get_current_user(token:Annotated[str,Depends(oauth2_bearer)]):
   try:
      payload=jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
      email=payload.get('sub')
      id=payload.get('id')
      role=payload.get('role')
      projects=payload.get('projects')
      is_active=payload.get('status')
      if email is None or id is None :
         logger.info(f"Email: {email}, id : {id}, is_active : {is_active}")
         logger.warning("Invalid token payload")
         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='Could not validate user')
      return{'email':email, 'id':id,'user_role':role,'projects':projects}
   except JWTError:
      raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='Token expired')

def send_verification_email(email: str, token: str):
   template = email_templates_env.get_template("email_verify.html")
   verification_link = f"http://0.0.0.0:80/auth/verify/{token}"
   html_content = template.render(verification_link=verification_link)
   msg = EmailMessage()
   msg['Subject'] = "Email Verify"
   msg['From'] = EMAIL_ADDRESS
   msg['To'] = email
   msg.set_content("This email requires an HTML-compatible email client.") 
   msg.add_alternative(html_content, subtype="html")


   with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
      smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
      smtp.send_message(msg)
