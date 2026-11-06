from app.main import load_index, retrieve

queries = [
    "What is the capital of Chhattisgarh?",
    "छत्तीसगढ़ की संस्कृति और प्रमुख त्योहार कौन से हैं?",
    "Chhattisgarh ke prasiddh paryatan sthal kaun se hain?",
]

load_index()

for query in queries:
    print("\n" + "=" * 75)
    print("QUERY:", query)
    print("=" * 75)

    docs = retrieve(query)

    for i, doc in enumerate(docs, start=1):
        print(f"\n{i}. TITLE: {doc.get('title', '')}")
        print("URL:", doc.get("source_url", ""))
        print("SCORE:", doc.get("score"))
        print("TEXT:", (doc.get("text", "") or "")[:450])
