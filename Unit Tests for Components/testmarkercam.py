import cv2
import numpy as np

def detect_shapes(frame):
    # Convert the frame to HSV color space
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Define the range for the red color
    lower_red1 = np.array([0, 70, 50])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([170, 70, 50])
    upper_red2 = np.array([180, 255, 255])

    # Define the range for the blue color
    lower_blue = np.array([100, 150, 0])
    upper_blue = np.array([140, 255, 255])

    # Create masks for the red and blue colors
    mask_red1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask_red2 = cv2.inRange(hsv, lower_red2, upper_red2)
    mask_red = mask_red1 + mask_red2
    mask_blue = cv2.inRange(hsv, lower_blue, upper_blue)

    # Combine the masks
    mask = mask_red + mask_blue

    # Find contours in the combined masked image
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for contour in contours:
        # Approximate the contour
        epsilon = 0.02 * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)

        # Check if the contour area is large enough
        area = cv2.contourArea(contour)
        if area > 15000:  # You can adjust the threshold as needed
            if len(approx) == 4:
                # Check if the shape is a square or a rectangle
                x, y, w, h = cv2.boundingRect(approx)

                # Determine the color of the square
                mask_color = cv2.inRange(hsv[y:y+h, x:x+w], lower_blue, upper_blue)
                if cv2.countNonZero(mask_color) > (w * h) / 2:
                    color = "Blue"
                    color_code = (255, 0, 0)
                else:
                    color = "Red"
                    color_code = (0, 0, 255)
                # It's a square
                cv2.drawContours(frame, [approx], 0, color_code, 5)
                cv2.putText(frame, f"{color} Square", (approx[0][0][0], approx[0][0][1] - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, color_code, 2)

    return frame

# Capture video from the webcam
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Detect red and blue squares in the frame
    frame = detect_shapes(frame)

    # Display the frame with detected shapes
    cv2.imshow('Frame', frame)

    # Press 'q' to exit the loop
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the webcam and close windows
cap.release()
cv2.destroyAllWindows()
