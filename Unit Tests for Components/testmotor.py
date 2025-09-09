import pigpio
import RPi.GPIO as GPIO
import time

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

    def forward(self):
        GPIO.output(self.INA, GPIO.HIGH)
        GPIO.output(self.INB, GPIO.LOW)

    def backward(self):
        GPIO.output(self.INA, GPIO.LOW)
        GPIO.output(self.INB, GPIO.HIGH)

    def stop(self):
        GPIO.output(self.INA, GPIO.LOW)
        GPIO.output(self.INB, GPIO.LOW)

    def speed(self, speed):
        # Adjust this formula based on the PWM range supported by pigpio
        self.pi.hardware_PWM(self.PWM_PIN, 10000, speed * 10000)

    def setMotor(self, direction, speed):
        self.speed(speed)
        if direction == "forward":
            self.forward()
        elif direction == "backward":
            self.backward()
        elif direction == "stop":
            self.stop()
        else:
            return

    def stopMotor(self):
        self.stop()
        self.pi.stop()

def main():
    GPIO.setmode(GPIO.BCM)
    myMotor1 = Motor(20, 21, 12)
    myMotor2 = Motor(26, 6, 13)
    speed1 = 0
    direction1 = "stop"
    speed2 = 0
    direction2 = "stop"
    myMotor1.setMotor(direction1, speed1)
    myMotor2.setMotor(direction2, speed2)
    try:
        while True:
            userInput = input("Choices: forward(w), backward(s), stop(x), speed(q), left(a), right(d) or exit(e): ")
            if userInput == "a":
                direction1 = "backward"
                direction2 = "forward"
                speed1 = 30
                speed2 = 45
            elif userInput == "d":
                direction1 = "forward"
                direction2 = "backward"
                speed1 = 45
                speed2 = 30
            elif userInput == "x":
                direction1 = "stop"
                direction2 = "stop"
            elif userInput == "q":
                userInput = int(input("What speed do you like? 0 to 100: "))
                if userInput > 100 or userInput < 0:
                    print("Invalid speed")
                else:
                    speed1 = userInput
                    speed2 = userInput
            elif userInput == "w":
                direction1 = "forward"
                direction2 = "forward"
                speed1 = 15
                speed2 = 15
            elif userInput == "s":
                direction1 = "backward"
                direction2 = "backward"
                speed1 = 15
                speed2 = 15
            elif userInput == "e":
                break
            myMotor1.setMotor(direction1, speed1)
            myMotor2.setMotor(direction2, speed2)
    except KeyboardInterrupt:
        pass
    finally:
        myMotor1.stopMotor()
        myMotor2.stopMotor()
        GPIO.cleanup()

if __name__ == "__main__":
    main()
