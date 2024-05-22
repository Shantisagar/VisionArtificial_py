-- phpMyAdmin SQL Dump
-- version 4.9.1
-- https://www.phpmyadmin.net/
--
-- Host: localhost
-- Generation Time: May 15, 2024 at 06:07 PM
-- Server version: 8.0.17
-- PHP Version: 7.3.10

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `registro_va`
--

-- --------------------------------------------------------

--
-- Table structure for table `desvio_papel`
--

CREATE TABLE `desvio_papel` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `unixtime` int(11) NOT NULL,
  `datetime` datetime NOT NULL,
  `desvio` float NOT NULL,
  `direccion` tinyint(1) NOT NULL,
  `enable` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


--
-- Dumping data for table `desvio_papel`
--


/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
