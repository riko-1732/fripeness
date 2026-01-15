import cv2
import numpy as np

def read_img(image_path):
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError("画像が読み込めませんでした。")
    return image

# HSV空間に変換
def BGRtoHSV(image):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    return hsv

# バナナの範囲を抽出
def extract_banana(hsv):
    lower_white = np.array([0, 0, 220])
    upper_white = np.array([255, 60, 255]) 
    white_mask = cv2.inRange(hsv, lower_white, upper_white)
    non_white_mask = cv2.bitwise_not(white_mask)
    return non_white_mask

# 【変更点1】H値からベーススコア（0～80点）を計算
def calc_Base_Score(hsv, non_white_mask):
    # H値の平均を計算
    h_values = hsv[:, :, 0][non_white_mask > 0]
    
    if len(h_values) > 0:
        mean_h = np.mean(h_values)
    else:
        mean_h = 0

    # --- 調整パラメータ ---
    # ①ALL GREEN のH値を 85 (緑) と定義 -> 0点
    # ⑥FULL YELLOW のH値を 20 (黄色) と定義 -> 80点 (満点ではない)
    min_h = 25  # 黄色の基準 (FULL YELLOW)
    max_h = 40  # 緑色の基準 (ALL GREEN)
    
    # 0〜80点の間でスコア付け
    if mean_h >= max_h:
        base_score = 0  # 緑すぎる場合
    elif mean_h <= min_h:
        base_score = 80 # 黄色（または茶色寄り）ならベース満点
    else:
        # 線形補間: 緑(max_h)から黄色(min_h)に近づくにつれて点数が上がる
        # 計算式: ( (85 - 現在のH) / (85 - 20) ) * 80
        ratio = (max_h - mean_h) / (max_h - min_h)
        base_score = ratio * 80

    return base_score

# 【変更点2】シュガースポットからボーナス点（0～20点+α）を計算
def calc_Spot_Bonus(hsv, non_white_mask):
    lower_brown = np.array([0, 0, 0])
    upper_brown = np.array([25, 225, 127])
    lower_brown2 = np.array([170, 0, 0])
    upper_brown2 = np.array([179, 225, 127])
    
    mask1 = cv2.inRange(hsv, lower_brown, upper_brown)
    mask2 = cv2.inRange(hsv, lower_brown2, upper_brown2)
    mask3 = cv2.bitwise_or(mask1, mask2)

    banana_brown_mask = cv2.bitwise_and(mask3, mask3, mask=non_white_mask)

    banana_area = np.sum(non_white_mask > 0)
    brown_area = np.sum(banana_brown_mask > 0)

    if banana_area > 0:
        brown_ratio = (brown_area / banana_area) * 100
    else:
        brown_ratio = 0

    # --- 調整パラメータ ---
    # ⑦STARの状態にするには、ある程度の斑点が必要。
    # 斑点が全体の10%あれば、+20点されて合計100%になるように調整
    # 係数を 2.0 に設定 (例: 斑点5% -> +10点, 斑点10% -> +20点)
    bonus_score = brown_ratio * 2.0

    return bonus_score

def banana_ripeness(image):
    hsv = BGRtoHSV(image)
    non_white_mask = extract_banana(hsv) 
    
    # ベースの熟度（色味だけで0~80%）
    base_score = calc_Base_Score(hsv, non_white_mask)
    
    # シュガースポットの加点（斑点で+20%を目指す）
    spot_bonus = calc_Spot_Bonus(hsv, non_white_mask)

    # 合計スコア
    total_score = base_score + spot_bonus
    
    # 上限を少し余裕を持たせるか、100で切るかは運用次第ですが、
    # STAR以上（真っ黒に近い）を判別するため上限なしにしておきます。
    ripeness = format(total_score, '.2f')
    
    return ripeness

# メイン処理
if __name__ == "__main__":
    image_path = 'upload/banana.jpg' # ここを判定したい画像のパスに変更
    try:
        image = read_img(image_path)
        ripeness = banana_ripeness(image)
        print(f"追熟度：{ripeness}%")
        
        # 結果の解釈を表示（デバッグ用）
        r = float(ripeness)
        if r == 0: print("判定：①ALL GREEN")
        elif r < 20: print("判定：②LIGHT GREEN")
        elif r < 40: print("判定：③HALF GREEN")
        elif r < 60: print("判定：④HALF YELLOW")
        elif r < 80: print("判定：⑤GREEN CHIP")
        elif r < 90: print("判定：⑥FULL YELLOW")
        elif r >= 90: print("判定：⑦STAR (食べごろ！)")
            
    except ValueError as e:
        print(e)