const fileInput = document.getElementById("fileInput");
const preview = document.getElementById("preview");

fileInput.addEventListener("change", (event) => {
  // プレビューエリアをクリア
  preview.innerHTML = "";

  // 選択されたファイルを取得
  const file = event.target.files[0];
  if (file) {
    // ファイルのURLを作成
    const reader = new FileReader();
    reader.onload = (e) => {
      // 画像要素を作成してプレビューエリアに表示
      const img = document.createElement("img");
      img.src = e.target.result;
      img.alt = "Selected Image";
      img.style.maxWidth = "300px";
      img.style.height = "auto";
      img.style.border = "1px solid #ddd";
      img.style.borderRadius = "10px";
      img.style.padding = "10px";
      preview.appendChild(img);
    };
    reader.readAsDataURL(file);
  }
});
