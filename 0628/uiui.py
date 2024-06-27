import tkinter as tk
from tkinter import *
from tkinter import filedialog
from moviepy.editor import VideoFileClip
import cv2
from PIL import Image, ImageTk
import numpy as np
import os
import ui_func as func

# 전역 변수로 비디오 클립 선언
video_clip = None
canvas = None
video_label = None
root = None
play_button = None
pause_button = None
paused = True
current_time = 0
subclip_duration = 0
video_load_on = 0

pts_cnt = 0
pts = np.zeros((4, 2), dtype=np.float32)
d_name = "transform"
img_time = "tt"

# 전역 변수로 scale과 time_label 선언
scale = None
time_label = None

def load_video():
    global video_clip, paused, current_time, subclip_duration, scale, time_label, var1
    file_path = filedialog.askopenfilename(filetypes=[("MP4 files", "*.mp4"), ("All files", "*.*")])
    if file_path:
        video_clip = VideoFileClip(file_path)
        status_label.config(text=f"Loaded video: {file_path}")
        paused = True
        current_time = 0
        subclip_duration = video_clip.duration
        
        # Scale과 time_label 생성
        var1 = IntVar()
        scale = Scale(root, variable=var1, orient="horizontal", showvalue=True, tickinterval=int(subclip_duration), to=int(subclip_duration), length=200, command=select)
        scale.pack()

        time_label = tk.Label(button_frame1)
        time_label.pack(side=tk.LEFT, anchor="n")

def resize_frame(frame, width, height):
    """cv2를 사용하여 프레임 크기 조정"""
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)  # RGB에서 BGR로 변환
    resized_frame = cv2.resize(frame, (width, height))
    return cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)  # BGR에서 RGB로 변환

def update_frame():
    global video_clip, canvas, current_time, paused, subclip_duration
    if video_clip and not paused:
        if current_time < subclip_duration:
            frame = video_clip.get_frame(current_time)
            frame = resize_frame(frame, 640, 480)
            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)
            canvas.create_image(0, 0, anchor=tk.NW, image=imgtk)
            canvas.image = imgtk
            current_time += 1 / video_clip.fps
        else:
            paused = True
        root.after(20, update_frame)

def play_video_at_time():
    global paused, current_time
    if video_clip:
        try:
            time = float(scale.get())
            if 0 <= time <= video_clip.duration:
                paused = False
                current_time = time
                update_frame()
            else:
                status_label.config(text="Invalid time: Out of range")
        except ValueError:
            status_label.config(text="Invalid time: Please enter a number")
    else:
        status_label.config(text="No video loaded")

def pause_video():
    global paused
    paused = True

def select(event):
    value = "Enter time to start (seconds) : "+ str(scale.get())
    time_label.config(text = value)

def perform_action():
    global video_clip
    # 새로운 창 생성
    new_root = tk.Toplevel()
    app = func.ImageEditor(new_root, video_clip)

def center_window(root, width, height):
    # 화면의 가로 세로 크기 가져오기
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    
    # 화면 중앙의 위치 계산
    x = int((screen_width / 2) - (width / 2))
    y = int((screen_height / 2) - (height / 2))
    
    # 윈도우 크기와 위치 설정
    root.geometry(f'{width}x{height}+{x}+{y}')

## ~ ## ~ ##
def onMouse(self, event, x, y):
    global pts_cnt
    if event == cv2.EVENT_LBUTTONDOWN:
        # 좌표에 초록색 동그라미 표시
        cv2.circle(self.imgtk, (x, y), 10, (0, 255, 0), -1)
        cv2.imshow("Scanning", self.imgtk)

        # 마우스 좌표 저장
        pts[pts_cnt] = [x, y]
        pts_cnt += 1
        if pts_cnt == 4:

            topLeft = pts[0]
            bottomRight = pts[2]
            topRight = pts[3]
            bottomLeft = pts[1]
            
            print("topLeft =", topLeft)
            print("bottomRight =", bottomRight)
            print("topRight =", topRight)
            print("bottomLeft =", bottomLeft)

            w = int(np.linalg.norm(np.array(topRight) - np.array(topLeft)))
            h = int(np.linalg.norm(np.array(bottomLeft) - np.array(topLeft)))
            print(f"{w} x {h}")
            
            # Coordinates that you want to Perspective Transform
            pts1 = np.float32([topLeft, topRight, bottomLeft, bottomRight])
            # Size of the Transformed Image
            pts2 = np.float32([[0, 0], [w, 0], [0, h], [w, h]])
            
            M = cv2.getPerspectiveTransform(pts1, pts2)
            dst = cv2.warpPerspective(self.imgtk, M, (int(w), int(h)))
            
            # Create the transformed images directory if it does not exist
            transformed_images_dir = "./transformed_images/"+d_name
            if not os.path.exists(transformed_images_dir):
                os.makedirs(transformed_images_dir)
            
            cv2.imwrite(os.path.join(transformed_images_dir, img_time + ".jpg"), dst)
            cv2.imshow("dst", dst)

            # Store the points in a text file within the dataset folder
            dataset_folder = "./"+d_name
            if not os.path.exists(dataset_folder):
                os.makedirs(dataset_folder)

            txt_file_path = os.path.join(dataset_folder, "mouse_points.txt")
            with open(txt_file_path, 'w') as f:
                for point in pts:
                    f.write(f"{point[0]}, {point[1]}\n")
            print(f"좌표가 {txt_file_path}에 저장되었습니다.")
## ~ ## ~ ##

# Tkinter 윈도우 생성
root = tk.Tk()
root.title("Simple Video Player")

# 윈도우 크기 설정 및 중앙 배치
window_width = 950
window_height = 600
center_window(root, window_width, window_height)

# UI 요소 추가

# 비디오 프레임 생성
video_frame = tk.Frame()
video_frame.pack(side=tk.LEFT, anchor="n")

status_label = tk.Label(video_frame, text="No video loaded")
status_label.pack(pady=20)

canvas = tk.Canvas(video_frame, width=640, height=480)
canvas.pack(side=tk.LEFT, anchor="nw")

# 버튼을 담을 프레임 생성
button_frame = tk.Frame()
button_frame.pack(side=tk.TOP, anchor="nw")

# 버튼을 담을 프레임1 생성
button_frame1 = tk.Frame()
button_frame1.pack(side=tk.TOP, anchor="c")

# 버튼을 담을 프레임2 생성
button_frame2 = tk.Frame()
button_frame2.pack(side=tk.BOTTOM, anchor="w")

load_button = tk.Button(button_frame, text="Load Video", command=load_video)
load_button.pack(side=tk.LEFT, anchor="nw")

play_button = tk.Button(button_frame, text="Play Video", command=play_video_at_time)
play_button.pack(side=tk.LEFT, anchor="nw")

pause_button = tk.Button(button_frame, text="Pause Video", command=pause_video)
pause_button.pack(side=tk.LEFT, anchor="nw")

perform_button = tk.Button(button_frame2, text="Perform", command=perform_action)
perform_button.pack(side=tk.LEFT, anchor="w")

# Tkinter 이벤트 루프 시작
root.mainloop()
