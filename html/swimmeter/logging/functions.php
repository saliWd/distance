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