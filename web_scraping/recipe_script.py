import pandas
import requests

ALL_RECIPES_URL = "https://www.allrecipes.com/recipe/"
SERVING_STRING1 = "data-servings="
SERVING_STRING2 = '<meta id="metaRecipeServings" itemprop="recipeYield" content="'
INPUT_FILE = 'csv/recipes_init.csv'
OUTPUT_PATH = 'csv/recipes_final.csv'
CREATE = True   #represents if the servings col is being created or modified

# converts a given time string into minutes
# inputs are in the form # [m,h,d] ...
# where m represents minutes, h represents hours, and d represents days
def convert_to_mins(time):
    components = time.split()
    total = 0

    # guaranteed times come in pairs
    for i in range(len(components)-1):
        num = components[i]
        unit = components[i+1]
        if (unit == 'm'):
            total += int(num)
        if (unit == 'h'):
            total += int(num)*60
        if (unit == 'd'):
            total += int(num)*1440

        i = i + 1
    return total

# if in improper format, convert the time to minutes
def convert_time(time):
    if (time == "X"):
        time_new = "NULL"
    elif(('m' in str(time)) or ('h' in str(time)) or ('d' in str(time))):
        time_new = convert_to_mins(time)
        return time_new
    else:
        return time

# get the serving size for the recipe
def get_servings(row):
    # only get the serving size if it is not already filled in
    if CREATE or pandas.isna(row["Servings"]):
        id = row['RecipeID']
        url = ALL_RECIPES_URL + str(id)
        res = requests.get(url)
        if(res.status_code == 200):
            data = res.text
            pos = data.find(SERVING_STRING1)
            if(pos != -1):
                pos += len(SERVING_STRING1)  # account for the length of "data-servings="
                end_pos = data.find("data-recipe-id=")
                if(end_pos == -1):
                    end_pos = pos+10

                servings = data[pos:end_pos].strip()
                return servings

            #different webpage format, extract servings by a different string
            pos = data.find(SERVING_STRING2)
            if (pos != -1):
                pos_end = data.find('">', pos)
                servings = data[pos + len(SERVING_STRING2): pos_end]
                return servings

    return row["Servings"]

# if error, remove the delimiter field -> depends on input file
df = pandas.read_csv(INPUT_FILE, delimiter=';')

# remove unnecessary columns
df = df.drop(['Review Count','Recipe Photo','Author','Ingredients', 'Directions'], axis=1, errors='ignore')

CREATE = not("Servings" in df.keys())

# convert the prep time, cook time, and total time to the correct format
df['Prepare Time'] = df['Prepare Time'].apply(convert_time)
df['Cook Time'] = df['Cook Time'].apply(convert_time)
df['Total Time'] = df['Total Time'].apply(convert_time)
df["Servings"] = df.apply(lambda row: get_servings(row), axis=1)


df.to_csv(OUTPUT_PATH)
