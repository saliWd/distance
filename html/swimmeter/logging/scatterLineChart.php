<?php   
declare(strict_types=1);

spl_autoload_register(function ($class_name) {
	$filename = str_replace('\\', DIRECTORY_SEPARATOR, $class_name) . '.php';
	include $filename;
});

use pChart\pColor;
use pChart\pDraw;
use pChart\pScatter;

function doGraph(array $rssi, array $xAxis): void {
  $WIDTH = 800;
  $HEIGHT = 400;
  
  $myPicture = new pDraw($WIDTH, $HEIGHT);

  $myPicture->myData->addPoints($xAxis,"time");
  $myPicture->myData->addPoints($rssi,"rssi");
  
  $myPicture->myData->setAxisProperties(0, ["Name" => "Index", "Identity" => AXIS_X, "Unit" => "s", "Position" => AXIS_POSITION_BOTTOM]);
  
  $myPicture->myData->setSerieOnAxis("rssi",1);
  $myPicture->myData->setAxisProperties(1, ["Name" => "Degree", "Identity" => AXIS_Y, "Unit" => "dBm", "Position" => AXIS_POSITION_RIGHT]);
  
  /* Create the 1st scatter chart binding */
  $myPicture->myData->setScatterSerie("time","rssi",0);
  $myPicture->myData->setScatterSerieProperties(0, ["Description" => "RSSI", "Color" => new pColor(0), "Ticks" => 4]);
  
  /* Draw the background */
  $myPicture->drawFilledRectangle(0,0,$WIDTH,$HEIGHT,["Color"=>new pColor(170,183,87), "Dash"=>TRUE, "DashColor"=>new pColor(190,203,107)]);
  
  /* Overlay with a gradient */
  $myPicture->drawGradientArea(0,0,$WIDTH,$HEIGHT,DIRECTION_VERTICAL,["StartColor"=>new pColor(219,231,139,50),"EndColor"=>new pColor(1,138,68,50)]);
  $myPicture->drawGradientArea(0,0,$WIDTH,20, DIRECTION_VERTICAL,["StartColor"=>new pColor(0,0,0,80),"EndColor"=>new pColor(50,50,50,80)]);
  
  // default font
  $myPicture->setFontProperties(["FontName"=>"Cairo-Regular.ttf"]);
  
  $myPicture->setFontProperties(["FontSize"=>10]); // title is bigger
  $myPicture->drawText(10,15,"RSSI versus Zeit",["Color"=>new pColor(255)]);
  $myPicture->setFontProperties(["FontSize"=>7]); // back to normal size
  
  $myPicture->drawRectangle(0,0,$WIDTH-1,$HEIGHT-1,["Color"=>new pColor(0)]); // Add a border to the picture
  $myPicture->setGraphArea(50,50,$WIDTH-50,$HEIGHT-50); // Set the graph area
  $myScatter = new pScatter($myPicture); // Create the Scatter chart object
  $myScatter->drawScatterScale(); // Draw the scale
  $myPicture->setShadow(TRUE,["X"=>1,"Y"=>1,"Color"=>new pColor(0,0,0,10)]); // Turn on shadow computing
  $myScatter->drawScatterLineChart(); // Draw a scatter plot chart
  $myScatter->drawScatterLegend(280,380,["Mode"=>LEGEND_HORIZONTAL,"Style"=>LEGEND_NOBORDER]); // Draw the legend
  $myPicture->autoOutput('graph.png'); // compression etc. at default values
}

