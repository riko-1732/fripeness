from flask import Flask, request, jsonify
import cv2
import numpy as np
import os

app = Flask(__name__)

# 画像の保存先
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# アップロードフォルダが存在しなければ作成
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# GrabCutでバナナ部分を抽出する関数
def extract_banana_with_grabcut(image):
    height, width = image.shape[:2]
    rect = (int(width * 0.1), int(height * 0.2), int(width * 0.8), int(height * 0.7))  # 適宜調整

    mask = np.zeros(image.shape[:2], np.uint8)
    bgd_model = np.zeros((1, 65), np.float64)
    fgd_model = np.zeros((1, 65), np.float64)

    cv2.grabCut(image, mask, rect, bgd_model, fgd_model, 5, cv2.GC_INIT_WITH_RECT)

    mask2 = np.where((mask == 2) | (mask == 0), 0, 1).astype('uint8')
    banana_image = image * mask2[:, :, np.newaxis]
    
    return banana_image, mask2

# シュガースポットを検出する関数
def detect_sugar_spots(image, banana_mask):
    masked_image = cv2.bitwise_and(image, image, mask=banana_mask)
    gray = cv2.cvtColor(masked_image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    return len(contours), thresh, contours

# バナナの色合いを評価する関数
def analyze_banana_color(image, banana_mask):
    masked_image = cv2.bitwise_and(image, image, mask=banana_mask)
    mean_color = cv2.mean(masked_image, mask=banana_mask)[:3]
    yellow_intensity = mean_color[2] - mean_color[1]  # 赤 - 青の差で黄色度を評価
    
    return yellow_intensity

# 追熟度を計算する関数
def calculate_ripeness(sugar_spots_count, color_intensity, max_spots=50, max_color_intensity=100):
    if sugar_spots_count <= 10:
        ripeness = min((color_intensity / max_color_intensity) * 100, 100)
    else:
        spots_ripeness = min((sugar_spots_count / max_spots) * 100, 100)
        color_ripeness = min((color_intensity / max_color_intensity) * 100, 100)
        ripeness = (spots_ripeness * 0.4) + (color_ripeness * 0.6)  # スポット60%、色40%の比重
    
    return ripeness

# 画像アップロードのエンドポイント
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'image' not in request.files:
        return jsonify({"error": "ファイルが見つかりません"}), 400

    file = request.files['image']

    if file.filename == '':
        return jsonify({"error": "ファイルが選択されていません"}), 400

    # 画像を一時的に保存
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)

    # 画像を読み込み
    image = cv2.imread(file_path)

    if image is None:
        return jsonify({"error": "画像の読み込みに失敗しました"}), 400

    # バナナの抽出と熟度判定の処理を行う
    banana_image, banana_mask = extract_banana_with_grabcut(image)
    sugar_spots_count, thresh_image, contours = detect_sugar_spots(image, banana_mask)
    color_intensity = analyze_banana_color(image, banana_mask)
    ripeness = calculate_ripeness(sugar_spots_count, color_intensity)

    # 結果を返す
    return jsonify({
        "sugar_spots": sugar_spots_count,
        "color_intensity": color_intensity,
        "ripeness": ripeness
    })

if __name__ == '__main__':
    app.run(debug=True)
