import json
import os
import yaml


def load_challenges(path="challenges.json"):
    base_chal_path = "./challenges/"
    chals = {}
    for file in os.listdir(base_chal_path):
        # if its a directory
        chalpath = os.path.join(base_chal_path, file)
        if os.path.isdir(chalpath):
            for chaldirfile in os.listdir(chalpath):
                if chaldirfile.endswith(".yaml"):
                    print("loading file: ", chaldirfile)
                    chal = load_chal(chaldirfile, base_chal_path=chalpath)
                    if chal is not None:
                        chals[chal.name] = chal
        else:
            chal = load_chal(file)
            if chal is not None:
                chals[chal.name] = chal
    return chals


def load_chal(filename=None, base_chal_path="./challenges/"):
    if not filename.endswith(".yaml"):
        return None
    f = open(os.path.join(base_chal_path, filename), 'r')
    chal_data = yaml.safe_load(f)
    f.close()

    name = chal_data["name"]
    flag = chal_data["flag"]
    chal = Chal(name, flag)

    if "message" in chal_data:
        chal.description = chal_data["message"]

    if "role" in chal_data:
        chal.role_id = chal_data["role"]

    if "attributes" in chal_data:
        chal.attributes = chal_data["attributes"]

    if "points" in chal_data:
        chal.points = chal_data["points"]

    if "files" in chal_data:
        chal.files = chal_data["files"]

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

    def __init__(self,
                 name,
                 flag,
                 description=None,
                 role_id=None,
                 files=[],
                 points=0,
                 attributes={}
                 ):
        self.name = name
        self.flag = flag
        self.description = description
        self.role_id = role_id
        self.files = files
        self.points = points
        self.attributes = attributes

    def verify(self, flag_guess):
        return self.flag == flag_guess

    def get_data_as_dict(self):
        chal_data = {}
        chal_data["name"] = self.name
        chal_data["flag"] = self.flag
        chal_data["message"] = self.description
        chal_data["role"] = self.role_id
        chal_data["files"] = self.files
        chal_data["points"] = self.points
        chal_data["attributes"] = self.attributes
        return chal_data

    def save_chal(self, override=False):
        base_chal_path = "./challenges/"
        chal_dir = base_chal_path + self.name
        if not os.path.exists(chal_dir):
            os.mkdir(chal_dir)
        if os.path.exists(chal_dir + self.name) and os.path.isfile(chal_dir + self.name):
            if override:
                print("Challenge already exists, not overriding")
                return False
            else:
                print("Overriding old challenge")
        chal_data = self.get_data_as_dict()
        f = open(chal_dir + "/" + self.name + ".yaml", 'w')
        yaml.dump(chal_data, f, default_flow_style=False)
        f.close()
        return True

    def print(self):
        print(self.get_data_as_dict())
        print(self.name)
        print(self.flag)
        print(self.description)
        print(self.role_id)
        print(self.files)
        print(self.points)
        print(self.attributes)


