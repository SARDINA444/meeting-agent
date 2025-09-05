import uuid

def test_save_and_get_final(qdrant_backend):
    # генерируем UUID так же, как в main.py
    process_id = str(uuid.uuid4())
    summary = "final summary"
    vector = [0.1] * 1024  # подгоняем под размер коллекции

    qdrant_backend.save_final(process_id, summary, vector)
    result = qdrant_backend.get_final(process_id)
    assert result == summary
