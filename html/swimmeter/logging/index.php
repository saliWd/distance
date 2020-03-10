<?php // declare(strict_types=1);
  // TODO: strict types does not work...
  require_once('functions.php');
  $dbConn = initialize();

// this site is called directly from within the app. There is POST variable with a json, containing the beacon data
// need to extract the correct data and store it into a db
function logData (object $dbConn, $data): bool {
  if (empty($data['reader'])) {
    return errorToFile(1);
  }
  
  if (strcmp(substr($data['reader'], 0, 9), 'widmedia_') !== 0) { // now I "know" the post request is from my app (should be widmedia_<something>, e.g. widmedia_s6)
    return errorToFile(2);
  }
  $deviceName = $data['reader'];
  foreach ($data['beacons'] as $beacon) {
    if (strcmp($beacon['beacon_type'], 'eddystone_url') == 0) {      
      $url = substr($beacon['eddystone_url_data']['url'], 0, 23);
      if (strcmp($url, 'https://www.widmedia.ch') == 0) { // now we are sure that my app did send my beacon
        $rssi = $beacon['rssi'];
        $distance = $beacon['distance'];
        $lastSeen = $beacon['last_seen'];
        
        return storeInDb($dbConn, $deviceName, $rssi, $distance, $lastSeen);        
      } // if
    } // if
  } // foreach
  return errorToFile(3); // none of the foreach loops did trigger
}

function errorToFile($errorNum): bool {
  $fp = fopen('error.log', 'a'); //opens file in append mode.
  fwrite($fp, 'Error happened: '.$line);
  fclose($fp);
  return false;
}

// DeviceName:widmedia_s6, rssi:-66, distance:11.095192891072, last_seen:1583761614714
function storeInDb (object $dbConn, $deviceName, $rssi, $distance, $lastSeen): bool {
  $safeA = mysqli_real_escape_string($dbConn, $deviceName);
  $safeB = mysqli_real_escape_string($dbConn, $rssi); // this is more precise than the distance
  $safeC = mysqli_real_escape_string($dbConn, $distance);
  $safeD = mysqli_real_escape_string($dbConn, $lastSeen); // cut the last 3 digits and it seems like a unix timestamp
  
  $result = $dbConn->query('INSERT INTO `swLog` (`deviceName`, `rssi`, `distance`, `lastSeen`) VALUES ("'.$safeA.'", "'.$safeB.'", "'.$safeC.'", "'.$safeD.'")');      
  if (!$result) { return errorToFile(4); }
  return $result;
}

$data = json_decode(file_get_contents('php://input'), true);
if (logData($dbConn, $data)) {
  // everything ok, data came from app, no need to do anything. Can finish the script  
} else { // forward to normal page
  echo '<html><head><meta http-equiv="refresh" content="0; URL=\'logging.php\'" />
    <title>Weiterleitungsseite</title>
  </head>
  <body><a href="logging.php">Weiterleitung zur swimmeter logging website</a></body></html>';
}


?>
