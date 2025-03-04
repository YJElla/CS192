UNLOCK TABLES;

DROP TABLE IF EXISTS `transcripts`;
DROP TABLE IF EXISTS `courses`;

DROP TABLE IF EXISTS `student`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `student` (
  `idStudent` int NOT NULL AUTO_INCREMENT,
  `student_name` varchar(100) NOT NULL,
  `email` varchar(50) UNIQUE,
  `password` varchar(255) ,
  `address` varchar(255) ,
  `phone_num` char(12) ,
  `sex` varchar(6) ,
  `birthdate` char(10) ,
  `university` char(255) ,
  `years_attended` char(20),
  `degree_title` char(255),
  PRIMARY KEY (`idStudent`)
);



--
-- Dumping data for table `student`
--

LOCK TABLES `student` WRITE;
/*!40000 ALTER TABLE `student` DISABLE KEYS */;
INSERT INTO `student` VALUES (202202031,'Ella','ycella@up.edu.ph',
'password','Cavite','9053025857','Male','06192003','UP Diliman','2022-2026','BS Computer Science');
/*!40000 ALTER TABLE `student` ENABLE KEYS */;
UNLOCK TABLES;

DROP TABLE IF EXISTS courses;
CREATE TABLE courses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    course_code VARCHAR(20),
    INDEX idx_course_code (course_code),
    `description` VARCHAR(255)
);

CREATE TABLE transcripts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    semester VARCHAR(50),
    academic_year VARCHAR(20),
    course_id INT,
    grade VARCHAR(10),
    units VARCHAR(10),
    FOREIGN KEY (student_id) REFERENCES student(idStudent),
    FOREIGN KEY (course_id) REFERENCES courses(id)
);

-- Dump completed on 2024-11-14 21:29:16
