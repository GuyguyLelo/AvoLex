/**
 * Toggle sidebar mobile + backdrop.
 */
export function initNav() {
  const sidebar = document.querySelector("[data-sidebar]");
  const toggle = document.querySelector("[data-sidebar-toggle]");
  const backdrop = document.querySelector("[data-sidebar-backdrop]");
  if (!sidebar || !toggle) {
    return;
  }

  const mq = window.matchMedia("(min-width: 1024px)");

  const setOpen = (open) => {
    sidebar.classList.toggle("is-open", open);
    toggle.setAttribute("aria-expanded", open ? "true" : "false");
    if (!mq.matches) {
      sidebar.setAttribute("aria-hidden", open ? "false" : "true");
    }
    if (backdrop) {
      backdrop.classList.toggle("is-visible", open);
    }
    document.body.style.overflow = open && !mq.matches ? "hidden" : "";
  };

  toggle.addEventListener("click", () => {
    setOpen(!sidebar.classList.contains("is-open"));
  });

  backdrop?.addEventListener("click", () => setOpen(false));

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
      setOpen(false);
    }
  });

  const syncDesktop = () => {
    sidebar.classList.remove("is-open");
    toggle.setAttribute("aria-expanded", "false");
    backdrop?.classList.remove("is-visible");
    document.body.style.overflow = "";
    if (mq.matches) {
      sidebar.removeAttribute("aria-hidden");
    } else {
      sidebar.setAttribute("aria-hidden", "true");
    }
  };

  mq.addEventListener("change", syncDesktop);
  syncDesktop();
}
