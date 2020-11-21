
# Imports
import requests

# MARGARET TODO: Add constants and files as necessary to global
# Constants
INGREDIENT_URL = 'https://cosylab.iiitd.edu.in/flavordb/entity_details?id='
INGREDIENT_FILE = 'csv/ingredient.csv'
CATEGORY_FILE = 'csv/category.csv'

# Open files for reading
ingredient_file_raw = open(INGREDIENT_FILE, 'r')
ingredient_file = ingredient_file_raw.readlines()
ingredient_file_array = [line.split(',') for line in ingredient_file]
ingredient_name_array = [line[1] for line in ingredient_file_array]

category_file_raw = open(CATEGORY_FILE, 'r')
category_file = category_file_raw.readlines()
category_file_array = [line.split(',') for line in category_file]
category_name_array = [line[1][:-1] for line in category_file_array]  # The [:-1] removes new line character

# Loop through all ingredient IDs starting with ID user inputs
ingredient_counter = eval(input('Starting FlavorDB Ingredient ID (0 if unknown): '))

while True:
	
	# Get HTML text from FlavorDB ingredients
	html_text = None
	while html_text is None:
		try:
			html_text = requests.get(INGREDIENT_URL + str(ingredient_counter)).text
		except:  # There could be a number of connection problems, so we're not going to handle each individually
			pass

	# MARGARET TODO: Uncomment for raw HTML (remove when done)
	# print(html_text)

	# Parse out synonyms from HTML
	name_start_text = '<h5>Synonyms: <strong><span class="text-capitalize">'
	name_pos = html_text.find(name_start_text)
	name_pos_end = html_text.find('</span></strong> </h5>', name_pos)
	if name_pos == -1 or name_pos_end == -1:
		if html_text.find('Not Found') == -1:
			print('Ingredient ' + str(ingredient_counter) + ' format issue')  # There is an issue with an unknown format
			continue  # Continue for loop, but stop this iteration since there was an issue
		else:
			break  # Stop while loop for the first page not found since it is an invalid ID
	name_text_array = html_text[name_pos + len(name_start_text):name_pos_end].split(', ')
	if name_text_array[0] == '':  # Empty name text array if no synonyms were found
		name_text_array = []

	# Parse out primary name from HTML and check if already in synonyms
	name_start_text = '<h1 class="text-primary text-capitalize">'
	name_pos = html_text.find(name_start_text)
	name_pos_end = html_text.find('</h1>', name_pos)
	if name_pos == -1 or name_pos_end == -1:
		print('Ingredient ' + str(ingredient_counter) + ' format issue')  # There is an issue with an unknown format
		continue  # Continue for loop, but stop this iteration since there was an issue
	name_text = html_text[name_pos + len(name_start_text):name_pos_end]
	if name_text not in name_text_array:
		name_text_array.append(name_text)
	name_text_array = [name.lower() for name in name_text_array]  # Ensure all ingredient names are lowercase

	# Check which existing ingredients match this Flavor DB ingredient
	ingredient_ids = []  # Stays as string since there's no reason to convert to integer
	for name in name_text_array:
		if name in ingredient_name_array:  # Check if normal name is already in ingredients
			ingredient_ids.append(ingredient_file_array[ingredient_name_array.index(name)][0])
		if name[-1] == 's':
			if name[:-1] in ingredient_name_array:  # Check if singular version of ingredient in ingredients
				ingredient_ids.append(ingredient_file_array[ingredient_name_array.index(name[:-1])][0])
		else:
			if name + 's' in ingredient_name_array:  # Check if plural version of ingredient in ingredients
				ingredient_ids.append(ingredient_file_array[ingredient_name_array.index(name + 's')][0])

	# Parse out food category from HTML
	category_start_text = '<h5>Category: <strong><span class="text-capitalize">'
	category_pos = html_text.find(category_start_text)
	category_pos_end = html_text.find('</span></strong> </h5>', category_pos)
	if category_pos == -1 or category_pos_end == -1:
		print('Ingredient ' + str(ingredient_counter) + ' format issue')  # There is an issue with an unknown format
		continue  # Stop iteration of this ingredient because no category can even be filled in
	category_text = html_text[category_pos + len(category_start_text):category_pos_end]

	# Add category to category file if necessary and record category id
	if category_text in category_name_array:
		category_id = category_file_array[category_name_array.index(category_text)][0]
	else:
		category_id = str(len(category_file_array) - 1)
		category_file.append(category_id + ',' + category_text + '\n')
		category_file_write = open(CATEGORY_FILE, 'w')
		for line in category_file:
			category_file_write.write(line)
		category_file_write.close()
		category_file_raw.close()
		category_file_raw = open(CATEGORY_FILE, 'r')
		category_file = category_file_raw.readlines()
		category_file_array = [line.split(',') for line in category_file]
		category_name_array = [line[1] for line in category_file_array]

	# Add category id to appropriate rows in ingredient file
	for ingredient in range(len(ingredient_file_array)):
		if ingredient_file_array[ingredient][0] in ingredient_ids:
			ingredient_file_array[ingredient][-1] = category_id
			ingredient_file[ingredient] = ingredient_file_array[ingredient][0] + ',' + \
			        ingredient_file_array[ingredient][1] + ',' + ingredient_file_array[ingredient][2] + '\n'
	ingredient_file_write = open(INGREDIENT_FILE, 'w')
	for line in ingredient_file:
		ingredient_file_write.write(line)
	ingredient_file_write.close()
	ingredient_file_raw.close()
	ingredient_file_raw = open(INGREDIENT_FILE, 'r')
	ingredient_file = ingredient_file_raw.readlines()
	ingredient_file_array = [line.split(',') for line in ingredient_file]
	ingredient_name_array = [line[1] for line in ingredient_file_array]

	# MARGARET TODO: Add code for composition, molecule, property, and flavor tables below this comment

	# Print to console that the current ingredient's parsing has finished
	print('Ingredient ' + str(ingredient_counter) + ' parsing complete')

	# Increase ingredient counter for next loop
	ingredient_counter += 1

	# MARGARET TODO: Break is to test on 1 web page without looping through them all. Remove when done
	break
