import conf
from boltiot import Sms, Email, Bolt
import json
import time
import random
import urllib.request
import requests
import threading

intermediate_value = 55
max_value = 80
max_turb = 10  # in Nephelometric Turbidity Units
max_temp = 40  # in degrees centigrade
acidic_ph = 6  # acidic
basic_ph = 8.5  # basic

mybolt = Bolt(conf.API_KEY, conf.DEVICE_ID)
sms = Sms(conf.SID, conf.AUTH_TOKEN, conf.TO_NUMBER, conf.FROM_NUMBER)
mailer = Email(conf.MAILGUN_API_KEY, conf.SANDBOX_URL,
               conf.SENDER_EMAIL, conf.RECIPIENT_EMAIL)


def thingspeak(water, temp, tempw, turb, ph):
    URL = 'https://api.thingspeak.com/update?api_key='
    KEY = '83HUIBXL89ETQ025'
    HEADER = '&field1={}&field2={}&field3={}&field4={}&field5={}'.format(
        water, temp, tempw, turb, ph)
    NEW_URL = URL + KEY + HEADER
    v = urllib.request.urlopen(NEW_URL)
    print("DATA SENT TO THINGSPEAK")


def twillo_message(message):
    try:
        print("Making request to Twilio to send an SMS")
        response = sms.send_sms(message)
        print("Response received from Twilio is: " + str(response))
        print("Status of SMS at Twilio is: " + str(response.status))
    except Exception as e:
        print("Below are the details")
        print(e)


def mailgun_message(head, message_1):
    try:
        print("Making request to Mailgun to send an email")
        response = mailer.send_email(head, message_1)
        print("Response received from Mailgun is: " + response.text)
    except Exception as e:
        print("Below are the details")
        print(e)


while True:
    print("Reading Water-Level Value")
    response_1 = mybolt.serialRead('10')
    response_2 = mybolt.serialRead('10')
    response_3 = mybolt.serialRead('10')
    response_4 = mybolt.serialRead('10')
    response = mybolt.analogRead('A0')

    data_1 = json.loads(response_1)
    data_2 = json.loads(response_2)
    data_3 = json.loads(response_3)
    data_4 = json.loads(response_4)
    data = json.loads(response)

    Water_level = data_1['value'].rstrip()
    Ph_level = data_2['value'].rstrip()
    Turb_level = data_3['value'].rstrip()
    Temp_level = data_4['value'].rstrip()

    print("Water Level value is: " + str(Water_level) + "%")
    print("Ph Level value is: " + str(Ph_level))
    print("Turbidity Level value is: " + str(Turb_level) + " NTU")
    print("Temperature Level value is: " + str(Temp_level) + " °C")

    sensor_value = float(data['value'])
    temp = ((5000 * sensor_value) / 1024) / 10
    temp_value = round(temp, 2) - 32
    print("Temperature is: " + str(temp_value) + "°C")

    try:
        if float(Water_level) >= max_value:
            message = "Red Alert!. Water level is increased by " + \
                str(Water_level) + "% at your place. Please Don't move out of the house. The Current Temperature is " + \
                str(temp_value) + "°C"
            head = "Red Alert!"
            message_1 = "Water level is increased by " + \
                str(Water_level) + "% at your place. Please Don't move out of the house. The Current Temperature is " + \
                str(temp_value) + "°C."
            twillo_message(message)
            mailgun_message(head, message_1)
        elif float(Water_level) >= intermediate_value:
            message = "Orange Alert!. Water level is increased by " + \
                str(Water_level) + "% at your place. Please be Safe. The current Temperature is " + \
                str(temp_value) + "°C."
            head = "Orange Alert"
            message_1 = "Water level is increased by " + \
                str(Water_level) + "% at your place. Please be Safe. The current Temperature is " + \
                str(temp_value) + "°C."
            twillo_message(message)
            mailgun_message(head, message_1)

        if float(Ph_level) >= basic_ph or float(Ph_level) <= acidic_ph:
            message = "Water is not safe for drinking at your place.\n" + \
                "Current pH level - " + str(Ph_level)
            head = "Ph Alert!"
            twillo_message(message)
            mailgun_message(head, message)

        if float(Turb_level) >= max_turb:
            message = "Water is not safe for drinking " + \
                "Current Turbidity level - " + str(Turb_level) + " NTU"
            head = "Turbidity Alert!"
            twillo_message(message)
            mailgun_message(head, message)

        if float(Temp_level) >= max_temp:
            message = "Water is unfit for aquatic life " + \
                "Current Temperature level - " + str(Temp_level) + "°C."
            head = "Water Temperature Alert!"
            twillo_message(message)
            mailgun_message(head, message)
    except Exception as e:
        print("Error occurred: Below are the details")
        print(e)

    thingspeak(Water_level, temp_value, Ph_level, Temp_level, Turb_level)
    time.sleep(32)
