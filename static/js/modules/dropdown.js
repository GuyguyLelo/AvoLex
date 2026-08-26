/** Menu déroulant compte (topbar). */
export function initDropdowns(root = document) {
  const dropdowns = root.querySelectorAll("[data-dropdown]");

  dropdowns.forEach((dropdown) => {
    const button = dropdown.querySelector("[data-dropdown-button]");
    const menu = dropdown.querySelector("[data-dropdown-menu]");
    if (!(button instanceof HTMLElement) || !(menu instanceof HTMLElement)) {
      return;
    }

    button.addEventListener("click", (event) => {
      event.stopPropagation();
      const willOpen = menu.hasAttribute("hidden");
      closeAllDropdowns(root);
      if (willOpen) {
        menu.removeAttribute("hidden");
        button.setAttribute("aria-expanded", "true");
      }
    });
  });

  document.addEventListener("click", () => closeAllDropdowns(root));
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
      closeAllDropdowns(root);
    }
  });
}

function closeAllDropdowns(root = document) {
  root.querySelectorAll("[data-dropdown]").forEach((dropdown) => {
    const button = dropdown.querySelector("[data-dropdown-button]");
    const menu = dropdown.querySelector("[data-dropdown-menu]");
    if (menu instanceof HTMLElement) {
      menu.setAttribute("hidden", "");
    }
    if (button instanceof HTMLElement) {
      button.setAttribute("aria-expanded", "false");
    }
  });
}
