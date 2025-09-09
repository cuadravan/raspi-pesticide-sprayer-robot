from RPLCD.i2c import CharLCD
import time

lcd = CharLCD('PCF8574', 0x27)

try:
    while True:
        lcd.write_string('LCD is working!')
        time.sleep(2)
        lcd.clear()
        lcd.write_string('!gnikrow si DCL')
        time.sleep(2)
        lcd.clear()

except KeyboardInterrupt:
    lcd.clear()
