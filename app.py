from flask import Flask, render_template, request, redirect, url_for, jsonify
import os
# utilsフォルダのripeness.pyから関数をインポート
from utils.ripeness import read_img, banana_ripeness

app = Flask(__name__)

# --- 設定 ---
UPLOAD_FOLDER = os.path.join('static', 'upload')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# フォルダが存在しなければ作成
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

# 画面遷移なしで画像をアップロードするためのAPI
@app.route('/api/analyze', methods=['POST'])
def analyze():
    # 1. 画像ファイルの存在チェック
    if 'banana_image' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['banana_image']
    
    if file.filename == '' or not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file'}), 400
    
    try:
        # 2. 画像を保存
        filename = file.filename
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(save_path)

        # 3. 遷移先のURLを作成 (/result/ファイル名)
        # ここではまだ計算せず、保存だけしてリダイレクト先を教えます
        target_url = url_for('result', filename=filename)

        # 4. JSONでURLを返す
        return jsonify({
            'status': 'success',
            'redirect_url': target_url
        })

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': 'Analysis failed'}), 500

# 結果表示ページ
@app.route('/result/<filename>')
def result(filename):
    if not filename:
        return redirect(url_for('index'))

    # 画像のパス
    image_path = url_for('static', filename=f'upload/{filename}')
    
    # 画像を読み込んで追熟度を計算
    try:
        full_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        image = read_img(full_path)
        ripeness = banana_ripeness(image)
    except Exception as e:
        print(f"Calculation Error: {e}")
        return redirect(url_for('index'))

    return render_template('result.html', ripeness=ripeness, uploaded_image=image_path)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)