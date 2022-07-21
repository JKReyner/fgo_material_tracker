# fgo_material_tracker
A project to create a spreadsheet that keeps track of inventories for the video game Fate/Grand Order.

This is a work in progress and will be updated periodically.

## create_spreadsheet

Initial program for the bulk of the project. It creates a database of the entire set of relevant assets as a spreadsheet.
Within the code, the spreadsheet is exported as 'test.xlsx'

A user will create a spreadsheet using this program and then manually input their user-specific data before proceeding to the next step.

## calculate_needed_items

The user first needs to reference the spreadsheet they filled out previously in the create_spreadsheet section. The program will automatically calculate the total amount of items needed to finish their leveling process, as well as how many they need compared to their current inventory.
The output will be a second .xlsx file with the relevant item information in the second tab.
