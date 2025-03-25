import re

from langdetect import detect, LangDetectException
from nltk.stem import SnowballStemmer
from django.conf import settings

stemmer_en = SnowballStemmer('english')
stemmer_ru = SnowballStemmer('russian')


def normalize_text(text, use_stemming=True, default_lang=None):
    """
    Текст и ключевые слова обрабатываются
    для приведения к единому формату(удаление пунктуации, семинг)
    """
    try:
        lang = detect(text)
    except LangDetectException:
        lang = default_lang or 'en'

    text = text

    text = re.sub(r'[^\w\s]', '', text.lower())  # \w включает буквы, цифры и _
    words = text.split()

    # Обработка для каждого языка
    if lang == 'ru':
        if use_stemming:
            return [stemmer_ru.stem(word) if word.isalpha() else word
                    for word in words]
    elif lang == 'he':
        # Удаление огласовок (никкуд) для иврита
        text = re.sub(r'[\u0591-\u05BD\u05BF-\u05C2\u05C4-\u05C7]', '', text)
        words = text.split()  # Повторное разбиение после обработки

    else:  # en и другие языки
        if use_stemming:
            return [stemmer_en.stem(word) if word.isalpha() else word
                    for word in words]

    return words


def similarity(a, b):
    """
    Расчет расстояния Левенштейна для вычисления процента схожести между словами
    """

    m, n = len(a), len(b)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m + 1):
        for j in range(n + 1):
            if i == 0:
                dp[i][j] = j
            elif j == 0:
                dp[i][j] = i
            else:
                cost = 0 if a[i - 1] == b[j - 1] else 1
                dp[i][j] = min(dp[i - 1][j] + 1, dp[i][j - 1] + 1, dp[i - 1][j - 1] + cost)
    max_len = max(m, n)
    return (1 - dp[m][n] / max_len) * 100 if max_len != 0 else 100.0


def keyword_search(
        text: str,
        keywords: list[str],
        threshold: int = settings.SEARCH_THRESHOLD
) -> list[str]:
    normalized_text = normalize_text(text)
    normalized_keywords = [normalize_text(kw) for kw in keywords]
    found_words = []

    for kw in normalized_keywords:
        kw_len = len(kw)
        if kw_len == 1:
            kw_word = kw[0]
            for idx, word in enumerate(normalized_text):
                sim = similarity(kw_word, word)
                if sim >= threshold:
                    found_words.append(word)
        else:
            for idx in range(len(normalized_text) - kw_len + 1):
                window = normalized_text[idx:idx + kw_len]
                sims = [similarity(kw[i], window[i]) for i in range(kw_len)]
                if not sims:
                    continue

                min_sim = min(sims)
                if min_sim >= threshold:
                    found_words.append(' '.join(kw))

    return found_words

