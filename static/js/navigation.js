(() => {
  document.getElementById("toTop")?.addEventListener("click", () => {
    window.scrollTo({ top: 0, behavior: "smooth" });
  });
  document.querySelectorAll("#prime_nav a, #mobile-nav a").forEach(link => {
    if (link.pathname === window.location.pathname) {
      link.closest("li")?.classList.add("current-menu-item", "current_page_item");
      link.setAttribute("aria-current", "page");
    }
  });
  document.querySelectorAll("#prime_nav .menu-item-has-children").forEach(item => {
    const button = item.querySelector(":scope > .dropdown-toggle");
    item.addEventListener("mouseenter", () => item.classList.add("menu-hover"));
    item.addEventListener("mouseleave", () => {
      if (button?.getAttribute("aria-expanded") !== "true") {
        item.classList.remove("menu-hover");
      }
    });
    if (button) {
      button.setAttribute("aria-label", "Toggle submenu");
      button.addEventListener("click", () => {
        const open = button.getAttribute("aria-expanded") !== "true";
        button.setAttribute("aria-expanded", String(open));
        item.classList.toggle("menu-hover", open);
      });
    }
  });
  const menu = document.getElementById("mobile-menu");
  const toggle = document.getElementById("nav-toggle");
  const close = document.getElementById("nav-cancel");
  if (!menu || !toggle || !close) return;
  function setOpen(open) {
    menu.classList.toggle("is-open", open);
    document.body.classList.toggle("noscroll", open);
    toggle.setAttribute("aria-expanded", String(open));
    if (open) menu.querySelector("a")?.focus();
    else toggle.focus();
  }
  toggle.setAttribute("aria-expanded", "false");
  toggle.addEventListener("click", () => setOpen(true));
  close.setAttribute("aria-label", "Close menu");
  close.addEventListener("click", () => setOpen(false));
  menu.querySelectorAll(".dropdown-toggle").forEach(button => {
    button.setAttribute("aria-label", "Toggle submenu");
    button.addEventListener("click", () => {
      const submenu = button.nextElementSibling;
      const open = button.getAttribute("aria-expanded") !== "true";
      button.setAttribute("aria-expanded", String(open));
      button.classList.toggle("toggle-on", open);
      if (submenu) submenu.classList.toggle("toggled-on", open);
    });
  });
  document.addEventListener("keydown", event => {
    if (event.key === "Escape" && menu.classList.contains("is-open")) setOpen(false);
  });
})();
