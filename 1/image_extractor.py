import cv2
import os

def save_frames_as_images(video_path, output_folder):
    # 동영상 파일 열기
    cap = cv2.VideoCapture(video_path)
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

# 마우스 클릭 이벤트를 처리할 콜백 함수
mouse_points = []

def mouse_callback(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        if len(mouse_points) < 4:
            mouse_points.append((x, y))
            print(f"Point {len(mouse_points)}: ({x}, {y})")
        if len(mouse_points) == 4:
            cv2.destroyAllWindows()

def main():
    video_name = 'kick_25'
    folder_path = './25/'
    # 동영상 파일 경로와 이미지를 저장할 폴더를 지정합니다.
    video_path = folder_path + video_name + ".mp4"
    output_folder = video_name

    # 프레임을 이미지로 저장
    save_frames_as_images(video_path, output_folder)
    
    # 첫 번째 프레임에서 마우스 클릭을 통한 좌표 저장
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("동영상 파일을 열 수 없습니다.")
        return

    ret, frame = cap.read()
    if ret:
        cv2.imshow('Frame', frame)
        cv2.setMouseCallback('Frame', mouse_callback)
        cv2.waitKey(0)

    cap.release()

    # 좌표를 텍스트 파일로 저장
    if len(mouse_points) == 4:
        txt_file_path = os.path.join(output_folder, "mouse_points.txt")
        with open(txt_file_path, 'w') as f:
            for point in mouse_points:
                f.write(f"{point[0]}, {point[1]}\n")
        print(f"좌표가 {txt_file_path}에 저장되었습니다.")

if __name__ == "__main__":
    main()

