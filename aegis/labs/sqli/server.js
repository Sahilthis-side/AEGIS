const express = require("express");
const initSqlJs = require("sql.js");

const app = express();
const PORT = 3000;

app.use(express.json());

let db;

async function startDatabase() {
    const SQL = await initSqlJs();

    db = new SQL.Database();

    db.run(`
        CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            username TEXT,
            role TEXT
        );
    `);

    db.run(`
        INSERT INTO users
        (username, role)
        VALUES
        ('alice', 'user'),
        ('bob', 'user'),
        ('admin', 'administrator');
    `);
}

app.get("/", (req, res) => {
    res.json({
        application: "Aegis SQL Injection Lab",
        endpoints: [
            "GET /health",
            "GET /search?q=<query>"
        ]
    });
});

app.get("/health", (req, res) => {
    res.json({
        status: "healthy"
    });
});


/*
 * INTENTIONALLY VULNERABLE.
 *
 * User input is directly inserted into
 * the SQL query.
 */
app.get("/search", (req, res) => {

    const query = req.query.q || "";

    const sql = `
        SELECT id, username, role
        FROM users
        WHERE username LIKE '%${query}%'
    `;

    try {

        const result = db.exec(sql);

        const rows = [];

        if (result.length > 0) {

            const columns = result[0].columns;
            const values = result[0].values;

            for (const value of values) {

                const row = {};

                columns.forEach(
                    (column, index) => {
                        row[column] = value[index];
                    }
                );

                rows.push(row);
            }
        }

        res.json({
            query,
            count: rows.length,
            results: rows
        });

    } catch (error) {

        res.status(500).json({
            error: "Database query failed"
        });
    }
});


startDatabase()
    .then(() => {

        app.listen(
            PORT,
            "0.0.0.0",
            () => {
                console.log(
                    `SQLi lab listening on ${PORT}`
                );
            }
        );

    })
    .catch((error) => {

        console.error(
            "Failed to initialize database:",
            error
        );

        process.exit(1);
    });