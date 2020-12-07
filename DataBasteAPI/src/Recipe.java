public class Recipe {

  private int recipeID;
  private String recipeName;
  private int prepTime;
  private int cookTime;
  private int totalTime;
  private int servings;
  private String imageURL;

  public Recipe(int recipeID, String recipeName, int prepTime, int cookTime, int totalTime,
      int servings, String imageURL) {
    this.recipeID = recipeID;
    this.recipeName = recipeName;
    this.prepTime = prepTime;
    this.cookTime = cookTime;
    this.totalTime = totalTime;
    this.servings = servings;
    this.imageURL = imageURL;
  }

  public int getRecipeID() {
    return recipeID;
  }

  public String getRecipeName() {
    return recipeName;
  }

  public int getPrepTime() {
    return prepTime;
  }

  public int getCookTime() {
    return cookTime;
  }

  public int getTotalTime() {
    return totalTime;
  }

  public int getServings() {
    return servings;
  }

  public String getImageURL() {
    return imageURL;
  }

  @Override
  public boolean equals(Object o) {
    if (this == o) {
      return true;
    }
    if (o == null || getClass() != o.getClass()) {
      return false;
    }

    Recipe recipe = (Recipe) o;

    return recipeID == recipe.recipeID;
  }

  @Override
  public int hashCode() {
    return recipeID;
  }
}