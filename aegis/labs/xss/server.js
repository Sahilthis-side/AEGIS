const express = require("express");

const app = express();

app.get("/", (req, res) => {
    res.json({
        name: "Aegis XSS Lab",
        status: "ok"
    });
});

app.get("/search", (req, res) => {

    const q = req.query.q || "";

    res.send(`
        <html>
            <body>
                <h1>Search</h1>
                <div>Results for: ${q}</div>
            </body>
        </html>
    `);
});

app.get("/health", (req, res) => {
    res.json({
        status: "ok"
    });
});

app.listen(3000, () => {
    console.log("XSS lab running on port 3000");
});