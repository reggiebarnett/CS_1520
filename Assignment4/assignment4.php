<html>
<body>

<?php
session_start();
// if there is anything in the session field, we'll display it as an error.
if (array_key_exists('message_error', $_SESSION)) {
  if (!empty($_SESSION['message_error']) or strlen($_SESSION['message_error']) > 0) {
    echo $_SESSION['message_error'];
  }
}

function writeFormField($id, $label) {
  echo "<label for=\"$id\">$label</label><br>";
  echo "<input type=\"text\" name=\"$id\" id=\"$id\" required=\"true\">";
  echo "<br><br><br>";
}
?>  

<h1>Fill out this form!</h1>
<form method="post" action="assign4_submit.php">

<?php 
writeFormField('name', 'What is your name: ');
writeFormField('quest', 'What is your quest: ');
writeFormField('color', 'What is your favorite color: ');
?>

<input type="submit">
</form>

</body>
</html>