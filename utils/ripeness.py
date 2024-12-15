# OpenCVライブラリをインポート
import cv2
import numpy as np

def read_img(image_path):
    # 指定されたパスから画像を読み込む
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError("画像が読み込めませんでした。")
    return image


# 画像を表示
def display_img(window_name,image):
    # 画像表示用のウィンドウを作成して表示 
    # ウインドウ名:window_name / 表示データ:image
    cv2.imshow(window_name, image)
    # キーが押されるまでウィンドウを保持
    cv2.waitKey(0)
    # ウィンドウを閉じてリソースを解放
    cv2.destroyAllWindows()

# HSV空間に変換
def BGRtoHSV(image):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    return hsv

#バナナの範囲を抽出、ピクセル数を計算
def extract_banana(hsv):
    # 白色を除外するためのマスク作成 (閾値は調整が必要)
    # HSV値の範囲はH:0~179、S, V:0～255
    # inRange関数はHSV画像の該当する範囲のピクセルを255(白)、その他を黒(0)にする
    lower_white = np.array([0, 0, 220])   # 明るくて彩度が低い部分を白色とみなす
    upper_white = np.array([255, 40, 255])
    white_mask = cv2.inRange(hsv, lower_white, upper_white) # 白い領域を取り出す
    non_white_mask = cv2.bitwise_not(white_mask)    # 白くない領域を取り出す

    return non_white_mask

# H値の平均値を計算する
def calc_HSV_average(hsv, non_white_mask):
    # H値の平均を計算
    h_values = hsv[:, :, 0][non_white_mask > 0]  # non_white_maskに対応するH値だけを取り出す
    if len(h_values) > 0:   # len(nnumber): リストの長さ
        mean_h = np.mean(h_values)
    else:
        mean_h = 0  # 対象範囲がない場合

    # 0～100に正規化
    min_h, max_h = 18, 35  # H値の最小値と最大値 
    if (min_h <= mean_h <= max_h): 
        h_percentage = 100 - ((mean_h - min_h) / (max_h - min_h)) * 100
    else: h_percentage = 0


    return h_percentage


def sugar_spot(hsv, non_white_mask):
    # 茶色の範囲を定義 (必要に応じて調整)
    lower_brown = np.array([0, 0, 0])  # 茶色の下限 (Hue, Saturation, Value)
    upper_brown = np.array([25, 225, 127])  # 茶色の上限
    lower_brown2 = np.array([170, 0, 0])    # 紫側の茶色の下限
    upper_brown2 = np.array([179, 225, 127])    # 紫側の茶色の上限


    # 茶色の部分をマスク
    mask1 = cv2.inRange(hsv, lower_brown, upper_brown)
    mask2 = cv2.inRange(hsv, lower_brown2, upper_brown2)
    mask3 = cv2.bitwise_or(mask1, mask2) # 2つの茶色領域をORする

    # バナナ部分の面積計算
    banana_area = np.sum(non_white_mask > 0)

    # 面積を計算 (白いピクセル数を計算)
    brown_area = np.sum(mask3 > 0)

    # バナナ部分に対する茶色部分の割合計算
    if banana_area > 0:
        brown_ratio = (brown_area / banana_area) * 100
    else:
        brown_ratio = 0

    return brown_ratio

def banana_ripeness(image):
    hsv = BGRtoHSV(image)
    non_white_mask = extract_banana(hsv) 
    h_percentage = calc_HSV_average(hsv, non_white_mask)
    brown_ratio = sugar_spot(hsv, non_white_mask)

    ripeness = format((h_percentage + (brown_ratio * 0.4)), '.2f')
    
    return ripeness


# メイン処理
if __name__ == "__main__":
    image_path = 'upload/banana.jpg'  # 画像パスを設定
    try:
        image = read_img(image_path)  # 画像を読み込む
        ripeness = banana_ripeness(image)  # 画像を引数として渡す
        print(f"追熟度：{ripeness}%")
    except ValueError as e:
        print(e)