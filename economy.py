import json

DATA_FILE = 'data.json'

# Ładowanie danych użytkowników
def load_data():
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

# Zapis danych użytkowników
def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

# Oblicz modyfikator zarobków/cen na podstawie reputacji
def rep_modifier(user_id):
    data = load_data()
    rep = data.get(str(user_id), {}).get('reputation', 0)
    modifier = (rep // 10) * 0.05
    return 1 + modifier  # 1 = brak zmian, >1 premie, <1 kary

# Aktualizacja reputacji użytkownika
def update_reputation(user_id, amount):
    data = load_data()
    user = data.setdefault(str(user_id), {'cash': 0, 'bank': 0, 'reputation': 0})

    user['reputation'] += amount
    user['reputation'] = max(min(user['reputation'], 100), -100)  # ograniczenie -100 do 100
    save_data(data)

def load_businesses():
    # np.:
    with open("data/businesses.json", "r") as f:
        return json.load(f)
        
# Pobranie danych użytkownika (stan)
def get_user_data(user_id):
    data = load_data()
    return data.get(str(user_id), {'cash': 0, 'bank': 0, 'reputation': 0})
