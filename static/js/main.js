document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("uploadForm");
  const loadingOverlay = document.getElementById("loadingOverlay");

  // フォームがないページでのエラーを防ぐ
  if (!form) return;

  form.addEventListener("submit", async (e) => {
    // 1. 通常のフォーム送信（画面リロード）をキャンセル
    e.preventDefault();

    // 2. ローディングアニメーションを表示
    if (loadingOverlay) {
      loadingOverlay.style.display = "flex";
    }

    const formData = new FormData(form);

    try {
      // 3. 非同期でサーバーに画像を送信
      const response = await fetch("/api/analyze", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error("Server returned error");
      }

      // 4. サーバーから返ってきたJSON（次のURLが入っている）を受け取る
      const data = await response.json();

      if (data.redirect_url) {
        // 5. 少し待ってから（アニメーションを見せるため）、指定されたURLへ移動
        setTimeout(() => {
          window.location.href = data.redirect_url;
        }, 1000); // 1秒待機
      } else {
        throw new Error("Redirect URL not found");
      }
    } catch (error) {
      console.error("Error:", error);
      alert("エラーが発生しました。もう一度試してください。");

      // エラー時はローディングを消して元の画面に戻す
      if (loadingOverlay) {
        loadingOverlay.style.display = "none";
      }
    }
  });
});
