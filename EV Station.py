import machine
from machine import Pin, SoftI2C, SPI
from lcd_api import LcdApi
from pico_i2c_lcd import I2cLcd
from hcsr04 import HCSR04
from mfrc522 import MFRC522
from machine import SoftSPI
import _thread
import network
import gc
import urequests
try:
  import urequests as requests
except:
  import requests
import time
import utime

# Wi-Fi Credentials
SSID = 'Redmi Note 11S'
PASSWORD = '12345678'

# Firebase Configuration
FIREBASE_URL = 'https://ev-charging-60202-default-rtdb.firebaseio.com/'
FIREBASE_SECRET = 'd9j9RlblPtBiSmfx9aXh19vWxOxQUuCvYqjSCpfw'

#LCD Config
I2C_ADDR = 0x27
totalRows = 2
totalColumns = 16
i2c = SoftI2C(scl=Pin(22), sda=Pin(21), freq=10000)  
lcd = I2cLcd(i2c, I2C_ADDR, totalRows, totalColumns)

#RFID Config
sck=18   #white
mosi=23  #gray
miso=19  #violet
rst=4    #yellow
cs=5     #black
spi = SoftSPI(baudrate=100000, polarity=0, phase=0, sck=sck, mosi=mosi, miso=miso)
spi.init()
rdr = MFRC522(spi=spi, gpioRst=4, gpioCs=5)

# Connect to Wi-Fi
def connect_to_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)

    print("Connecting to Wi-Fi...")
    lcd.move_to(0,0)
    lcd.putstr("Connecting to Wi-Fi...") 
    while not wlan.isconnected():
        time.sleep(1)
    print("Connected to Wi-Fi!")
    lcd.clear()
    lcd.move_to(0,0)
    lcd.putstr("Connected to Wi-Fi!")
    print("IP address:", wlan.ifconfig()[0])

#SMS Parameters
account_sid = 'ACf7e127987438806dc425307e0a1dc996'
auth_token = '2e196fbef276125835845d60c7f5beb6'
recipient_num = '+919994058429'
sender_num = '+12164466886'

def send_sms(recipient, sender,
             message, auth_token, account_sid):
      
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    data = "To={}&From={}&Body={}".format(recipient,sender,message)
    url = "https://api.twilio.com/2010-04-01/Accounts/{}/Messages.json".format(account_sid)
    
    print("Sending SMS")
    lcd.clear()
    lcd.move_to(0,0)
    lcd.putstr('Sending SMS')
    
    response = requests.post(url,
                             data=data,
                             auth=(account_sid,auth_token),
                             headers=headers)
    
    if response.status_code == 201:
        print("SMS sent!")
        lcd.clear()
        lcd.move_to(0,0)
        lcd.putstr('SMS sent!')
        time.sleep(5)
    else:
        print("Error sending SMS: {}".format(response.text))
        lcd.clear()
        lcd.move_to(0,0)
        lcd.putstr("SMS can't be sent")
        
# Firebase: Write Data
def write_data(card, field, value):
    url = f"{FIREBASE_URL}/{card}/.json?auth={FIREBASE_SECRET}"
    data = {field: value}
    print("Data being sent:", data)
    

    try:
        response = urequests.patch(url, json=data)
        response.close()
    except Exception as e:
        print("Error while writing data:", e)

# Firebase: Read Data
def read_data(card, field):
    url = f"{FIREBASE_URL}/{card}/{field}.json?auth={FIREBASE_SECRET}"

    try:
        response = urequests.get(url)
        if response.status_code == 200:
            data = response.json()
            print(f"Data read from {field}:", data)
            return data
        else:
            print("Failed to read data:", response.status_code)
            return None
    except Exception as e:
        print("Error while reading data:", e)
        return None

# RFID Reader
def read_rfid():
    (stat, tag_type) = rdr.request(rdr.REQIDL)
    if stat == rdr.OK:
        (stat, raw_uid) = rdr.anticoll()
        if stat == rdr.OK:
            # Calculate the UID based on the length of raw_uid
            card_id = sum(byte * (256 ** idx) for idx, byte in enumerate(reversed(raw_uid)))
            print("UID:", card_id)
            buzzing()
            return card_id
    return None

def buzzing():
    buz.value(1)
    utime.sleep_ms(170)
    buz.value(0)
    time.sleep(1)

def beep():
    buz.on()     
    time.sleep(0.1) 
    buz.off()    
    time.sleep(0.1) 
    
# Initialize Components
def initialize_components():
    global sensor, rdr, relay, ir, buz
    sensor = HCSR04(trigger_pin=25, echo_pin=26, echo_timeout_us=10000)  # Ultrasonic sensor
    relay = Pin(2, Pin.OUT)  # Relay control pin
    ir = Pin(34, Pin.IN)  # IR sensor input pin
    buz = Pin(32, Pin.OUT) #Buzzer Pin

def main():
    initialize_components()
    COST_PER_ENERGY = 10;
    connect_to_wifi()
    while True:
        distance = sensor.distance_cm()
        lcd.clear()
        lcd.move_to(4,0)
        lcd.putstr("Welcome")
        if distance < 5:  # Vehicle detected
            lcd.clear()
            lcd.move_to(0,0)
            lcd.putstr("Vehicle detectedWaiting for RFID")
            print("Vehicle detected. Waiting for RFID...")
            time.sleep(2)
            if distance < 100:  # Vehicle in range and IR sensor active
                for _ in range(3):
                    beep()
                    card = read_rfid()
                    if card:  # Valid card read
                        energy = 0
                        lcd.clear()
                        lcd.move_to(0,0)
                        lcd.putstr("Setting Zero")
                        write_data(card, 'Energy', energy)

                        # Turn on the relay and start charging
                        while True:
                            distance = sensor.distance_cm()
                            if distance < 100:  # Vehicle in range and IR sensor active
                                relay.value(1)
                                print("Charging in progress...")
                                lcd.clear()
                                lcd.move_to(0,0)
                                lcd.putstr("Charging in progress")
                                time.sleep(3)  
                            else:
                                relay.value(0)  
                                print("Charging stopped.")
                                lcd.clear()
                                lcd.move_to(0,0)
                                lcd.putstr("Charging stopped")
                                time.sleep(1)
                                break

                read_energy = read_data(card, 'Energy')
                balance = read_data(card, 'Balance')
                balance=int(balance)
                
                print("Energy after charging:", read_energy)
                lcd.clear()
                lcd.move_to(0,0)
                lcd.putstr(f"Energy: {read_energy} W")
                time.sleep(2)
                if read_energy is not None:
                    # Calculate billing
                    total_cost = float(read_energy) * COST_PER_ENERGY
                    print("Total cost:", total_cost)
                    lcd.clear()
                    lcd.move_to(0, 0)
                    lcd.putstr(f"Cost: {total_cost} Rs")
                    time.sleep(2)
                    balance-= total_cost
                    write_data(card, 'Balance', balance)
                    lcd.clear()
                    lcd.move_to(0, 0)
                    lcd.putstr("Payment done")
                    time.sleep(2)
                    message=f"Total Energy consumed: {read_energy} W \n\n Total Cost: {total_cost}"
                    send_sms(recipient_num, sender_num, message, auth_token, account_sid)

        time.sleep(1)

# Run the main function
if __name__ == '__main__':
    main()
