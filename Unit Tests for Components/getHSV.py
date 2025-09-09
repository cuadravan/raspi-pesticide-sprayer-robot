import cv2
import numpy as np

# Load the image
image = cv2.imread("/home/kenvason/Documents/RaspiCode/kenvason/images/image_1722402409.jpg")

# Get the dimensions of the image
height, width, _ = image.shape

# Define the size of the central square region (adjust as needed)
region_size = 50

# Calculate the top-left corner of the central square region
x = (width // 2) - (region_size // 2)
y = (height // 2) - (region_size // 2)

# Convert the image to HSV color space
hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

# Function to get the HSV values of a region
def get_hsv_range(image, x, y, width, height):
    # Crop the region
    region = image[y:y+height, x:x+width]
    # Convert the region to HSV
    hsv_region = cv2.cvtColor(region, cv2.COLOR_BGR2HSV)
    # Calculate the average HSV values
    mean_hsv = np.mean(hsv_region, axis=(0, 1))
    return mean_hsv

# Get the mean HSV values of the central square region
mean_hsv = get_hsv_range(image, x, y, region_size, region_size)
print("Mean HSV:", mean_hsv)

# Define the HSV range with some tolerance
lower_green = np.array([mean_hsv[0] - 5, mean_hsv[1] - 20, mean_hsv[2] - 20])
upper_green = np.array([mean_hsv[0] + 5, mean_hsv[1] + 20, mean_hsv[2] + 20])

print("Lower Green:", lower_green)
print("Upper Green:", upper_green)

# Create a mask for the specific green color
mask = cv2.inRange(hsv_image, lower_green, upper_green)
result = cv2.bitwise_and(image, image, mask=mask)

# Draw a rectangle around the sampled region for visualization
cv2.rectangle(image, (x, y), (x + region_size, y + region_size), (255, 0, 0), 2)

# Display the original image with the rectangle, mask, and result
cv2.imshow("Original Image", image)
cv2.imshow("Mask", mask)
cv2.imshow("Detected Green Plant", result)

cv2.destroyAllWindows()
