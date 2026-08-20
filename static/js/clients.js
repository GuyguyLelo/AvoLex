/** Bascule champs personne / société sur le formulaire client. */

function setContainerFields(container, disabled) {
  container.querySelectorAll("input, select, textarea").forEach((el) => {
    el.disabled = disabled;
  });
}

function syncClientTypeFields(form) {
  const select = form.querySelector("#id_client_type");
  if (!select) return;
  const isCompany = select.value === "company";
  form.querySelectorAll("[data-person-only]").forEach((el) => {
    el.hidden = isCompany;
    setContainerFields(el, isCompany);
  });
  form.querySelectorAll("[data-company-only]").forEach((el) => {
    el.hidden = !isCompany;
    setContainerFields(el, !isCompany);
  });
}

document.querySelectorAll("[data-client-form]").forEach((form) => {
  const select = form.querySelector("#id_client_type");
  if (!select) return;
  syncClientTypeFields(form);
  select.addEventListener("change", () => syncClientTypeFields(form));
});
