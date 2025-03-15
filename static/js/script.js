document.addEventListener("DOMContentLoaded", function () {
    console.log("✅ Script.js loaded successfully!");

    const fetchWeatherBtn = document.getElementById("fetch-weather-btn");

    let eventListenersAttached = false; // Track if listeners are attached
    let isSending = false; // Prevent duplicate requests

    // 🟢 Navbar Toggle
    const navbarToggler = document.querySelector(".navbar-toggler");
    const navbarCollapse = document.getElementById("navbarNav");

    if (navbarToggler && navbarCollapse) {
        console.log("✅ Navbar elements found!");

        // Close navbar when clicking a menu item (for mobile view)
        document.querySelectorAll(".nav-link").forEach(link => {
            link.addEventListener("click", function () {
                if (window.innerWidth < 992) {
                    const bsCollapse = new bootstrap.Collapse(navbarCollapse);
                    bsCollapse.hide();
                }
            });
        });
    } else {
        console.error("❌ ERROR: Navbar elements NOT found!");
    }

    // 🟢 Fetch all projects for Projects Page
    const projectsContainer = document.getElementById("projects-container");
    if (projectsContainer) {
        console.log("📂 Fetching projects...");
        fetch("/api/projects")
            .then(response => response.json())
            .then(projects => {
                projectsContainer.innerHTML = "";
                projects.forEach(project => {
                    projectsContainer.innerHTML += `
                        <div class="col-md-4 mb-4">
                            <a href="/projects/${project.id}" class="text-decoration-none text-dark">
                                <div class="card project-card shadow-sm">
                                    <div class="card-body">
                                        <h3 class="card-title">${project.title}</h3>
                                        <p><strong>Technologies:</strong> ${project.technologies}</p>
                                        <p>${project.short_description}</p>
                                        <button class="btn btn-outline-primary mt-2">Learn More</button>
                                    </div>
                                </div>
                            </a>
                        </div>
                    `;
                });
                console.log("✅ Projects loaded successfully!");
            })
            .catch(error => console.error("❌ Error fetching projects:", error));
    }

    // 🟢 Fetch Project Details for Project Details Page
    if (document.getElementById("project-title")) {
        console.log("📂 Fetching project details...");
        const projectId = window.location.pathname.split("/").pop(); // Extract project ID from URL

        fetch(`/api/projects/${projectId}`)
            .then(response => response.json())
            .then(project => {
                if (project.error) {
                    console.error("❌ Error: Project not found");
                    document.getElementById("project-title").innerText = "Project Not Found";
                    return;
                }

                // Populate project details dynamically
                document.getElementById("project-title").innerText = project.title;
                document.getElementById("project-technologies").innerHTML = `<strong>Technologies Used:</strong> ${project.technologies}`;
                document.getElementById("project-description").innerText = project.detailed_description;
                document.getElementById("project-use-case").innerText = project.commercial_use_case;

                // Show deployment guide for "flask-aws-deployment" project only
                if (project.id === "flask-aws-deployment") {
                    document.getElementById("deployment-guide").style.display = "block";
                }

                console.log("✅ Project details loaded successfully!");
            })
            .catch(error => console.error("❌ Error fetching project details:", error));
    }

    // 🟢 Fetch and display GitHub commits
    const commitsContainer = document.getElementById("github-commits");
    if (commitsContainer) {
        console.log("📂 Fetching latest GitHub commits...");

        fetch("/api/github-commits")
            .then(response => response.json())
            .then(commits => {
                if (commits.error) {
                    commitsContainer.innerHTML = `<li class="list-group-item text-danger">${commits.error}</li>`;
                    return;
                }

                commitsContainer.innerHTML = "";
                commits.forEach(commit => {
                    const commitItem = document.createElement("li");
                    commitItem.classList.add("list-group-item");
                    commitItem.innerHTML = `
                        <strong>${commit.message}</strong><br>
                        <small>By: ${commit.author} on ${new Date(commit.date).toLocaleString()}</small><br>
                        <a href="${commit.url}" target="_blank">View on GitHub</a>
                    `;
                    commitsContainer.appendChild(commitItem);
                });

                console.log("✅ GitHub commits loaded successfully!");
            })
            .catch(error => {
                console.error("❌ Error fetching GitHub commits:", error);
                commitsContainer.innerHTML = `<li class="list-group-item text-danger">Failed to load commits.</li>`;
            });
    }

    // 🟢 Fetch Random Number
    const randomButton = document.querySelector("#random-btn");
    const resultDisplay = document.querySelector("#random-result");

    if (randomButton) {
        console.log("🎲 Random number button found!");
        randomButton.addEventListener("click", function () {
            fetch("/api/random-number")
                .then(response => response.json())
                .then(data => {
                    resultDisplay.innerText = `Your random number is: ${data.random_number}`;
                })
                .catch(error => console.error("❌ Error fetching random number:", error));
        });
    } else {
        console.warn("⚠️ Random number button NOT found in the DOM!");
    }

    // 🟢 AWS Certifications
    const certContainer = document.getElementById("certifications-container");
    if (certContainer) {
        console.log("🎓 Loading AWS Certifications...");

        const certifications = [
            { id: "952f0071-5974-4753-9487-a7b47566859c" },
            { id: "8d927d2f-3ae9-42a8-a545-c1cb5f94975e" },
            { id: "e91dc156-f68b-4e50-a677-bae2e41c0c8f" },
            { id: "0598dd26-4893-4ff4-a8c1-3d0185ddddb7" },
            { id: "1f308bfe-d638-4840-9925-56440d9ea6c2" }
        ];

        certifications.forEach(cert => {
            const certDiv = document.createElement("div");
            certDiv.classList.add("col-md-3", "mb-4", "text-center");
            certDiv.innerHTML = `
                <div data-iframe-width="150" data-iframe-height="270"
                    data-share-badge-id="${cert.id}" data-share-badge-host="https://www.credly.com">
                </div>
            `;
            certContainer.appendChild(certDiv);
        });

        // Load Credly Embed Script
        const script = document.createElement("script");
        script.type = "text/javascript";
        script.src = "//cdn.credly.com/assets/utilities/embed.js";
        script.async = true;
        document.body.appendChild(script);

        console.log("✅ AWS Certifications loaded successfully!");
    }

    // 🟢 S3 File Manager Functions
    function fetchFiles() {
        fetch("/api/s3/list")
            .then(response => response.json())
            .then(data => console.log("✅ S3 Files Fetched:", data))
            .catch(error => console.error("❌ Error fetching S3 files:", error));
    }

    function uploadFile() {
        let file = document.getElementById("fileInput").files[0];
        let formData = new FormData();
        formData.append("file", file);

        fetch("/api/s3/upload", { method: "POST", body: formData })
            .then(response => response.json())
            .then(data => console.log("✅ File uploaded:", data))
            .catch(error => console.error("❌ Error uploading file:", error));
    }

    function deleteFile(fileName) {
        fetch("/api/s3/delete", {
            method: "POST",
            body: JSON.stringify({ file_name: fileName }),
            headers: { "Content-Type": "application/json" }
        })
            .then(response => response.json())
            .then(data => console.log("✅ File deleted:", data))
            .catch(error => console.error("❌ Error deleting file:", error));
    }

    if (window.location.pathname === "/s3-file-manager") {
        fetchFiles();
    }
    // 🟢 Serverless Chatbot Integration (Prevent Duplicates)
    function sendMessage() {
        if (isSending) return; // Prevent duplicate submissions
        isSending = true;

        let userInputField = document.getElementById("user-input");
        let userInput = userInputField.value.trim();

        if (!userInput) {
            isSending = false;
            return;
        }

        let chatBox = document.getElementById("chat-box");

        // ✅ Display user message
        chatBox.innerHTML += `<div><strong>You:</strong> ${userInput}</div>`;

        // ✅ Send request to Flask API
        fetch("/api/chatbot", {
            method: "POST",
            body: JSON.stringify({ message: userInput }),
            headers: { "Content-Type": "application/json" }
        })
        .then(response => response.json())
        .then(data => {
            console.log("📡 Chatbot API Response:", data);

            if (data && data.response) {
                chatBox.innerHTML += `<div><strong>Bot:</strong> ${data.response}</div>`;
            } else {
                chatBox.innerHTML += `<div><strong>Error:</strong> No response from chatbot.</div>`;
            }

            chatBox.scrollTop = chatBox.scrollHeight; // Auto-scroll to latest message
            userInputField.value = ""; // Clear input field
            isSending = false; // Allow new messages
        })
        .catch(error => {
            console.error("❌ Fetch Error:", error);
            chatBox.innerHTML += `<div><strong>Error:</strong> Failed to connect to chatbot.</div>`;
            isSending = false;
        });
    }

    function handleKeyPress(event) {
        if (event.key === "Enter") {
            sendMessage();
        }
    }

    // ✅ Ensure chatbot works only on the chatbot page
    if (window.location.pathname.includes("serverless-chatbot")) {
        console.log("🟢 Chatbot page detected. Ready to handle messages.");

        let sendButton = document.getElementById("send-btn");
        let userInput = document.getElementById("user-input");

        if (!sendButton || !userInput) {
            console.error("❌ ERROR: Chatbot elements NOT found!");
            return;
        }

        console.log("✅ Send button detected!");

        // ✅ Attach event listeners **only once**
        if (!eventListenersAttached) {
            sendButton.addEventListener("click", sendMessage);
            userInput.addEventListener("keypress", handleKeyPress);
            eventListenersAttached = true; // Mark as attached
        }
    }

    if (fetchWeatherBtn) {
        fetchWeatherBtn.addEventListener("click", fetchWeather);
    }

    // Allow pressing "Enter" in any field to trigger the search
    document.querySelectorAll(".weather-input").forEach(input => {
        input.addEventListener("keypress", function (event) {
            if (event.key === "Enter") {
                event.preventDefault(); // Prevent form submission
                fetchWeather();
            }
        });
    });

    function fetchWeather() {
        console.log("🔍 Fetching weather...");

        const city = document.getElementById("city-input").value.trim();
        const state = document.getElementById("state-input").value.trim().toUpperCase();
        const zip = document.getElementById("zip-input").value.trim();
        const country = document.getElementById("country-input").value.trim().toUpperCase() || "US";

        let url = "/weather?";

        if (zip) {
            url += `zip=${zip},${country}`;
        } else if (city && state) {
            url += `city=${city}&state=${state}&country=${country}`;
        } else if (city) {
            url += `city=${city}&country=${country}`;
        } else {
            alert("⚠️ Please enter a city and state or a zip code.");
            return;
        }

        console.log(`🌍 API Request URL: ${url}`);

        fetch(url)
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    alert(`❌ ${data.error}`);
                    return;
                }

                document.getElementById("weather-city").innerText = `📍 City: ${data.city}, ${data.country}`;
                document.getElementById("weather-temp").innerText = `🌡️ Temperature: ${data.temperature}°F`;
                document.getElementById("weather-low-high").innerText = `🔻 Low: ${data.temp_min}°F | 🔺 High: ${data.temp_max}°F`;
                document.getElementById("weather-humidity").innerText = `💧 Humidity: ${data.humidity}%`;
                document.getElementById("weather-description").innerText = `☁️ Description: ${data.weather}`;

                const iconUrl = `https://openweathermap.org/img/wn/${data.icon}.png`;
                const weatherIcon = document.getElementById("weather-icon");
                weatherIcon.src = iconUrl;
                weatherIcon.style.display = "inline"; // Show the weather icon
            })
            .catch(error => console.error("❌ Error fetching weather data:", error));
    }
    const contactForm = document.getElementById("contactForm");
    const successMessage = document.getElementById("successMessage");

    contactForm.addEventListener("submit", function (event) {
        event.preventDefault();

        // Basic validation
        const name = document.getElementById("name").value.trim();
        const email = document.getElementById("email").value.trim();
        const message = document.getElementById("message").value.trim();

        if (!name || !email || !message) {
            alert("Please fill in all fields.");
            return;
        }

        // Show success message
        successMessage.style.display = "block";

        // Hide success message after 3 seconds
        setTimeout(() => {
            successMessage.style.display = "none";
        }, 3000);

        // Reset the form
        contactForm.reset();
    });
  
});

