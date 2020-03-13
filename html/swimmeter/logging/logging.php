<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" lang="de">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
<title>widmedia.ch SwimMeter</title>
<meta name="author" content="Daniel Widmer">
<meta name="description" content="swim meter, SwimMeter">    
<meta name="keywords" content="count your swimming lanes">
<meta name="robots" content="index, follow">
<meta name="revisit-after" content="20 days">
<meta name="audience" content="all">
<meta name="distribution" content="global">
<meta name="content-language" content="de">
<meta name="language" content="deutsch, de">

<!-- Mobile Specific Metas -->
<meta name="viewport" content="width=device-width, initial-scale=1">
  
<!-- Favicon -->
<link rel="icon" type="image/png" sizes="96x96" href="../images/favicon.png">
<link rel="stylesheet" href="../css/font.css" type="text/css" />
<link rel="stylesheet" href="../css/normalize.css" type="text/css" />
<link rel="stylesheet" href="../css/skeleton.css" type="text/css" />
<style type="text/css">
body {
	background-color: #666;	
	color: #f90;
}
a {
  padding: 2px 4px 1px 1px;
  color: #7d2a43;  
  text-decoration: none;}
a:hover {
  color: #0FA0CE; 
  text-decoration: none;}
</style>
</head>
<body>
<div class="section categories noBottom">
  <div class="container">
  <h3 class="section-heading">Logging Data</h3>

  <?php // declare(strict_types=1);
  require_once('functions.php');
  
  function preprocLastSeen(string $in, int $min): int {
    return ((int)$in - $min);
    //return substr($in, 7, 3); // "158_3786693_759" cut the first 3 (158) and the last 3 digits
  }
  
  $dbConn = initialize();
  
  $doSafe = safeIntFromExt ('GET', 'do', 1);
  if ($doSafe == 1) { // delete all data    
    if ($dbConn->query('DELETE FROM `swLog` WHERE 1')) {
      echo '<div class="row twelve columns linktext">did delete all data</div>';
    } else {
      echo '<div class="row twelve columns linktext">error, could not delete data</div>';
    }
  }
  
  
  
  if ($result = $dbConn->query('SELECT `lastSeen`, `rssi` FROM `swLog` WHERE 1 ORDER BY `lastSeen` LIMIT 1000')) { // newest at bottom
    if ($result->num_rows < 3) { // db is empty or almost empty
      echo '<div class="row twelve columns linktext">less than 3 results in DB</div>';
    } else {
      
      $resultExtrema = $dbConn->query('SELECT MIN(`lastSeen`), MIN(`rssi`), MAX(`rssi`) FROM `swLog` WHERE 1');
      $extrema = $resultExtrema->fetch_assoc();
      $lastSeenMin = (int)$extrema['MIN(`lastSeen`)'];
      
      $WIDTH = 1200;
      $HEIGHT = 800;
      $GRID_DIV = 7; // resulting in 'one more' axis labels
      $rssi = [];
      $xAxis = [];
      // TODO: could be converted into a do_while?
      
      $row = $result->fetch_assoc(); // do it once (there is at least one result)            
      $rssi[]   = $row['rssi'];
      $xAxisOld = preprocLastSeen($row['lastSeen'], $lastSeenMin);  // ignore some digits
      $xAxis[]  = $xAxisOld;
      
      while ($row = $result->fetch_assoc()) {
        
        if (preprocLastSeen($row['lastSeen'], $lastSeenMin) != $xAxisOld) { // need to ignore non-distinct values on lastSeen
          $rssi[]   = $row['rssi'];
          $xAxisOld = preprocLastSeen($row['lastSeen'], $lastSeenMin);
          $xAxis[]  = $xAxisOld;
        } // else just skip
      } // while
      
      $rowHeightY = floor(($extrema['MAX(`rssi`)'] - $extrema['MIN(`rssi`)'])/$GRID_DIV);
      $grid = array(0=>array("Min"=>0,"Max"=>$xAxisOld,"Rows"=>$GRID_DIV,"RowHeight"=>(floor($xAxisOld/$GRID_DIV))),1=>array("Min"=>$extrema['MIN(`rssi`)'],"Max"=>$extrema['MAX(`rssi`)'],"Rows"=>$GRID_DIV,"RowHeight"=>$rowHeightY));
      doGraph($rssi, $xAxis, $WIDTH, $HEIGHT, $grid);
      echo '<div class="row twelve columns u-max-full-width"><img src="out/graph.png" width="100%" alt="rssi vs. time plot"></div>';  
    } // have at least one entry
    $result->close(); // free result set
  } // query   
  
  ?>  
  </div>
  <div class="section noBottom">
    <div class="container">
      <div class="row twelve columns"><hr /></div>
      <div class="row">      
        <div class="four columns"><a class="button differentColor" href="../index.html">Startseite</a></div>
        <div class="four columns"><a class="button differentColor" href="logging.php?do=1">Daten löschen</a></div>
        <div class="four columns"><a class="button differentColor" href="logging.php">neu laden</a></div>
      </div>
    </div>
  </div>
</div></div></body></html>
