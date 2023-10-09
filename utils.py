import urllib.request, urllib.parse
import urllib
import time
import requests

prestoBot = "5876869228:AAFk644pEKRBnEhZ6jbG2nXRlj4fsyZEYgg"
prestoStayGroup = "4050514650"

def sendTelegram(params):
    try:
        url = "https://api.telegram.org/bot"+prestoBot+"/sendMessage?chat_id=-"+prestoStayGroup+"&text=" + urllib.parse.quote(params)
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
