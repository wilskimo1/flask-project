document.addEventListener("DOMContentLoaded", function () {
    console.log("✅ Script.js loaded successfully!");

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

        // 🟢 AI Image Recognition Feature
        const imageRecognizeButton = document.getElementById("recognize-btn");
        const imageUploadButton = document.getElementById("upload-btn");
        const objectDetectButton = document.getElementById("object-detect-btn");
        const faceRecognizeButton = document.getElementById("face-recognize-btn");
        const ocrButton = document.getElementById("ocr-btn");
        const imageRecognitionResult = document.getElementById("image-recognition-result");
        const previewImage = document.getElementById("preview-image");
        const loadingIndicator = document.getElementById("loading");
    
        function fetchImageAnalysis(endpoint, method = "POST", bodyData = {}) {
            loadingIndicator.style.display = "block";
            imageRecognitionResult.innerHTML = "";
    
            fetch(endpoint, {
                method: method,
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(bodyData)
            })
            .then(response => response.json())
            .then(data => {
                loadingIndicator.style.display = "none";
                if (data.labels || data.text || data.faces) {
                    (data.labels || data.text || data.faces).forEach(item => {
                        let listItem = document.createElement("li");
                        listItem.classList.add("list-group-item");
                        listItem.innerText = item.label || item.text || `Face detected with confidence ${(item.confidence * 100).toFixed(2)}%`;
                        imageRecognitionResult.appendChild(listItem);
                    });
                } else {
                    imageRecognitionResult.innerText = "⚠️ No results found.";
                }
            })
            .catch(error => {
                loadingIndicator.style.display = "none";
                console.error("❌ Fetch error:", error);
                imageRecognitionResult.innerText = "⚠️ Error processing request.";
            });
        }
    
        if (imageRecognizeButton) {
            imageRecognizeButton.addEventListener("click", function () {
                const imageUrl = document.getElementById("image-url").value;
                if (!imageUrl) {
                    alert("⚠️ Please enter an image URL.");
                    return;
                }
                previewImage.src = imageUrl;
                previewImage.style.display = "block";
                fetchImageAnalysis("/api/image-recognition", "POST", { image_url: imageUrl });
            });
        }
    
        if (imageUploadButton) {
            imageUploadButton.addEventListener("click", function () {
                const fileInput = document.getElementById("image-file");
                const file = fileInput.files[0];
                if (!file) {
                    alert("⚠️ Please upload an image file.");
                    return;
                }
    
                const formData = new FormData();
                formData.append("image", file);
    
                loadingIndicator.style.display = "block";
                previewImage.src = URL.createObjectURL(file);
                previewImage.style.display = "block";
                imageRecognitionResult.innerHTML = "";
    
                fetch("/api/image-upload", {
                    method: "POST",
                    body: formData
                })
                .then(response => response.json())
                .then(data => {
                    loadingIndicator.style.display = "none";
                    if (data.labels) {
                        data.labels.forEach(label => {
                            let listItem = document.createElement("li");
                            listItem.classList.add("list-group-item");
                            listItem.innerText = `${label.label} (Confidence: ${(label.score * 100).toFixed(2)}%)`;
                            imageRecognitionResult.appendChild(listItem);
                        });
                    } else {
                        imageRecognitionResult.innerText = "⚠️ Error recognizing image.";
                    }
                })
                .catch(error => {
                    loadingIndicator.style.display = "none";
                    console.error("❌ Upload error:", error);
                    imageRecognitionResult.innerText = "⚠️ Failed to recognize image.";
                });
            });
        }
    
        if (objectDetectButton) {
            objectDetectButton.addEventListener("click", function () {
                fetchImageAnalysis("/api/object-detection", "POST", { image_url: previewImage.src });
            });
        }
    
        if (faceRecognizeButton) {
            faceRecognizeButton.addEventListener("click", function () {
                fetchImageAnalysis("/api/face-recognition", "POST", { image_url: previewImage.src });
            });
        }
    
        if (ocrButton) {
            ocrButton.addEventListener("click", function () {
                fetchImageAnalysis("/api/ocr", "POST", { image_url: previewImage.src });
            });
        }
    
        // 🟢 AI Stock Price Prediction Feature
        const stockPredictButton = document.getElementById("predict-btn");
        const stockPredictionResult = document.getElementById("stock-prediction-result");
    
        if (stockPredictButton) {
            console.log("📈 Stock prediction feature initialized!");
    
            stockPredictButton.addEventListener("click", function () {
                console.log("🟢 Predict button clicked!");
    
                const stockSymbol = document.getElementById("stock-symbol").value.trim().toUpperCase();
    
                if (!stockSymbol) {
                    alert("⚠️ Please enter a stock symbol.");
                    return;
                }
    
                fetch("/api/stock-predictor", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ stock_symbol: stockSymbol })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.latest_price) {
                        stockPredictionResult.innerHTML = `<strong>${data.stock_symbol}</strong>: $${data.latest_price.toFixed(2)}`;
                        console.log("✅ Stock price received:", data.latest_price);
                    } else {
                        stockPredictionResult.innerText = `⚠️ ${data.error}`;
                        console.error("❌ Error:", data);
                    }
                })
                .catch(error => {
                    stockPredictionResult.innerText = "⚠️ Failed to fetch stock price.";
                    console.error("❌ Fetch error:", error);
                });
            });
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
                            <a href="/projects/${project.id}" class="project-link">
                                <div class="card project-card">
                                    <div class="card-body">
                                        <h3>${project.title}</h3>
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
    // 🟢 AI Text Summarization Feature
    const summarizeButton = document.getElementById("summarize-btn");
    const summaryResult = document.getElementById("summary-result");

    if (summarizeButton) {
        console.log("📄 Summarization feature initialized!");
        
        summarizeButton.addEventListener("click", function () {
            console.log("🟢 Summarize button clicked!");

            const textInput = document.getElementById("text-input").value;

            if (!textInput) {
                alert("⚠️ Please enter some text to summarize.");
                return;
            }

            fetch("/api/summarize", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ text: textInput })
            })
            .then(response => response.json())
            .then(data => {
                if (data.summary) {
                    summaryResult.innerText = data.summary;
                    console.log("✅ Summary received:", data.summary);
                } else {
                    summaryResult.innerText = "⚠️ Error generating summary.";
                    console.error("❌ Error:", data);
                }
            })
            .catch(error => {
                summaryResult.innerText = "⚠️ Failed to summarize text.";
                console.error("❌ Fetch error:", error);
            });
        });
    } else {
        console.warn("⚠️ Summarize button NOT found in the DOM!");
    }
});
