-- MySQL dump 10.13  Distrib 8.0.42, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: rincondelsabor
-- ------------------------------------------------------
-- Server version	8.0.42

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `receta_ingrediente`
--

DROP TABLE IF EXISTS `receta_ingrediente`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `receta_ingrediente` (
  `idReceta` int DEFAULT NULL,
  `idIngrediente` int DEFAULT NULL,
  `idRecetaIngrediente` int NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`idRecetaIngrediente`),
  KEY `idReceta` (`idReceta`),
  KEY `idIngrediente` (`idIngrediente`),
  CONSTRAINT `receta_ingrediente_ibfk_1` FOREIGN KEY (`idReceta`) REFERENCES `recetas` (`idReceta`),
  CONSTRAINT `receta_ingrediente_ibfk_2` FOREIGN KEY (`idIngrediente`) REFERENCES `ingredientes` (`idIngrediente`)
) ENGINE=InnoDB AUTO_INCREMENT=97 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `receta_ingrediente`
--

LOCK TABLES `receta_ingrediente` WRITE;
/*!40000 ALTER TABLE `receta_ingrediente` DISABLE KEYS */;
INSERT INTO `receta_ingrediente` VALUES (1,10,1),(1,11,2),(1,1,3),(2,12,4),(2,13,5),(2,14,6),(2,2,7),(3,15,8),(3,16,9),(3,1,10),(3,17,11),(4,15,12),(4,17,13),(4,1,14),(5,32,15),(5,18,16),(5,19,17),(5,6,18),(5,1,19),(6,18,20),(6,20,21),(6,7,22),(6,13,23),(6,38,24),(7,21,25),(7,19,26),(7,13,27),(7,1,28),(8,21,29),(8,22,30),(8,23,31),(8,1,32),(9,16,33),(9,24,34),(9,1,35),(9,17,36),(10,19,37),(10,6,38),(10,13,39),(10,1,40),(11,4,41),(11,19,42),(11,13,43),(11,1,44),(12,3,45),(12,11,46),(12,14,47),(12,26,48),(13,21,49),(13,12,50),(13,14,51),(13,1,52),(14,15,53),(14,19,54),(14,1,55),(15,27,56),(15,30,57),(15,14,58),(15,1,59),(16,28,60),(16,13,61),(16,5,62),(16,2,63),(17,19,64),(17,13,65),(17,1,66),(18,24,67),(18,32,68),(18,1,69),(19,32,70),(19,19,71),(19,13,72),(19,14,73),(20,29,74),(20,30,75),(20,26,76),(20,31,77),(21,33,78),(21,21,79),(21,13,80),(21,38,81),(22,35,82),(22,13,83),(22,19,84),(22,1,85),(23,3,86),(23,19,87),(23,32,88),(23,1,89),(24,36,90),(24,32,91),(24,11,92),(24,14,93),(25,5,94),(25,32,95),(25,37,96);
/*!40000 ALTER TABLE `receta_ingrediente` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-10-27 18:16:01
