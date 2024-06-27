import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import math
import csv
from datetime import datetime
from tkinter import scrolledtext
import matplotlib.colors as mcolors
from moviepy.editor import VideoFileClip

class ImageEditor:
    def __init__(self, root, image_path):
        self.color_dict = {'x': 'blue', 'y': 'green', 'z': 'orange'}
        self.mouse_x = 0
        self.mouse_y = 0
        self.root = root
        self.root.title("Image Editor")

        self.image_path = image_path
        self.image = cv2.imread(image_path)
        self.image = image_path
        self.image = cv2.resize(self.image, (640, 480))
        self.image_copies = [self.image.copy()]
        self.display_image = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
        self.photo = ImageTk.PhotoImage(image=Image.fromarray(self.display_image))

        # Create frame
        self.frame = tk.Frame(root)
        self.frame.pack()

        # Creating and Placing canvas
        self.canvas = tk.Canvas(self.frame, width=self.image.shape[1], height=self.image.shape[0])
        self.canvas.pack(side=tk.LEFT)

        # Add Image
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)
      
        # 버튼을 담을 프레임 생성
        self.button_frame = tk.Frame(self.frame)
        self.button_frame.pack(side=tk.TOP, anchor="nw")

        self.load_video_button = tk.Button(self.button_frame, text="Load Video", command=self.load_video, fg="blue")
        self.load_video_button.pack(side=tk.LEFT, anchor="nw")

        self.play_video_button = tk.Button(self.button_frame, text="Play Video", command=self.play_video_at_time, fg="green")
        self.play_video_button.pack(side=tk.LEFT, anchor="nw")
        
        self.pause_video_button = tk.Button(self.button_frame, text="Pause Video", command=self.pause_video, fg="orange")
        self.pause_video_button.pack(side=tk.LEFT, anchor="nw")

        self.pick_line_button = tk.Button(self.button_frame, text="Line Maker", command=lambda: self.pick_points('z'), fg="black")
        self.pick_line_button.pack(side=tk.LEFT, anchor="nw")

        self.time_label = tk.Label(root, text="Enter time to start (seconds):")
        self.time_label.pack(pady=15)     
        self.time_entry = tk.Entry(root)
        self.time_entry.pack(pady=5)

        status_label = tk.Label(root, text="No video loaded")
        status_label.pack(pady=20)

        
        # 버튼 프레임 아래에 라벨 배치
        self.mini_image_label = tk.Label(self.frame, text="Mini Image")
        self.mini_image_label.pack(side=tk.TOP, anchor="nw")

        # Display the mini image
        self.display_mini_image()
        
        self.clear_button = tk.Button(root, text="Clear", command=self.clear_lines)
        self.clear_button.pack(side=tk.RIGHT, padx=1)

        # Points for 'z' group
        self.z_points = [] 
        self.z_lines = []
        
        self.current_group = None

        self.csv_filename = "lines_data.csv"  # CSV file to store line coordinates

        self.points = []
        self.canvas.bind("<Motion>", self.display_mouse_position)
        

    def display_mouse_position(self, event):
        self.mouse_x = event.x
        self.mouse_y = event.y

        # 마우스 위치가 변경될 때마다 미니 이미지 업데이트
        self.display_mini_image()


    def pick_points(self, group):
        self.current_group = group
        self.points = []  # Reset points when a new group is selected
        self.canvas.bind("<Button-1>", self.get_point)
        self.canvas.bind("<Motion>", self.display_mouse_position)


    def get_point(self, event):
        x, y = event.x, event.y
        self.points.append((x, y))

        # Draw a small circle at the picked point with group-specific color
        point_color= self.color_dict.get(self.current_group)
        rgb_color = mcolors.to_rgb(point_color)
        point_color = (int(rgb_color[2] * 255), int(rgb_color[1] * 255), int(rgb_color[0] * 255))

        cv2.circle(self.image, (x, y), 3, point_color, -1)
        getattr(self, f"{self.current_group}_points").append((x, y))

        if len(self.points) == 2:
            # Draw a line between the two points with group-specific color
            line_color = self.color_dict.get(self.current_group)
            rgb_color = mcolors.to_rgb(line_color)
            line_color = (int(rgb_color[2] * 255), int(rgb_color[1] * 255), int(rgb_color[0] * 255))
            cv2.line(self.image, self.points[0], self.points[1], line_color, 2)

            # Store the line coordinates for the current group
            getattr(self, f"{self.current_group}_lines").append(self.points)
            self.points = []
            self.image_copies.append(self.image.copy())
                
            # Reset points after drawing a line
            self.points = []

        # Update the displayed image
        self.display_image = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
        self.photo = ImageTk.PhotoImage(image=Image.fromarray(self.display_image))
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)      

    def draw_marker(self, intersection_point, color):
        # Draw a marker or line at the calculated intersection point
        if intersection_point:
            self.update_displayed_image()            
        
    def clear_lines(self):
        if self.current_group is not None:
            # Remove the last line for the currently selected group
            group_lines = getattr(self, f"{self.current_group}_lines")
            if group_lines:
                group_lines.pop()

            # Remove the last two points for the currently selected group
            group_points = getattr(self, f"{self.current_group}_points")
            if len(group_points) >= 2:
                group_points.pop()
                group_points.pop()

            self.image = cv2.imread(self.image_path)
            self.image = cv2.resize(self.image, (640, 480))
            self.update_displayed_image()
            
    def update_displayed_image(self):
            for group in ['x', 'y', 'z']:
                group_points = getattr(self, f"{group}_points")
                group_lines = getattr(self, f"{group}_lines")
                line_color = self.color_dict.get(group)
                rgb_color = mcolors.to_rgb(line_color)
                line_color = (int(rgb_color[2] * 255), int(rgb_color[1] * 255), int(rgb_color[0] * 255))

                # Redraw all points for the current group
                for point in group_points:
                    x, y = point
                    cv2.circle(self.image, (x, y), 3, line_color, -1)

                # Redraw all lines for the current group
                for line in group_lines:
                    x1, y1 = line[0]
                    x2, y2 = line[1]
                    cv2.line(self.image, (x1, y1), (x2, y2), line_color, 2)

            self.display_image = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
            self.photo = ImageTk.PhotoImage(image=Image.fromarray(self.display_image))
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)
            # Call the method to update the mini image
            self.display_mini_image()
            
    def display_mini_image(self):
        # Set area size based on center
        region_size = 100
        
        image_height, image_width = self.image.shape[:2]

        # Calculate the desired size of the area at the mouse location
        top_left_x = self.mouse_x - 50
        top_left_y = self.mouse_y - 50
        bottom_right_x = self.mouse_x + 50
        bottom_right_y = self.mouse_y + 50

        # Create a full area of black background first
        image_zoom = np.zeros((region_size, region_size, 3), dtype=np.uint8)

        # Calculate where to insert the actual image
        insert_x1 = max(0, -top_left_x)
        insert_y1 = max(0, -top_left_y)
        insert_x2 = region_size - max(0, bottom_right_x - image_width)
        insert_y2 = region_size - max(0, bottom_right_y - image_height)

        # Calculate the coordinates to import from the source image
        src_x1 = max(0, top_left_x)
        src_y1 = max(0, top_left_y)
        src_x2 = min(image_width, bottom_right_x)
        src_y2 = min(image_height, bottom_right_y)

        # Cut the area from the image and insert it into the black background
        image_zoom[insert_y1:insert_y2, insert_x1:insert_x2] = self.image[src_y1:src_y2, src_x1:src_x2]

        mini_photo = cv2.resize(image_zoom, (200, 200))

        mini_photo = cv2.cvtColor(mini_photo, cv2.COLOR_BGR2RGB)
        cv2.circle(mini_photo, (100, 100), 7, (255, 255, 255), 2)
        mini_photo = ImageTk.PhotoImage(image=Image.fromarray(mini_photo))

        self.mini_image_label.config(image=mini_photo)
        self.mini_image_label.image = mini_photo
### ### ###
    def load_video(self):
        global video_clip, paused, current_time, subclip_duration
        file_path = None
        file_path = filedialog.askopenfilename(filetypes=[("MP4 files", "*.mp4"), ("All files", "*.*")])
        if file_path:
            video_clip = VideoFileClip(file_path)
            # self.status_label.config(text=f"Loaded video: {file_path}")
            paused = True
            current_time = 0
            subclip_duration = video_clip.duration

    def resize_frame(self, frame, width, height):
        """cv2를 사용하여 프레임 크기 조정"""
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)  # RGB에서 BGR로 변환
        resized_frame = cv2.resize(frame, (width, height))
        return cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)  # BGR에서 RGB로 변환
    
    def update_frame(self):
        global video_clip, canvas, current_time, paused, subclip_duration
        if video_clip and not paused:
            if current_time < subclip_duration:
                frame = video_clip.get_frame(current_time)
                frame = self.resize_frame(frame, 640, 480)
                img = Image.fromarray(frame)
                imgtk = ImageTk.PhotoImage(image=img)
                self.canvas.create_image(0, 0, anchor=tk.NW, image=imgtk)
                self.canvas.image = imgtk
                current_time += 1 / video_clip.fps
            else:
                paused = True
            self.root.after(20, self.update_frame)

    def play_video_at_time(self):
        global paused, current_time
        if video_clip:
            try:
                time = float(self.time_entry.get())
                if 0 <= time <= video_clip.duration:
                    paused = False
                    current_time = time
                    self.update_frame()
                else:
                    self.status_label.config(text="Invalid time: Out of range")
            except ValueError:
                self.status_label.config(text="Invalid time: Please enter a number")
        else:
            self.status_label.config(text="No video loaded")

    def pause_video(self):
        global paused
        paused = True