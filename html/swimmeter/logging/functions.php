<?php declare(strict_types=1);
// This file is a pure function definition file. It is included in other sites

function initialize () {
  require_once('../../start/php/dbConn.php'); // this will return the $dbConn variable as 'new mysqli'
  // NB: this file is not included in the git repository, have to create it yourself (content like: $dbConn = new mysqli("localhost", "DBNAME", "PW", "USER", 3306);)
  if ($dbConn->connect_error) {
    die();
  }
  $dbConn->set_charset('utf8');
  return $dbConn;
}

// checks whether a get/post/cookie variable exists and makes it safe if it does. If not, returns 0
function safeIntFromExt (string $source, string $varName, int $length): int {
  if (($source === 'GET') and (isset($_GET[$varName]))) {
    return makeSafeInt($_GET[$varName], $length);    
  } elseif (($source === 'POST') and (isset($_POST[$varName]))) {
    return makeSafeInt($_POST[$varName], $length);    
  } elseif (($source === 'COOKIE') and (isset($_COOKIE[$varName]))) {
    return makeSafeInt($_COOKIE[$varName], $length);  
  } else {
    return 0;
  }
}

// returns a 'safe' integer. Return value is 0 if the checks did not work out
function makeSafeInt ($unsafe, int $length): int {  
  $unsafe = filter_var(substr($unsafe, 0, $length), FILTER_SANITIZE_NUMBER_INT); // sanitize a length-limited variable
  if (filter_var($unsafe, FILTER_VALIDATE_INT)) { 
    return (int)$unsafe;
  } else { 
    return 0;
  }  
}

spl_autoload_register(function ($class_name) {
	$filename = str_replace('\\', DIRECTORY_SEPARATOR, $class_name) . '.php';
	include $filename;
});

use pChart\pColor;
use pChart\pDraw;
use pChart\pScatter;

function doGraph(array $rssi, array $xAxis, string $title, int $width, int $height): void {
  $myPicture = new pDraw($width, $height);

  $myPicture->myData->addPoints($xAxis,"time");
  $myPicture->myData->addPoints($rssi,"rssi");
  
  $myPicture->myData->setAxisProperties(0, ["Name" => "Time", "Identity" => AXIS_X, "Position" => AXIS_POSITION_BOTTOM]);
  
  $myPicture->myData->setSerieOnAxis("rssi",1);
  $myPicture->myData->setAxisProperties(1, ["Name" => "RSSI", "Identity" => AXIS_Y, "Unit" => "dBm", "Position" => AXIS_POSITION_RIGHT]);
  
  /* Create the 1st scatter chart binding */
  $myPicture->myData->setScatterSerie("time","rssi",0);
  $myPicture->myData->setScatterSerieProperties(0, ["Description" => "RSSI", "Color" => new pColor(0)]);
  
  /* Draw the background */
  $myPicture->drawFilledRectangle(0,0,$width,$height,["Color"=>new pColor(170,183,87), "Dash"=>TRUE, "DashColor"=>new pColor(190,203,107)]);
  
  /* Overlay with a gradient */
  $myPicture->drawGradientArea(0,0,$width,$height,DIRECTION_VERTICAL,["StartColor"=>new pColor(219,231,139,50),"EndColor"=>new pColor(1,138,68,50)]);
  $myPicture->drawGradientArea(0,0,$width,20, DIRECTION_VERTICAL,["StartColor"=>new pColor(0,0,0,80),"EndColor"=>new pColor(50,50,50,80)]);
  
  // default font
  $myPicture->setFontProperties(["FontName"=>"Cairo-Regular.ttf"]);
  
  $myPicture->setFontProperties(["FontSize"=>10]); // title is bigger
  $myPicture->drawText(10,15,$title.': RSSI versus Zeit',["Color"=>new pColor(255)]);
  $myPicture->setFontProperties(["FontSize"=>7]); // back to normal size
  
  $myPicture->drawRectangle(0,0,$width-1,$height-1,["Color"=>new pColor(0)]); // Add a border to the picture
  $myPicture->setGraphArea(50,50,$width-50,$height-50); // Set the graph area
  $myScatter = new pScatter($myPicture); // Create the Scatter chart object
  $myScatter->drawScatterScale(); // Draw the scale
  $myPicture->setShadow(TRUE,["X"=>1,"Y"=>1,"Color"=>new pColor(0,0,0,10)]); // Turn on shadow computing
  $myScatter->drawScatterPlotChart(); // Draw a scatter plot chart
  $myScatter->drawScatterLegend(80,80,["Mode"=>LEGEND_HORIZONTAL,"Style"=>LEGEND_NOBORDER]); // Draw the legend
  $myPicture->autoOutput($title.'.png'); // compression etc. at default values
}

