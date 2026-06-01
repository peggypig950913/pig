from flask import Flask, render_template, request, jsonify
import cv2
import mediapipe as mp
import numpy as np
import base64
import math
import time

app = Flask(__name__)

status = {
    "player_hp": 100,
    "boss_hp": 200,
    "calories": 0,
    "score": 0,
    "seconds": 0,
    "game_over": False,
    "result": "",
    "food_equiv": ""
}

mp_pose = mp.solutions.pose
pose = mp_pose.Pose()

squat_down = False
jumping_open = False
plank_active = False
plank_start = None
leg_raise_active = False
start_time = time.time()

def calculate_angle(a, b, c):
    ax, ay = a
    bx, by = b
    cx, cy = c
    angle = math.degrees(math.atan2(cy - by, cx - bx) - math.atan2(ay - by, ax - bx))
    return abs(angle)

def calories_to_food(calories):
    rice_bowls = calories // 200
    eggs = calories // 70
    chocolate = calories // 250
    return f"等效食物：約 {rice_bowls} 碗白飯、{eggs} 顆雞蛋、{chocolate} 條巧克力棒"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/analyze", methods=["POST"])
def analyze():
    global squat_down, jumping_open, plank_active, plank_start, leg_raise_active, start_time

    img_data = request.json["image"]
    img_bytes = base64.b64decode(img_data.split(",")[1])
    np_arr = np.frombuffer(img_bytes, np.uint8)
    frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(rgb_frame)

    if results.pose_landmarks:
        landmarks = results.pose_landmarks.landmark

        # 深蹲
        hip = (landmarks[mp_pose.PoseLandmark.LEFT_HIP].x, landmarks[mp_pose.PoseLandmark.LEFT_HIP].y)
        knee = (landmarks[mp_pose.PoseLandmark.LEFT_KNEE].x, landmarks[mp_pose.PoseLandmark.LEFT_KNEE].y)
        ankle = (landmarks[mp_pose.PoseLandmark.LEFT_ANKLE].x, landmarks[mp_pose.PoseLandmark.LEFT_ANKLE].y)
        angle = calculate_angle(hip, knee, ankle)
        if angle < 90:
            squat_down = True
        elif angle > 160 and squat_down:
            status["score"] += 10
            status["calories"] += 5
            status["boss_hp"] -= 10
            squat_down = False

        # 開合跳
        left_hand = landmarks[mp_pose.PoseLandmark.LEFT_WRIST].y
        right_hand = landmarks[mp_pose.PoseLandmark.RIGHT_WRIST].y
        head = landmarks[mp_pose.PoseLandmark.NOSE].y
        left_leg = landmarks[mp_pose.PoseLandmark.LEFT_ANKLE].x
        right_leg = landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE].x
        if left_hand < head and right_hand < head and abs(left_leg - right_leg) > 0.3:
            jumping_open = True
        elif jumping_open and left_hand > head and right_hand > head and abs(left_leg - right_leg) < 0.15:
            status["score"] += 15
            status["calories"] += 8
            status["boss_hp"] -= 15
            jumping_open = False

        # 平板撐
        shoulder = (landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER].x, landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER].y)
        hip = (landmarks[mp_pose.PoseLandmark.LEFT_HIP].x, landmarks[mp_pose.PoseLandmark.LEFT_HIP].y)
        ankle = (landmarks[mp_pose.PoseLandmark.LEFT_ANKLE].x, landmarks[mp_pose.PoseLandmark.LEFT_ANKLE].y)
        plank_angle = calculate_angle(shoulder, hip, ankle)
        if 160 < plank_angle < 200:
            if not plank_active:
                plank_active = True
                plank_start = time.time()
            else:
                elapsed = time.time() - plank_start
                if elapsed >= 1:
                    status["score"] += 5
                    status["calories"] += 2
                    status["boss_hp"] -= 5
                    plank_start = time.time()
        else:
            plank_active = False

        # 抬腿
        knee_y = landmarks[mp_pose.PoseLandmark.LEFT_KNEE].y
        hip_y = landmarks[mp_pose.PoseLandmark.LEFT_HIP].y
        if knee_y < hip_y:
            if not leg_raise_active:
                leg_raise_active = True
                status["score"] += 12
                status["calories"] += 6
                status["boss_hp"] -= 12
        else:
            leg_raise_active = False

    status["seconds"] = int(time.time() - start_time)

    if status["boss_hp"] <= 0:
        status["game_over"] = True
        status["result"] = "勝利 🎉"
        status["food_equiv"] = calories_to_food(status["calories"])
    elif status["player_hp"] <= 0:
        status["game_over"] = True
        status["result"] = "失敗 💀"
        status["food_equiv"] = calories_to_food(status["calories"])

    return jsonify(status)

@app.route("/restart")
def restart_game():
    global start_time
    start_time = time.time()
    status.update({
        "player_hp": 100,
        "boss_hp": 200,
        "calories": 0,
        "score": 0,
        "seconds": 0,
        "game_over": False,
        "result": "",
        "food_equiv": ""
    })
    return "遊戲已重新開始！"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
