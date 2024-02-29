models = [
    "MonoHime/rubert-base-cased-sentiment-new",
    "ai-forever/sbert_large_nlu_ru",
    "Vikhrmodels/VikhrT5-240m",
]

keys_to_embed = [
    ['about', 'key_skills', 'position', 'description'],
    ['name', 'keywords', 'description'],
]

prompt = '''Тебе будет дано описание вакансии на должность в IT компании, из неё ты должен извлечь следующую информацию:
Требуемый возраст(min age, max age), Уровень образования (Высшее/null), Опыт работы (количество лет), Требуемые языки, Страна проживания.
Если какой-то информации не хватает, обозначь её null. Ты должен дать лишь ответ в формате json и больше ничего.
Пример работы:
input:
Требования: 4+ года опыта работы с Java 8+ или Kotlin, 2+ года C++. Набираются кандидаты в возрасте от 25 лет. Работа происходит на русском языке, требуются знания английского.
output:
{"min age": 25, "max age": null, "education level": null, "experience": 4, "languages": ["Русский", "Английский"], "country": "Россия"}

input:
'''

invoke_url = "https://api.nvcf.nvidia.com/v2/nvcf/pexec/functions/8f4118ba-60a8-4e6b-8574-e38a4067a4a3"

headers = {
    "Authorization": "Bearer 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",
    "accept": "text/event-stream",
    "content-type": "application/json",
}