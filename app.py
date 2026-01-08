from flask import Flask, render_template, request, redirect, url_for, jsonify
import os
# utilsフォルダの中にあるripeness.pyから関数を読み込む
from utils.ripeness import read_img, banana_ripeness

app = Flask(__name__)

# --- 設定周り ---
# 画像の保存先
UPLOAD_FOLDER = os.path.join('static', 'upload')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# フォルダがなければ作成
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# 許可する拡張子
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# --- ここが抜けていました！関数定義 ---
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- ルーティング ---

@app.route('/')
def index():
    return render_template('index.html')

# (古い処理：念のため残しておきますが、今回は使いません)
@app.route('/loading', methods=['POST'])
def loading():
    if 'banana_image' not in request.files:
        return redirect(url_for('index'))
    
    file = request.files['banana_image']
    if file.filename == '' or not allowed_file(file.filename):
        return "Invalid file format", 400
    
    filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filename)
    return render_template('loading.html', filename=file.filename)

@app.route('/result/<filename>')
def result(filename):
    if not filename:
        return redirect(url_for('index'))

    image_path = url_for('static', filename=f'upload/{filename}')
    image = read_img(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    ripeness = banana_ripeness(image)

    return render_template('result.html', ripeness=ripeness, uploaded_image=image_path)

# --- ★新しい非同期通信用のルート ---
@app.route('/api/analyze', methods=['POST'])
def analyze():
    # 1. 画像チェック
    if 'banana_image' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['banana_image']
    
    if file.filename == '' or not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file'}), 400
    
    try:
        # 2. 保存
        filename = file.filename
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(save_path)
        
        # ★重要: ここで追熟度の計算は行わず、画像の保存だけして遷移させる手もありますが、
        # もし計算が重いならここでやってしまってもOKです。
        # 今回は「resultページを開いた時」に計算するロジックが既にあるので、
        # 単にファイル名だけ渡してリダイレクト先を教えます。

        # 3. 遷移先のURLを作成 (/result/ファイル名)
        target_url = url_for('result', filename=filename)

        # 4. JSONでURLを返す
        return jsonify({
            'status': 'success',
            'redirect_url': target_url
        })

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': 'Analysis failed'}), 500
    
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)