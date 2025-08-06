
import time
from economy import load_data, save_data

def check_prison(user_id):
    data = load_data()
    user = data.get(str(user_id), {})
    prison_time = user.get("prison", 0)

    # Jeśli czas więzienia jeszcze nie minął, gracz nadal siedzi
    if prison_time > time.time():
        return True

    # Jeśli czas minął, wyczyść status więzienia
    if "prison" in user:
        del user["prison"]
        data[str(user_id)] = user
        save_data(data)

    return False
