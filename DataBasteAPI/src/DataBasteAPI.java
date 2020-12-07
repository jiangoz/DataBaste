import java.sql.Connection;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.*;

public class DataBasteAPI {

  private DBUtils dbu;

  /**
   * Set connection settings
   *
   * @param url
   * @param user
   * @param password
   */
  public void authenticate(String url, String user, String password) {
    this.dbu = new DBUtils(url, user, password);
  }

  /**
   * Close the connection when application finishes
   */
  public void closeConnection() {
    this.dbu.closeConnection();
  }

  /**
   * Abstracted helper method for getting recipe list
   *
   * @param sql given SQL statement
   * @return list of recipes
   */
  private List<Recipe> getRecipeListHelper(String sql) {

    List<Recipe> recipes = new ArrayList<Recipe>();

    try {
      // get connection and initialize statement
      Connection con = dbu.getConnection();
      Statement stmt = con.createStatement();
      ResultSet rs = stmt.executeQuery(sql);
      while (rs.next()) {

        recipes.add(new Recipe(rs.getInt("recipe_id"), rs.getString("recipe_name"),
            rs.getInt("prep_time"), rs.getInt("cook_time"), rs.getInt("total_time"),
            rs.getInt("servings"), rs.getString("image")));

      }
      rs.close();
      stmt.close();
    } catch (SQLException e) {
      System.err.println(e.getMessage());
      e.printStackTrace();
    }

    return recipes;
  }

  /**
   * Get recipes with rating equal or above given value
   *
   * @param rating given rating value
   * @return list of recipes
   */
  public List<Recipe> getRecipesWithRating(int rating) {
    String sql =
        "Select recipe_id, recipe_name, prep_time, cook_time, "
            + "total_time, servings, image, avg(rating)\n"
            + "From recipe\n"
            + "Left join review using (recipe_id)\n"
            + "Group by recipe_id\n"
            + "Having avg(rating) >= " + rating;

    return getRecipeListHelper(sql);
  }

  /**
   * Get recipes that have the given 1 ingredient
   *
   * @param ingredient given ingredient name
   * @return list of recipes
   */
  private List<Recipe> getRecipesWithOneIngredient(String ingredient) {
    String sql = "Select *\n"
        + "From recipe\n"
        + "Left join amount using (recipe_id)\n"
        + "Left join ingredient using (ingredient_id)\n"
        + "Where ingredient_name = " + "\"" + ingredient + "\"";

    return getRecipeListHelper(sql);
  }

  /**
   * Get recipes that have the given ingredient(s). Works for multiple ingredients or just one
   * ingredient.
   *
   * @param ingredients list of ingredient names
   * @return list of recipes
   */
  public List<Recipe> getRecipesWithIngredients(List<String> ingredients) {

    List<Recipe> output = getRecipesWithOneIngredient(ingredients.get(0));

    for (int i = 1; i < ingredients.size(); i++) {
      output.retainAll(getRecipesWithOneIngredient(ingredients.get(i)));
    }

    return output;
  }

  /**
   * Get recipes that contain some given flavor, sorted by flavor score
   *
   * @param flavor given flavor name
   * @return list of recipes, ordered from highest to lowest flavor score
   */
  public List<Recipe> getRecipesWithFlavor(String flavor) {
    String sql = "Select *\n"
        + "From recipe\n"
        + "Left join amount using (recipe_id)\n"
        + "Left join ingredient using (ingredient_id)\n"
        + "Left join composition using (ingredient_id)\n"
        + "Left join molecule using (pubchem_id)\n"
        + "Left join property using (pubchem_id)\n"
        + "Left join flavor using (flavor_id)\n"
        + "Where flavor_name = " + "\"" + flavor + "\"";

    List<Recipe> result = getRecipeListHelper(sql);

    // Get flavor of each recipe and store in HashMap
    HashMap<Recipe, Float> map = new HashMap<Recipe, Float>();
    for (Recipe recipe : result) {
      map.put(recipe, getRecipeFlavorScore(recipe, flavor));
    }

    // Sort HashMap by flavor score value
    Map<Recipe, Float> sortedMap = sortByValue(map);

    // Return final recipe list sorted by flavor score descending
    return new ArrayList<Recipe>(sortedMap.keySet());
  }

  /**
   * Get recipes that are above or equal to given rating AND contains given flavor
   *
   * @param rating
   * @param flavor flavor name
   * @return list of recipes
   */
  public List<Recipe> getRecipesWithRatingFlavor(int rating, String flavor) {
    List<Recipe> output = getRecipesWithRating(rating);
    output.retainAll(getRecipesWithFlavor(flavor));
    return output;
  }

  /**
   * Get recipes that are above or equal to given rating AND contain given ingredient(s)
   *
   * @param rating
   * @param ingredients list of ingredient names
   * @return list of recipes
   */
  public List<Recipe> getRecipesWithRatingIngredient(int rating, List<String> ingredients) {
    List<Recipe> output = getRecipesWithRating(rating);
    output.retainAll(getRecipesWithIngredients(ingredients));
    return output;

  }

  /**
   * Get recipes that contain given ingredient(s) AND contains given flavor
   *
   * @param ingredients list of ingredient names
   * @param flavor      flavor name
   * @return list of recipes
   */
  public List<Recipe> getRecipesWithIngredientFlavor(List<String> ingredients, String flavor) {
    List<Recipe> output = getRecipesWithIngredients(ingredients);
    output.retainAll(getRecipesWithFlavor(flavor));
    return output;
  }

  /**
   * Get recipes that are above/equal to rating AND contain given ingredient(s) AND flavor
   *
   * @param rating
   * @param ingredients list of ingredient names
   * @param flavor      flavor name
   * @return list of recipes
   */
  public List<Recipe> getRecipesWithRatingIngredientFlavor(int rating, List<String> ingredients,
      String flavor) {
    List<Recipe> output = getRecipesWithRating(rating);
    output.retainAll(getRecipesWithIngredients(ingredients));
    output.retainAll(getRecipesWithFlavor(flavor));
    return output;
  }


  /**
   * Get all the possible ingredient names in database
   *
   * @return list of ingredient names
   */
  public List<String> getIngredientNames() {

    String sql = "Select * \n"
        + "From ingredient;";

    List<String> ingredients = new ArrayList<String>();

    try {
      // get connection and initialize statement
      Connection con = dbu.getConnection();
      Statement stmt = con.createStatement();
      ResultSet rs = stmt.executeQuery(sql);
      while (rs.next()) {

        ingredients.add(rs.getString("ingredient_name"));

      }
      rs.close();
      stmt.close();
    } catch (SQLException e) {
      System.err.println(e.getMessage());
      e.printStackTrace();
    }

    return ingredients;
  }

  /**
   * Get all the possible flavor names in database
   *
   * @return list of flavor names
   */
  public List<String> getFlavorNames() {

    String sql = "Select * \n"
        + "From flavor;";

    List<String> flavors = new ArrayList<String>();

    try {
      // get connection and initialize statement
      Connection con = dbu.getConnection();
      Statement stmt = con.createStatement();
      ResultSet rs = stmt.executeQuery(sql);
      while (rs.next()) {

        flavors.add(rs.getString("flavor_name"));

      }
      rs.close();
      stmt.close();
    } catch (SQLException e) {
      System.err.println(e.getMessage());
      e.printStackTrace();
    }

    return flavors;

  }

  /**
   * Get flavor score of given recipe, flavor
   *
   * @param recipe: recipe to get the flavor score of
   * @return flavor score, range 0-1.
   * The percentage of the recipe's ingredients flavors that match the given flavor
   */
  private float getRecipeFlavorScore(Recipe recipe, String flavor) {
    String sql =
        "select ifnull(avg(flavor_percentage.flavor_percentage),0) as 'flavor_score'"
            + "from amount a"
            + "inner join ("
            +   "select"
            +     "i.ingredient_id,"
            +     "specific_flavors.flavor_id,"
            +     "specific_flavors.flavor_count / total_flavors.flavor_count as 'flavor_percentage'"
            +   "from ingredient i"
            +   "inner join ("
            +     "select"
            +       "c1.ingredient_id as 'ingredient_id',"
            +       "f1.flavor_id as 'flavor_id',"
            +       "count(f1.flavor_id) as 'flavor_count'"
            +     "from composition c1"
            +     "inner join property p1 on (c1.pubchem_id = p1.pubchem_id)"
            +     "inner join flavor f1 on (p1.flavor_id = f1.flavor_id)"
            +     "group by c1.ingredient_id, f1.flavor_id"
            +   ") specific_flavors on (i.ingredient_id = specific_flavors.ingredient_id)"
            +   "inner join ("
            +     "select"
            +       "c2.ingredient_id as 'ingredient_id',"
            +       "count(f2.flavor_id) as 'flavor_count'"
            +     "from composition c2"
            +     "inner join property p2 on (c2.pubchem_id = p2.pubchem_id)"
            +     "inner join flavor f2 on (p2.flavor_id = f2.flavor_id)"
            +     "group by c2.ingredient_id"
            +   ") total_flavors on (i.ingredient_id = total_flavors.ingredient_id)"
            + ") flavor_percentage on (a.ingredient_id = flavor_percentage.ingredient_id)"
            + "inner join flavor f on (flavor_percentage.flavor_id = f.flavor_id)"
            + "where a.recipe_id = " + recipe.getRecipeID()
            + "and f.flavor_name = '" + flavor + "'";

    float flavorScore = 0;
    try {
      // get connection and initialize statement
      Connection con = dbu.getConnection();
      Statement stmt = con.createStatement();
      ResultSet rs = stmt.executeQuery(sql);
      // get flavor score from query
      flavorScore = rs.getFloat("flavor_score");
      rs.close();
      stmt.close();
    } catch (SQLException e) {
      System.err.println(e.getMessage());
      e.printStackTrace();
    }

    return flavorScore;
  }

  /**
   * Private function to sort a <Recipe, Float> HashMap by the float values
   *
   * @param hm: HashMap to sort
   * @return New sorted HashMap
   */
  private static HashMap<Recipe, Float> sortByValue(HashMap<Recipe, Float> hm) {
    // Create a list from elements of HashMap
    List<Map.Entry<Recipe, Float> > list = new LinkedList<Map.Entry<Recipe, Float> >(hm.entrySet());

    // Sort the list
    Collections.sort(list, new Comparator<Map.Entry<Recipe, Float> >() {
      public int compare(Map.Entry<Recipe, Float> o1, Map.Entry<Recipe, Float> o2) {
        return (o2.getValue()).compareTo(o1.getValue());
      }
    });

    // put data from sorted list to hashmap
    HashMap<Recipe, Float> temp = new LinkedHashMap<Recipe, Float>();
    for (Map.Entry<Recipe, Float> aa : list) {
      temp.put(aa.getKey(), aa.getValue());
    }
    return temp;
  }




}