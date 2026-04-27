document.querySelectorAll("form[data-confirm]").forEach((form) => {
  form.addEventListener("submit", (event) => {
    const message = form.getAttribute("data-confirm");
    if (message && !window.confirm(message)) {
      event.preventDefault();
    }
  });
});

document.querySelectorAll("[data-dialog-open]").forEach((button) => {
  button.addEventListener("click", () => {
    const dialog = document.getElementById(button.getAttribute("data-dialog-open"));
    if (dialog) {
      dialog.showModal();
    }
  });
});

document.querySelectorAll("[data-dialog-close]").forEach((button) => {
  button.addEventListener("click", () => {
    button.closest("dialog")?.close();
  });
});

document.querySelectorAll("dialog").forEach((dialog) => {
  dialog.addEventListener("click", (event) => {
    if (event.target === dialog) {
      dialog.close();
    }
  });
});

document.querySelectorAll("form[data-auto-submit]").forEach((form) => {
  let timeoutId;
  const submitForm = (delay = 0) => {
    window.clearTimeout(timeoutId);
    timeoutId = window.setTimeout(() => {
      form.requestSubmit ? form.requestSubmit() : form.submit();
    }, delay);
  };

  form.querySelectorAll("select").forEach((select) => {
    select.addEventListener("change", () => submitForm());
  });

  form.querySelectorAll("input").forEach((input) => {
    input.addEventListener("input", () => submitForm(450));
  });
});

document.querySelectorAll("[data-filter]").forEach((input) => {
  const scopeName = input.getAttribute("data-filter");
  input.addEventListener("input", () => {
    const query = input.value.trim().toLowerCase();
    document.querySelectorAll(`[data-filter-scope="${scopeName}"] [data-filter-row]`).forEach((row) => {
      row.hidden = query.length > 0 && !row.textContent.toLowerCase().includes(query);
    });
  });
});

window.setTimeout(() => {
  document.querySelectorAll(".toast").forEach((toast) => {
    toast.style.opacity = "0";
    toast.style.transform = "translateY(-4px)";
    toast.style.transition = "opacity 180ms ease, transform 180ms ease";
  });
}, 4200);
