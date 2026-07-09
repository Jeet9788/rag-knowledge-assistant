from app.chunking import chunk_pages, fixed_size_chunks, sentence_aware_chunks


def test_fixed_size_chunks_respects_size_and_overlap():
    text = "a" * 1000
    chunks = fixed_size_chunks(text, chunk_size=300, overlap=50)
    assert len(chunks) >= 4
    assert all(len(c.content) <= 300 for c in chunks)


def test_sentence_aware_does_not_split_mid_sentence():
    text = "First sentence here. Second sentence follows. Third one is last."
    chunks = sentence_aware_chunks(text, chunk_size=40, overlap=10)
    assert chunks
    for c in chunks:
        assert c.content.strip()
        # each chunk should end at sentence punctuation
        assert c.content.rstrip()[-1] in ".!?"


def test_empty_text_produces_no_chunks():
    assert fixed_size_chunks("", 100, 10) == []
    assert sentence_aware_chunks("   ", 100, 10) == []


def test_chunk_pages_preserves_page_numbers():
    pages = [(1, "Page one text. More text."), (2, "Page two content here.")]
    chunks = chunk_pages(pages, chunk_size=1000, overlap=0, strategy="sentence")
    page_numbers = {c.page for c in chunks}
    assert page_numbers == {1, 2}
