import tkinter as tk
from tkinter import *
from tkinter import filedialog
from moviepy.editor import VideoFileClip
import cv2
from PIL import Image, ImageTk
import numpy as np
import os
import ui_func as func
import t1 as t 

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

# 전역 변수로 scale과 time_label 선언
scale = None
time_label = None

def load_video():
    global video_clip, paused, current_time, subclip_duration, scale, time_label, var1
    status_label.config(text="Extracting frame from video...")
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

        ## ##

        output_folder = 'extract_video'
        cap = cv2.VideoCapture(file_path)
        if not cap.isOpened():
            print("동영상 파일을 열 수 없습니다.")
            return

        # 이미지 저장을 위한 폴더 생성
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        # 이미지 저장
        frame_count = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # 이미지 파일명 생성 (프레임 번호를 시간으로 변환하여 사용)
            time_in_ms = cap.get(cv2.CAP_PROP_POS_MSEC)
            time_in_sec = time_in_ms / 1000
            image_name = "%s/frame_%.2f.jpg" % (output_folder, time_in_sec)

            # 이미지 저장
            cv2.imwrite(image_name, frame)
            frame_count += 1
        
        # 작업 완료 후 해제
        cap.release()
        print(f"{frame_count}개의 이미지를 저장했습니다.")
        ## ## 


def resize_frame(frame, width, height):
    """cv2를 사용하여 프레임 크기 조정"""
    # frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)  # RGB에서 BGR로 변환
    resized_frame = cv2.resize(frame, (width, height))
    return resized_frame#cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)  # BGR에서 RGB로 변환

def update_frame():
    global current_image_index, images, canvas, paused
    if not paused and current_image_index < len(images):
        frame = images[current_image_index]
        frame = resize_frame(frame, 640, 480)
        img = Image.fromarray(frame)
        imgtk = ImageTk.PhotoImage(image=img)
        canvas.create_image(0, 0, anchor=tk.NW, image=imgtk)
        canvas.image = imgtk
        current_image_index += 1
        root.after(20, update_frame)
    else:
        paused = True

def play_images():
    global video_load_on

    if video_load_on == 0:
        global images, current_image_index
        images = []
        current_image_index = 0
        folder_path = filedialog.askdirectory()
        if folder_path:
            for filename in sorted(os.listdir(folder_path)):
                if filename.endswith('.jpg'):
                    img_path = os.path.join(folder_path, filename)
                    img = cv2.imread(img_path)
                    if img is not None:
                        images.append(img)
            status_label.config(text=f"Loaded {len(images)} images from: {folder_path}")
    
    video_load_on = 1
    global paused
    paused = False
    update_frame()

def pause_images():
    global paused, current_image_index
    print("Stop frame : "+str(current_image_index))
    paused = True

# def load_images():
#     global images, current_image_index
#     images = []
#     current_image_index = 0
#     folder_path = filedialog.askdirectory()
#     if folder_path:
#         for filename in sorted(os.listdir(folder_path)):
#             if filename.endswith('.jpg'):
#                 img_path = os.path.join(folder_path, filename)
#                 img = cv2.imread(img_path)
#                 if img is not None:
#                     images.append(img)
#         status_label.config(text=f"Loaded {len(images)} images from: {folder_path}")

def select(event):
    value = "Enter time to start (seconds) : "+ str(scale.get())
    time_label.config(text = value)

def transform_action():
    global video_clip
    # 새로운 창 생성
    new_root = tk.Toplevel()
    # app = func.ImageEditor(new_root, video_clip)
    app = t.ImageEditor(new_root, video_clip)

def speed_est():
    print("speed!")
    on_mouse_active = True
    canvas.bind("<Button-1>", onMouse)

# Mouse callback function for length and speed estimation
def onMouse(self, event, x, y, flags, param):
    global estimated_length, full_length, img_time
    full_length = 6

    if event == cv2.EVENT_LBUTTONDOWN:
        cv2.circle(canvas.image, (x, y), 10, (0, 255, 0), -1)
        # cv2.imshow(win_name, transformed_frame)
        estimated_length = (x / width1) * full_length  # meters
        print(img_time)
        estimated_velocity = (estimated_length / 1000.0) / ((float(img_time) - time_start) / 3600.0)  # km/h
        print("length : %.1f [m]" % estimated_length)
        print("velocity : %.1f [km/h]" % estimated_velocity)

# cv2.setMouseCallback(win_name, onMouse)

def center_window(root, width, height):
    # 화면의 가로 세로 크기 가져오기
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    
    # 화면 중앙의 위치 계산
    x = int((screen_width / 2) - (width / 2))
    y = int((screen_height / 2) - (height / 2))
    
    # 윈도우 크기와 위치 설정
    root.geometry(f'{width}x{height}+{x}+{y}')


# Function to update img_time with the current extrac_frame name
def update_img_time_from_frame_name(frame_name):
    global img_time
    timestamp = frame_name.split('_')[1].replace('.jpg', '')
    img_time = timestamp

def start_checker():
    global time_start, width1, img_time
    img_time = update_img_time_from_frame_name(images[current_image_index])
    time_start = img_time
    width1 = t.ImageEditor.width_contain()

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

play_button = tk.Button(button_frame, text="Play Video", command=play_images)
play_button.pack(side=tk.LEFT, anchor="nw")

pause_button = tk.Button(button_frame, text="Pause Video", command=pause_images)
pause_button.pack(side=tk.LEFT, anchor="nw")

perform_button = tk.Button(button_frame2, text="Transform", command=transform_action)
perform_button.pack(side=tk.LEFT, anchor="w")
perform_button1 = tk.Button(button_frame2, text="Speed Estimation", command=speed_est)
perform_button1.pack(side=tk.LEFT, anchor="w")
perform_button2 = tk.Button(button_frame2, text="Sart time", command=start_checker)
perform_button2.pack(side=tk.LEFT, anchor="w")

# Tkinter 이벤트 루프 시작
root.mainloop()
