import cv2
import time
import os

def take_picture(filename, cap):
    # Capture a frame
    ret, frame = cap.read()

    if ret:
        # Save the frame as an image file
        cv2.imwrite(filename, frame)
        print(f"Picture taken and saved as {filename}")
    else:
        print("Failed to capture image")

def main():
    print("Press 'p' to take a picture, or 'q' to quit.")
    
    # Open a connection to the camera
    cap = cv2.VideoCapture(4)
    
    # Check if the camera opened successfully
    if not cap.isOpened():
        print("Error: Could not open camera.")
        return

    # Check the working directory
    print(f"Current working directory: {os.getcwd()}")
    
    while True:
        # Read a frame to display
        ret, frame = cap.read()
        if ret:
            cv2.imshow("Camera", frame)
        else:
            print("Failed to capture frame")

        # Check for key presses using OpenCV
        key = cv2.waitKey(1) & 0xFF
        if key == ord('p'):
            # Create directory if it doesn't exist
            if not os.path.exists('images'):
                os.makedirs('images')

            # Define the filename with a timestamp
            filename = f"images/image_{int(time.time())}.jpg"

            # Take a picture
            take_picture(filename, cap)
        
        elif key == ord('q'):
            print("Program stopped by user")
            break

    # Release the camera and close windows
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
