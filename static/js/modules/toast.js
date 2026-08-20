/**
 * Convertit les messages Django flash en toasts éphémères.
 */
export function initToasts() {
  const region = document.querySelector("[data-toast-region]");
  const source = document.querySelector("[data-flash-messages]");
  if (!region || !source) {
    return;
  }

  const items = source.querySelectorAll("[data-flash]");
  items.forEach((item, index) => {
    const toast = document.createElement("div");
    toast.className = "toast";
    toast.setAttribute("role", "status");
    toast.textContent = item.textContent?.trim() || "";
    region.appendChild(toast);

    window.setTimeout(() => {
      toast.remove();
    }, 4200 + index * 400);
  });
}
