import iniltx


def test_inherit():
    cfg = """
    [ins1]
    val1 = hello
    
    [ins2]:ins1
    val2 = world
    
    [ins3]:ins1,ins2
    val3 = hi
    """

    tokens = iniltx._tokenize(cfg)
    data = iniltx.parse(tokens)

    assert "val1" in data["ins2"]
    assert "val2" in data["ins3"]
    assert "val1" in data["ins3"]


def test_interpolations():
    cfg = """
    val1 = hello
    val2 = world
    val3 = %val1% %val2%
    
    [ins1]
    val1 = foo
    val2 = bar
    val3 = %ins1:val1% %ins1:val2%
    """

    tokens = iniltx._tokenize(cfg)
    data = iniltx.parse(tokens)

    assert data["val3"] == "hello world"
    assert data["ins1"]["val3"] == "foo bar"


def test_directives():
    cfg = """
    #include test.ini
    
    [main]
    val = hello world
    """

    tokens = iniltx._tokenize(cfg)
    data = iniltx.parse(tokens)

    assert "is_test" in data
    assert "secret" in data
