const express = require("express");

const app = express();
const PORT = 3000;

app.use(express.json());
app.use(express.urlencoded({ extended: true }));

app.get("/", (req, res) => {
    res.send(`
        <!DOCTYPE html>
        <html>
        <head>
            <title>Aegis Test Application</title>
        </head>

        <body>

            <h1>Aegis Security Test App</h1>

            <a href="/login">Login</a>
            <br>
            <a href="/search">Search</a>

            <form action="/login" method="POST">
                <input
                    type="text"
                    name="username"
                    placeholder="Username"
                >

                <input
                    type="password"
                    name="password"
                    placeholder="Password"
                >

                <button type="submit">
                    Login
                </button>
            </form>

            <script src="/app.js"></script>

        </body>
        </html>
    `);
});

app.get("/health", (req, res) => {
    res.json({
        status: "healthy"
    });
});

app.get("/login", (req, res) => {
    res.json({
        message: "Login endpoint"
    });
});

app.post("/login", (req, res) => {
    res.json({
        message: "Login request received",
        username: req.body.username
    });
});

app.get("/search", (req, res) => {
    res.json({
        query: req.query.q || ""
    });
});

app.get("/app.js", (req, res) => {
    res.type("application/javascript");

    res.send(`
        console.log("Aegis test application");
    `);
});

app.listen(PORT, "0.0.0.0", () => {
    console.log(
        "Test application listening on port " + PORT
    );
});