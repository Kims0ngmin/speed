import cv2
import numpy as np
import os

d_name = "18"
win_name = "scanning"
img_time = "0.00"
frame = cv2.imread("./"+d_name+"/frame_" + img_time + ".jpg")
draw = frame.copy()

pts_cnt = 0
pts = np.zeros((4, 2), dtype=np.float32)

def onMouse(event, x, y, flags, param):
    global pts_cnt
    if event == cv2.EVENT_LBUTTONDOWN:
        # 좌표에 초록색 동그라미 표시
        cv2.circle(draw, (x, y), 10, (0, 255, 0), -1)
        cv2.imshow(win_name, draw)

        # 마우스 좌표 저장
        pts[pts_cnt] = [x, y]
        pts_cnt += 1
        if pts_cnt == 4:

            topLeft = pts[0]
            bottomRight = pts[2]
            topRight = pts[3]
            bottomLeft = pts[1]

            # Using pre-defined values for topLeft as given
            #topLeft = [385., 563.]

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
            dst = cv2.warpPerspective(frame, M, (int(w), int(h)))
            
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

cv2.imshow(win_name, frame)
cv2.setMouseCallback(win_name, onMouse)

cv2.waitKey(0)
cv2.destroyAllWindows()

