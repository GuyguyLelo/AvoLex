/**
 * Point d'entrée JS AvoLex (progressive enhancement).
 */
import { initNav } from "./modules/nav.js";
import { initDropdowns } from "./modules/dropdown.js";
import { initToasts } from "./modules/toast.js";
import { initModals } from "./modules/modal.js";
import { initSortableTables } from "./modules/table-sort.js";

function boot() {
  initNav();
  initDropdowns();
  initToasts();
  initModals();
  initSortableTables();
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", boot);
} else {
  boot();
}
