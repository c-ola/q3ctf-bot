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
    base_chal_path = "./challenges/"
    chals = {}
    for file in os.listdir(base_chal_path):
        # if its a directory
        chalpath = os.path.join(base_chal_path, file)
        if os.path.isdir(chalpath):
            for chaldirfile in os.listdir(chalpath):
                if chaldirfile.endswith(".yaml"):
                    chal = load_chal(chaldirfile, base_chal_path=chalpath)
                    if chal is not None:
                        chals[chal.chal_id] = chal
        else:
            chal = load_chal(file)
            if chal is not None:
                chals[chal.chal_id] = chal
    return chals


def load_chal(filename=None, base_chal_path="./challenges/"):
    if not filename.endswith(".yaml"):
        return None
    f = open(os.path.join(base_chal_path, filename), 'r')
    chal_data = yaml.safe_load(f)
    f.close()

    print(chal_data)
    chal_id = chal_data["name"]
    flag = chal_data["flag"]
    chal = Chal(chal_id, flag)

    if "message" in chal_data:
        chal.description = chal_data["message"]

    if "role" in chal_data:
        chal.role_id = chal_data["role"]

    if "attributes" in chal_data:
        chal.attributes = chal_data["attributes"]

    if "files" in chal_data:
        if chal_data["files"] is not None:
            for chal_file in chal_data["files"]:
                chal.files.append(chal_file)

    return chal


class Chal:
    """
    The challenge struct
    Attributes can be really just about anything, it will be possible to filter out challenges by different attributes, depending on what you put in the attribute field
    For example, if you want a "difficulty and category attribute"
    add
    attributes:
        difficulty: easy
        category: steganography
    This challenge will then appear when searching for easy or steganography
    This is kind of like a 'hints' property (honestly could be replaced by that)
    Just use something like hints: [easy, steganography]
    This can then be filtered with main filter and subfilter
    """

    def __init__(self, chal_id, flag,
                 description=None, role_id=None,
                 files=[], points=0, attributes={}):
        self.chal_id = chal_id
        self.flag = flag
        self.description = description
        self.role_id = role_id
        self.files = files
        self.points = points
        self.attributes = attributes

    def verify(self, flag_guess):
        return self.flag == flag_guess
