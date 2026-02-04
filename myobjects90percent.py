import RPi.GPIO as GPIO
from RPLCD.i2c import CharLCD
from twilio.rest import Client
import os
from dotenv import load_dotenv
import pigpio
import time
import cv2
import numpy as np

class DistanceSensor:
    def __init__(self, trigPin, echoPin):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(trigPin, GPIO.OUT)
        GPIO.setup(echoPin, GPIO.IN)
        self.trigPin = trigPin
        self.echoPin = echoPin
        # Define timeout duration based on 100 cm distance
        self.TIMEOUT = 70 * 2 / 34300  # in seconds, using speed of sound (34300 cm/s)

    def __sendUltrasonic(self):
        GPIO.output(self.trigPin, False)
        time.sleep(0.1)
        GPIO.output(self.trigPin, True)
        time.sleep(0.00001)
        GPIO.output(self.trigPin, False)

    def __receiveUltrasonic(self):
        pulseStart = 0
        pulseEnd = 0
        timeoutStart = time.time()

        while GPIO.input(self.echoPin) == 0:
            pulseStart = time.time()
            if pulseStart - timeoutStart > self.TIMEOUT:
                return self.TIMEOUT  # Timeout if echo not received in time

        pulseEnd = pulseStart
        while GPIO.input(self.echoPin) == 1:
            pulseEnd = time.time()
            if pulseEnd - pulseStart > self.TIMEOUT:
                return self.TIMEOUT  # Timeout if echo not received in time

        pulseDuration = pulseEnd - pulseStart
        return pulseDuration

    def getDistance(self):
        self.__sendUltrasonic()
        duration = self.__receiveUltrasonic()
        if duration >= self.TIMEOUT:
            return 71  # Return 101 if the duration indicates a timeout
        distance = duration * 17150
        distance = round(distance, 2)
        return distance


class Motor:
    def __init__(self, INA, INB, PWM):
        self.INA = INA
        self.INB = INB
        self.PWM_PIN = PWM
        
        GPIO.setup(self.INA, GPIO.OUT)
        GPIO.setup(self.INB, GPIO.OUT)

        self.pi = pigpio.pi()
        self.pi.set_mode(self.PWM_PIN, pigpio.OUTPUT)
        self.pi.hardware_PWM(self.PWM_PIN, 10000, 0)

    def __forward(self):
        GPIO.output(self.INA, GPIO.HIGH)
        GPIO.output(self.INB, GPIO.LOW)

    def __backward(self):
        GPIO.output(self.INA, GPIO.LOW)
        GPIO.output(self.INB, GPIO.HIGH)

    def __stop(self):
        GPIO.output(self.INA, GPIO.LOW)
        GPIO.output(self.INB, GPIO.LOW)

    def __speed(self, speed):
        # Adjust this formula based on the PWM range supported by pigpio
        self.pi.hardware_PWM(self.PWM_PIN, 10000, speed * 10000)

    def setMotor(self, direction, speed):
        self.__speed(speed)
        if direction == "forward":
            self.__forward()
        elif direction == "backward":
            self.__backward()
        elif direction == "stop":
            self.__stop()
        elif direction == "off":
            self.__stop()
            self.pi.stop()
        else:
            return
   
class MotorSystem:
    def __init__(self, MotorA, MotorB):
        self.MotorA = MotorA
        self.MotorB = MotorB
        
    def moveForward(self):
        self.MotorA.setMotor("forward", 12)
        self.MotorB.setMotor("forward", 12)
        
    def moveBackward(self):
        self.MotorA.setMotor("backward", 12)
        self.MotorB.setMotor("backward", 12)
        
    def moveLeft(self):
        #self.MotorA.setMotor("forward", 50)
        #self.MotorB.setMotor("backward", 50)
        #time.sleep(0.1)
        self.MotorA.setMotor("forward", 45)
        self.MotorB.setMotor("backward", 30)
        
    def moveRight(self):
        #self.MotorA.setMotor("backward", 50)
        #self.MotorB.setMotor("forward", 50)
        #time.sleep(0.1)
        self.MotorA.setMotor("backward", 30)
        self.MotorB.setMotor("forward", 45)
        
    def stopSystem(self):
        self.MotorA.setMotor("stop", 0)
        self.MotorB.setMotor("stop", 0)
        
    def offSystem(self):
        self.MotorA.setMotor("off", 0)
        self.MotorB.setMotor("off", 0)

class LCD:
    def __init__(self):
        try:
            self.lcd = CharLCD('PCF8574', 0x27)
            self.lcd.write_string("Good day!")
            self.lcd.cursor_pos = (1, 0)
            self.lcd.write_string("-AutoPestSprayer")
            time.sleep(2)
        except Exception as e:
            print(f"Error initializing LCD: {e}")

    def displayInformation(self, leftLevel, rightLevel, direction, waterDistance):
        try:
            self.lcd.clear()
            self.lcd.write_string(f"L:{leftLevel} R:{rightLevel} Dir:{direction}")
            self.lcd.cursor_pos = (1, 0)
            if waterDistance >= 0 and waterDistance < 8:
                self.lcd.write_string(f"WatL:{waterDistance}cm HIGH")
            elif waterDistance >= 4 and waterDistance < 12:
                self.lcd.write_string(f"WatL:{waterDistance}cm MID")
            else:
                self.lcd.write_string(f"WatL:{waterDistance}cm LOW")
        except Exception as e:
            print(f"Error displaying information on LCD: {e}")

    def turnOffLCD(self):
        try:
            self.lcd.clear()
            self.lcd.close()
        except Exception as e:
            print(f"Error turning off LCD: {e}")

class SMS:
    def __init__(self):
        load_dotenv()
        self.account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.client = Client(self.account_sid, self.auth_token)
    
    def sendSMS(self, waterDistance):
        message = self.client.messages.create(
            from_='whatsapp:+639123456789',
            body=f'Robot is shutting down due to low pesticide levels at {waterDistance} cm from top of container. Please refill your water container.',
            to='whatsapp:+639123456789'
        )

class Camera:
    def __init__(self, markerCamera, leftCamera, rightCamera):
        self.markerCamera = markerCamera
        self.leftCamera = leftCamera
        self.rightCamera = rightCamera
        self.lower_red = [np.array([0, 70, 50]), np.array([170, 70, 50])]
        self.upper_red = [np.array([10, 255, 255]), np.array([180, 255, 255])]
        self.lower_blue = np.array([100, 150, 0])
        self.upper_blue = np.array([140, 255, 255])
        self.lower_greenl = np.array([45.3567, 76.9016, 51.4])
        self.upper_greenl = np.array([55.3568, 116.9016, 131.4])
        self.lower_greenr = np.array([31.3828, 60.7828, 107.3056])
        self.upper_greenr = np.array([53.8816, 100.7828, 147.3056])
        self.cap1 = cv2.VideoCapture(self.markerCamera)
        self.cap2 = cv2.VideoCapture(self.leftCamera)
        self.cap3 = cv2.VideoCapture(self.rightCamera)
        self.cap2.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap2.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap3.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap3.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    def takeMarkerFrame(self):
        for i in range(5):
            ret, frame = self.cap1.read()
        ret, frame = self.cap1.read()
        if not ret:
            return "No Frame Captured for marker camera"

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask_red = sum(cv2.inRange(hsv, lr, ur) for lr, ur in zip(self.lower_red, self.upper_red))
        mask_blue = cv2.inRange(hsv, self.lower_blue, self.upper_blue)
        mask = mask_red + mask_blue

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        shapes = [0, 0]  # [red squares, blue squares]

        for contour in contours:
            if cv2.contourArea(contour) > 15000:  # Adjust threshold as needed
                approx = cv2.approxPolyDP(contour, 0.02 * cv2.arcLength(contour, True), True)
                if len(approx) == 4:  # Check if the shape is a square or rectangle
                    x, y, w, h = cv2.boundingRect(approx)
                    #if 0.9 <= w / h <= 1.1:  # Check if the aspect ratio is roughly 1 (square)
                    mask_color = cv2.inRange(hsv[y:y+h, x:x+w], self.lower_blue, self.upper_blue)
                    if cv2.countNonZero(mask_color) > (w * h) / 2:
                        shapes[1] += 1
                    else:
                        shapes[0] += 1

        return shapes
    
    def takeGreenFrameLeft(self):
        for i in range(5):
            ret, frame = self.cap2.read()
        ret, frame = self.cap2.read()
        if not ret:
            return "No Frame Captured for green camera"
            
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Create a mask for the green color
        mask = cv2.inRange(hsv, self.lower_greenl, self.upper_greenl)
        
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

        # Find contours in the mask
        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        # Get the frame dimensions
        height, width = frame.shape[:2]

        # Define the center region (a box in the middle of the frame)
        center_x, center_y = width // 2, height // 2
        center_region_size = 100
        top_left = (center_x - center_region_size, center_y - center_region_size)
        bottom_right = (center_x + center_region_size, center_y + center_region_size)

        # Draw the center region rectangle
        cv2.rectangle(frame, top_left, bottom_right, (0, 255, 0), 2)

        # Boolean flag to check if a green object is in the center
        green_in_center = False

    # Check if any contour is within the center region
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            if (center_x - center_region_size < x + w/2 < center_x + center_region_size) and \
            (center_y - center_region_size < y + h/2 < center_y + center_region_size):
                green_in_center = True

        return green_in_center
        
    
    def takeGreenFrameRight(self):
        for i in range(5):
            ret, frame = self.cap3.read()
        ret, frame = self.cap3.read()
        if not ret:
            return "No Frame Captured for green camera"
            
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Create a mask for the green color
        mask = cv2.inRange(hsv, self.lower_greenr, self.upper_greenr)
        
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

        # Find contours in the mask
        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        # Get the frame dimensions
        height, width = frame.shape[:2]

        # Define the center region (a box in the middle of the frame)
        center_x, center_y = width // 2, height // 2
        center_region_size = 100
        top_left = (center_x - center_region_size, center_y - center_region_size)
        bottom_right = (center_x + center_region_size, center_y + center_region_size)

        # Draw the center region rectangle
        cv2.rectangle(frame, top_left, bottom_right, (0, 255, 0), 2)

        # Boolean flag to check if a green object is in the center
        green_in_center = False

    # Check if any contour is within the center region
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            if (center_x - center_region_size < x + w/2 < center_x + center_region_size) and \
            (center_y - center_region_size < y + h/2 < center_y + center_region_size):
                green_in_center = True

        return green_in_center
    
    def turnOffCamera(self):
        self.cap1.release()
        self.cap2.release()
        self.cap3.release()
        
class PesticideSprayingSystem:
    def __init__(self, leftSystem, rightSystem, motorSystem, sms, lcd, leftUS, rightUS, waterUS, camera):
        self.leftSystem = leftSystem
        self.rightSystem = rightSystem
        self.motorSystem = motorSystem
        self.sms = sms
        self.lcd = lcd
        self.leftUS = leftUS
        self.rightUS = rightUS
        self.waterUS = waterUS
        self.camera = camera
        self.rotateLeftDelay = 1.5 # Adjust rotation time as needed
        self.rotateRightDelay = 1.5
        self.sprayTimes = {0: 0, 1: 0.7, 2: 1, 3: 1.4} 

        for leftsystem in self.leftSystem: # Initialize all spraying systems and open relays
            GPIO.setup(leftsystem, GPIO.OUT)
            GPIO.output(leftsystem, GPIO.HIGH)

        for rightsystem in self.rightSystem:
            GPIO.setup(rightsystem, GPIO.OUT)
            GPIO.output(rightsystem, GPIO.HIGH)

        self.motorSystem.moveForward() # Robot shall start moving

    def __getLeftDistance(self):
        distances = []
        for i in range(3):
            distances.append(self.leftUS[i].getDistance())
        return distances
    
    def __getRightDistance(self):
        distances = []
        for i in range(3):
            distances.append(self.rightUS[i].getDistance())
        return distances
    
    def __getWaterDistance(self):
        distance = self.waterUS.getDistance()
        return distance
    
    def __checkLevel(self, distances):
        index = 0
        for index in reversed(range(3)):
            if distances[index] <= 70:
                return index + 1       
        return 0
    
    def __setSpray(self, system, level):
        if level == 0:
            GPIO.output(system[0], GPIO.HIGH)
            GPIO.output(system[1], GPIO.HIGH)
            GPIO.output(system[2], GPIO.HIGH)
        elif level == 3:
            GPIO.output(system[0], GPIO.LOW)
            GPIO.output(system[1], GPIO.LOW)
            GPIO.output(system[2], GPIO.LOW)
        elif level == 2:
            GPIO.output(system[0], GPIO.LOW)
            GPIO.output(system[1], GPIO.LOW)
            GPIO.output(system[2], GPIO.HIGH)
        elif level == 1:
            GPIO.output(system[0], GPIO.LOW)
            GPIO.output(system[1], GPIO.HIGH)
            GPIO.output(system[2], GPIO.HIGH)
    
    def __activateLevel(self, leftLevel, rightLevel, waterDistance):
        #leftFrame
        self.motorSystem.stopSystem()
        if(rightLevel != 0):
            rightHasGreen = self.camera.takeGreenFrameRight()
            rightLevel = rightLevel if rightHasGreen == True else 0
            
        if(leftLevel != 0):
            leftHasGreen = self.camera.takeGreenFrameLeft()
            leftLevel = leftLevel if leftHasGreen == True else 0
        print(f"PROCESSED = LEFT LEVEL: {leftLevel}     RIGHT LEVEL: {rightLevel}   WATER DISTANCE: {waterDistance}")
        self.lcd.displayInformation(leftLevel, rightLevel, "F", waterDistance) # DIsplay on LCD
        if(leftLevel == 0 and rightLevel == 0):
            self.motorSystem.moveForward()
            return

        # Configure GPIO for left and right systems based on levels
        self.__setSpray(self.leftSystem, leftLevel) # Turn on respective spraying levels
        self.__setSpray(self.rightSystem, rightLevel)
        
        leftSprayTime = self.sprayTimes[leftLevel]
        rightSprayTime = self.sprayTimes[rightLevel]

        # Then we ensure spraying is equivalent to a spray time (some subtraction is needed if levels of both sides are unequal)
        if leftLevel > rightLevel:
            time.sleep(rightSprayTime)
            self.__setSpray(self.rightSystem, 0)
            time.sleep(leftSprayTime - rightSprayTime)
            self.__setSpray(self.leftSystem, 0)
        elif rightLevel > leftLevel:
            time.sleep(leftSprayTime)
            self.__setSpray(self.leftSystem, 0)
            time.sleep(rightSprayTime - leftSprayTime)
            self.__setSpray(self.rightSystem, 0)
        else:
            time.sleep(leftSprayTime)
            self.__setSpray(self.leftSystem, 0)
            self.__setSpray(self.rightSystem, 0)
        
        self.motorSystem.moveForward()
    
    def sprayMode(self):
        leftDistances = self.__getLeftDistance() # Get left distances
        rightDistances = self.__getRightDistance() # Get right distances
        waterDistance = self.__getWaterDistance() # Get water levels
        if waterDistance >= 12.3: # If water level is critical
            self.sms.sendSMS(waterDistance) # Send SMS, and return False to exit loop
            return False
        leftLevel = self.__checkLevel(leftDistances) # If not, process level of both sides
        rightLevel = self.__checkLevel(rightDistances)
        print(f"Pre-processed = Left Level: {leftLevel}     Right Level: {rightLevel}   Water Distance: {waterDistance}")
        if(leftLevel != 0 or rightLevel != 0):
            self.__activateLevel(leftLevel, rightLevel, waterDistance) # Activate the level
        self.lcd.displayInformation(0, 0, "F", waterDistance)
        return True # Return True to continue loop
        
    def navigateMode(self):
        navigationColor = self.camera.takeMarkerFrame() # Before getting distances, first check marker through camera
        print(f"Colors: {navigationColor}")
        if(navigationColor[0] == 0 and navigationColor[1] == 1): # If marker is a blue square
            self.motorSystem.stopSystem() # Stop robot
            self.motorSystem.moveRight() # Let it rotate right
            self.lcd.displayInformation(0, 0, "R", 0) # LCD display
            print("Moving right")
            time.sleep(self.rotateRightDelay) # Let it rotate fully
            self.motorSystem.stopSystem() # Stop rotation
            self.motorSystem.moveForward() # Resume forward movement
        elif(navigationColor[0] == 1 and navigationColor[1] == 0): # Else if red square, same thing except left
            self.motorSystem.stopSystem()
            self.motorSystem.moveLeft()
            self.lcd.displayInformation(0, 0, "L", 0)
            print("Moving left")
            time.sleep(self.rotateLeftDelay)
            self.motorSystem.stopSystem()
            self.motorSystem.moveForward()
        
    def stopMode(self): # If loop is exited, either through Keyboard Interrupt or critical Water Level
        self.motorSystem.stopSystem() # Stop movement
        self.lcd.turnOffLCD() # Turn off LCD
        self.camera.turnOffCamera() # Turn off camera
        GPIO.cleanup() # Turn of all GPIO (Ultrasonic Sensors, Spraying Systems, and Motors)
