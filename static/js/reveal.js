// Scroll reveal: elements marked data-reveal fade/slide in once they enter
// the viewport. Progressive enhancement, if IntersectionObserver isn't
// available the content is just shown immediately.

document.addEventListener("DOMContentLoaded", () => {
    const targets = document.querySelectorAll("[data-reveal]");
    if (targets.length === 0) return;

    if (!("IntersectionObserver" in window)) {
        targets.forEach((el) => el.classList.add("in-view"));
        return;
    }

    const observer = new IntersectionObserver(
        (entries) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    entry.target.classList.add("in-view");
                    observer.unobserve(entry.target);
                }
            });
        },
        { threshold: 0.15, rootMargin: "0px 0px -40px 0px" }
    );

    targets.forEach((el) => observer.observe(el));
});
