document.addEventListener("DOMContentLoaded", () => {
    const questionInput = document.getElementById("question");
    const generateBtn = document.getElementById("generateBtn");
    const answerSection = document.getElementById("answerSection");
    const answerText = document.getElementById("answerText");

    generateBtn.addEventListener("click", async () => {
        const question = questionInput.value.trim();
        if (!question) {
            alert("Please enter a question.");
            return;
        }

        // Disable button while loading
        generateBtn.innerText = "Generating...";
        generateBtn.disabled = true;

        try {
            const response = await fetch(
                `https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key=YOUR_API_KEY_HERE`,
                {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        contents: [{ parts: [{ text: question }] }]
                    })
                }
            );

            const data = await response.json();
            if (data.candidates && data.candidates[0].content.parts[0].text) {
                answerText.innerText = data.candidates[0].content.parts[0].text;
            } else {
                answerText.innerText = "Something went wrong. Please try again.";
            }

            answerSection.classList.remove("hidden"); // Show answer section
        } catch (error) {
            console.error("Error generating answer:", error);
            answerText.innerText = "Failed to get an answer.";
        } finally {
            generateBtn.innerText = "Generate Answer";
            generateBtn.disabled = false;
        }
    });
});
