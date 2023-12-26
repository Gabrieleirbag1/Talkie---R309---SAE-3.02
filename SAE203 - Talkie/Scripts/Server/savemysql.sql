-- MySQL dump 10.13  Distrib 8.0.35, for Linux (x86_64)
--
-- Host: localhost    Database: Talkie
-- ------------------------------------------------------
-- Server version	8.0.35-0ubuntu0.22.04.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `acces_salon`
--

DROP TABLE IF EXISTS `acces_salon`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `acces_salon` (
  `id_salon` int NOT NULL AUTO_INCREMENT,
  `nom` varchar(50) DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  `user` int DEFAULT NULL,
  PRIMARY KEY (`id_salon`),
  KEY `FK_UsernameSalon` (`user`),
  CONSTRAINT `FK_UsernameSalon` FOREIGN KEY (`user`) REFERENCES `user` (`id_user`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `demande`
--

DROP TABLE IF EXISTS `demande`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `demande` (
  `id_demande` int NOT NULL AUTO_INCREMENT,
  `type` varchar(30) DEFAULT NULL,
  `date_demande` datetime DEFAULT NULL,
  `demandeur` varchar(45) DEFAULT NULL,
  `receveur` varchar(45) DEFAULT NULL,
  `concerne` varchar(30) DEFAULT NULL,
  `validate` tinyint(1) DEFAULT NULL,
  `reponse` tinyint(1) DEFAULT '0',
  PRIMARY KEY (`id_demande`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `friends`
--

DROP TABLE IF EXISTS `friends`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `friends` (
  `id_friends` int NOT NULL AUTO_INCREMENT,
  `friend1` varchar(45) DEFAULT NULL,
  `friend2` varchar(45) DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  PRIMARY KEY (`id_friends`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `message`
--

DROP TABLE IF EXISTS `message`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `message` (
  `id_message` int NOT NULL AUTO_INCREMENT,
  `message` varchar(255) DEFAULT NULL,
  `user` int DEFAULT NULL,
  `date_envoi` datetime DEFAULT NULL,
  `salon` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id_message`),
  KEY `FK_UsernameMessage` (`user`),
  CONSTRAINT `FK_UsernameMessage` FOREIGN KEY (`user`) REFERENCES `user` (`id_user`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `private`
--

DROP TABLE IF EXISTS `private`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `private` (
  `id_private` int NOT NULL AUTO_INCREMENT,
  `user1` int DEFAULT NULL,
  `user2` int DEFAULT NULL,
  `contenu` varchar(255) DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  PRIMARY KEY (`id_private`),
  KEY `user1` (`user1`),
  KEY `user2` (`user2`),
  CONSTRAINT `private_ibfk_1` FOREIGN KEY (`user1`) REFERENCES `user` (`id_user`),
  CONSTRAINT `private_ibfk_2` FOREIGN KEY (`user2`) REFERENCES `user` (`id_user`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sanction`
--

DROP TABLE IF EXISTS `sanction`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sanction` (
  `id_sanction` int NOT NULL AUTO_INCREMENT,
  `type` varchar(30) DEFAULT NULL,
  `date_sanction` datetime DEFAULT NULL,
  `date_fin` datetime DEFAULT NULL,
  `user` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id_sanction`),
  UNIQUE KEY `uc_user` (`user`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `user`
--

DROP TABLE IF EXISTS `user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user` (
  `id_user` int NOT NULL AUTO_INCREMENT,
  `username` varchar(45) NOT NULL,
  `password` varchar(45) DEFAULT NULL,
  `mail` varchar(320) DEFAULT NULL,
  `date_creation` datetime DEFAULT NULL,
  `alias` varchar(20) DEFAULT NULL,
  `is_admin` tinyint(1) DEFAULT '0',
  `sanction` tinyint(1) DEFAULT '0',
  `description` varchar(300) DEFAULT NULL,
  `photo` varchar(50) DEFAULT 'bear',
  PRIMARY KEY (`id_user`),
  UNIQUE KEY `unique_username` (`username`),
  CONSTRAINT `CK_username_chars` CHECK ((not(regexp_like(`username`,_utf8mb4'[#&%\']'))))
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

INSERT INTO `user` (`username`, `password`, `mail`, `date_creation`, `alias`, `is_admin`)
VALUES ('TheAdmin', 'toto', 'admin@example.com', NOW(), 'Admin', 1);

INSERT INTO `user` (`username`, `password`, `mail`, `date_creation`, `alias`, `is_admin`)
VALUES ('Marcel', 'titi', 'marcel@mail.com', NOW(), 'Marcelito', 0);

INSERT INTO `acces_salon` (`nom`, `date`, `user`)
VALUES ('Général', NOW(), 1);

INSERT INTO `acces_salon` (`nom`, `date`, `user`)
VALUES ('Blabla', NOW(), 1);

INSERT INTO `acces_salon` (`nom`, `date`, `user`)
VALUES ('Comptabilité', NOW(), 1);

INSERT INTO `acces_salon` (`nom`, `date`, `user`)
VALUES ('Informatique', NOW(), 1);

INSERT INTO `acces_salon` (`nom`, `date`, `user`)
VALUES ('Marketing', NOW(), 1);

INSERT INTO `acces_salon` (`nom`, `date`, `user`)
VALUES ('Général', NOW(), 2);


/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2023-12-26 11:48:35
