
# Imports
import requests
from bs4 import BeautifulSoup

# Constants
INGREDIENT_URL = 'https://cosylab.iiitd.edu.in/flavordb/entity_details?id='
INGREDIENT_FILE = 'csv/ingredient.csv'
CATEGORY_FILE = 'csv/category.csv'
MOLECULE_FILE = 'csv/molecule.csv'
FLAVOR_FILE = 'csv/flavor.csv'
PROPERTY_FILE = 'csv/property.csv'
COMPOSITION_FILE = 'csv/composition.csv'


# Open files for reading
ingredient_file_raw = open(INGREDIENT_FILE, 'r')
ingredient_file = ingredient_file_raw.readlines()
ingredient_file_array = [line.split(',') for line in ingredient_file]
ingredient_name_array = [line[1] for line in ingredient_file_array]

category_file_raw = open(CATEGORY_FILE, 'r')
category_file = category_file_raw.readlines()
category_file_array = [line.split(',') for line in category_file]
category_name_array = [line[1][:-1] for line in category_file_array]  # The [:-1] removes new line character

molecule_file_raw = open(MOLECULE_FILE, 'r')
molecule_file = molecule_file_raw.readlines()
molecule_file_array = [line.split(',') for line in molecule_file]
molecule_id_array = [line[0] for line in molecule_file_array]

flavor_file_raw = open(FLAVOR_FILE, 'r')
flavor_file = flavor_file_raw.readlines()
flavor_file_array = [line.split(',') for line in flavor_file]
flavor_name_array = [line[1][:-1] for line in flavor_file_array]

property_file_raw = open(PROPERTY_FILE, 'r')
property_file = property_file_raw.readlines()
property_file_array = [line.split(',') for line in property_file]
property_id_array = [line[0] for line in property_file_array]

composition_file_raw = open(COMPOSITION_FILE, 'r')
composition_file = composition_file_raw.readlines()
composition_file_array = [line.split(',') for line in composition_file]
composition_id_array = [line[0] for line in composition_file_array]


# Loop through all ingredient IDs starting with ID user inputs
ingredient_counter = eval(input('Starting FlavorDB Ingredient ID (0 if unknown): '))
skipped = []

while True:
	
	# Get HTML text from FlavorDB ingredients
	html_text = None
	while html_text is None:
		try:
			html_text = requests.get(INGREDIENT_URL + str(ingredient_counter)).text
		except:  # There could be a number of connection problems, so we're not going to handle each individually
			pass


	# Parse out synonyms from HTML
	name_start_text = '<h5>Synonyms: <strong><span class="text-capitalize">'
	name_pos = html_text.find(name_start_text)
	name_pos_end = html_text.find('</span></strong> </h5>', name_pos)
	if name_pos == -1 or name_pos_end == -1:
		if html_text.find('Not Found') == -1:
			print('Ingredient ' + str(ingredient_counter) + ' format issue')  # There is an issue with an unknown format
			continue  # Continue for loop, but stop this iteration since there was an issue
		else:
			skipped.append(ingredient_counter)
			if ingredient_counter == 1000:	#no more webpages after this so break
				break
			ingredient_counter += 1
			continue
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
		if len(name) > 1 and name[-1] == 's':
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
		category_name_array = [line[1][:-1] for line in category_file_array]

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


	if len(ingredient_ids) > 0:

		soup = BeautifulSoup(html_text, 'html.parser')
		soup.prettify()

		# get the molecule table
		table = soup.find('table', {"id": "molecules"}).tbody
		rows = table.findAll(lambda tag: tag.name == 'tr')
		molecules = []	# keeps track of the molecules in this ingredient
		added_molecule = False 	# keeps track if any new entries to the molecule table were added

		# go through each table entry and extract necessary information
		for row in rows:
			cells = row.find_all("td")
			text = row.text
			info = text.split("\n")

			# get the name of the molecule, pubchem id, and list of flavors
			try:
				name = info[1]
				pubchem_id = info[2]
				flavors = info[3]
			except:
				pass #error extracting data- handle on a case by case basis


			molecules.append(pubchem_id)

			# add the molecule to the molecules table if not already there
			if not (pubchem_id in molecule_id_array):
				added_molecule = True
				name = name.replace(',', ';')	#replace commas with semicolons
				molecule_file.append(pubchem_id + ',' + name + '\n')

			# determine if properties need to be added for a molecule
			add_properties = not pubchem_id in property_id_array

			flavors = flavors.split(",")

			# add to the property and flavor csvs
			num_flavors_added = 0
			for flavor in flavors:
				flavor = flavor.strip().lower()

				flavor_id = -1
				# add each flavor to the flavor table if its not already there
				if not (flavor in flavor_name_array):
					flavor_id = str(len(flavor_file_array) - 1 + num_flavors_added)
					flavor_file.append(flavor_id + ',' + flavor + '\n')
					num_flavors_added += 1
				else:
					# get the flavor id already in the csv
					flavor_id = flavor_file_array[flavor_name_array.index(flavor)][0]

				# add the flavor and molecule to the property table, if not already there
				if add_properties:
					property_added = True
					if flavor_id != -1:
						property_file.append(pubchem_id + ',' + flavor_id + '\n')
					else:
						print("Issue adding flavor " + flavor + " for molecule " + pubchem_id + " to property table")

			# a new flavor was added onto the flavor file, so save the write
			if num_flavors_added > 0:
				flavor_file_write = open(FLAVOR_FILE, 'w')
				for line in flavor_file:
					flavor_file_write.write(line)
				flavor_file_write.close()
				flavor_file_raw.close()
				flavor_file_raw = open(FLAVOR_FILE, 'r')
				flavor_file = flavor_file_raw.readlines()
				flavor_file_array = [line.split(',') for line in flavor_file]
				flavor_name_array = [line[1][:-1] for line in flavor_file_array]

			# If properties were added, save the write
			if add_properties:
				property_file_write = open(PROPERTY_FILE, 'w')
				for line in property_file:
					property_file_write.write(line)
				property_file_write.close()
				property_file_raw.close()
				property_file_raw = open(PROPERTY_FILE, 'r')
				property_file = property_file_raw.readlines()
				property_file_array = [line.split(',') for line in property_file]
				property_id_array = [line[0] for line in property_file_array]

		# new molecules were added to the molecule file, so save the write
		if added_molecule:
			molecule_file_write = open(MOLECULE_FILE, 'w')
			for line in molecule_file:
				molecule_file_write.write(line)
			molecule_file_write.close()
			molecule_file_raw.close()
			molecule_file_raw = open(MOLECULE_FILE, 'r')
			molecule_file = molecule_file_raw.readlines()
			molecule_file_array = [line.split(',') for line in molecule_file]
			molecule_id_array = [line[0] for line in molecule_file_array]

		# add the ingredient and the molecules its comprised of to the composition table
		added_comp = False 	#represents if anything was added to the composition table this round
		for ingredient_id in ingredient_ids:
			if ingredient_id not in composition_id_array:
				for molec in molecules:
					composition_file.append(ingredient_id + ',' + molec + '\n')
					added_comp = True

		# if compositions were added, save the write
		if added_comp:
			composition_file_write = open(COMPOSITION_FILE, 'w')
			for line in composition_file:
				composition_file_write.write(line)
			composition_file_write.close()
			composition_file_raw.close()
			composition_file_raw = open(COMPOSITION_FILE, 'r')
			composition_file = composition_file_raw.readlines()
			composition_file_array = [line.split(',') for line in composition_file]
			composition_id_array = [line[0] for line in composition_file_array]

	# Print to console that the current ingredient's parsing has finished
	print('Ingredient ' + str(ingredient_counter) + ' parsing complete')

	# Increase ingredient counter for next loop
	ingredient_counter += 1


print("Skipped: " + str(skipped))