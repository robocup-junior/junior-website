(() => {
  document.getElementById("toTop")?.addEventListener("click", () => {
    window.scrollTo({ top: 0, behavior: "smooth" });
  });

  // Mark the current page. When a parent and its first child share a URL
  // (e.g. Soccer > Soccer Leagues), mark only the child.
  const here = window.location.pathname.replace(/index\.html$/, "");
  ["#prime_nav", "#mobile-nav"].forEach(selector => {
    const links = [...document.querySelectorAll(`${selector} a`)].filter(link => link.pathname === here);
    const deepest = links.filter(link => !links.some(other => other !== link && link.closest("li").contains(other)));
    deepest.forEach(link => {
      link.closest("li")?.classList.add("current-menu-item", "current_page_item");
      link.setAttribute("aria-current", "page");
      let ancestor = link.closest("li")?.parentElement?.closest("li");
      while (ancestor) {
        ancestor.classList.add("current-menu-ancestor");
        ancestor = ancestor.parentElement?.closest("li");
      }
    });
  });

  // Desktop dropdowns: hover opens; the toggle button opens for keyboard
  // users; Escape or moving focus away closes.
  const desktopItems = [...document.querySelectorAll("#prime_nav .menu-item-has-children")];
  function setDesktopOpen(item, open) {
    const button = item.querySelector(":scope > .dropdown-toggle");
    button?.setAttribute("aria-expanded", String(open));
    item.classList.toggle("menu-hover", open);
    if (!open) item.querySelectorAll(".menu-item-has-children").forEach(child => setDesktopOpen(child, false));
  }
  desktopItems.forEach(item => {
    const button = item.querySelector(":scope > .dropdown-toggle");
    item.addEventListener("mouseenter", () => item.classList.add("menu-hover"));
    item.addEventListener("mouseleave", () => {
      if (button?.getAttribute("aria-expanded") !== "true") item.classList.remove("menu-hover");
    });
    item.addEventListener("focusout", event => {
      if (!item.contains(event.relatedTarget)) setDesktopOpen(item, false);
    });
    button?.addEventListener("click", () => {
      const open = button.getAttribute("aria-expanded") !== "true";
      // Close sibling menus at the same level.
      item.parentElement.querySelectorAll(":scope > .menu-item-has-children").forEach(sibling => {
        if (sibling !== item) setDesktopOpen(sibling, false);
      });
      setDesktopOpen(item, open);
    });
  });
  document.addEventListener("keydown", event => {
    if (event.key !== "Escape") return;
    const open = desktopItems.filter(item => item.classList.contains("menu-hover"));
    if (!open.length) return;
    const focusedItem = open.find(item => item.contains(document.activeElement));
    open.forEach(item => setDesktopOpen(item, false));
    focusedItem?.querySelector(":scope > .dropdown-toggle")?.focus();
  });

  // Mobile menu
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
  toggle.addEventListener("click", () => setOpen(true));
  close.addEventListener("click", () => setOpen(false));
  menu.querySelectorAll(".dropdown-toggle").forEach(button => {
    button.addEventListener("click", () => {
      const submenu = button.nextElementSibling;
      const open = button.getAttribute("aria-expanded") !== "true";
      button.setAttribute("aria-expanded", String(open));
      button.classList.toggle("toggle-on", open);
      if (submenu) submenu.classList.toggle("toggled-on", open);
    });
  });
  document.addEventListener("keydown", event => {
    if (!menu.classList.contains("is-open")) return;
    if (event.key === "Escape") setOpen(false);
    // Keep Tab focus inside the open menu.
    if (event.key === "Tab") {
      const focusable = [...menu.querySelectorAll("a, button")].filter(el => el.offsetParent !== null);
      const first = focusable[0], last = focusable[focusable.length - 1];
      if (event.shiftKey && document.activeElement === first) { last.focus(); event.preventDefault(); }
      else if (!event.shiftKey && document.activeElement === last) { first.focus(); event.preventDefault(); }
    }
  });
})();
