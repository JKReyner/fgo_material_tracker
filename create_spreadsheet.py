import pandas as pd
import json
import requests

import xlsxwriter

# this file will create an initialized spreadsheet for the inventory

# load json from Atlas Academy

raw_json = requests.get('https://api.atlasacademy.io/export/JP/nice_servant_lang_en.json')
text = raw_json.text
data = json.loads(text)

'''

prepare the servant data frames

these are to be fixed data frames that fill out based on the in-game assets

'''

# function to find QP and items associated with ascension

def qp_asc(ids):
    ascension_number = ['0', '1', '2', '3']
    qp = []
    for ascension in ascension_number:
        qp.append({
            "ascension" : int(ascension),
            "amount" : data[ids]['ascensionMaterials'][ascension]['qp']
        })
    return qp

def item_asc(ids):
    ascension_number = ['0', '1', '2', '3']
    items = []
    for ascension in ascension_number:
        for index in range(len(data[ids]['ascensionMaterials'][ascension]['items'])):
            items.append({
                "ascension": int(ascension),
                "item": data[ids]['ascensionMaterials'][ascension]['items'][index]['item']['name'],
                "quantity": data[ids]['ascensionMaterials'][ascension]['items'][index]['amount']
            })
    return items

# function to find QP and items associated with skill leveling
# because of how similarly append skills are coded, these functions can be run with single functions

def qp_skl(ids, type = 0):
    if type == 0:
        material_lookup = 'skillMaterials'
    else:
        material_lookup = 'appendSkillMaterials'

    skill_level = ['1', '2', '3', '4', '5', '6', '7', '8', '9']
    qp = []
    for levels in skill_level:
        qp.append({
            "skill_level" : int(levels),
            "amount" : data[ids][material_lookup][levels]['qp']
        })
    return qp

def item_skl(ids, type = 0):
    if type == 0:
        material_lookup = 'skillMaterials'
    else:
        material_lookup = 'appendSkillMaterials'

    skill_level = ['1', '2', '3', '4', '5', '6', '7', '8', '9']
    items = []
    for levels in skill_level:
        for index in range(len(data[ids][material_lookup][levels]['items'])):
            items.append({
                "skill_level": int(levels),
                "item": data[ids][material_lookup][levels]['items'][index]['item']['name'],
                "quantity": data[ids][material_lookup][levels]['items'][index]['amount']
            })
    return items

# servant dictionary contains: id, name, class, rarity, ascension materials, skill materials, append materials

# initialize servant dictionary

servant_df = []

# create set of Servant list, based on collection number
# there are certain non-playable units in this list that will be dropped
# number 83, 149, 151, 152, 168, 240, and 333 get dropped

# ID number 1, Mashu, does not have ascension materials
# she needs to be dropped from the automated list it will cause an error otherwise
# she will have her materials added individually

npc_numbers = [1, 83, 149, 151, 152, 168, 240, 333]

# create a function that will return a list of playable Servants

def find_playable_servants(npc_list):
    playable_list = []

    for ids in range(len(data)):
        playable_list.append(data[ids]['collectionNo'])

    for item in npc_list:
        playable_list.remove(item)

    # use the playable list to find the list of the ID numbers

    servant_list = []

    for ids in range(len(data)):
        if data[ids]['collectionNo'] in playable_list:
            servant_list.append(ids)

    return servant_list

servant_list = find_playable_servants(npc_numbers)

# create a function that will identify Mashu's ID number regardless of position in the data

def find_mashu_id():
    for i in range(len(data)):
        if data[i]['collectionNo'] == 1:
            mashu_id = i
    return mashu_id

# run function

mashu_id = find_mashu_id()

# add Mashu to the data frame

servant_df.append( {
    "id" : data[mashu_id]['collectionNo'],
    "name" : data[mashu_id]['name'],
    "class" : data[mashu_id]['className'],
    "rarity" : data[mashu_id]['rarity'],
    "skill_item" : item_skl(mashu_id),
    "skill_qp" : qp_skl(mashu_id),
    "append_item" : item_skl(mashu_id, 1),
    "append_qp" : qp_skl(mashu_id, 1)
} )

for ids in servant_list:
    servant_df.append( {
        "id" : data[ids]['collectionNo'],
        "name" : data[ids]['name'],
        "class" : data[ids]['className'],
        "rarity" : data[ids]['rarity'],
        "ascension_item" : item_asc(ids),
        "ascension_qp" : qp_asc(ids),
        "skill_item" : item_skl(ids),
        "skill_qp" : qp_skl(ids),
        "append_item" : item_skl(ids, 1),
        "append_qp" : qp_skl(ids, 1)
    } )

# prepare for export

# create a function that will concate a dataframe based on each singular metric

def concat_dataframe(metric, df = servant_df):
    new_df = pd.concat([pd.json_normalize(x, metric, ['id', 'name', 'class', 'rarity'])
                        if metric in x
                        else pd.json_normalize(x)
                        for x in df])
    return new_df

# create data frames for each item category

# ascensions, since Mashu does not have any we perform a data slice

ascension_df_base = servant_df[1:]

ascension_df_1 = concat_dataframe('ascension_item', ascension_df_base)
ascension_df_2 = concat_dataframe('ascension_qp', ascension_df_base)

# skills

skill_df_1 = concat_dataframe('skill_item')
skill_df_2 = concat_dataframe('skill_qp')

# append skills

append_df_1 = concat_dataframe('append_item')
append_df_2 = concat_dataframe('append_qp')

# reorder columns for the six data frames so that id, name, class, and rarity appear first

ascension_item = ascension_df_1[ascension_df_1.columns[[3, 4, 5, 6, 0, 1, 2]]]
ascension_qp = ascension_df_2[ascension_df_2.columns[[2, 3, 4, 5, 0, 1]]]

skill_item = skill_df_1[skill_df_1.columns[[3, 4, 5, 6, 0, 1, 2]]]
skill_qp = skill_df_2[skill_df_2.columns[[2, 3, 4, 5, 0, 1]]]

append_item = append_df_1[append_df_1.columns[[3, 4, 5, 6, 0, 1, 2]]]
append_qp = append_df_2[append_df_2.columns[[2, 3, 4, 5, 0, 1]]]

'''

prepare master inventory sections

these will be for a specific user to keep track of their inventory

'''

# create the master_inventory data frame for the user to keep track of their Servant inventory

# function to look up relevant servant details for creating the data frame

def find_info(ids, type):
    info = (data[ids][type])
    return info

# we will use the previous find_playable_servants function again to access our list of objects to enter into the new df

master_inventory = []

npc_numbers = [83, 149, 151, 152, 168, 240, 333]

master_list = find_playable_servants(npc_numbers)

# fill out the master_inventory value

# owned, ascension, skill 1-3 and append 1-3 are meant to be filled out by the user so are blank during this stage

# master list will also include two separate columns, "Bond" and "Valentine" which the user can input info as they desire

for ids in master_list:
    master_inventory.append({
        "ID" : find_info(ids, 'collectionNo'),
        "Name" : find_info(ids, 'name'),
        "Class" : find_info(ids, 'className').capitalize(),
        "Rarity" : find_info(ids, 'rarity'),
        "Owned" : '',
        "Ascension" : '',
        "Skill 1" : '',
        "Skill 2" : '',
        "Skill 3" : '',
        "Append 1" : '',
        "Append 2" : '',
        "Append 3" : '',
        "Bond" : '',
        "Valentine" : ''
    })

# turn master_inventory into a data frame, sorted by the ID number

master_df = pd.DataFrame(master_inventory).sort_values(by='ID')

'''

create item data frame

we are only interested in certain items used during leveling
as a result, we can more easily get a list of items from our already existing data frame
a JSON file of all in-game items is available, but not needed

'''

# since we are referencing ascensions, to prevent an error we need to remove Mashu again

npc_numbers = [1, 83, 149, 151, 152, 168, 240, 333]
item_servant_list = find_playable_servants(npc_numbers)

# create list to fill with the necessary items
# initialize with QP

item_list = [{
    "ID": 1,
    "Name": "QP",
    "Quantity": ''
}]

ascension_number = ['0', '1', '2', '3']
items = []

# fill list with ascension items

for ids in item_servant_list:
    for ascension in ascension_number:
        for index in range(len(data[ids]['ascensionMaterials'][ascension]['items'])):
            new_object = {"ID": data[ids]['ascensionMaterials'][ascension]['items'][index]['item']['id'],
                          "Name": data[ids]['ascensionMaterials'][ascension]['items'][index]['item']['name'],
                          "Quantity": ''}
            if new_object not in item_list:
                item_list.append(new_object)

# since there are certain items needed for skill leveling, we repeat the process for skill levels
# we also can do this for append skill materials at the same time, since they have the same number of levels
# although they tend not to require different items

skill_level = ['1', '2', '3', '4', '5', '6', '7', '8', '9']

for ids in item_servant_list:
    skill_types = ['skillMaterials', 'appendSkillMaterials']
    for levels in skill_level:
        for types in skill_types:
            for index in range(len(data[ids][types][levels]['items'])):
                new_object = {"ID": data[ids][types][levels]['items'][index]['item']['id'],
                              "Name": data[ids][types][levels]['items'][index]['item']['name'],
                              "Quantity": ''}
                if new_object not in item_list:
                    item_list.append(new_object)

item_df = pd.DataFrame(item_list).sort_values(by='ID')

'''

create a dataframe for the inventory
it will be used to keep track of each in-game item as well as QP

'''

'''excel_writer = pd.ExcelWriter('test1.xlsx', engine='xlsxwriter')
# use to_excel function and specify the sheet_name and index
# to store the dataframe in specified sheet

# the user's sheets are placed first

master_df.to_excel(excel_writer, sheet_name="master_data", index=False)
item_df.to_excel(excel_writer, sheet_name="inventory_data", index=False)

# the reference sheets are placed last

ascension_item.to_excel(excel_writer, sheet_name="ascension_item", index=False)
ascension_qp.to_excel(excel_writer, sheet_name="ascension_qp", index=False)
skill_item.to_excel(excel_writer, sheet_name="skill_item", index=False)
skill_qp.to_excel(excel_writer, sheet_name="skill_qp", index=False)
append_item.to_excel(excel_writer, sheet_name="append_item", index=False)
append_qp.to_excel(excel_writer, sheet_name="append_qp", index=False)

excel_writer.save()'''
