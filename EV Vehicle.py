from INA219 import INA219
from machine import Pin,ADC,I2C
from pico_i2c_lcd import I2cLcd
import time
import network
import urequests
import _thread
import ufirebase as firebase
try:
  import urequests as requests
except:
  import requests
import gc
import BlynkLib

BLYNK_AUTH =""
card=''

#16x2 LCD
i2c = I2C(1, sda=Pin(18), scl=Pin(19), freq=40000)
I2C_ADDR = i2c.scan()[0]
lcd = I2cLcd(i2c, I2C_ADDR, 2, 16)

#WiFi Connection
ssid = '  '
password = ''

def connect_wifi(ssid, password):
  station = network.WLAN(network.STA_IF)
  station.active(True)
  station.connect(ssid, password)
  while station.isconnected() == False:
    pass
  print('Connection successful')
  lcd.clear()
  lcd.move_to(0,0)
  lcd.putstr("WiFi connected")
  print(station.ifconfig())

connect_wifi(ssid, password)

blynk = BlynkLib.Blynk(BLYNK_AUTH)
firebase.setURL("")

#LCD Button
button = Pin(0, Pin.IN, Pin.PULL_UP)
last_button_state=0; 

#current sensor
sda = Pin(16)
scl = Pin(17)
i2c = I2C(0,sda=sda,scl=scl,freq=400000)
currentSensor = INA219(i2c)
currentSensor.set_calibration_16V_400mA()

#voltage sensor
adc_voltage = 0
in_voltage = 0
R1 = 30000
R2 = 7500
vtg=ADC(27);

energy_wh = 0 
last_time = time.time()

def read_ina219():
    current = currentSensor.current/1000
    val=vtg.read_u16();
    adc_voltage  = (val * 3.3) / 65535;
    in_voltage = adc_voltage / (R2/(R1+R2)) ;
    power = in_voltage * current  # Power in watts
    return in_voltage, current, power

def lcd_bt(previous_state, variable):
    current_state = button.value()
    if previous_state == 1 and current_state == 0:
        variable = 1 if variable == 0 else 0
    return current_state, variable

def put_fb(card,field,energy_wh):
    firebase.put(f"{card}/{field}","{:.4f}".format(energy_wh),bg=0,id=0)
def get_fb(card, field):
    try:
        firebase.get(f'{card}/{field}', 'data', bg=0, id=0)
        balance = firebase.data
        print(balance)  # Print balance for debugging
        return balance
    except Exception as e:
        print("Error fetching balance from Firebase:", e)
        return None
    
    
blynk.run()
bal=get_fb(card,'Balance')
blynk.virtual_write(6,bal)
while True:
    put_fb(card,'Energy',energy_wh)
    in_voltage, current, power = read_ina219()
    if (current>0.005):
        blynk.virtual_write(8, 255)
    else:
        blynk.virtual_write(8, 0)
    current_time = time.time()
    delta_time = current_time - last_time 
    last_time = current_time
    energy_wh += power * (delta_time / 3600)
    
    blynk.virtual_write(4, in_voltage)
    blynk.virtual_write(5, current)
    blynk.virtual_write(6, energy_wh)
    
    current_button_state = button.value()
    if current_button_state != last_button_state:
        lcd.clear()  # Clear the display once when the button state changes
        last_button_state = current_button_state

    if current_button_state == 1:
        lcd.move_to(0, 0)
        lcd.putstr("Voltage: {:.2f} V".format(in_voltage))
        lcd.move_to(0, 1)
        lcd.putstr("Current:{:6.3f} A".format(current))
    else:
        lcd.move_to(0, 0)
        lcd.putstr("Power: {:.2f} W".format(power))
        lcd.move_to(0, 1)
        lcd.putstr("Energy:{:.4f}Wh".format(energy_wh))
        
    print("Voltage: {:.2f}V".format(in_voltage))
    print("Current:  {:6.3f} A".format(current))
    print("Power: {:.2f} W".format(power))
    print("Energy: {:.4f} Wh".format(energy_wh))

    print("")
    print("")
    
    time.sleep(0.5)    
