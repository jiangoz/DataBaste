import java.sql.*;

public class DBUtils {

  private String url;
  private String user;
  private String password;
  private Connection con = null;

  public DBUtils(String url, String user, String password) {
    this.url = url;
    this.user = user;
    this.password = password;
    this.con = getConnection();
  }

  public Connection getConnection()
  {
    if (con == null) {
      try {
        con = DriverManager.getConnection(url, user, password);
        return con;
      } catch (SQLException e) {
        System.err.println(e.getMessage());
        System.exit(1);
      }
    }

    return con;
  }

  public void closeConnection() {
    try {
      con.close();
    } catch (SQLException e) {
      System.err.println(e.getMessage());
      e.printStackTrace();
    }
  }

  public int insertOneRecord(String insertSQL)
  {
    // System.out.println("INSERT STATEMENT: "+insertSQL);
    int key = -1;
    try {

      // get connection and initialize statement
      Connection con = getConnection();
      Statement stmt = con.createStatement();

      stmt.executeUpdate(insertSQL, Statement.RETURN_GENERATED_KEYS);

      // extract auto-incremented ID
      ResultSet rs = stmt.getGeneratedKeys();
      if (rs.next()) key = rs.getInt(1);

      // Cleanup
      rs.close();
      stmt.close();

    } catch (SQLException e) {
      System.err.println("ERROR: Could not insert record: "+insertSQL);
      System.err.println(e.getMessage());
      e.printStackTrace();
    }
    return key;
  }


}
