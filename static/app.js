const navLinks = Array.from(document.querySelectorAll(".side-nav a"));

function setActiveNav() {
  const current = window.location.hash || "#dashboard";
  navLinks.forEach((link) => {
    link.classList.toggle("active", link.getAttribute("href") === current);
  });
}

window.addEventListener("hashchange", setActiveNav);
setActiveNav();

document.querySelectorAll("form[data-confirm]").forEach((form) => {
  form.addEventListener("submit", (event) => {
    const message = form.getAttribute("data-confirm");
    if (message && !window.confirm(message)) {
      event.preventDefault();
    }
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
