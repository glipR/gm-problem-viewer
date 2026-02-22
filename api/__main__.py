import uvicorn
from api.config import get_settings


def main():
    settings = get_settings()
    uvicorn.run("api.main:app", host="0.0.0.0", port=settings.port, reload=True)


if __name__ == "__main__":
    main()
