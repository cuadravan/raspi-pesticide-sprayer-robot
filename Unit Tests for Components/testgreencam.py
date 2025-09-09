import cv2
import numpy as np

# Define the range for the green color in HSV
#lower_green = np.array([32.7516, 167.3768, 76.9592])
#upper_green = np.array([52.7516, 207.3768, 116.9592])
#lower_green = np.array([38.2836, 47.6532, 91.3284])
#upper_green = np.array([58.2836, 127.6532, 171.3284])
#lower_green = np.array([28.6244, 141.16, 120.1752])
#upper_green = np.array([48.6264, 221.16, 200.1752])


# Initialize the webcam
index = int(input("Which camera do you want to use? 2 or 4: "))
cap = cv2.VideoCapture(index)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
if index == 2:
    lower_green = np.array([45.3567, 76.9016, 51.4])
    upper_green = np.array([55.3568, 116.9016, 131.4])
elif index == 4:
    lower_green = np.array([43.8816, 60.7828, 107.3056])
    upper_green = np.array([53.8816, 100.7828, 147.3056])


while True:
    greenDetect = False
    # Capture frame-by-frame
    ret, frame = cap.read()

    if not ret:
        print("Failed to capture image")
        break

    # Convert the frame to the HSV color space
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
        # Create a mask for the green color
    mask = cv2.inRange(hsv, lower_green, upper_green)
    
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

    # Find contours in the mask
    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # Get the frame dimensions
    height, width = frame.shape[:2]

    # Define the center region (a box in the middle of the frame)
    center_x, center_y = width // 2, height // 2
    center_region_size = 50
    top_left = (center_x - center_region_size, center_y - center_region_size)
    bottom_right = (center_x + center_region_size, center_y + center_region_size)

    # Draw the center region rectangle
    cv2.rectangle(frame, top_left, bottom_right, (0, 255, 0), 2)

    # Check if any contour is within the center region
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        if (center_x - center_region_size < x < center_x + center_region_size) and \
           (center_y - center_region_size < y < center_y + center_region_size):
            # Draw the contour
            cv2.drawContours(frame, [contour], -1, (0, 255, 0), 2)
            greenDetect = True
    if greenDetect == True:
        print("Green is detected")
    else:
        print("Green is not detected")
        
    # Display the resulting frame
    cv2.imshow('Frame', frame)
    cv2.imshow('Mask', mask)

    # Break the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the webcam and close all OpenCV windows
cap.release()
cv2.destroyAllWindows()
