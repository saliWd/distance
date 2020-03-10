<?php   
/* CAT:Scatter chart */

/* pChart library inclusions */
require_once("bootstrap.php");

use pChart\pColor;
use pChart\pDraw;
use pChart\pScatter;

/* Create the pChart object */
$myPicture = new pDraw(800,400);

/* Create the X axis and the binded series */
$Points_1 = [];
$Points_xAxis = [];
for($i=0;$i<=360;$i=$i+10) 
{
	$Points_1[] = cos(deg2rad($i))*20;
	$Points_xAxis[] = $i;
}
$myPicture->myData->addPoints($Points_1,"Probe 1");
$myPicture->myData->addPoints($Points_xAxis,"Probe 3");

$myPicture->myData->setAxisProperties(0, ["Name" => "Index", "Identity" => AXIS_X, "Position" => AXIS_POSITION_BOTTOM]);

$myPicture->myData->setSerieOnAxis("Probe 3",1);
$myPicture->myData->setAxisProperties(1, ["Name" => "Degree", "Identity" => AXIS_Y, "Unit" => "°", "Position" => AXIS_POSITION_RIGHT]);

/* Create the 1st scatter chart binding */
$myPicture->myData->setScatterSerie("Probe 1","Probe 3",0);
$myPicture->myData->setScatterSerieProperties(0, ["Description" => "This year", "Color" => new pColor(0), "Ticks" => 4]);

/* Draw the background */
$myPicture->drawFilledRectangle(0,0,800,400,["Color"=>new pColor(170,183,87), "Dash"=>TRUE, "DashColor"=>new pColor(190,203,107)]);

/* Overlay with a gradient */
$myPicture->drawGradientArea(0,0,800,400,DIRECTION_VERTICAL,["StartColor"=>new pColor(219,231,139,50),"EndColor"=>new pColor(1,138,68,50)]);
$myPicture->drawGradientArea(0,0,800,20, DIRECTION_VERTICAL,["StartColor"=>new pColor(0,0,0,80),"EndColor"=>new pColor(50,50,50,80)]);

// default font
$myPicture->setFontProperties(["FontName"=>"Cairo-Regular.ttf"]);

$myPicture->setFontProperties(["FontSize"=>10]); // title is bigger
$myPicture->drawText(10,15,"drawScatterLineChart() - Draw a scatter line chart",["Color"=>new pColor(255)]);
$myPicture->setFontProperties(["FontSize"=>7]); // back to normal size

/* Add a border to the picture */
$myPicture->drawRectangle(0,0,799,399,["Color"=>new pColor(0)]);

/* Set the graph area */
$myPicture->setGraphArea(50,50,750,350);

/* Create the Scatter chart object */
$myScatter = new pScatter($myPicture);

/* Draw the scale */
$myScatter->drawScatterScale();

/* Turn on shadow computing */
$myPicture->setShadow(TRUE,["X"=>1,"Y"=>1,"Color"=>new pColor(0,0,0,10)]);

/* Draw a scatter plot chart */
$myScatter->drawScatterLineChart();

/* Draw the legend */
$myScatter->drawScatterLegend(280,380,["Mode"=>LEGEND_HORIZONTAL,"Style"=>LEGEND_NOBORDER]);

/* Render the picture (choose the best way) */
$myPicture->autoOutput("temp/example.drawScatterLineChart.png");

