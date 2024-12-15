from flask import Flask, render_template, request, redirect, url_for
from waitress import serve  # waitressをインポート
import os
from utils.ripeness import read_img, banana_ripeness  # ripeness.pyから関数をインポート

app = Flask(__name__)

# アップロードされた画像の保存先ディレクトリ
UPLOAD_FOLDER = 'upload'  # フォルダ名を統一
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

@app.route('/upload', methods=['POST'])
def upload():
    if request.method == 'POST':
        if 'banana_image' not in request.files:
            return redirect(request.url)  # ファイルが送信されていない場合、元のページにリダイレクト
    
        file = request.files['banana_image']
    
        # ファイル名が適切でない場合
        if file.filename == '':
            return redirect(request.url)
    
        # ファイルが許可された形式か確認
        if file and allowed_file(file.filename):
            # ファイル名をセキュアにして保存
            filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filename)

            # 画像を読み込んで追熟度を計算
            image = read_img(filename)  # read_imgで画像を読み込む
            ripeness = banana_ripeness(image)  # 追熟度を計算

            return render_template('result.html', ripeness=ripeness)  # 結果ページにリダイレクト
    
        return '許可されていないファイル形式です。', 400  # 不正なファイル形式の場合

if __name__ == '__main__':
    serve(app, host='0.0.0.0', port=5000)