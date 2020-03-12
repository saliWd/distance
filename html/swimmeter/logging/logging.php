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
<link rel="icon" type="image/png" sizes="96x96" href="../../start/images/favicon.png">
<link rel="stylesheet" href="../../start/css/font.css" type="text/css" />
<link rel="stylesheet" href="../../start/css/normalize.css" type="text/css" />
<link rel="stylesheet" href="../../start/css/skeleton.css" type="text/css" />
<style type="text/css">
body {
	background-color: #666;
	margin-left: 20%;
	margin-top: 15%;
	margin-right: 20%;  
	color: #F90;
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
  
  function preprocLastSeen(string $in): string {
    return substr($in, 5, 8);    
  }
  
  $dbConn = initialize();
  if ($result = $dbConn->query('SELECT `lastSeen`, `rssi`, `deviceName` FROM `swLog` WHERE 1 ORDER BY `lastSeen` LIMIT 1000')) { // newest at bottom
    if ($result->num_rows == 0) { // most probably a new user
      echo '<div class="row twelve columns linktext">nothing in DB</div>';
    } else {
      $WIDTH = 800;
      $HEIGHT = 400;
      $rssi = [];
      $xAxis = [];
      // TODO: could be converted into a do_while?
      
      $row = $result->fetch_assoc(); // do it once (there is at least one result)      
      $deviceNameOld = $row['deviceName'];
      $rssi[]   = $row['rssi'];
      $xAxisOld = $row['lastSeen'];  // ignore some digits (TBD which ones)
      $xAxis[]  = $xAxisOld;
      
      while ($row = $result->fetch_assoc()) {
        
        if ($row['deviceName'] != $deviceNameOld) {
          // TODO: whenever there is a change in device name, I want a new graph
        }
        
        // need to ignore non-distinct values on lastSeen
        if ($row['lastSeen'] != $xAxisOld) {
          $deviceNameOld = $row['deviceName'];
          $rssi[]   = $row['rssi'];
          $xAxisOld = $row['lastSeen'];
          $xAxis[]  = $xAxisOld;
        } // else just skip
      } // while
      doGraph($rssi, $xAxis, $deviceNameOld, $WIDTH, $HEIGHT);
      echo '<div class="row twelve columns"><img src="'.$deviceNameOld.'.png" width="'.$WIDTH.'" height="'.$HEIGHT.'" alt="rssi vs. time plot"></div>';  
    } // have at least one entry
    $result->close(); // free result set
  } // query   
  
  ?>  
  </div>
  <div class="section noBottom">
    <div class="container">
      <div class="row twelve columns"><hr /></div>
      <div class="row">      
        <div class="six columns"><a class="button differentColor" href="../index.html">Startseite</a></div>
        <div class="six columns"><a class="button differentColor" href="logging.php">neu laden</a></div>
      </div>
    </div>
  </div>
</div></div></body></html>
