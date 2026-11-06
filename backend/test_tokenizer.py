import app.main as m

queries = [
    "बस्तर दशहरा की परंपराएँ बताइए",
    "बस्तर दशहरा",
    "Bastar Dussehra festival traditions",
]

for q in queries:
    print("\nQuery:", q)
    print("Tokens:", m.tokenize(q))
