document.addEventListener("DOMContentLoaded", () => {
  const selector = document.getElementById("languageSelector");

  // 要素がない場合は処理を中断（エラー防止）
  if (!selector) return;

  // 1. 以前の設定 > ブラウザの言語 > 英語 の順で初期言語を決定
  const savedLang = localStorage.getItem("appLang");
  const browserLang = navigator.language.startsWith("ja") ? "ja" : "en";
  const currentLang = savedLang || browserLang;

  // セレクトボックスの表示を合わせる
  selector.value = currentLang;

  // 初回の言語適用
  loadLanguage(currentLang);

  // 2. ユーザーが言語を切り替えた時の処理
  selector.addEventListener("change", (e) => {
    const selectedLang = e.target.value;
    loadLanguage(selectedLang);
    // 設定をブラウザに保存 (次回来た時も同じ言語になる)
    localStorage.setItem("appLang", selectedLang);
  });
});

async function loadLanguage(lang) {
  try {
    // Flaskの構成に合わせて絶対パスで指定
    const response = await fetch(`/static/locales/${lang}.json`);

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const translations = await response.json();

    // data-i18n 属性がついている全ての要素を書き換える
    const elements = document.querySelectorAll("[data-i18n]");

    elements.forEach((element) => {
      const key = element.getAttribute("data-i18n");
      if (translations[key]) {
        element.innerHTML = translations[key];
      }
    });

    // HTMLタグのlang属性も更新
    document.documentElement.lang = lang;
  } catch (error) {
    console.error("Language file loading failed:", error);
  }
}
