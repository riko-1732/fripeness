from flask import Flask, render_template, request, redirect, url_for
import os
from utils.ripeness import read_img, banana_ripeness  # ripeness.pyから関数をインポート

app = Flask(__name__)

# アップロードされた画像の保存先ディレクトリ
UPLOAD_FOLDER = os.path.join('static', 'upload')  # staticディレクトリ内のuploadフォルダ
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 保存先ディレクトリが存在しない場合は作成する
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# アップロードできるファイルの拡張子を設定
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# ファイル拡張子が許可されているか確認する関数
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')  # アップロードフォームの表示

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

    # アップロードされた画像のパスを作成
    server_file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    # 画像を読み込んで追熟度を計算
    image = read_img(server_file_path)
    ripeness = banana_ripeness(image)
    
    browser_image_url = url_for('static', filename=f'upload/{filename}')

    # result.html にアップロード画像と結果を渡す
    return render_template('result.html', ripeness=ripeness, uploaded_image=browser_image_url)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
