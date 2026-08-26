import { initDropdowns } from "./modules/dropdown.js";
import { initSidebar } from "./modules/nav.js";

document.addEventListener("DOMContentLoaded", () => {
  initSidebar();
  initDropdowns();
});
