from email.message import EmailMessage
import os
import pprint
import smtplib
import urllib.request, urllib.parse
import urllib
import time
import requests

prestoBot = "5876869228:AAFk644pEKRBnEhZ6jbG2nXRlj4fsyZEYgg"
prestoStayGroup = "4050514650"


def sendAnEmail(title, subject, message, email_receiver, path=None):
    print("Attempting to send an email")
    print(email_receiver)
    print(type(email_receiver))

    email_sender = os.environ["PRESTO_MAIL_USERNAME"]
    email_password = os.environ["PRESTO_MAIL_PASSWORD"]

    # sendtelegram("\nSending an email to " + str(email_receiver))

    # Add the image banner to the email content

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
        @font-face {{
            font-family: 'Plus Jakarta';
            src: url('PlusJakartaSans-VariableFont_wght.woff2') format('woff2-variations'),
                url('PlusJakartaSans-Italic-VariableFont_wght.woff2') format('woff2-variations');
            font-weight: 100 500; /* Adjust font weights based on available weights */
            font-style: normal;
        }}

        body {{
            font-family: 'Plus Jakarta', sans-serif;
            color: #000;
            margin: auto 5vw;
        }}

        div{{
            font-family: 'Plus Jakarta', sans-serif;
            font-weight:400;
        }}


        </style>

    </head>
    <body style="margin:auto 5vw; color:black; font-family: 'Plus Jakarta', sans-serif; font-weight:400;">

        
        <!-- Your banner image above -->


        <div style="font-family:'Poppins', sans serif; font-weight: 400; font-size: 20px; line-height:26px; color: #000;">
            {message}
        </div>


        <h6 style="font-weight:200; font-size: 14px;">This email is powered by <a href='https://prestoghana.com'>PrestoGhana</a></h6>
    </body>
    </html>
    """

    em = EmailMessage()
    em["From"] = f"{title} <{email_sender}>"
    em["To"] = email_receiver
    em["Subject"] = subject

    em.set_content("")
    em.add_alternative(html_content, subtype="html")

    print(em)

    if path != None:
        em.add_attachment(
            open(path, "rb").read(),
            maintype="application",
            subtype="pdf",
            filename=title,
        )

    smtp_server = "mail.privateemail.com"
    port = 465

    server = smtplib.SMTP_SSL(smtp_server, port)
    server.login(email_sender, email_password)
    server.sendmail(email_sender, email_receiver, em.as_string())
    server.quit()
    return "Done!"


def sendTelegram(params):
    try:
        url = "https://api.telegram.org/bot"+prestoBot+"/sendMessage?chat_id=-"+prestoStayGroup+"&text=" + urllib.parse.quote(params)
        content = urllib.request.urlopen(url).read()
        print(content)
        return content
    except Exception as e:
        print(e)
        return e
    
def sendVendorTelegram(params,chatId):
    try:
        url = "https://api.telegram.org/bot"+prestoBot+"/sendMessage?chat_id=-"+chatId+"&text=" + urllib.parse.quote(params)
        content = urllib.request.urlopen(url).read()
        print(content)
        return content
    except Exception as e:
        print(e)
        return e
    
def reportTelegram(error_message):

    # Construct the Telegram message
    telegram_message = f"500 Internal Server Error: {error_message}"


    url = f"https://api.telegram.org/bot{prestoBot}/sendMessage"
    
    try:
        response = requests.post(url, json={
            'chat_id': prestoStayGroup,
            'text': telegram_message
        })

        if response.status_code == 200:
            print('Message sent to Telegram successfully!')
        else:
            print(f'Error sending message to Telegram. HTTP {response.status_code} - {response.text}')
    
    except Exception as e:
        print(f'An error occurred while sending the Telegram message: {str(e)}')
    
    

def apiResponse(code, message, data, startTime):
    response = {
        "code":code,
        "duration":time.now() - startTime,
        "data":data,
        "message":message
    }
    return response

def send_sms(phone,message):
    api_key = "aniXLCfDJ2S0F1joBHuM0FcmH" #Remember to put your own API Key here
    params = {"key":api_key,"to":phone,"msg":message,"sender_id":"PrestoStay"}
    url = 'https://apps.mnotify.net/smsapi?'+ urllib.parse.urlencode(params)
    content = urllib.request.urlopen(url).read()
    print(content)
    print(url)

import requests

def sendMnotifySms(sender_id, recipients, message):
    endPoint = 'https://api.mnotify.com/api/sms/quick'
    api_key = "whmBov51IDjkTtj6AAWmakuid9NljoRPFdr4Jx6rbqM4T" #Remember to put your own API Key here
    data = {
    'recipient[]': recipients,
    'sender': sender_id,
    'message': message,
    'is_schedule': False,
    'schedule_date': ''
    }
    url = endPoint + '?key=' + api_key
    response = requests.post(url, data)
    data = response.json()
    pprint.pprint(data)
    return data
    




# def payWithPrestoPay(candidate, amount, phone, network, channel, costPerVote):
#     numberOfVotes = amount / award.costPerVote
#     newTransaction = Transactions(
#         candidate = candidate.id, 
#         candidateName = candidate.name, 
#         amount = amount,  
#         award=candidate.award, 
#         account=phone, 
#         channel=channel,
#         costPerVote = costPerVote,
#         ref="none",
#         votes =numberOfVotes,
#         network = network,
#         pending=True
#         )          
        
#     db.session.add(newTransaction)
#     db.session.commit()

#     transactionId = newTransaction.id

#     # Am I not supposed to create a transaction?
  

#     description = str(amount) + " vote for " + str(candidate.id) + str(candidate.name)

#     # if network == "CARD":
#     #     cardTransaction = True
#     #     network = "MTN"

#     paymentInfo = {
#             "appId":candidate.award, #tca kaf
#             "ref":transactionId,
#             "description":description,
#             "reference":candidate.name+"-"+str(newTransaction.id),
#             "paymentId":candidate.id, 
#             "phone":"0"+phone[-9:],
#             "amount":amount,
#             "total":amount,
#             "recipient":"external", #TODO:Change!
#             "percentage":"3",
#             "callbackUrl":baseUrl+"/confirm/"+str(transactionId),#TODO: UPDATE THIS VALUE
#             "firstName":candidate.name,
#             "network":network
#         }

#     response = requests.post(prestoUrl+"/korba", json=paymentInfo)

#     app.logger.info("-----prestoPay------")
#     app.logger.info(paymentInfo)
#     app.logger.info(prestoUrl)
#     status = response
#     status = response.status_code
#     app.logger.info(status)
#     # app.logger.info(response.json())
 
#     try:
#         newTransaction.ref = response.json()["transactionId"]
#         db.session.commit()
#     except Exception as e:
#         app.logger.info("e")
#         app.logger.info(e)
#         app.logger.info("Couldnt set transaction reference!")

#     # if transaction.network == "CARD"
#     if test == True:
#         url = "https://sandbox.prestoghana.com/verifyvote/"
#         # url = "localhost:4000/verifyvote/"
#     else:
#         url = "https://prestovotes.com/verifyvote/"
        
#     if network == 'CARD':
#                 # create korba - presto transaction here and assign to orderId
#         app.logger.info(network)
#         # transaction = korbaCheckout(candidate, amount, phone)
#         transaction = newTransaction
#         description = "Buying "+ str(amount) +" votes for "+ str(candidate.name) + " "+str(candidate.award) + " election."
#         callbackUrl = url+str(transaction.id)
#         app.logger.info(callbackUrl)
        
#     responseBody = {
#         "transactionId":transactionId,
#         "orderId":prestoPrefix+newTransaction.ref,
#         "merchantID" : merchantID ,
#         "description" : "Buying "+ str(amount) +" votes for "+ str(candidate.name) + " " + str(award) + " election.",
#         "callbackUrl" :  url+str(newTransaction.id)
#     }
#     # app.logger.info(callbackUrl)

#     return responseBody


def create_folder(folder_path):
    print(f"Checkign to see if the {folder_path} exists")
    # Check if the folder already exists
    if not os.path.exists(folder_path):
        # Create the folder if it doesn't exist
        os.makedirs(folder_path)
        print(f"Folder '{folder_path}' created successfully.")
    else:
        print(f"Folder '{folder_path}' already exists.")
    
    print(f'Folder Path:{folder_path}')
    return folder_path

def logger(message, flash=False):
    print(message)
    if flash == True:
        flash(message)
    # send telegram as log.
    # add to db as entry
