
# Imports
import json
import requests
import re
import unicodedata

# Constants
ALLRECIPES_URL = 'http://allrecipes.com/recipe/'
AMOUNTS_FILE = 'csv/amount.csv'
INGREDIENT_FILE = 'csv/ingredient.csv'
RECIPE_FILE = 'csv/recipes_final.csv'

# Get list of recipe ids from file
recipe_file = open(RECIPE_FILE, 'r').readlines()[1:]  # Ignore title line when reading
recipe_id_list = [eval(line.split(',')[-2]) for line in recipe_file]

# Get list of current ingredient names from ingredient csv
ingredient_file = open(INGREDIENT_FILE, 'r').readlines()
ingredient_name_list = [line.split(',')[1] for line in ingredient_file[1:]]

# Load current amount file for updating and take out recipes from id list whose ids have already been recorded
amount_file = open(AMOUNTS_FILE, 'r').readlines()
for line in amount_file[1:]:
	recipe_id = eval(line.split(',')[2])
	if recipe_id in recipe_id_list:
		recipe_id_list.remove(recipe_id)
print(recipe_id_list)

for recipe_id in recipe_id_list:
	# Get HTML text from allrecipes
	html_text = None
	while html_text is None:
		try:
			html_text = requests.get(ALLRECIPES_URL + str(recipe_id)).text
		except:
			pass

	# Parse out JSON in HTML and turn into JSON object
	json_text_start = 'script type="application/ld+json">'
	pos = html_text.find(json_text_start)
	if pos == -1:
		# Print any unfilled recipes
		print('Unfilled Recipe (format incompatible): ' + str(recipe_id))
	else:
		pos_end = html_text.find('</script>', pos)
		json_text = html_text[pos + len(json_text_start):pos_end]
		json_data = json.loads(json_text)

		# Parse out ingredient list in HTML and put into array ingredient_list
		ingredient_list_text_start = 'data-recipe_food_main_ingredients="'
		pos = html_text.find(ingredient_list_text_start)
		pos_end = html_text.find('"', pos + len(ingredient_list_text_start))
		ingredient_text = html_text[pos + len(ingredient_list_text_start):pos_end]
		ingredient_raw = ingredient_text.split(',')  # Get all items in ingredient list
		ingredient_list = ingredient_raw.copy()
		for ingredient in ingredient_raw:  # Ingredients starting with space were continuation of previous ingredient
			ingredient_list[ingredient_list.index(ingredient)] = re.sub(r' \(.*\)', '', ingredient)
			if ingredient[0] == ' ' and ingredient in ingredient_list:
				ingredient_list.remove(ingredient)

		# Find ingredient data in JSON
		ingredient_data = json_data[1].get('recipeIngredient')
		if ingredient_data is None:  # Only continue if there wasn't a problem finding the ingredient data
			# Print any unfilled recipes
			print('Unfilled Recipe (temp JSON request problem): ' + str(recipe_id))
		else:
			# Loop through ingredients in ingredient data, splitting into amounts, units, and ingredients
			amount_list = []
			unit_list = []
			for ingredient in range(len(ingredient_data)):
				# Remove anything in parentheses since they are just user notes
				ing_str = re.sub(r'\([^)]*\)', '', ingredient_data[ingredient])

				# Remove anything after a comma since they are just notes for the user
				ing_str = re.sub(r',.*', '', ing_str)

				# Turn any vulgar fractions (such as unicode ½) into numeric representations in string
				new_ing_str = ''
				for i in range(len(ing_str)):
					if ing_str[i].isdigit():
						new_ing_str += ing_str[i]
					else:
						new_ing_str += str(unicodedata.numeric(ing_str[i], ing_str[i]))

				# Turn group of characters before first letter or dash into an amount number
				amount_str = re.search("^(.*?)[a-zA-Z].*", new_ing_str)
				if amount_str is None:
					amount_str = ''
				else:
					amount_str = amount_str.group(1)
				amount_str = amount_str.split()  # Split by space to get amounts to add (ex. 1.0 0.5 should be 1.5 in end)
				amount = 0
				# Add elements of split array to get final amount
				for num in amount_str:
					try:
						amount += float(num)
					except ValueError:
						pass
				amount_list.append(amount)

				# Find units by finding first letter and taking string until ingredient
				start_pos = re.search('([a-zA-Z])', new_ing_str)
				start_pos = start_pos.start(1)
				end_pos = new_ing_str.find(' ' + ingredient_list[ingredient])
				if end_pos == -1:  # If the ingredient wasn't found, assume there's no unit
					unit_str = ''
				else:
					unit_str = new_ing_str[start_pos:end_pos]
				unit_list.append(unit_str)

			# Add to ingredients and amounts tables if not already there
			for ingredient in range(len(ingredient_data)):
				# Add to ingredient table if ingredient not already in the table
				ingredient_id = 0
				if ingredient_list[ingredient] not in ingredient_name_list:
					ingredient_name_list.append(ingredient_list[ingredient])
					ingredient_id = len(ingredient_name_list) - 1
					# Add to ingredient file
					ingredient_file_write = open(INGREDIENT_FILE, 'a')
					ingredient_file_write.write(str(ingredient_id) + ',' + ingredient_list[ingredient] + ',-1\n')
					ingredient_file_write.close()
				else:
					ingredient_id = ingredient_name_list.index(ingredient_list[ingredient])
				# Add to amount file
				amount_file_write = open(AMOUNTS_FILE, 'a')
				amount_file_write.write(str(amount_list[ingredient]) + ',' + str(unit_list[ingredient]) + ',' +
				                        str(recipe_id) + ',' + str(ingredient_id) + '\n')
				amount_file_write.close()
	print('Recipe ' + str(recipe_id_list.index(recipe_id) + 1) + '/' + str(len(recipe_id_list)) + ' complete')