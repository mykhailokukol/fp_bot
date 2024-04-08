from os import getenv

from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())


class Settings:
    TG_TOKEN: str = getenv("TG_TOKEN")
    CHANNEL_NAME: str = getenv("CHANNEL_NAME")
    MONGODB_CLIENT_URL: str = getenv("MONGODB_CLIENT_URL")


settings = Settings()
