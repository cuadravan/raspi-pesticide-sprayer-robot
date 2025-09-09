import RPi.GPIO as GPIO
import time

class DistanceSensor:
    def __init__(self, trigPin, echoPin):       
        GPIO.setup(trigPin, GPIO.OUT)
        GPIO.setup(echoPin, GPIO.IN)
        self.trigPin = trigPin
        self.echoPin = echoPin

    def __sendUltrasonic(self):
        GPIO.output(self.trigPin, False)
        time.sleep(0.1)  
        GPIO.output(self.trigPin, True)
        time.sleep(0.00001)  
        GPIO.output(self.trigPin, False)

    def __receiveUltrasonic(self, timeout = 0.1):
        try:
            pulseStart = 0
            pulseEnd = 0
            startTime = time.time()

            # Wait for the echo pin to go high
            while GPIO.input(self.echoPin) == 0:
                pulseStart = time.time()
                if pulseStart - startTime > timeout:
                    raise TimeoutError("Timeout waiting for echo pin to go high")

            # Wait for the echo pin to go low
            while GPIO.input(self.echoPin) == 1:
                pulseEnd = time.time()
                if pulseEnd - pulseStart > timeout:
                    raise TimeoutError("Timeout waiting for echo pin to go low")

            pulseDuration = pulseEnd - pulseStart
            return pulseDuration
        except TimeoutError as e:
            print(f"Error receiving ultrasonic signal: {e}")
            return float('inf')
        except Exception as e:
            print(f"Unexpected error receiving ultrasonic signal: {e}")
            return float('inf')
    
    def getDistance(self):
        self.__sendUltrasonic()
        duration = self.__receiveUltrasonic()
        distance = duration * 17150
        distance = round(distance, 2)
        return distance

class WaterLevelSensor(DistanceSensor):   
    def getWaterLevel(self, waterCapacity, measurementFull, measurementEmpty):
        distance = super().getDistance()
        
        relativeFullDistance = measurementFull - measurementEmpty

        if relativeFullDistance == 0:
            return 0.0

        relativeDistance = distance - measurementFull
        waterPercent = 100 - ((relativeDistance / relativeFullDistance) * 100)
        waterLevel = waterCapacity * waterPercent / 100 
        return waterLevel
    
    def checkLowPesticideLevel(self, lowPesticideLevel):
        if self.getWaterLevel() < lowPesticideLevel:
            return True
        else:
            return False

def main():
    GPIO.setmode(GPIO.BCM) 
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
        
    distances = []
    for i in range(3):
        print(f"Testing right sensor {i}") 
        for j in range(5):
            myRightUS[i].getDistance()
        
    for i in range(3):
        print(f"Testing left sensor {i}") 
        for j in range(5):
            myLeftUS[i].getDistance()
    
    print("Testing water sensor")        
    for i in range(5):
        mywaterUS.getDistance()
        
        

    GPIO.cleanup()

if __name__ == "__main__":
    main()
