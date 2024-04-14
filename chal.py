import json
import os
import yaml


def load_chals_json(path="challenges.json"):
    f = open(path)
    chals_unparsed = json.load(f)
    f.close()
    chals = {}
    for chal_data in chals_unparsed["challenges"]:
        chal_id = chal_data["chal_id"]
        flag = chal_data["flag"]
        chal = Chal(chal_id, flag)
        if "role_id" in chal_data:
            role_id = chal_data["role_id"]
            chal.role_id = role_id
        if "description" in chal_data:
            description = chal_data["description"]
            chal.role_id = description
        chals[chal_id] = chal


def load_challenges(path="challenges.json"):
    chal_path = "./challenges"
    chals = {}
    for filename in os.listdir(chal_path):
        if not filename.endswith(".yaml"):
            continue
        f = open(os.path.join(chal_path, filename), 'r')
        chal_data = yaml.safe_load(f)
        f.close()
        print(chal_data)
        chal_id = chal_data["name"]
        flag = chal_data["flag"]
        chal = Chal(chal_id, flag)
        if "role" in chal_data:
            chal.role_id = chal_data["role"]
        if "attributes" in chal_data:
            if "role" in chal_data["attributes"]:
                chal.role_id = chal_data["attributes"]["role"]
        if "message" in chal_data:
            chal.description = chal_data["message"]
        if "files" in chal_data:
            if chal_data["files"] is not None:
                for chal_file in chal_data["files"]:
                    chal.files.append(chal_file)
        chals[chal_id] = chal

    return chals


class Chal:
    def __init__(self, chal_id, flag, description=None, role_id=None, files=[]):
        self.chal_id = chal_id
        self.flag = flag
        self.description = description
        self.role_id = role_id
        self.files = files

    def verify(self, flag_guess):
        return self.flag == flag_guess
