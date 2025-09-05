def test_save_and_get_intermediate(redis_backend):
    process_id = "redis_test_1"
    step = 0
    summary = "test summary"

    redis_backend.save_intermediate(process_id, step, summary)
    assert redis_backend.get_intermediate(process_id, step) == summary

def test_list_intermediates(redis_backend):
    process_id = "redis_test_2"
    redis_backend.save_intermediate(process_id, 0, "summary 0")
    redis_backend.save_intermediate(process_id, 1, "summary 1")

    items = redis_backend.list_intermediates(process_id)
    assert len(items) == 2
    assert "summary 0" in items
    assert "summary 1" in items
