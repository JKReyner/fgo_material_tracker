import pandas as pd
import json
import requests

# load json from Atlas Academy

raw_json = requests.get('https://api.atlasacademy.io/export/JP/nice_servant_lang_en.json')
text = raw_json.text
data = json.loads(text)

# this code can be used to reference a full list of Servant IDs

def check_servant_ids():
    for i in range(len(data)):
        print(i, ":", data[i]['name'])
        print("Code number:", data[i]['id'])
        print("Collection number:", data[i]['collectionNo'])

# create a reverse lookup function to find a Servant ID based on name input

def return_lookup(name, id):
    print('Name:', name)
    print("ID Number:", id)

def servant_reverse_lookup(name):
    for i in range(len(data)):
        if name in data[i]['name']:
            print('Name:', data[i]['name'])
            print("Code number:", data[i]['id'])
            print("Collection number:", data[i]['collectionNo'])
            print('Class:', data[i]['className'])
            print('Rarity:', data[i]['rarity'])
            print("ID Number:", i)
            print()

        # function overloading so a JP text name can be inputted
        if name in data[i]['originalName']:
            print('Name:', data[i]['name'])
            print("Code number:", data[i]['id'])
            print("Collection number:", data[i]['collectionNo'])
            print('Class:', data[i]['className'])
            print('Rarity:', data[i]['rarity'])
            print("ID Number:", i)
            print()

''' reference codes, section 1

code to access the number of ascension materials for servant ID = id, stage = ascension_number
# len(data[id]['ascensionMaterials'][ascension_number]['items'])

code to access the name of an ascension material for servant ID = id, stage = ascension_number, item = index
# data[id]['ascensionMaterials'][ascension_number]['items'][index]['item']['name']
# data[id]['ascensionMaterials'][ascension_number]['items'][index]['amount']

code to find qp cost of ascension for servant ID = id, stage = ascension_number, item = index
# data[id]['ascensionMaterials'][ascension_number]['qp']

'''

# code to check ascension materials of a specific servant, use ID based on the lookup

def ascension_requirements(id):
    ascension_number = ['0', '1', '2', '3']
    print('Servant Name:', data[id]['name'])
    for ascension in ascension_number:
        print('Ascension Number:', ascension)
        for index in range(len(data[id]['ascensionMaterials'][ascension]['items'])):
            print("Item:", data[id]['ascensionMaterials'][ascension]['items'][index]['item']['name'])
            print("Amount:", data[id]['ascensionMaterials'][ascension]['items'][index]['amount'])
            print("QP:", data[id]['ascensionMaterials'][ascension]['qp'])

''' reference codes, section 2

code to access the name/amount of a skill material for servant ID = id, skill level = skill_level, item = index
# data[id]['skillMaterials'][skill_level]['items'][index]['item']['name']
# data[id]['skillMaterials'][skill_level]['items'][index]['amount']

'''

# code to check skill requirements of a specific servant

def skill_requirements(id):
    skill_level = ['1', '2', '3', '4', '5', '6', '7', '8', '9']
    print('Servant Name:', data[id]['name'])
    for levels in skill_level:
        print('Skill Level:', levels)
        for index in range(len(data[id]['skillMaterials'][levels]['items'])):
            print("Item:", data[id]['skillMaterials'][levels]['items'][index]['item']['name'])
            print("Amount:", data[id]['skillMaterials'][levels]['items'][index]['amount'])
        print("QP:", data[id]['skillMaterials'][levels]['qp'])

# code to check append skill requirements of a specific servant

def append_requirements(id):
    skill_level = ['1', '2', '3', '4', '5', '6', '7', '8', '9']
    print('Servant Name:', data[id]['name'])
    for levels in skill_level:
        print('Skill Level:', levels)
        for index in range(len(data[id]['appendSkillMaterials'][levels]['items'])):
            print("Item:", data[id]['appendSkillMaterials'][levels]['items'][index]['item']['name'])
            print("Amount:", data[id]['appendSkillMaterials'][levels]['items'][index]['amount'])
        print("QP:", data[id]['appendSkillMaterials'][levels]['qp'])

# combine ascension + skill + append requirements

def servant_requirements(id):
    print()
    ascension_requirements(id)
    print()
    skill_requirements(id)
    print()
    append_requirements(id)

# code to return a Servant's mugshot icon

def find_servant_icon(id):
    ascension_number = ['1', '2', '3', '4']
    for ascension in ascension_number:
        print(data[id]['extraAssets']['faces']['ascension'][ascension])
    if 'costume' in data[id]['extraAssets']['faces']:
        print("Costumes:")
        for item in data[id]['extraAssets']['faces']['costume']:
            print(data[id]['extraAssets']['faces']['costume'][item])

data = dict = [{
    'id': 1,
    'name': 'A',
    'class': '1',
    'item_details': [
        {'level': 1,
         'item': 'item A',
         'quantity': 5},
        {'level': 3,
         'item': 'item A',
         'quantity': 5},
        {'level': 3,
         'item': 'item C',
         'quantity': 5}
    ]
},
{
    'id': 2,
    'name': 'B',
    'class': '2',
    'item_details': [
        {'level': 1,
         'item': 'item B',
         'quantity': 2},
        {'level': 2,
         'item': 'item D',
         'quantity': 10}
    ]
},

{
    'id': 3,
    'name': 'B',
    'class': '3'
}]

df = pd.concat([pd.json_normalize(x, 'item_details', ['id', 'name', 'class'])
                    if 'item_details' in x
                    else pd.json_normalize(x)
                    for x in data])
pd.set_option('display.max_columns', None)
print(df)
