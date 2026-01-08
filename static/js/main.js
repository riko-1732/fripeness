document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("uploadForm");
  const loadingOverlay = document.getElementById("loadingOverlay");

  if (!form) return;

  form.addEventListener("submit", async (e) => {
    e.preventDefault(); // 通常の送信をキャンセル

    // 1. ローディング画面を表示
    if (loadingOverlay) loadingOverlay.style.display = "flex";

    const formData = new FormData(form);

    try {
      // 2. サーバーへ送信
      const response = await fetch("/api/analyze", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error("Server returned error");
      }

      const data = await response.json();

      // 3. サーバーから遷移先URLが返ってきたら移動する！
      if (data.redirect_url) {
        // 少しだけローディングを見せてから遷移（ユーザー体験のため）
        setTimeout(() => {
          window.location.href = data.redirect_url;
        }, 500);
      } else {
        throw new Error("Redirect URL not found");
      }
    } catch (error) {
      console.error("Error:", error);
      alert("エラーが発生しました。もう一度試してください。");
      if (loadingOverlay) loadingOverlay.style.display = "none";
    }
  });
});
