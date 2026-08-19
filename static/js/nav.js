// Mobile hamburger menu toggle. Progressive enhancement only, the site
// works without JS, this just adds the collapsible drawer on small screens.

document.addEventListener("DOMContentLoaded", () => {
    const toggle = document.getElementById("nav-toggle");
    const menu = document.getElementById("mobile-menu");

    if (!toggle || !menu) return;

    const close = () => {
        menu.classList.remove("open");
        toggle.classList.remove("active");
        toggle.setAttribute("aria-expanded", "false");
    };

    toggle.addEventListener("click", () => {
        const isOpen = menu.classList.toggle("open");
        toggle.classList.toggle("active", isOpen);
        toggle.setAttribute("aria-expanded", isOpen ? "true" : "false");
    });

    // Close the drawer once a link inside it is used.
    menu.querySelectorAll("a").forEach((link) => {
        link.addEventListener("click", close);
    });

    // Close if the viewport grows back past the collapse breakpoint.
    window.addEventListener("resize", () => {
        if (window.innerWidth > 900) close();
    });
});
