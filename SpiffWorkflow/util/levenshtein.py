from difflib import ndiff


def distance(str1, str2):
    counter = {"+": 0, "-": 0}
    distance = 0
    for edit_code, *_ in ndiff(str1, str2):
        if edit_code == " ":
            distance += max(counter.values())
            counter = {"+": 0, "-": 0}
        else:
            counter[edit_code] += 1
    distance += max(counter.values())
    return distance


def most_similar(value, item_list, limit):
    distances = [(key, distance(value, key)) for key in item_list]
    distances.sort(key=lambda x: x[1])
    return [x[0] for x in distances[:limit]]

