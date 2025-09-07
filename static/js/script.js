const btn = document.getElementById("theme-toggle");
btn.onclick = () => {
  const t = document.documentElement.getAttribute("data-theme");
  document.documentElement.setAttribute("data-theme", t === "dark" ? "light" : "dark");
};
