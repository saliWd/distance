<?php 

// at v: 
// Array
// (
    // [reader] => s6
    // [beacons] => Array
        // (
            // [0] => Array
                // (
                    // [hashcode] => -647315039
                    // [beacon_type] => eddystone_url
                    // [manufacturer] => 65194
                    // [tx_power] => -41
                    // [rssi] => -59
                    // [distance] => 5.8271277612308
                    // [last_seen] => 1583507860652
                    // [eddystone_url_data] => Array
                        // (
                            // [url] => https://www.widmedia.ch
                        // )

                    // [n] => 
                // )
        // )
// )

// at h:
// Array
// (
//     [reader] => s6a
//     [beacons] => Array
//         (
//             [0] => Array
//                 (
//                     [hashcode] => -1319653246
//                     [beacon_type] => eddystone_url
//                     [manufacturer] => 65194
//                     [tx_power] => -41
//                     [rssi] => -70
//                     [distance] => 18.291520218788
//                     [last_seen] => 1583699079336
//                     [eddystone_url_data] => Array
//                         (
//                             [url] => https://www.widmedia.ch/swim
//                         )
// 
//                     [telemetry_data] => Array
//                         (
//                             [version] => 1
//                             [battery_milli_volts] => 55193
//                             [temperature] => 40.765625
//                             [pdu_count] => 861046502
//                             [uptime_seconds] => 2666472481
//                         )
// 
//                     [n] => 
//                 )
// 
//         )
// 
// )

$data = json_decode(file_get_contents('php://input'), true);
$deviceName = htmlentities(substr($data['reader'], 0, 9));  // should be widmedia_<something>, e.g. widmedia_s6

$dbg_error_msg = ''; // TODO: remove that again

if (strcmp($deviceName, 'widmedia_') == 0) { // now I "know" the post request is from my app
  foreach ($data['beacons'] as $beacon) {
    if (strcmp($beacon['beacon_type'], 'eddystone_url') == 0) {
      // TODO: should check on the url itself, not just on the beacon type
      fwrite($fp, "DeviceName:\t". $data['reader']."\t");
      $hashcode = $beacon['hashcode'];
      $manufacturer = $beacon['manufacturer'];
      $rssi = $beacon['rssi'];
      $distance = $beacon['distance'];
      $last_seen = $beacon['last_seen'];
  
      $line = "hashcode:\t".$hashcode."\tmanufacturer:\t".$manufacturer."\trssi:\t".$rssi."\tdistance:\t".$distance."\tlast_seen:\t".$last_seen."\n";
      $fp = fopen('data.log', 'a');//opens file in append mode.
      fwrite($fp, $line);
      fclose($fp);
    } else {
      $dbg_error_msg .= 'beacon_type did not match ';
    }
  }
} else {
  $dbg_error_msg .= 'deviceName did not match ';
}

if (strlen($dbg_error_msg) > 5) {
  echo 'Error: '.$dbg_error_msg;
  // $fp = fopen('data.log', 'a');//opens file in append mode.
  // fwrite($fp, $dbg_error_msg);
  // fclose($fp);
}
?>
