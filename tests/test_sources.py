from praxis.sources import act_reference, verify_url


def test_verify_url_for_each_code():
    assert verify_url("gk-rf", "431") == "https://www.zakonrf.info/gk/431/"
    assert verify_url("uk-rf", "159") == "https://www.zakonrf.info/uk/159/"
    assert verify_url("nk-rf", "220") == "https://www.zakonrf.info/nk/220/"
    assert verify_url("tk-rf", "81") == "https://www.zakonrf.info/tk/81/"
    assert verify_url("koap-rf", "12.8") == "https://www.zakonrf.info/koap/12.8/"
    # ЖК на zakonrf.info — slug jk, не zhk.
    assert verify_url("zhk-rf", "30") == "https://www.zakonrf.info/jk/30/"


def test_verify_url_tolerates_sample_suffix():
    # sample-корпус нумерует акты: "gk-rf-1" должен свестись к тому же slug.
    assert verify_url("gk-rf-1", "10") == "https://www.zakonrf.info/gk/10/"


def test_verify_url_unknown_or_empty():
    assert verify_url("fake-act", "1") is None
    assert verify_url("gk-rf", "") is None
    assert verify_url("", "431") is None


def test_act_reference_formats_number_and_date():
    assert act_reference("51-ФЗ", "1994-11-30") == "51-ФЗ от 30.11.1994"


def test_act_reference_number_only_when_no_date():
    assert act_reference("51-ФЗ", None) == "51-ФЗ"
    assert act_reference("51-ФЗ", "bad-date") == "51-ФЗ"


def test_act_reference_none_without_number():
    assert act_reference(None, "1994-11-30") is None
