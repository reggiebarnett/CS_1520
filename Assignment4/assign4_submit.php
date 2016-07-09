<html>
<body>

<?php
session_start();

function log_error($message) {
  if (empty($_SESSION['message_error'])) {
    $_SESSION['message_error'] = '';
  }
  $_SESSION['message_error'] .= $message . "<br>";
}

# We'll clear the errors first.
$_SESSION['message_error'] = '';

# This will set the variables to the posted parameters.
$name = $_POST['name'];
$quest = $_POST['quest'];
$color = $_POST['color'];

// we'll connect to the database here.
$conn = mysqli_connect("localhost","","", "test");

if ($conn->connect_error) {
  log_error("can't connect to db. abandon all hope ye who enter here");
} else {

  $statement = $conn->prepare("INSERT INTO survey (name, quest, color) VALUES (?,?,?)");

  $statement->bind_param("sss", $a, $b, $c);
  
  $a = $name;
  $b = $quest;
  $c = $color;
  
  $statement->execute();
}

$conn->close();

// If there are no errors, we'll go back to the "show messages" screen.
if (!empty($_SESSION['message_error']) and strlen($_SESSION['message_error']) > 0) {
  header('location:assignment4.php');
} else {
  header('location:assign4_show.php');
}
?>

</body>
</html>