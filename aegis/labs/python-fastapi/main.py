from fastapi import FastAPI, Query

app = FastAPI(
    title="Aegis Python FastAPI Lab"
)


@app.get("/")
def root():
    return {
        "name": "Aegis Python FastAPI Lab",
        "endpoint": "/search",
    }


@app.get("/health")
def health():
    return {
        "status": "ok"
    }


@app.get("/search")
def search(
    q: str = Query(default="")
):
    # Intentionally reflects user input.
    # This will later give Aegis an XSS test target.
    return {
        "query": q
    }