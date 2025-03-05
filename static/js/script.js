document.addEventListener("DOMContentLoaded", function () {
    // Smooth scrolling
    document.querySelectorAll("a.nav-link").forEach(anchor => {
        anchor.addEventListener("click", function (event) {
            if (this.hash !== "") {
                event.preventDefault();
                document.querySelector(this.hash).scrollIntoView({ behavior: "smooth" });
            }
        });
    });
});
