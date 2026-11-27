// Light/dark theme toggle. The theme itself is applied before first paint by
// the inline script in layouts/_partials/head.html; this file wires up the
// buttons and keeps following the system setting until the visitor chooses.
(() => {
  const root = document.documentElement;
  const buttons = document.querySelectorAll(".rcj-theme-toggle");
  const media = window.matchMedia("(prefers-color-scheme: dark)");
  const stored = () => { try { return localStorage.getItem("rcj-theme"); } catch (e) { return null; } };

  function apply(theme) {
    root.dataset.theme = theme;
    const dark = theme === "dark";
    buttons.forEach(button => {
      button.setAttribute("aria-pressed", String(dark));
      button.setAttribute("aria-label", dark ? "Switch to light mode" : "Switch to dark mode");
      button.title = dark ? "Light mode" : "Dark mode";
    });
  }

  apply(root.dataset.theme === "dark" ? "dark" : "light");
  buttons.forEach(button => button.addEventListener("click", () => {
    const next = root.dataset.theme === "dark" ? "light" : "dark";
    try { localStorage.setItem("rcj-theme", next); } catch (e) { /* private mode: still switch */ }
    apply(next);
  }));
  // Follow the system setting while the visitor hasn't picked a theme.
  media.addEventListener("change", event => {
    if (stored() !== "light" && stored() !== "dark") apply(event.matches ? "dark" : "light");
  });
})();
