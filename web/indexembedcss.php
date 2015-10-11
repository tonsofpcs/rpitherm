<?php
$setwhat = htmlspecialchars($_GET["set"]);

switch ($setwhat) {
   case "back":
     header ( 'refresh: 2; url=/index.php' );
     break;
   case "occupied":
     header ( 'refresh: 2; url=/index.php' );
     break;
}
?>
<html>
<head>
<!--<?=$setwhat?>-->
<title>Thermostat!</title>
<link rel="stylesheet" href="/screen.css" type="text/css" media="Screen" />
<link rel="stylesheet" href="/mobile.css" type="text/css" media="handheld" />
<style>

#menu-icon {font-size: 20pt;}
body {background: #e6e0d7; width: 100%; }
#nav-wrap {background: #e6e0d7; margin: 0 auto; padding: 1em 0 0 0; font-family: sans; font-size: 20pt;}

#nav {list-style: none; padding: 0; margin: 0 auto; width: 90%; font-size: 0.8em;background: #e6e0d7;}
#nav li {display: block; float: left; width: 90%; margin: 0; padding: 0;}
#nav li a {display: block; width: 100%; padding: 0.5em; border-width: 1px; border-color: #ffe #aaab9c #ccc #fff; border-style: solid; color: #555; text-decoration: none; background: #e6e0d7;}
#nav li a:hover {display: block; width: 100%; padding: 0.5em; border-width: 1px; border-color: #ffe #aaab9c #ccc #fff; border-style: solid; color: #444; text-decoration: none; background: #a6a097;}
#nav li a:active {display: block; width: 100%; padding: 0.5em; border-width: 1px; border-color: #ffe #aaab9c #ccc #fff; border-style: solid; color: #000; text-decoration: none; background: #fff;}
p {display: block; clear: left;}
</style>
</head>
<nav id="nav-wrap">

	<div id="menu-icon">RaspberryPi Thermostat</div>

	<ul id="nav">
		<li><a href="?set=back">Set-back</a></li>
		<li><a href="?set=occupied">Set Occupied</a></li>
		<li><a href="?set=up">TEMP UP</a></li>
		<li><a href="?set=down">TEMP DOWN</a></li>
	</ul>
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
</nav>
</body>
</html>
