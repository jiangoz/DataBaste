import pandas
import requests

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

def convert_time(time):
    if (time == "X"):
        time_new = "NULL"
    else:
        time_new = convert_to_mins(time)
    return time_new

# get the serving size for the recipe
def get_servings(id):
    url = "https://www.allrecipes.com/recipe/" + str(id)
    res = requests.get(url)
    if(res.status_code == 200):
        data = res.text
        pos = data.find("data-servings=")
        if(pos == -1):
            return "NULL"
        pos += 14  # account for the length of "data-servings="
        end_pos = data.find("data-recipe-id=")
        if(end_pos == -1):
            end_pos = pos+10

        servings = data[pos:end_pos].strip()
        print(str(id) + ": " + servings)
        return servings

    return "NULL"


df = pandas.read_csv('csv/recipes_init.csv', sep=';')

# remove unnecessary columns
del df['Review Count']
del df['Recipe Photo']
del df['Author']
del df['Ingredients']
del df['Directions']

# convert the prep time, cook time, and total time to the correct format
df['Prepare Time'] = df['Prepare Time'].apply(convert_time)
df['Cook Time'] = df['Cook Time'].apply(convert_time)
df['Total Time'] = df['Total Time'].apply(convert_time)
df["Servings"] = df["RecipeID"].apply(get_servings)


df.to_csv('recipes_modified.csv')
