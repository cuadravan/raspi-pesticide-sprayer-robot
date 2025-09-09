import RPi.GPIO as GPIO
import time

class EightRelay:
    def __init__(self, arrayIn):
        self.arrayIn = arrayIn
        for i in self.arrayIn:
            GPIO.setup(i, GPIO.OUT)
            GPIO.output(i, GPIO.HIGH)
        
    def closeRelay(self, channelNumber):
        GPIO.output(self.arrayIn[channelNumber-1], GPIO.HIGH)

    def openRelay(self, channelNumber):
        GPIO.output(self.arrayIn[channelNumber-1], GPIO.LOW)

    def toggleRelay(self, channelNumber):
        if(GPIO.input(self.arrayIn[channelNumber-1])) == GPIO.HIGH:
            GPIO.output(self.arrayIn[channelNumber-1], GPIO.LOW)
        else:
            GPIO.output(self.arrayIn[channelNumber-1], GPIO.HIGH)

    def closeAllRelay(self):
        for i in self.arrayIn:
            GPIO.output(i, GPIO.HIGH)
        
    def openAllRelay(self):
        for i in self.arrayIn:
            GPIO.output(i, GPIO.LOW)
        
def main():
    GPIO.setmode(GPIO.BCM)
    pinList = [4, 17, 27, 22, 10, 9]
    myEightRelay = EightRelay(pinList)
    try:
        while True:
            choice = int(input("Select a relay module to toggle (1-6) or close all (7) or open all (8): "))
            if(choice == 7):
                myEightRelay.closeAllRelay()
            elif(choice == 8):
                myEightRelay.openAllRelay()
            elif(choice < 0 or choice > 9 or choice == 9):
                print("Invalid choice")
            else:
                myEightRelay.toggleRelay(choice)
    except KeyboardInterrupt:
        print("Keyboard interrupt detected. Terminating program.")
    except ValueError:
        print("That is not a valid input. Terminating program.")
    finally:    
        GPIO.cleanup()

if __name__ == "__main__":
    main()
