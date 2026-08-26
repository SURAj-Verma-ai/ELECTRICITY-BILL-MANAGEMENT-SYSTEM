// scrolls the important links strip left/right
document.addEventListener("DOMContentLoaded", () => {
    const strip = document.getElementById("links-strip");
    const prev = document.getElementById("strip-prev");
    const next = document.getElementById("strip-next");
    if (!strip || !prev || !next) return;

    prev.addEventListener("click", () => strip.scrollBy({ left: -220, behavior: "smooth" }));
    next.addEventListener("click", () => strip.scrollBy({ left: 220, behavior: "smooth" }));
});
