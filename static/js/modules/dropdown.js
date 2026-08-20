/**
 * Menus déroulants accessibles (clavier + clic extérieur).
 */
export function initDropdowns() {
  const dropdowns = document.querySelectorAll("[data-dropdown]");

  dropdowns.forEach((root) => {
    const button = root.querySelector("[data-dropdown-button]");
    const menu = root.querySelector("[data-dropdown-menu]");
    if (!button || !menu) {
      return;
    }

    const close = () => {
      menu.hidden = true;
      button.setAttribute("aria-expanded", "false");
    };

    const open = () => {
      menu.hidden = false;
      button.setAttribute("aria-expanded", "true");
    };

    button.addEventListener("click", (event) => {
      event.stopPropagation();
      if (menu.hidden) {
        open();
      } else {
        close();
      }
    });

    document.addEventListener("click", (event) => {
      if (!root.contains(event.target)) {
        close();
      }
    });

    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape") {
        close();
      }
    });
  });
}
