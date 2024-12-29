document.getElementById("loginForm").addEventListener("submit", async function (event) {
    event.preventDefault();

    const formData = new FormData(event.target);

    try {
        const response = await fetch("/api/login", {
            method: "POST",
            body: formData, 
            credentials: "include", 
        });

        if (!response.ok) {
            throw new Error("Login failed");
        }

        alert("Login successful!");
        // Перенаправлення або інші дії
    } catch (error) {
        console.error("Error:", error);
        alert("Invalid credentials");
    }
});
