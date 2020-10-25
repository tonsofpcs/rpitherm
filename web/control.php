<?php
$setwhat = htmlspecialchars($_GET["set"]);
$target = 10;
$tmode = "Slow";
header ( 'refresh: 60; url=/control.php' );
$modefile = "/home/pi/thermostat/mode.txt";
$tmode = file($modefile)[0];
$targetfile = "/home/pi/thermostat/target.cfg";
$target = file($targetfile)[0];
switch ($setwhat) {
   case "slow":
     exec("/home/pi/thermostat/setslow.sh");
     $tmode = "SLOW";
     break;
   case "norm":
     exec("/home/pi/thermostat/setnorm.sh");
     $tmode = "NORM";
     break;
   case "fast":
     exec("/home/pi/thermostat/setfast.sh");
     $tmode = "FAST";
     break;
   case "vaca":
     exec("/home/pi/thermostat/setvaca.sh");
     $tmode = "VACATION";
     break;
   case "seventy":
     $target = 70;
     file_put_contents ( $targetfile , strval($target));
     break;
   case "up":
     $target += 1;
     file_put_contents ( $targetfile , strval($target));
     break;
   case "down":
     $target -= 1;
     file_put_contents ( $targetfile , strval($target));
     break;
}
?>
<html>
<head>
<!--<?=$setwhat?>-->
<title>Home Thermostat!</title>
<meta name="viewport" content="width=device-width">
<link rel="stylesheet" href="/control.css" type="text/css" />
</head>
<nav id="nav-wrap">
        <div id="menu-icon">RaspberryPi Thermostat</div>

<div id=ctl>
        <ul>
                <li><a href="?set=up">UP</a></li>
                <li><a href="?set=seventy">70</a></li>
                <li><a href="?set=down">DOWN</a></li>
        </ul>
<p>Target: <br /><?=$target;?>&deg;F<br /><?=$tmode;?></p>
</div>
<p>
<?php
$tempfile = file("/sys/bus/w1/devices/28-0000055d5974/w1_slave");
$tempsplit = (split('t=',$tempfile[1])[1]);
// echo print_r($tempsplit)."<br />";
$tempC = $tempsplit / 1000 - 1.2;
echo $tempC."&deg;C<br />";
$tempF = ($tempC * 1.8 + 32);
echo $tempF."&deg;F";
?>
</p>
<!-- p>Set Mode:</p -->
        <ul id="nav">
                <li><a href="?set=slow">Slow Response</a></li>
                <li><a href="?set=norm">Normal Response</a></li>
                <li><a href="?set=fast">Fast Response</a></li>
                <li><a href="?set=vaca">Vacation Mode</a></li>
        </ul>
<a href="week.png?"><img src="day.png?" width=95% /></a>
</nav>
</body>
</html>