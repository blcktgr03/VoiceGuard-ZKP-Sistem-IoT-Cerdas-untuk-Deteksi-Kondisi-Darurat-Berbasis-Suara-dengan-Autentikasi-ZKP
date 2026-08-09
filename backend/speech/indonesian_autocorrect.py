import re


MAX_EDIT_DISTANCE = 3
EMERGENCY_PRIORITY_WORDS = {
    "ambulans", "api", "asap", "bahaya", "banjir", "bantuan", "darurat",
    "evakuasi", "gempa", "kebakaran", "kecelakaan", "ledakan", "medis",
    "pingsan", "polisi", "sakit", "terbakar", "terjebak", "terluka",
    "tertimpa", "tolong",
}
EMERGENCY_ALIASES = {
    # Permintaan pertolongan. Beberapa bentuk berasal dari keluaran Whisper
    # yang pernah muncul saat pengujian mikrofon INMP441.
    "dalong": "tolong",
    "talong": "tolong",
    "tlong": "tolong",
    "tolon": "tolong",
    "tolongg": "tolong",
    "tong": "tolong",
    "tulung": "tolong",
    "tung": "tolong",
    "bantua": "bantuan",
    "bantuam": "bantuan",
    "bantun": "bantuan",

    # Kebakaran dan kecelakaan.
    "kebakalan": "kebakaran",
    "kebakaraan": "kebakaran",
    "kebakarann": "kebakaran",
    "kebakran": "kebakaran",
    "keperkaran": "kebakaran",
    "kubakaran": "kebakaran",
    "kcelakaan": "kecelakaan",
    "kecelakan": "kecelakaan",
    "kecelakaann": "kecelakaan",
    "tebakar": "terbakar",
    "terbakarr": "terbakar",

    # Kondisi dan layanan darurat.
    "darura": "darurat",
    "darurad": "darurat",
    "daruratt": "darurat",
    "ambulan": "ambulans",
    "ambulance": "ambulans",
    "ambulanss": "ambulans",
    "mediss": "medis",
    "polis": "polisi",
    "polisy": "polisi",

    # Kondisi korban.
    "pinsan": "pingsan",
    "pingsang": "pingsan",
    "pingsn": "pingsan",
    "sakid": "sakit",
    "sakir": "sakit",
    "sakitt": "sakit",
    "teluka": "terluka",
    "terlukaa": "terluka",
    "terlka": "terluka",
    "tertimpah": "tertimpa",
    "tertimpan": "tertimpa",
    "tertipa": "tertimpa",
    "terjebakk": "terjebak",
    "terjbak": "terjebak",
    "tangaku": "tanganku",

    # Bencana dan bahaya lingkungan.
    "banjer": "banjir",
    "banjirr": "banjir",
    "gemba": "gempa",
    "assap": "asap",
    "asapp": "asap",
    "ledakkan": "ledakan",
    "ledakn": "ledakan",
    "efakuasi": "evakuasi",
    "evakusi": "evakuasi",
    "evakuas": "evakuasi",
    "bocorr": "bocor",
    "kebocorann": "kebocoran",
    "jato": "jatuh",
    "jatoh": "jatuh",
    "jatu": "jatuh",
}

# Domain vocabulary is intentionally bounded so names and unrelated words are
# not aggressively rewritten. Common words protect normal Indonesian phrases.
INDONESIAN_VOCABULARY = (
    "ada", "aman", "anda", "api", "area", "atas", "atau", "bantuan",
    "aduh", "bahaya", "banjir", "bantu", "bekerja", "bukan", "butuh",
    "cuma", "dalam",
    "dan", "darah", "darurat", "datang", "dengan", "di", "evakuasi",
    "gas", "gempa", "hanya", "hati", "ini", "jatuh", "kami", "karena",
    "kalau", "kasih", "kebakaran", "kecelakaan", "keadaan", "kerja",
    "keselamatan", "korban",
    "listrik", "lokasi", "luka", "medis", "mesin", "mohon", "normal",
    "orang", "palsu", "panggil", "pekerja", "pekerjaan", "perlu",
    "pingsan", "polisi",
    "sakit", "saya", "segera", "selamat", "semua", "sirene", "sudah",
    "suara", "teman", "tempat", "terbakar", "terdeteksi", "terima",
    "terjadi", "terjebak", "terluka", "tertimpa", "tidak", "tolong",
    "butuhkan", "ambulans", "yang",
    "ledakan", "asap", "bocor", "kebocoran", "kebanjiran", "pertolongan",
)


def levenshtein_distance(left: str, right: str, limit: int = MAX_EDIT_DISTANCE) -> int:
    """Return edit distance, stopping once the requested limit is exceeded."""
    if left == right:
        return 0
    if abs(len(left) - len(right)) > limit:
        return limit + 1

    previous = list(range(len(right) + 1))
    for row, left_char in enumerate(left, start=1):
        current = [row]
        row_minimum = row
        for column, right_char in enumerate(right, start=1):
            current_value = min(
                current[column - 1] + 1,
                previous[column] + 1,
                previous[column - 1] + (left_char != right_char),
            )
            current.append(current_value)
            row_minimum = min(row_minimum, current_value)
        if row_minimum > limit:
            return limit + 1
        previous = current
    return previous[-1]


def correct_indonesian_text(text: str) -> tuple[str, list[tuple[str, str, int]]]:
    """Correct only reviewed Indonesian/ASR aliases to avoid false rewrites."""
    corrections: list[tuple[str, str, int]] = []

    def replace(match: re.Match[str]) -> str:
        original = match.group(0)
        normalized = original.lower()
        if normalized in EMERGENCY_ALIASES:
            best_word = EMERGENCY_ALIASES[normalized]
            distance = levenshtein_distance(normalized, best_word, MAX_EDIT_DISTANCE)
            corrected = best_word.capitalize() if original[:1].isupper() else best_word
            corrections.append((original, corrected, distance))
            return corrected

        # Jangan mencari kata terdekat dari seluruh kosakata. Pendekatan lama
        # dapat mengubah kata valid dari dataset, misalnya "tapi" menjadi
        # "api". Kata yang belum ditinjau dibiarkan untuk dipahami IndoBERT.
        return original

    corrected_text = re.sub(r"[^\W\d_]+", replace, text, flags=re.UNICODE)
    return corrected_text, corrections
