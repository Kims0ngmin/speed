import cv2
import numpy as np
import os
import tkinter as tk
from PIL import Image, ImageTk

class ImageEditor:
    def __init__(self, root, video_clip):
        self.color_dict = {'x': 'blue', 'y': 'green', 'z': 'orange'}
        self.mouse_x = 0
        self.mouse_y = 0
        self.root = root
        self.root.title("Image Editor")

        self.video_clip = video_clip
        self.image = self.get_first_frame(video_clip)
        self.image_copies = self.image.copy()
        self.display_image = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
        self.photo = ImageTk.PhotoImage(image=Image.fromarray(self.display_image))

        self.frame = tk.Frame(root)
        self.frame.pack()

        self.canvas = tk.Canvas(self.frame, width=self.image.shape[1], height=self.image.shape[0])
        self.canvas.pack(side=tk.LEFT)

        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)

        self.button_frame = tk.Frame(self.frame)
        self.button_frame.pack(side=tk.TOP, anchor="nw")

        self.perform_button = tk.Button(self.button_frame, text="Perform", command=lambda: self.close_window(root), fg="black")
        self.perform_button.pack(side=tk.LEFT, anchor="nw")

        self.onMouse_button = tk.Button(self.button_frame, text="onMouse", command=self.activate_on_mouse, fg="black")
        self.onMouse_button.pack(side=tk.LEFT, anchor="nw")

        self.mini_image_label = tk.Label(self.frame, text="Mini Image")
        self.mini_image_label.pack(side=tk.TOP, anchor="nw")

        self.display_mini_image()

        self.clear_button = tk.Button(root, text="Clear", command=self.clear_lines)
        self.clear_button.pack(side=tk.RIGHT, padx=1)

        self.z_points = []
        self.z_lines = []

        self.current_group = None
        self.csv_filename = "lines_data.csv"
        self.points = []
        self.canvas.bind("<Motion>", self.display_mouse_position)

        self.pts_cnt = 0
        self.pts = np.zeros((4, 2), dtype=np.float32)
        self.on_mouse_active = False

    def get_first_frame(self, video_clip):
        frame = video_clip.get_frame(0)
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        frame = cv2.resize(frame, (640, 480))
        return frame

    def display_mouse_position(self, event):
        self.mouse_x = event.x
        self.mouse_y = event.y
        self.display_mini_image()

    def activate_on_mouse(self):
        self.on_mouse_active = True
        self.canvas.bind("<Button-1>", self.on_mouse)

    def on_mouse(self, event):
        if self.on_mouse_active:
            x, y = event.x, event.y
            self.pts[self.pts_cnt] = [x, y]
            self.pts_cnt += 1

            cv2.circle(self.image, (x, y), 5, (0, 255, 0), -1)
            self.update_displayed_image()

            if self.pts_cnt == 4:
                self.process_points()
                self.on_mouse_active = False
                self.canvas.unbind("<Button-1>")

    def process_points(self):
        topLeft = self.pts[0]
        bottomRight = self.pts[2]
        topRight = self.pts[3]
        bottomLeft = self.pts[1]

        print("topLeft =", topLeft)
        print("bottomRight =", bottomRight)
        print("topRight =", topRight)
        print("bottomLeft =", bottomLeft)

        w = int(np.linalg.norm(np.array(topRight) - np.array(topLeft)))
        h = int(np.linalg.norm(np.array(bottomLeft) - np.array(topLeft)))
        print(f"{w} x {h}")

        pts1 = np.float32([topLeft, topRight, bottomLeft, bottomRight])
        pts2 = np.float32([[0, 0], [w, 0], [0, h], [w, h]])

        M = cv2.getPerspectiveTransform(pts1, pts2)
        dst = cv2.warpPerspective(self.image_copies, M, (int(w), int(h)))

        transformed_images_dir = "./transformed_images"
        if not os.path.exists(transformed_images_dir):
            os.makedirs(transformed_images_dir)

        cv2.imwrite(os.path.join(transformed_images_dir, "transform.jpg"), dst)

        self.txt_file_path = os.path.join(transformed_images_dir, "mouse_points.txt")
        with open(self.txt_file_path, 'w') as f:
            for point in self.pts:
                f.write(f"{point[0]}, {point[1]}\n")
        print(f"Coordinates saved to {self.txt_file_path}")

    def display_mini_image(self):
        region_size = 80
        image_height, image_width = self.image.shape[:2]
        top_left_x = self.mouse_x - 40
        top_left_y = self.mouse_y - 40
        bottom_right_x = self.mouse_x + 40
        bottom_right_y = self.mouse_y + 40

        image_zoom = np.zeros((region_size, region_size, 3), dtype=np.uint8)

        insert_x1 = max(0, -top_left_x)
        insert_y1 = max(0, -top_left_y)
        insert_x2 = region_size - max(0, bottom_right_x - image_width)
        insert_y2 = region_size - max(0, bottom_right_y - image_height)

        src_x1 = max(0, top_left_x)
        src_y1 = max(0, top_left_y)
        src_x2 = min(image_width, bottom_right_x)
        src_y2 = min(image_height, bottom_right_y)

        image_zoom[insert_y1:insert_y2, insert_x1:insert_x2] = self.image[src_y1:src_y2, src_x1:src_x2]

        mini_photo = cv2.resize(image_zoom, (160, 160))
        mini_photo = cv2.cvtColor(mini_photo, cv2.COLOR_BGR2RGB)
        cv2.circle(mini_photo, (80, 80), 7, (255, 255, 255), 2)
        mini_photo = ImageTk.PhotoImage(image=Image.fromarray(mini_photo))

        self.mini_image_label.config(image=mini_photo)
        self.mini_image_label.image = mini_photo

    def clear_lines(self):
        self.pts_cnt = 0
        self.pts = np.zeros((4, 2), dtype=np.float32)
        self.image = self.get_first_frame(self.video_clip)
        self.update_displayed_image()

    def update_displayed_image(self):
        self.display_image = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
        self.photo = ImageTk.PhotoImage(image=Image.fromarray(self.display_image))
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)

## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## 
## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## 

    # Function to load stored mouse points
    def load_mouse_points(self, file_path):
        points = []
        with open(file_path, 'r') as file:
            for line in file:
                x, y = map(float, line.strip().split(','))
                points.append([x, y])
        return np.array(points, dtype=np.float32)

    # Function to apply perspective transformation
    def apply_perspective_transform(self, extrac_frame, points):
        topLeft = points[0]
        bottomRight = points[2]
        topRight = points[3]
        bottomLeft = points[1]

        w = int(np.linalg.norm(np.array(topRight) - np.array(topLeft)))
        h = int(np.linalg.norm(np.array(bottomLeft) - np.array(topLeft)))

        pts1 = np.float32([topLeft, topRight, bottomLeft, bottomRight])
        pts2 = np.float32([[0, 0], [w, 0], [0, h], [w, h]])

        M = cv2.getPerspectiveTransform(pts1, pts2)
        dst = cv2.warpPerspective(extrac_frame, M, (int(w), int(h)))

        return dst

    # Function to load the next extrac_frame
    def load_next_frame_index(self, current_index):
        next_index = current_index + 1
        if next_index < len(self.frame_files):
            return next_index
        else:
            return current_index

    # Function to load the previous extrac_frame
    def load_prev_frame_index(self, current_index):
        prev_index = current_index - 1
        if prev_index >= 0:
            return prev_index
        else:
            return current_index
        
    # Function to add extrac_frame name to the image
    def add_frame_name_to_image(self, image, frame_name):
        cv2.putText(image, frame_name, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.1, (255, 255, 255), 2, cv2.LINE_AA)

    # Function to update img_time with the current extrac_frame name
    def update_img_time_from_frame_name(self, frame_name):
        global img_time
        timestamp = frame_name.split('_')[1].replace('.jpg', '')
        img_time = timestamp



    def close_window(self, window):
        # # Load all extrac_frame names in the dataset directory
        # dataset_dir = f"./extract_video/"
        # self.frame_files = sorted([f for f in os.listdir(dataset_dir) if f.startswith('frame_') and f.endswith('.jpg')])

        # current_frame_index = 0
        # current_frame_index = self.load_next_frame_index(current_frame_index)
        # frame_path = os.path.join(dataset_dir, self.frame_files[current_frame_index])
        # extrac_frame = cv2.imread(frame_path)

        # mouse_points = self.load_mouse_points(self.txt_file_path)
        # transformed_frame = self.apply_perspective_transform(extrac_frame, mouse_points)
        # width = transformed_frame.shape[1]

        # transformed_image_path = f"./test_fol/{self.frame_files[current_frame_index]}"
            
        # cv2.imwrite(transformed_image_path, transformed_frame)

        # # Display the initial frame with frame name
        # win_name = "length_estimation"
        # self.update_img_time_from_frame_name(self.frame_files[current_frame_index])
        # self.add_frame_name_to_image(transformed_frame, self.frame_files[current_frame_index])
        # cv2.imshow(win_name, transformed_frame)
        # Function to process and save all frames
        # Load all frame names in the dataset directory
        dataset_dir = f"./extract_video/"
        self.frame_files = sorted([f for f in os.listdir(dataset_dir) if f.startswith('frame_') and f.endswith('.jpg')])

        # Load mouse points
        mouse_points = self.load_mouse_points(self.txt_file_path)

        # Create output directory if it doesn't exist
        output_dir = "./test_fol/"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        for frame_file in self.frame_files:
            frame_path = os.path.join(dataset_dir, frame_file)
            frame = cv2.imread(frame_path)
            frame = cv2.resize(frame, (640, 480))
            if frame is None:
                continue

            transformed_frame = self.apply_perspective_transform(frame, mouse_points)
            transformed_image_path = os.path.join(output_dir, frame_file)

            self.update_img_time_from_frame_name(frame_file)
            self.add_frame_name_to_image(transformed_frame, frame_file)
            cv2.imwrite(transformed_image_path, transformed_frame)
            print(f"Processed and saved: {transformed_image_path}")

        print("All frames have been processed and saved.")

        window.destroy()
