<html>
<body>

<?php

// let's establish a connection.
$conn = new mysqli("localhost", "", "", "test");
if ($conn->connect_error) {
  echo "There is a problem connecting to DB guy (or girl).";
} else {

  // once we've connected we'll retrieve the data from the DB.
  $sql = "SELECT name, quest, color FROM survey";
  $result = $conn->query($sql);
  
  // the num_rows property identifies how many records were returned by the query.
  if ($result->num_rows > 0) {
  
    // for each result, we'll need to retrieve the underlying values.
    // when there are no more records, this will return null.
    while ($row = $result->fetch_assoc()) {
    
      // we'll build some HTML out of the record.
      echo "Your name is: " . $row['name'] . "<br>";
      echo "Your quest is: " . $row['quest'] . "<br>";
	  echo "Your favorite color is: " . $row['color'] . "<br>";

      echo "<br><br><br>";
    }
  } else {
    echo "There are no results.";
  }
}

$conn->close();

?>
<a href="assignment4.php">Fill out a new form</a>

</body>
</html>