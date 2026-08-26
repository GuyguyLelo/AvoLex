/** Navigation latérale (mobile). */
export function initSidebar(root = document) {
  const toggle = root.querySelector("[data-sidebar-toggle]");
  const sidebar = root.querySelector("[data-sidebar]");
  const backdrop = root.querySelector("[data-sidebar-backdrop]");
  if (!(toggle instanceof HTMLElement) || !(sidebar instanceof HTMLElement)) {
    return;
  }

  const setOpen = (open) => {
    sidebar.classList.toggle("is-open", open);
    if (backdrop instanceof HTMLElement) {
      backdrop.classList.toggle("is-visible", open);
    }
    toggle.setAttribute("aria-expanded", open ? "true" : "false");
    toggle.setAttribute(
      "aria-label",
      open ? "Fermer le menu" : "Ouvrir le menu",
    );
  };

  toggle.addEventListener("click", () => {
    setOpen(!sidebar.classList.contains("is-open"));
  });

  if (backdrop instanceof HTMLElement) {
    backdrop.addEventListener("click", () => setOpen(false));
  }

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
      setOpen(false);
    }
  });
}
