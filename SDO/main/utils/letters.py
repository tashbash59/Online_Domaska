TRANSLIT_DICT = {
    # Строчные буквы
    'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'e',
    'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
    'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
    'ф': 'f', 'х': 'kh', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'shch',
    'ы': 'y', 'э': 'e', 'ю': 'yu', 'я': 'ya',
    # Заглавные буквы
    'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Е': 'E', 'Ё': 'E',
    'Ж': 'Zh', 'З': 'Z', 'И': 'I', 'Й': 'Y', 'К': 'K', 'Л': 'L', 'М': 'M',
    'Н': 'N', 'О': 'O', 'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T', 'У': 'U',
    'Ф': 'F', 'Х': 'Kh', 'Ц': 'Ts', 'Ч': 'Ch', 'Ш': 'Sh', 'Щ': 'Shch',
    'Ы': 'Y', 'Э': 'E', 'Ю': 'Yu', 'Я': 'Ya',
}
def convert_fio_to_english(fio):
    """Конвертирует ФИО из кириллицы в латиницу в формате 'IvanovII'."""
    parts = fio.split()
    if len(parts) != 3:
        raise ValueError("ФИО должно быть в формате 'Фамилия Имя Отчество'")

    last_name, first_name, patronymic = parts
    
    # Транслитерация фамилии
    latin_last_name = ''.join([TRANSLIT_DICT.get(c.lower(), c) for c in last_name]).capitalize()
    
    # Первые буквы имени и отчества (заглавные)
    initials = (first_name[0] + patronymic[0]).upper()
    latin_initials = ''.join([TRANSLIT_DICT.get(c.lower(), c) for c in initials])
    
    return f"{latin_last_name}{latin_initials}"