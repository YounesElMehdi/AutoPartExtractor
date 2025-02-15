from app.regex_matcher import find_part_numbers

def test_regex_matching():
    text = "Part numbers: 127020634, E00001231_JLR, 16AC45000"
    matches = find_part_numbers(text)
    assert "127020634" in matches
    assert "E00001231_JLR" in matches
    assert "16AC45000" in matches