def load_dictionary(path: str) -> set:
    with open(path, 'r', encoding="utf-8-sig") as file:
        return set([x.rstrip() for x in file.readlines()])

def unix_timestamp_to_str(timestamp: int) -> str:
    from datetime import datetime, UTC
    raw = datetime.fromtimestamp(timestamp, UTC)
    
    day = raw.day
    month = raw.month
    year = raw.year

    return f"{day}.{month}.{year}"

def bool_to_str(b: bool) -> str:
    if b:
        return "Положительный"
    return "Отрицательный"

def is_political(dictionary: set, review: str) -> bool:
    review_words = words(review.lower())
    for word in review_words:
        if word in dictionary:
            return True
    return False

def in_date_range(timestamp: int) -> bool:
    from datetime import datetime, UTC
    
    raw = datetime.fromtimestamp(timestamp, UTC)

    return raw.year == 2023

def canonize(s: str) -> str:
    # Alphabet with lower symbols
    al = set(["а","б","в","г","д","е","ё","ж","з","и","й",
              "к","л","м","н","о","п","р","с","т","у","ф",
              "х","ц","ч","ш","щ","ъ","ы","ь","э","ю","я"])
    
    # Alphabet with upper symbols
    au = set([x.upper() for x in al])

    # Digits
    dg = set(['1', '2', '3', '4', '5', '6', '7', '8', '9', '0'])
    
    # Special symbols
    spec = set(['.', ';', ':', '?', '!', ' ', '-', '(', ')', ','])
    
    return ''.join([c for c in s.replace("\n", " ") if c in al | au | spec | dg])

def words(s: str) -> str:
    # Alphabet with lower symbols
    al = set(["а","б","в","г","д","е","ё","ж","з","и","й",
              "к","л","м","н","о","п","р","с","т","у","ф",
              "х","ц","ч","ш","щ","ъ","ы","ь","э","ю","я"])
    
    # Alphabet with upper symbols
    au = set([x.upper() for x in al])

    # Digits
    dg = set(['1', '2', '3', '4', '5', '6', '7', '8', '9', '0'])

    # Special symbols
    spec = set([' '])

    replace = lambda c: c if c in al | au | spec | dg else ' '

    k = ''.join([replace(c) for c in s])

    return set(k.lower().split(" "))
