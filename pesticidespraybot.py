import time
from myobjects90percent import DistanceSensor, Motor, MotorSystem, LCD, SMS, Camera, PesticideSprayingSystem
import RPi.GPIO as GPIO

def main():
    GPIO.setmode(GPIO.BCM) 
    
    myleftsystem = [4, 17, 27]
    myrightsystem = [22, 10, 9]
    
    myMotorA = Motor(26, 6, 13)
    myMotorB = Motor(20, 21, 12)
    myMotorSystem = MotorSystem(myMotorA, myMotorB)

    mySMS = SMS()
    myLCD = LCD()

    myLeftUS = []
    myLeftUSPins = [(1, 14), (1, 15), (1, 23)] #(TrigPin, EchoPin) for each ultrasonic sensor
    for trig, echo in myLeftUSPins:
        distancesensor = DistanceSensor(trigPin=trig, echoPin=echo)
        myLeftUS.append(distancesensor)

    myRightUS = []
    myRightUSPins = [(1, 24), (1, 25), (1, 8)]
    for trig, echo in myRightUSPins:
        distancesensor = DistanceSensor(trigPin=trig, echoPin=echo)
        myRightUS.append(distancesensor)

    mywaterUS = DistanceSensor(1, 7)
    
    myCamera = Camera(0, 2, 4)
    
    myPesticideSprayingSystem = PesticideSprayingSystem(myleftsystem, myrightsystem, myMotorSystem, mySMS, myLCD, myLeftUS, myRightUS, mywaterUS, myCamera)
    ongoing = True
    try:
        while ongoing:
            myPesticideSprayingSystem.navigateMode()
            ongoing = myPesticideSprayingSystem.sprayMode()
            time.sleep(0.5)  # Sleep for 1 second between checks
    except KeyboardInterrupt:
        pass
    finally:
        myPesticideSprayingSystem.stopMode()

if __name__ == "__main__":
    main()
