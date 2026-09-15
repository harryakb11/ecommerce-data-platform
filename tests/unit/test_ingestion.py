from src.ingestion.main import run


def test_ingestion_import():
    assert callable(run)
