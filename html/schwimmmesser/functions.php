<?php declare(strict_types=1);

// returns a 'safe' integer. Return value is 0 if the checks did not work out
function makeSafeInt($unsafe, int $length):int {  
  $unsafe = filter_var(value: substr(string: $unsafe, offset: 0, length: $length), filter: FILTER_SANITIZE_NUMBER_INT); // sanitize a length-limited variable
  if (filter_var(value: $unsafe, filter: FILTER_VALIDATE_INT)) { 
    return (int)$unsafe;
  } else { 
    return 0;
  }  
}
// returns a 'safe' string. Not that much to do though for a string
function makeSafeStr($unsafe, int $length):string {
  return htmlentities(string: substr(string: $unsafe, offset: 0, length: $length)); // length-limited variable, HTML encoded
}
// checks whether a get/post/cookie variable exists and makes it safe if it does. If not, returns 0
function safeIntFromExt(string $source, string $varName, int $length):int {
  if (($source === 'GET') and isset($_GET[$varName])) {
    return makeSafeInt($_GET[$varName], $length);    
  } elseif (($source === 'POST') and isset($_POST[$varName])) {
    return makeSafeInt($_POST[$varName], $length);    
  } elseif (($source === 'COOKIE') and isset($_COOKIE[$varName])) {
    return makeSafeInt($_COOKIE[$varName], $length);  
  } else {
    return 0;
  }
}
function safeStrFromExt(string $source, string $varName, int $length):string {
  if (($source === 'GET') and isset($_GET[$varName])) {
     return makeSafeStr(unsafe: $_GET[$varName], length: $length);
   } elseif (($source === 'POST') and isset($_POST[$varName])) {
     return makeSafeStr(unsafe: $_POST[$varName], length: $length);
   } elseif (($source === 'COOKIE') and isset($_COOKIE[$varName])) {
     return makeSafeStr(unsafe: $_COOKIE[$varName], length: $length);
   } else {
     return '';
   }
}
