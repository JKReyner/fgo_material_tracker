import pandas as pd
import numpy as np

import json
import requests

from collections import defaultdict
import openpyxl
import xlsxwriter

# load json from Atlas Academy

raw_json = requests.get('https://api.atlasacademy.io/export/JP/nice_servant_lang_en.json')
text = raw_json.text
data = json.loads(text)

# import excel file

f = pd.ExcelFile('test1.xlsx')

# split into data frames

# if append skills are not filled out, it will be assumed that they are not something the user is interested in
# they will be given a default value of 0 which will make coding around them simpler

master_data = f.parse(sheet_name = 'master_data').fillna(0)
inventory_data = f.parse(sheet_name = 'inventory_data')
ascension_item = f.parse(sheet_name = 'ascension_item')
ascension_qp = f.parse(sheet_name = 'ascension_qp')
skill_item = f.parse(sheet_name = 'skill_item')
skill_qp = f.parse(sheet_name = 'skill_qp')
append_item = f.parse(sheet_name = 'append_item')
append_qp = f.parse(sheet_name = 'append_qp')

pd.set_option('display.max_columns', None)

# using loop to get dictionaries
# one of the most common issues this code faces is adding values to dictionaries
# resulting in a list of dictionaries when a single dictionary is the goal
# the function will allow any list of dictionaries to be converted into a dictionary

def dict_convert(list_of_dicts):
    res = defaultdict(list)
    for sub in list_of_dicts:
        for key in sub:
            res[key].append(sub[key])
    return res

# create a sublist of all the servants owned by the user to reference

owned_list = []

for ids in range(len(master_data)):
    if master_data.loc[ids]['Owned'] == 'Y':
        owned_list.append(master_data.loc[ids])

# create a list of reverse-lookup IDs

def create_lookup_ids(owned_data):

    # collection_ids is a list of the index for each Servant based on in-game files
    # this is present in the first column of the data frame and is being extracted into a single list

    collection_ids = []

    for ids in range(len(owned_data)):
        collection_ids.append(owned_data[ids]['ID'])

    # using the collection, reverse lookup on the original JSON file to create lookup_ids
    # lookup_ids is the unique ID that is needed in order to access the original data frame

    lookup_ids = []

    # the loop will find the correct lookup_id for each item in our collection_id dataframe

    for items in collection_ids:
        for ids in range(len(data)):
            if data[ids]['collectionNo'] == items:
                lookup_ids.append(ids)

    # combine collection_ids and lookup_ids into a single data frame, reference_ids
    # placing them in a data frame will make sure that the ids are always aligned to the same Servant

    reference_ids = pd.DataFrame(np.column_stack([collection_ids, lookup_ids]),
                               columns=['collection_ids', 'lookup_ids'])

    return reference_ids

# create a function to find the remaining levels of ascension

def find_ascension_levels(collection_id):
    ascension_levels = ['0', '1', '2', '3']

    current_ascension_level = int(master_data[master_data['ID'] == collection_id]['Ascension'])
    remaining_levels = ascension_levels[current_ascension_level:]

    return remaining_levels

# create a function to find the remaining levels of skills for servant based on collection ID and the skill number
# this same code is identical for append skills

def find_skill_levels(collection_id, skill_number):
    skill_level = ['1', '2', '3', '4', '5', '6', '7', '8', '9']

    if int(master_data[master_data['ID'] == collection_id][skill_number]) > 0:
        # due to data formatting, to find the total materials needed for each level-up
        # subtracting 1 is necessary
        current_skill_level = int(master_data[master_data['ID'] == collection_id][skill_number]) - 1
    else:
        # the skill level is not 9, but since it is being ignored if it was unfilled
        # setting it to 9 is a simple way to cause the data to fill it with an empty value
        current_skill_level = 9
    remaining_levels = skill_level[current_skill_level:]

    return remaining_levels

# create a function that will return a set of all levels using only a single line of code

def find_levels(collection_id):
    ascension_level = find_ascension_levels(collection_id)
    skill_level_1 = find_skill_levels(collection_id, 'Skill 1')
    skill_level_2 = find_skill_levels(collection_id, 'Skill 2')
    skill_level_3 = find_skill_levels(collection_id, 'Skill 3')
    append_level_1 = find_skill_levels(collection_id, 'Append 1')
    append_level_2 = find_skill_levels(collection_id, 'Append 2')
    append_level_3 = find_skill_levels(collection_id, 'Append 3')
    return ascension_level, \
           skill_level_1, skill_level_2, skill_level_3, \
           append_level_1, append_level_2, append_level_3

# create a function to find the total QP required to level

def find_ascension_qp(lookup_id, ascension_number = ['0', '1', '2', '3']):
    qp = []
    for ascension in ascension_number:
        qp.append({
            "ID" : 1,
            "item" : 'QP',
            "Total Required" : data[lookup_id]['ascensionMaterials'][ascension]['qp']
        })
    output = dict_convert(qp)
    return output

def find_skill_qp(ids, type = 0, levels = ['1', '2', '3', '4', '5', '6', '7', '8', '9']):
    if type == 0:
        material_lookup = 'skillMaterials'
    else:
        material_lookup = 'appendSkillMaterials'

    qp = []
    for levels in levels:
        qp.append({
            "ID" : 1,
            "item" : 'QP',
            "Total Required" : data[ids][material_lookup][levels]['qp']
        })
    output = dict_convert(qp)
    return output

def find_skill_items(lookup_id, type = ['skillMaterials'],
                     skill_number = ['1', '2', '3', '4', '5', '6', '7', '8', '9']):
    needed_items = []

    for levels in skill_number:
        for index in range(len(data[lookup_id][type][levels]['items'])):
            needed_items.append({
                "ID": data[lookup_id][type][levels]['items'][index]['item']['id'],
                "item": data[lookup_id][type][levels]['items'][index]['item']['name'],
                "Total Required": data[lookup_id][type][levels]['items'][index]['amount']
            })

    output = dict_convert(needed_items)
    return output

# create a function that will find the items required for a specific ascension & skill

def find_ascension_items(lookup_id, ascension_number = ['0', '1', '2', '3']):
    needed_items = []

    for ascension in ascension_number:
        for index in range(len(data[lookup_id]['ascensionMaterials'][ascension]['items'])):
            needed_items.append({
                "ID": data[lookup_id]['ascensionMaterials'][ascension]['items'][index]['item']['id'],
                "item": data[lookup_id]['ascensionMaterials'][ascension]['items'][index]['item']['name'],
                "Total Required": data[lookup_id]['ascensionMaterials'][ascension]['items'][index]['amount']
            })

    output = dict_convert(needed_items)
    return output

def find_skill_items(lookup_id, type = ['skillMaterials'],
                     skill_number = ['1', '2', '3', '4', '5', '6', '7', '8', '9']):
    needed_items = []

    for levels in skill_number:
        for index in range(len(data[lookup_id][type][levels]['items'])):
            needed_items.append({
                "ID": data[lookup_id][type][levels]['items'][index]['item']['id'],
                "item": data[lookup_id][type][levels]['items'][index]['item']['name'],
                "Total Required": data[lookup_id][type][levels]['items'][index]['amount']
            })

    output = dict_convert(needed_items)
    return output

# item_lookup will run across a list of reference IDs
# and return a data frame with the total amount of items
# required to level everything to maximum

def item_lookup(id_dataframe, entry):
    collection_id = id_dataframe['collection_ids'][entry]
    lookup_id = id_dataframe['lookup_ids'][entry]

    needed_items = []

    ascension_level, \
    skill_level_1, skill_level_2, skill_level_3, \
    append_level_1, append_level_2, append_level_3 = find_levels(collection_id)

    for levels in ascension_level:
        level_items = pd.DataFrame(find_ascension_items(lookup_id, levels))
        needed_items.append(level_items)
        level_qp = pd.DataFrame(find_ascension_qp(lookup_id, levels))
        needed_items.append(level_qp)

    for levels in [skill_level_1, skill_level_2, skill_level_3]:
        skill_items = pd.DataFrame(find_skill_items(lookup_id, 'skillMaterials', levels))
        needed_items.append(skill_items)
        level_qp = pd.DataFrame(find_skill_qp(lookup_id, 'skillMaterials', levels))
        needed_items.append(level_qp)

    for levels in [append_level_1, append_level_2, append_level_3]:
        skill_items = pd.DataFrame(find_skill_items(lookup_id, 'appendSkillMaterials', levels))
        needed_items.append(skill_items)
        level_qp = pd.DataFrame(find_skill_qp(lookup_id, 'appendSkillMaterials', levels))
        needed_items.append(level_qp)

    output = pd.concat(needed_items)

    return output

reference_ids = create_lookup_ids(owned_list)

# create the list of required items

required_items = pd.DataFrame()

for entries in range(1,len(reference_ids)):
    update = item_lookup(reference_ids, entries)
    required_items = pd.concat([required_items, update])

# grouping similar items together, this will return a data frame with the total amount of items needed

total_required_items = required_items.groupby(['ID', 'item']).sum()

'''

with the total_required_items data frame, the next step is to compare it to the user's current inventory
this process is very simple, perform a merge of data frames

'''

# merge data frames

mergedRes = pd.merge(inventory_data, total_required_items, on ='ID', how ="left")

# calculate remaining required

mergedRes['Remaining Needed'] = mergedRes['Total Required'] - mergedRes['Quantity']

excel_writer = pd.ExcelWriter('test3.xlsx', engine='xlsxwriter')
# use to_excel function and specify the sheet_name and index
# to store the dataframe in specified sheet

master_data.to_excel(excel_writer, sheet_name="master_data", index=False)
mergedRes.to_excel(excel_writer, sheet_name="inventory_data", index=False)

excel_writer.save()