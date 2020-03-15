-- phpMyAdmin SQL Dump
-- version 4.9.0.1
-- https://www.phpmyadmin.net/
--
-- Host: localhost:3306
-- Erstellungszeit: 15. Mrz 2020 um 16:19
-- Server-Version: 10.2.31-MariaDB
-- PHP-Version: 7.1.14

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Datenbank: `widmedia`
--

-- --------------------------------------------------------

--
-- Tabellenstruktur für Tabelle `swLog`
--

CREATE TABLE `swLog` (
  `id` int(11) UNSIGNED NOT NULL,
  `deviceName` varchar(30) NOT NULL,
  `rssi` int(11) NOT NULL,
  `distance` float NOT NULL,
  `lastSeen` varchar(14) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Daten für Tabelle `swLog`
--

INSERT INTO `swLog` (`id`, `deviceName`, `rssi`, `distance`, `lastSeen`) VALUES
(212, 'widmedia_s6', -75, 10.5296, '1584282016'),
(213, 'widmedia_s6', -90, 65.0902, '1584282034'),
(214, 'widmedia_s6', -85, 83.4236, '1584282037'),
(215, 'widmedia_s6', -95, 102.572, '1584282050'),
(216, 'widmedia_s6', -95, 102.572, '1584282050'),
(217, 'widmedia_s6', -93, 101.154, '1584282053'),
(218, 'widmedia_s6', -95, 105.459, '1584282056'),
(219, 'widmedia_s6', -92, 101.468, '1584282065'),
(220, 'widmedia_s6', -89, 98.3696, '1584282078'),
(221, 'widmedia_s6', -88, 84.2026, '1584282087'),
(222, 'widmedia_s6', -83, 75.5842, '1584282093'),
(223, 'widmedia_s6', -86, 73.4723, '1584282096'),
(224, 'widmedia_s6', -91, 76.4657, '1584282102'),
(225, 'widmedia_s6', -91, 76.4657, '1584282102'),
(226, 'widmedia_s6', -95, 99.7537, '1584282118'),
(227, 'widmedia_s6', -86, 86.3751, '1584282130'),
(228, 'widmedia_s6', -92, 86.7624, '1584282143'),
(229, 'widmedia_s6', -84, 77.2442, '1584282152'),
(230, 'widmedia_s6', -80, 56.6435, '1584282161');

--
-- Indizes der exportierten Tabellen
--

--
-- Indizes für die Tabelle `swLog`
--
ALTER TABLE `swLog`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT für exportierte Tabellen
--

--
-- AUTO_INCREMENT für Tabelle `swLog`
--
ALTER TABLE `swLog`
  MODIFY `id` int(11) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=277;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
