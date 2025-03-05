UNLOCK TABLES;

DROP TABLE IF EXISTS `transcripts`;
DROP TABLE IF EXISTS `courses`;
DROP TABLE IF EXISTS `prereqs`;
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

CREATE TABLE prereqs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    program VARCHAR(50) NOT NULL,  
    core_course_code VARCHAR(20) NOT NULL,
    prereq_course_code VARCHAR(20) NOT NULL,  
    description VARCHAR(1000) NOT NULL  
);

INSERT INTO prereqs (program, core_course_code, prereq_course_code, description) VALUES
('MS', 'CS204' , 'CS133', 'Alphabet, words, languages and algorithmic problems, finite automata and hierarchy of languages, Turing machines, tractable and intractable problems, uncomputable functions, the halting problem'),
('MS', 'CS210', 'CS135' , 'Algorithm analysis: asymptotic analysis, time and space tradeoffs, recurrence relations. Greedy, divide and conquer, heuristics and other algorithm design strategies. Fundamental computing algorithms for sorting, selection, trees and graphs. Intractability and approximation'),
('MS', 'CS220', 'CS150' , 'Survey of Programming Languages: History and overview of programming languages, Programming paradigms: imperative, functional, object-oriented, logic, Type systems, Declaration and modularity, Introduction to syntax and semantics'),
('MS', 'CS250', 'CS140' , 'Operating system concepts; virtualization and multiprocessing, issues and considerations in designing and implementing common features of operating systems; virtual machines and hypervisors; introduction to real-time operating systems, and operating systems for embedded systems'),
('MS', 'CS260', 'CS192' , 'Software Implementation and Maintenance, Integration Strategies, and Security Issues'),
('MS', 'CS270', 'CS165' , 'Relational database concepts: Entity Relation modeling, relational model, relational algebra, relational database design and normalization, structured query language, query optimization, File management, Storage and Indexing, Transaction Management, Data warehousing. Non-relational/modern database systems'),
('MS', 'Math Background', 'Math Background' , 'Math, Statistics, Algebra, Probability, Statistics, Trigonometry, Calculus, Numerical Methods');