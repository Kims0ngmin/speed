import tkinter as tk
from tkinter import filedialog
from moviepy.editor import VideoFileClip
import cv2
import numpy as np
from PIL import Image, ImageTk

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

def load_video():
    global video_clip, paused, current_time, subclip_duration
    file_path = filedialog.askopenfilename(filetypes=[("MP4 files", "*.mp4"), ("All files", "*.*")])
    if file_path:
        video_clip = VideoFileClip(file_path)
        status_label.config(text=f"Loaded video: {file_path}")
        paused = True
        current_time = 0
        subclip_duration = video_clip.duration

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
            time = float(time_entry.get())
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

def center_window(root, width, height):
    # 화면의 가로 세로 크기 가져오기
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    
    # 화면 중앙의 위치 계산
    x = int((screen_width / 2) - (width / 2))
    y = int((screen_height / 2) - (height / 2))
    
    # 윈도우 크기와 위치 설정
    root.geometry(f'{width}x{height}+{x}+{y}')

# Tkinter 윈도우 생성
root = tk.Tk()
root.title("Simple Video Player")

# 윈도우 크기 설정 및 중앙 배치
window_width = 800
window_height = 600
center_window(root, window_width, window_height)

# UI 요소 추가
load_button = tk.Button(root, text="Load Video", command=load_video)
load_button.pack(pady=10)

time_label = tk.Label(root, text="Enter time to start (seconds):")
time_label.pack(pady=5)

time_entry = tk.Entry(root)
time_entry.pack(pady=5)

play_button = tk.Button(root, text="Play Video", command=play_video_at_time)
play_button.pack(pady=10)

pause_button = tk.Button(root, text="Pause Video", command=pause_video)
pause_button.pack(pady=10)

status_label = tk.Label(root, text="No video loaded")
status_label.pack(pady=20)

canvas = tk.Canvas(root, width=640, height=480)
canvas.pack()

# Tkinter 이벤트 루프 시작
root.mainloop()
