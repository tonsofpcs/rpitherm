<?php
$setwhat = htmlspecialchars($_GET["set"]);

switch ($setwhat) {
   case "back":
     header ( 'refresh: 2; url=/index.php' );
     break;
   case "occupied":
     header ( 'refresh: 2; url=/index.php' );
     break;
   case "hot":
     header ( 'refresh: 2; url=/index.php' );
     break;
   case "vaca":
     header ( 'refresh: 2; url=/index.php' );
     break;
}
?>
<html>
<head>
<!--<?=$setwhat?>-->
<title>Home Thermostat!</title>
<meta name="viewport" content="width=device-width">
<link rel="stylesheet" href="/screen.css" type="text/css" media="Screen" />
<link rel="stylesheet" href="/mobile.css" type="text/css" media="handheld" />
</head>
<nav id="nav-wrap">

	<div id="menu-icon">RaspberryPi Thermostat</div>

<p>
<?php
switch ($setwhat) {
   case "back":
     exec("/home/pi/thermostat/setback.sh");
     echo "BACK<br />";
     break;
   case "occupied":
     exec("/home/pi/thermostat/setoccupied.sh");
     echo "OCCUPIED<br />";
     break;
   case "hot":
     exec("/home/pi/thermostat/sethot.sh");
     echo "Hot<br />";
     break;
   case "vaca":
     exec("/home/pi/thermostat/setvaca.sh");
     echo "Vacation<br />";
     break;
   case "up":
     echo "UP<br />";
    // insert code for up 
     break;
   case "down":
     echo "DOWN<br />";
    // insert code for down
     break;
}
?>
<?php
$tempfile = file("/sys/bus/w1/devices/28-0000055d5974/w1_slave");
$tempsplit = (split('t=',$tempfile[1])[1]);
// echo print_r($tempsplit)."<br />";
$tempC = $tempsplit / 1000;
echo $tempC."C<br />";
$tempF = ($tempC * 1.8 + 32);
echo $tempF."F";
?>
</p>
	<ul id="nav">
		<li><a href="?set=back">Set-back</a></li>
		<li><a href="?set=occupied">Set Occupied</a></li>
<!--		<li><a href="?set=up">TEMP UP</a></li>
		<li><a href="?set=down">TEMP DOWN</a></li>//-->
		<li><a href="hour.png">Last Hour</a></li>
		<li><a href="day.png">Last Day</a></li>
		<li><a href="week.png">Last Week</a></li>
		<li><a href="?set=hot">Set HOT Mode</a></li>
		<li><a href="?set=vaca">Set Vacation Mode</a></li>
	</ul>
</nav>
</body>
</html>
