document.addEventListener("DOMContentLoaded", function () {
    // Apply dark mode immediately before rendering
    const darkModeEnabled = localStorage.getItem("darkMode") === "enabled";
    if (darkModeEnabled) {
        document.body.classList.add("dark-mode");
    }

    // Dark Mode Toggle Button
    let darkModeToggle = document.getElementById("dark-mode-toggle");

    if (!darkModeToggle) {
        darkModeToggle = document.createElement("button");
        darkModeToggle.id = "dark-mode-toggle";
        darkModeToggle.style.position = "fixed";
        darkModeToggle.style.bottom = "20px";
        darkModeToggle.style.right = "20px";
        darkModeToggle.style.padding = "10px 15px";
        darkModeToggle.style.background = "#000";
        darkModeToggle.style.color = "#fff";
        darkModeToggle.style.border = "none";
        darkModeToggle.style.borderRadius = "5px";
        darkModeToggle.style.cursor = "pointer";
        darkModeToggle.style.zIndex = "1000";
        document.body.appendChild(darkModeToggle);
    }

    // Function to update button text correctly
    function updateButtonText() {
        darkModeToggle.innerText = document.body.classList.contains("dark-mode") ? "Dark Mode" : "Light Mode";
    }

    // Apply correct button text at start
    updateButtonText();

    // Toggle Dark Mode
    darkModeToggle.addEventListener("click", function () {
        document.body.classList.toggle("dark-mode");
        const isDarkMode = document.body.classList.contains("dark-mode");
        localStorage.setItem("darkMode", isDarkMode ? "enabled" : "disabled");
        updateButtonText();
    });

    // Fix white flash issue when navigating pages
    document.body.style.transition = "none";
    setTimeout(() => {
        document.body.style.transition = "background 0.3s, color 0.3s";
    }, 100);
});
