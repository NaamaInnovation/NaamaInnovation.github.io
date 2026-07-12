const menuToggle = document.querySelector(".menu-toggle");
const sidebar = document.querySelector(".sidebar");

if (menuToggle && sidebar) {
  menuToggle.addEventListener("click", () => {
    const isOpen = document.body.classList.toggle("menu-open");
    menuToggle.setAttribute("aria-expanded", String(isOpen));
    menuToggle.setAttribute("aria-label", isOpen ? "Close menu" : "Open menu");
  });

  sidebar.addEventListener("click", (event) => {
    if (event.target.closest("a")) {
      document.body.classList.remove("menu-open");
      menuToggle.setAttribute("aria-expanded", "false");
      menuToggle.setAttribute("aria-label", "Open menu");
    }
  });
}
