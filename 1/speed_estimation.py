import cv2
import numpy as np
import os

d_name = "18"
img_time = "4.00"  ##어차피 이미지 이름으로 계속 업데이트 될거라 안바꿔줘도 됨



time_start = 3.00
full_length = 12  # meters


estimated_length = 0  # meters

# Function to load stored mouse points
def load_mouse_points(file_path):
    points = []
    with open(file_path, 'r') as file:
        for line in file:
            x, y = map(float, line.strip().split(','))
            points.append([x, y])
    return np.array(points, dtype=np.float32)

# Function to apply perspective transformation
def apply_perspective_transform(frame, points):
    topLeft = points[0]
    bottomRight = points[2]
    topRight = points[3]
    bottomLeft = points[1]

    w = int(np.linalg.norm(np.array(topRight) - np.array(topLeft)))
    h = int(np.linalg.norm(np.array(bottomLeft) - np.array(topLeft)))

    pts1 = np.float32([topLeft, topRight, bottomLeft, bottomRight])
    pts2 = np.float32([[0, 0], [w, 0], [0, h], [w, h]])

    M = cv2.getPerspectiveTransform(pts1, pts2)
    dst = cv2.warpPerspective(frame, M, (int(w), int(h)))

    return dst

# Load all frame names in the dataset directory
dataset_dir = f"./{d_name}/"
frame_files = sorted([f for f in os.listdir(dataset_dir) if f.startswith('frame_') and f.endswith('.jpg')])

# Function to load the next frame
def load_next_frame_index(current_index):
    next_index = current_index + 1
    if next_index < len(frame_files):
        return next_index
    else:
        return current_index

# Function to load the previous frame
def load_prev_frame_index(current_index):
    prev_index = current_index - 1
    if prev_index >= 0:
        return prev_index
    else:
        return current_index

# Load the initial frame and mouse points
mouse_points_path = f"./{d_name}/mouse_points.txt"
mouse_points = load_mouse_points(mouse_points_path)

current_frame_index = 0
frame_path = os.path.join(dataset_dir, frame_files[current_frame_index])
frame = cv2.imread(frame_path)
transformed_frame = apply_perspective_transform(frame, mouse_points)

width = transformed_frame.shape[1]

# Function to add frame name to the image
def add_frame_name_to_image(image, frame_name):
    cv2.putText(image, frame_name, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

# Function to update img_time with the current frame name
def update_img_time_from_frame_name(frame_name):
    global img_time
    timestamp = frame_name.split('_')[1].replace('.jpg', '')
    img_time = timestamp

# Display the initial frame with frame name
win_name = "length_estimation"
update_img_time_from_frame_name(frame_files[current_frame_index])
add_frame_name_to_image(transformed_frame, frame_files[current_frame_index])
cv2.imshow(win_name, transformed_frame)

# Mouse callback function for length and speed estimation
def onMouse(event, x, y, flags, param):
    global estimated_length

    if event == cv2.EVENT_LBUTTONDOWN:
        cv2.circle(transformed_frame, (x, y), 10, (0, 255, 0), -1)
        cv2.imshow(win_name, transformed_frame)
        estimated_length = (x / width) * full_length  # meters
        print(img_time)
        estimated_velocity = (estimated_length / 1000.0) / ((float(img_time) - time_start) / 3600.0)  # km/h
        print("length : %.1f [m]" % estimated_length)
        print("velocity : %.1f [km/h]" % estimated_velocity)

cv2.setMouseCallback(win_name, onMouse)

# Keyboard event handling to detect right and left arrow key press
while True:
    key = cv2.waitKey(0)
    if key == 27:  # ESC key to exit
        break
    elif key == 83:  # Right arrow key
        current_frame_index = load_next_frame_index(current_frame_index)
        frame_path = os.path.join(dataset_dir, frame_files[current_frame_index])
        
        if os.path.exists(frame_path):
            frame = cv2.imread(frame_path)
            transformed_frame = apply_perspective_transform(frame, mouse_points)
            update_img_time_from_frame_name(frame_files[current_frame_index])
            add_frame_name_to_image(transformed_frame, frame_files[current_frame_index])
            
            transformed_image_path = f"./transformed_images/{d_name}/{frame_files[current_frame_index]}"
            if not os.path.exists(os.path.dirname(transformed_image_path)):
                os.makedirs(os.path.dirname(transformed_image_path))
            
            cv2.imwrite(transformed_image_path, transformed_frame)
            cv2.imshow(win_name, transformed_frame)
        else:
            print("No more frames available.")
    elif key == 81:  # Left arrow key
        current_frame_index = load_prev_frame_index(current_frame_index)
        frame_path = os.path.join(dataset_dir, frame_files[current_frame_index])
        
        if os.path.exists(frame_path):
            frame = cv2.imread(frame_path)
            transformed_frame = apply_perspective_transform(frame, mouse_points)
            update_img_time_from_frame_name(frame_files[current_frame_index])
            add_frame_name_to_image(transformed_frame, frame_files[current_frame_index])
            
            transformed_image_path = f"./transformed_images/{d_name}/{frame_files[current_frame_index]}"
            if not os.path.exists(os.path.dirname(transformed_image_path)):
                os.makedirs(os.path.dirname(transformed_image_path))
            
            cv2.imwrite(transformed_image_path, transformed_frame)
            cv2.imshow(win_name, transformed_frame)
        else:
            print("No more frames available.")

cv2.destroyAllWindows()

