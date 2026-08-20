/**
 * Tri client des tableaux marqués data-sortable (progressive enhancement).
 */
export function initSortableTables() {
  document.querySelectorAll("table[data-sortable]").forEach((table) => {
    const headers = table.querySelectorAll("th[data-sort-key]");
    headers.forEach((th) => {
      th.setAttribute("aria-sort", "none");
      const button = document.createElement("button");
      button.type = "button";
      button.className = "table-sort";
      button.innerHTML = `${th.textContent}<span class="sort-icon" aria-hidden="true"></span>`;
      th.textContent = "";
      th.appendChild(button);

      button.addEventListener("click", () => {
        const key = th.getAttribute("data-sort-key");
        const tbody = table.tBodies[0];
        if (!tbody || !key) {
          return;
        }

        const current = th.getAttribute("aria-sort");
        const next = current === "ascending" ? "descending" : "ascending";
        headers.forEach((h) => h.setAttribute("aria-sort", "none"));
        th.setAttribute("aria-sort", next);

        const rows = Array.from(tbody.rows);
        const index = Array.from(th.parentNode.children).indexOf(th);
        rows.sort((a, b) => {
          const av = a.cells[index]?.textContent?.trim() || "";
          const bv = b.cells[index]?.textContent?.trim() || "";
          const cmp = av.localeCompare(bv, "fr", { numeric: true, sensitivity: "base" });
          return next === "ascending" ? cmp : -cmp;
        });
        rows.forEach((row) => tbody.appendChild(row));
      });
    });
  });
}
