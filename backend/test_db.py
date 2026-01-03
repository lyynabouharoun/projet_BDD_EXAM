from backend.database import fetch_formations

formations = fetch_formations()
print(len(formations), "formations loaded")
