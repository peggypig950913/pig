import cv2
import mediapipe as mp
from game import Game

game = Game()
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
mp_drawing = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(rgb)

    if results.pose_landmarks:
        mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
        landmarks = results.pose_landmarks.landmark

        # 深蹲判斷：膝蓋低於臀部
        left_knee = landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value]
        left_hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP.value]
        if left_knee.y > left_hip.y:
            game.squat()
            cv2.putText(frame, "Squat! Boss HP -10", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)

        # 開合跳判斷：雙手高於頭
        left_wrist = landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value]
        right_wrist = landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value]
        nose = landmarks[mp_pose.PoseLandmark.NOSE.value]
        if left_wrist.y < nose.y and right_wrist.y < nose.y:
            game.jumping_jack()
            cv2.putText(frame, "Jumping Jack! Score +2", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,255), 2)

        # 抬腿判斷：膝蓋高於臀部
        if left_knee.y < left_hip.y:
            game.leg_raise()
            cv2.putText(frame, "Leg Raise! Dodge!", (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,0,0), 2)

        # 平板撐判斷：手腕與肩膀接近水平
        left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
        left_wrist = landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value]
        if abs(left_shoulder.y - left_wrist.y) < 0.05:
            game.plank()
            cv2.putText(frame, "Plank! Defense +2", (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,0), 2)

        # Boss 攻擊 (模擬)
        game.boss_attack()

    # 顯示遊戲資訊
    cv2.putText(frame, f"Player HP: {game.player_hp}", (20, 300), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2)
    cv2.putText(frame, f"Boss HP: {game.boss_hp}", (20, 350), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,0,0), 2)
    cv2.putText(frame, f"Calories: {game.calories}", (20, 400), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,255), 2)
    cv2.putText(frame, f"Score: {game.score}", (20, 450), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)

    cv2.imshow("FatBurn Game", frame)
    if cv2.waitKey(10) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
