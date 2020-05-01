import json
import os
import sys

from slpp import slpp as lua

# run this script from the factorio-clustering folder root!

# get all files in the input directory
filenames = [file.path for file in os.scandir(os.path.join(
    os.getcwd(), 'data_extractor', 'input')) if file.is_file()]

# iterate through all files and process their contents
all_ingredients = []
for filename in filenames:
    # read the file in a safe way ('with' ensures that it will be closed)
    with open(filename, 'r') as file:
        contents = file.read()

    # strip unnecessary strings which would obstruct Lua decoding
    contents = contents.replace('data:extend', '').replace(
        '(', '').replace(')', '')

    # convert from Lua format into Python dictionary
    recipes = lua.decode(contents)

    # iterate through the recipes and convert them into a common format
    for recipe in recipes:
        recipe_name = recipe.get('name', None)
        if recipe_name is None:
            print(f'Recipe has no name: {recipe}')
            continue

        ingredients = recipe.get('ingredients', None)

        # for certain recipes, ingredients is not in the top level, but within the 'normal' node
        if ingredients is None:
            normal = recipe.get('normal', None)
            if normal is not None:
                ingredients = normal.get('ingredients', None)

        if ingredients is None:
            print(f'Recipe has no ingredients: {recipe_name}')
            continue

        for ingredient in ingredients:
            # most ingredients are simply arrays
            # e.g. ['cannon-shell', 1]
            if isinstance(ingredient, list):
                if len(ingredient) >= 2:
                    all_ingredients.append({
                        'recipe_name': recipe_name,
                        'ingredient_name': ingredient[0],
                        'ingredient_amount': ingredient[1]
                    })
                else:
                    print(
                        f'Recipe has ingredient which is an array but has <2 items: {recipe_name}')
            # other ingredients are dictionaries
            # e.g. {'type': 'fluid', 'name': 'crude-oil', 'amount': 100}
            else:
                if 'name' in ingredient and 'amount' in ingredient:
                    all_ingredients.append({
                        'recipe_name': recipe_name,
                        'ingredient_name': ingredient['name'],
                        'ingredient_amount': ingredient['amount']
                    })
                else:
                    print(
                        f'Recipe has ingredient is a dict but lacks the name or amount property: {recipe_name}')

with open('ingredients.json', 'w') as file:
    file.write(json.dumps(all_ingredients, indent=2))

print(f'Wrote {len(all_ingredients)} ingredients from {len(filenames)} files into ingredients.json.')
