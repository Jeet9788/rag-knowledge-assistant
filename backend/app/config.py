from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql://rag:ragpassword@localhost:5432/ragdb"

    # LLM provider: ollama | gemini | openai
    llm_provider: str = "ollama"

    ollama_base_url: str = "http://host.docker.internal:11434"
    ollama_model: str = "llama3.1"

    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.0-flash"

    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"

    # Embeddings (local, CPU via fastembed)
    embedding_model: str = "BAAI/bge-small-en-v1.5"
    embedding_dim: int = 384

    # Retrieval
    retrieve_top_k: int = 20
    final_top_k: int = 5
    use_reranker: bool = True
    reranker_model: str = "Xenova/ms-marco-MiniLM-L-6-v2"

    # Chunking
    chunk_size: int = 800
    chunk_overlap: int = 120

    # App
    backend_cors_origins: str = "http://localhost:3000"
    max_upload_mb: int = 25

    @property
    def cors_origins(self) -> list[str]:
        return [o.strip() for o in self.backend_cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
