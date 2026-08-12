const express = require("express");
const path = require("path");
const fs = require("fs");

const app = express();

const PORT = 3000;

const PUBLIC_DIR = path.join(__dirname, "public");
const PRIVATE_DIR = path.join(__dirname, "private");

// Create lab directories.
fs.mkdirSync(PUBLIC_DIR, { recursive: true });
fs.mkdirSync(PRIVATE_DIR, { recursive: true });

// Controlled file outside the public directory.
// Aegis will use this marker as deterministic evidence.
const secretFile = path.join(
    PRIVATE_DIR,
    "aegis-secret.txt"
);

if (!fs.existsSync(secretFile)) {
    fs.writeFileSync(
        secretFile,
        "AEGIS_PATH_TRAVERSAL_7f3c91"
    );
}

app.get("/", (req, res) => {
    res.json({
        name: "Aegis Path Traversal Lab",
        endpoint: "/download",
        parameter: "file"
    });
});

app.get("/health", (req, res) => {
    res.json({
        status: "ok"
    });
});

// INTENTIONALLY VULNERABLE.
// Do not use this pattern in production.
app.get("/download", (req, res) => {

    const file = req.query.file || "";

    const requestedPath = path.join(
        PUBLIC_DIR,
        file
    );

    if (!fs.existsSync(requestedPath)) {
        return res.status(404).json({
            error: "File not found"
        });
    }

    res.sendFile(
        path.resolve(requestedPath)
    );
});

app.listen(PORT, "0.0.0.0", () => {
    console.log(
        `Path Traversal lab running on port ${PORT}`
    );
});