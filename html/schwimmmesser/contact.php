<?php
// TODO: move to own file
// returns a 'safe' integer. Return value is 0 if the checks did not work out
function makeSafeInt($unsafe, int $length):int {  
  $unsafe = filter_var(substr($unsafe, 0, $length), FILTER_SANITIZE_NUMBER_INT); // sanitize a length-limited variable
  if (filter_var($unsafe, FILTER_VALIDATE_INT)) { 
    return (int)$unsafe;
  } else { 
    return 0;
  }  
}
// returns a 'safe' string. Not that much to do though for a string
function makeSafeStr($unsafe, int $length):string {
  return (htmlentities(substr($unsafe, 0, $length))); // length-limited variable, HTML encoded
}
// checks whether a get/post/cookie variable exists and makes it safe if it does. If not, returns 0
function safeIntFromExt(string $source, string $varName, int $length):int {
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
function safeStrFromExt(string $source, string $varName, int $length):string {
  if (($source === 'GET') and (isset($_GET[$varName]))) {
     return makeSafeStr($_GET[$varName], $length);
   } elseif (($source === 'POST') and (isset($_POST[$varName]))) {
     return makeSafeStr($_POST[$varName], $length);
   } elseif (($source === 'COOKIE') and (isset($_COOKIE[$varName]))) {
     return makeSafeStr($_COOKIE[$varName], $length);
   } else {
     return '';
   }
}


echo '<!DOCTYPE html>
  <html>
  <head>
  <meta charset="utf-8">
  <title>SchwimmMesser Kontaktformular</title>
  <meta name="description" content="zählt deine Längen">  
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="stylesheet" href="css/schwimmmesser.css" type="text/css">
  <script src="script/flowbite.min.js"></script>
  </head>
  <body>
  ';
  echo '<div class="container mx-auto px-4 py-2 lg text-center mt-14 scroll-mt-14" id="anchorTopOfPage">';
$SPAM_SCHUTZ_TRUTH = 28;



$name = safeStrFromExt(source:'POST', varName:'contactForm_name', length:63);
$email = safeStrFromExt(source:'POST', varName:'contactForm_email', length:63);
$schutz = safeIntFromExt(source:'POST', varName:'contactForm_schutz', length:3);
$div = safeStrFromExt(source:'POST', varName:'contactForm_div', length:1023);
$process = safeIntFromExt(source:'POST', varName:'contactForm_process', length:1);

$okOrNot = '';
$procErr = FALSE;
$procErrDet = ''; // error message
$output = ''; // success message

if ($process !== 1) {
  $procErr = TRUE;
  $procErrDet .= 'Du musst der Datenverarbeitung zustimmen...<br>';
}
if ($schutz !== $SPAM_SCHUTZ_TRUTH) {
  $procErr = TRUE;
  $procErrDet .= 'Spamschutzrechnung ist nicht korrekt...<br>';
}
if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
  $procErr = TRUE;
  $procErrDet .= 'Emailadresse scheint ungültig zu sein...<br>';
}

if ($procErr) {
  $okOrNot = 'Fehler';
  $output .= '<div class="text-red-600">'.$procErrDet.'</div>Es wurde keine Email verschickt.<br><br>Bitte Kontaktformular nochmals ausfüllen: <a href="https://strommesser.ch/#post-194" class="underline">zurück</a><br><br>';
} else {
  $mailBody  = 'Name: '.$name."\n";
  $mailBody .= 'Email:'.$email."\n";
  $mailBody .= 'Weitere Infos: '.$div."\n";
  $mailBody .= 'Datenverarbeitung: '.$process."\n";

  $mailOk = mail(
    to:'web@widmedia.ch;',
    subject:'SchwimmMesser Kontaktanfrage',
    message:$mailBody
  );
  if ($mailOk) {
    $okOrNot = 'Kontaktdaten wurden verschickt';
    $output .= 'Email wurde verschickt (du erhältst wegen Spamschutz keine Kopie). Ich werde mich aber in Kürze bei dir melden...<br>Folgende Angaben wurden gesendet:<br>';
  } else {
    $okOrNot = 'Fehler beim Mailversand';
    $output .= 'Das Kontaktformular wurde korrekt ausgefüllt aber Email konnte nicht verschickt werden...<br>Nochmals versuchen? <br><a href="https://widmedia.ch/schwimmmesser/" class="underline">zurück</a>';
  }
}

$output .= '<div class="font-bold">Daten Kontaktformular</div>Name: '.$name.', Email:'.$email.', Weitere Infos: '.$div.', Datenverarbeitung: '.$process.'<br>';
echo '
<div class="text-left block p-6 bg-white border border-gray-200 rounded-lg shadow hover:bg-gray-100">
  <h3 class="mb-2 text-xl font-bold tracking-tight text-gray-900">'.$okOrNot.'</h3>
  <p class="font-normal text-gray-700">'.$output.'</p>
  <p>&nbsp;</p>
  <p class="font-normal text-gray-700"><a href="https://widmedia.ch/schwimmmesser/" class="underline">zurück zur Startseite</a></p>
</div>
</div></body></html>';
?>