package DataBasteAPI.src;

import java.sql.Connection;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.ArrayList;
import java.util.List;

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
    String sql = "Select *, avg(rating)\n"
        + "From recipe\n"
        + "Left join review using (recipe_id)\n"
        + "Group by recipe_id\n"
        + "Having avg(rating) >= " + rating;

    return getRecipeListHelper(sql);
  }

  /**
   * Get recipes that have the given ingredient
   *
   * @param ingredient given ingredient name
   * @return list of recipes
   */
  public List<Recipe> getRecipesWithIngredient(String ingredient) {
    String sql = "Select *\n"
        + "From recipe\n"
        + "Left join amount using (recipe_id)\n"
        + "Left join ingredient using (ingredient_id)\n"
        + "Where ingredient_name = " + ingredient;

    return getRecipeListHelper(sql);
  }

  /**
   * Get recipes that contain some given flavor
   *
   * @param flavor given flavor name
   * @return list of recipes
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
        + "Where flavor_name = " + flavor;

    return getRecipeListHelper(sql);
  }

  /**
   * Get recipes that are above or equal to given rating AND contains given flavor
   *
   * @param rating
   * @param flavor
   * @return list of recipes
   */
  public List<Recipe> getRecipesWithRatingFlavor(int rating, String flavor) {
    List<Recipe> output = getRecipesWithRating(rating);
    output.retainAll(getRecipesWithFlavor(flavor));
    return output;
  }

  /**
   * Get recipes that are above or equal to given rating AND contains given ingredient
   *
   * @param rating
   * @param ingredient
   * @return list of recipes
   */
  public List<Recipe> getRecipesWithRatingIngredient(int rating, String ingredient) {
    List<Recipe> output = getRecipesWithRating(rating);
    output.retainAll(getRecipesWithIngredient(ingredient));
    return output;

  }

  /**
   * Get recipes that contains given ingredient AND contains given flavor
   *
   * @param ingredient
   * @param flavor
   * @return list of recipes
   */
  public List<Recipe> getRecipesWithIngredientFlavor(String ingredient, String flavor) {
    List<Recipe> output = getRecipesWithIngredient(ingredient);
    output.retainAll(getRecipesWithFlavor(flavor));
    return output;
  }

  /**
   * Get recipes that are above/equal to rating AND contains given ingredient AND flavor
   *
   * @param rating
   * @param ingredient
   * @param flavor
   * @return list of recipes
   */
  public List<Recipe> getRecipesWithRatingIngredientFlavor(int rating, String ingredient,
      String flavor) {
    List<Recipe> output = getRecipesWithRating(rating);
    output.retainAll(getRecipesWithIngredient(ingredient));
    output.retainAll(getRecipesWithFlavor(flavor));
    return output;
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


}