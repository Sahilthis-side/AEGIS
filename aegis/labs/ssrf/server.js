const express = require("express");

const app = express();
const PORT = 3000;

// Controlled internal service.
// This represents an internal resource that should not be
// reachable through the public application's fetch endpoint.
const internalApp = express();

internalApp.get("/internal-secret", (req, res) => {
    res.status(200).send("AEGIS_SSRF_7f3c91");
});

internalApp.listen(4000, "0.0.0.0", () => {
    console.log("Internal service listening on port 4000");
});

// Vulnerable public application.
app.get("/", (req, res) => {
    res.json({
        name: "Aegis SSRF Lab",
        endpoint: "/fetch",
    });
});

app.get("/health", (req, res) => {
    res.json({ status: "ok" });
});

app.get("/fetch", async (req, res) => {
    const url = req.query.url;

    if (!url) {
        return res.status(400).json({
            error: "Missing url parameter",
        });
    }

    try {
        const response = await fetch(url);
        const body = await response.text();

        res.status(response.status).send(body);
    } catch (error) {
        res.status(500).json({
            error: "Request failed",
        });
    }
});

app.listen(PORT, "0.0.0.0", () => {
    console.log(`Public application listening on port ${PORT}`);
});