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

# H値の平均値を計算する
def calc_HSV_average(hsv):
    # 白色を除外するためのマスク作成 (閾値は調整が必要)
    # HSV値の範囲はH:0~179、S, V:0～255
    # inRange関数はHSV画像の該当する範囲のピクセルを255(白)、その他を黒(0)にする
    lower_white = np.array([0, 0, 220])   # 明るくて彩度が低い部分を白色とみなす
    upper_white = np.array([179, 40, 255])
    white_mask = cv2.inRange(hsv, lower_white, upper_white) # 白い領域を取り出す
    non_white_mask = cv2.bitwise_not(white_mask)    # 白くない領域を取り出す

    # H値の平均を計算
    h_values = hsv[:, :, 0][non_white_mask > 0]  # non_white_maskに対応するH値だけを取り出す
    if len(h_values) > 0:   # len(nnumber): リストの長さ
        mean_h = np.mean(h_values)
    else:
        mean_h = 0  # 対象範囲がない場合

    # 0～100に正規化
    min_h, max_h = 18, 70  # H値の最小値と最大値 
    if (min_h <= mean_h <= max_h): 
        normalized_value = ((mean_h - min_h) / (max_h - min_h)) * 100
    else: 0

    # 各マスクを保存
    #cv2.imwrite('color_mask.png', color_mask)
    #cv2.imwrite('non_white_mask.png', non_white_mask)
    #cv2.imwrite('combined_mask.png', combined_mask)

    # 表示
    #cv2.imshow('Combined Mask', combined_mask)
    #cv2.imshow('Color Mask', color_mask)
    #cv2.waitKey(0)
    #cv2.destroyAllWindows()

    #print(f"平均色相 (H): {mean_h}")
    #print(f"パーセンテージ（H）: {normalized_value}%")
    
    return non_white_mask, normalized_value


def sugar_spot(image, hsv, non_white_mask):
    # バナナ部分の色範囲を定義
    lower_range = np.array([18, 100, 100])
    upper_range = np.array([70, 255, 255])

    color_mask = cv2.inRange(hsv, lower_range, upper_range)
    combined_mask = cv2.bitwise_and(color_mask, non_white_mask)
    
    banana_area = np.sum(non_white_mask > 0)

    lower_brown = np.array([0, 0, 0])
    upper_brown = np.array([179, 225, 127])
    
    brown_mask = cv2.inRange(hsv, lower_brown, upper_brown)
    non_color_mask = cv2.bitwise_not(color_mask)
    combined_mask = cv2.bitwise_and(brown_mask, non_color_mask)

    result = image.copy()  # ここで image を利用
    result[combined_mask > 0] = [0, 255, 0]

    brown_area = np.sum(combined_mask > 0)
    
    if banana_area > 0:
        brown_ratio = (brown_area / banana_area) * 100
    else:
        brown_ratio = 0


    #print(f"茶色部分の面積: {brown_area} ピクセル")
    #print(f"茶色部分の割合: {brown_ratio}%")

    # 結果を保存
    #cv2.imwrite('output_image.jpg', result)

    # 結果を表示 (必要に応じて)
    #cv2.imshow('Original', image)
    #cv2.imshow('Mask', combined_mask)
    #cv2.imshow('Result', result)
    #cv2.waitKey(0)
    #cv2.destroyAllWindows()
    
    return brown_ratio


def banana_ripeness(image):
    hsv = BGRtoHSV(image)
    non_white_mask, normalized_value = calc_HSV_average(hsv)
    brown_ratio = sugar_spot(image, hsv, non_white_mask)  # image と non_white_mask を渡す

    if brown_ratio > 10:
        ripeness = format((brown_ratio * 0.6) + (normalized_value * 0.4), '.2f')
    else:
        ripeness = format(normalized_value, '.2f')

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