UNLOCK TABLES;

DROP TABLE IF EXISTS `transcripts`;
DROP TABLE IF EXISTS `prereqs`;
DROP TABLE IF EXISTS `courses`;

DROP TABLE IF EXISTS `student`;

/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;

CREATE TABLE `student` (
  `idStudent` int NOT NULL AUTO_INCREMENT,
  `student_name` varchar(100) NOT NULL,
  `email` varchar(50) UNIQUE,
  `password` varchar(255),
  `address` varchar(255),
  `phone_num` char(12),
  `sex` varchar(6),
  `birthdate` char(10),
  `university` char(255),
  `years_attended` char(20),
  `degree_title` char(255),
  `extracted_text` LONGTEXT, 

  PRIMARY KEY (`idStudent`)
);

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
    program ENUM('MS', 'PhD', 'Bioinformatics') NOT NULL,  
    core_course_code VARCHAR(50) NOT NULL,
    prereq_course_code VARCHAR(50) NOT NULL,  
    description VARCHAR(1000) NOT NULL
);

INSERT INTO prereqs (program, core_course_code, prereq_course_code, description) VALUES
('MS', 'CS204', 'CS133', 'Alphabet, words, languages and algorithmic problems, finite automata and hierarchy of languages, Turing machines, tractable and intractable problems, uncomputable functions, the halting problem'),
('PhD', 'CS204', 'CS133', 'Alphabet, words, languages and algorithmic problems, finite automata and hierarchy of languages, Turing machines, tractable and intractable problems, uncomputable functions, the halting problem'),
('Bioinformatics', 'Calculus and Matrix Algebra', 'Calculus Matrix Algebra Background', 'Elementary Analysis, Elementary Analysis I, Elementary Analysis II, Elementary Analysis III, Functions and their graphs, concepts of limit and continuity, theory of differentiation, derivatives of algebraic and trigonometric functions, theory of integrals, applications of the definite integral, Integration methods, determinants, plane and solid analytics, hyperbolic functions, polar coordinates, vectors, parametrics equations, Partial differentiation, multiple integrals, infinite series, differential equations'),

('MS', 'CS210', 'CS135', 'Algorithm analysis: asymptotic analysis, time and space tradeoffs, recurrence relations. Greedy, divide and conquer, heuristics and other algorithm design strategies. Fundamental computing algorithms for sorting, selection, trees and graphs. Intractability and approximation'),
('PhD', 'CS210', 'CS135', 'Algorithm analysis: asymptotic analysis, time and space tradeoffs, recurrence relations. Greedy, divide and conquer, heuristics and other algorithm design strategies. Fundamental computing algorithms for sorting, selection, trees and graphs. Intractability and approximation'),
('Bioinformatics', 'Probability and Statistics', 'Stat101', 'Statistics, Elementary Statistics,	Presentation of data, frequency distributions, measures of central tendency, measures of dispersion, index numbers, probability distributions, statistical inference, correlation and regression'),

('MS', 'CS220', 'CS150', 'Survey of Programming Languages: History and overview of programming languages, Programming paradigms: imperative, functional, object-oriented, logic, Type systems, Declaration and modularity, Introduction to syntax and semantics'),
('PhD', 'CS220', 'CS150', 'Survey of Programming Languages: History and overview of programming languages, Programming paradigms: imperative, functional, object-oriented, logic, Type systems, Declaration and modularity, Introduction to syntax and semantics'),
('Bioinformatics', 'Computer Programming', 'CS11', 'Basic Programming, Programming Constructs, Programming Logic'),

('MS', 'CS250', 'CS140', 'Operating system concepts; virtualization and multiprocessing, issues and considerations in designing and implementing common features of operating systems; virtual machines and hypervisors; introduction to real-time operating systems, and operating systems for embedded systems'),
('PhD', 'CS250', 'CS140', 'Operating system concepts; virtualization and multiprocessing, issues and considerations in designing and implementing common features of operating systems; virtual machines and hypervisors; introduction to real-time operating systems, and operating systems for embedded systems'),
('Bioinformatics', 'Biochemistry', 'Chem 40', 'An elementary treatment of structure-function relationship of biomolecules and biochemical mechanisms, Elementary Biochemistry'),

('MS', 'CS260', 'CS192', 'Software Implementation and Maintenance, Integration Strategies, and Security Issues'),
('PhD', 'CS260', 'CS192', 'Software Implementation and Maintenance, Integration Strategies, and Security Issues'),
('Bioinformatics', 'Molecular Biology', 'MBB 110', 'Molecular diversity, physiology and genetics of microorganisms, Fundamentals of Molecular Microbiology'),

('MS', 'CS270', 'CS165', 'Relational database concepts: Entity Relation modeling, relational model, relational algebra, relational database design and normalization, structured query language, query optimization, File management, Storage and Indexing, Transaction Management, Data warehousing. Non-relational/modern database systems'),
('PhD', 'CS270', 'CS165', 'Relational database concepts: Entity Relation modeling, relational model, relational algebra, relational database design and normalization, structured query language, query optimization, File management, Storage and Indexing, Transaction Management, Data warehousing. Non-relational/modern database systems'),

('MS', 'Math Background', 'Math Background', 'Math, Statistics, Algebra, Probability, Statistics, Trigonometry, Calculus, Numerical Methods'),
('PhD', 'Math Background', 'Math Background', 'Math, Statistics, Algebra, Probability, Statistics, Trigonometry, Calculus, Numerical Methods');
