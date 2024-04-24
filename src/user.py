from chal import Chal
import json
import os

def load_users():
    base_user_path = "./users/"
    users_file = "users.json"
    users = {}
    user_data = []
    path = os.path.join(base_user_path, users_file)
    if os.path.exists(path):
        f = open(path, 'r')
        user_data = json.load(f)
        f.close()
    print(user_data)
    for user in user_data:
        users[user["user_id"]] = User(user["user_id"], user["name"], user["completed"])
    return users

def save_users(users):
    base_user_path = "./users/"
    users_file = "users.json"
    path = os.path.join(base_user_path, users_file)
    user_data = []
    for user in users:
        user_data.append(users[user].get_data())
    if os.path.exists(path):
        f = open(path, 'w', encoding='utf-8')
        json.dump(user_data, f, ensure_ascii=False, indent=4)
        f.close()


class User:
    def __init__(self, user_id, name, completed=[]):
        self.user_id = user_id
        self.name = name
        self.completed = completed

    def add_chal(self, chal: Chal):
        if chal.name not in self.completed: # should be a hashset
            self.completed.append(chal.name)

    def remove_chal(self, target: Chal):
        for chal in self.completed:
            if chal.name == target.name:
                self.completed.remove(chal.name)

    def get_points(self, challenges):
        points = 0
        for chalname in self.completed:
            points += challenges[chalname].points
        return points

    def get_data(self):
        data = {}
        data["user_id"] = self.user_id
        data["name"] = self.name
        data["completed"] = self.completed
        return data
