/**
 * Modales accessibles (ouvrir / fermer / Escape / focus).
 */
export function initModals() {
  const openers = document.querySelectorAll("[data-modal-open]");

  openers.forEach((opener) => {
    const id = opener.getAttribute("data-modal-open");
    const modal = id ? document.getElementById(id) : null;
    if (!modal) {
      return;
    }

    const closeButtons = modal.querySelectorAll("[data-modal-close]");
    let lastFocus = null;

    const close = () => {
      modal.hidden = true;
      document.body.style.overflow = "";
      lastFocus?.focus();
    };

    const open = () => {
      lastFocus = document.activeElement;
      modal.hidden = false;
      document.body.style.overflow = "hidden";
      const focusable = modal.querySelector(
        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])',
      );
      focusable?.focus();
    };

    opener.addEventListener("click", (event) => {
      event.preventDefault();
      open();
    });

    closeButtons.forEach((btn) => btn.addEventListener("click", close));

    modal.addEventListener("keydown", (event) => {
      if (event.key === "Escape") {
        close();
      }
    });
  });
}
