<?php 

// json object:
// {
//   "reader": "s6",
//   "beacons": [
//     {
//       "hashcode": -1561581011,
//       "beacon_type": "ibeacon",
//       "manufacturer": 76,
//       "tx_power": -50,
//       "rssi": -97,
//       "distance": 41.11457992513615,
//       "last_seen": 1582978519951,
//       "ibeacon_data": {
//         "uuid": "50765cb7-d9ea-4e21-99a4-fa879613a492",
//         "major": "11199",
//         "minor": "42113"
//       },
//       "n": false
//     }
//   ]
// }

// working. prints something like this:
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

$data = json_decode(file_get_contents('php://input'), true);
$string = print_r($data, TRUE);
$fp = fopen('data.log', 'a');//opens file in append mode.
fwrite($fp, $data["beacons"]);
fwrite($fp, $string);
fclose($fp);

?>
