from pgex_api.services import random_code

def test_if_function_random_code_generate_unique_random_string():
    array = []
    for i in range(0, 100):
        array.append(random_code())
    assert type(array[0]) == str
    assert len(array) == len(list(set(array)))