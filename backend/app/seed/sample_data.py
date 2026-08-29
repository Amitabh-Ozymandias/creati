"""
VidyaSearch — Sample Indian College Resource Seed Data

Provides structured realistic academic documents across NPTEL, SWAYAM,
IITs, NITs, and GATE for immediate search engine indexing and testing.
"""

from typing import List, Dict

SAMPLE_DOCUMENTS: List[Dict] = [
    {
        "url": "https://nptel.ac.in/courses/106/106/106106184/",
        "title": "NPTEL :: Computer Science and Engineering - Data Structures and Algorithms",
        "domain": "nptel.ac.in",
        "description": "Comprehensive course on Data Structures and Algorithms by Prof. Naveen Garg, IIT Delhi. Covers asymptotic analysis, arrays, stacks, queues, trees, heaps, graphs, hashing, sorting, and dynamic programming.",
        "body": "NPTEL Data Structures and Algorithms by Prof. Naveen Garg, Department of Computer Science and Engineering, IIT Delhi. Module 1: Introduction to Data Structures and Asymptotic Analysis (Big-O, Big-Omega, Big-Theta). Module 2: Arrays, Linked Lists, Stacks and Queues. Implementation of FIFO queues and LIFO stacks. Module 3: Binary Trees, Binary Search Trees (BST), AVL Trees, Red-Black Trees, and B-Trees. Module 4: Heaps and Priority Queues, Binary Heap, Heapsort algorithm. Module 5: Graph Algorithms including Breadth First Search (BFS), Depth First Search (DFS), Dijkstra's shortest path, Bellman-Ford, Prim's and Kruskal's Minimum Spanning Tree (MST). Module 6: Sorting Algorithms - Quick Sort, Merge Sort, Radix Sort, Counting Sort. Module 7: Hashing with chaining and open addressing. Module 8: Dynamic Programming - Matrix Chain Multiplication, Longest Common Subsequence, 0/1 Knapsack problem.",
        "pagerank_score": 0.95,
    },
    {
        "url": "https://nptel.ac.in/courses/106/106/106106139/",
        "title": "NPTEL :: Computer Science and Engineering - Machine Learning",
        "domain": "nptel.ac.in",
        "description": "Machine Learning course by Prof. Balaraman Ravindran, IIT Madras. Covers supervised learning, unsupervised learning, neural networks, decision trees, SVM, reinforcement learning.",
        "body": "NPTEL Machine Learning course taught by Prof. Balaraman Ravindran at IIT Madras. Supervised Learning: Linear Regression, Logistic Regression, Cost Functions, Gradient Descent optimization. Classification techniques including Naive Bayes classifier, k-Nearest Neighbors (k-NN), Decision Trees (ID3, C4.5), and Support Vector Machines (SVM) with kernel trick. Unsupervised Learning: Clustering with k-Means, Hierarchical Clustering, Expectation Maximization, Gaussian Mixture Models (GMM), and Principal Component Analysis (PCA) for dimensionality reduction. Neural Networks: Perceptrons, Multi-Layer Perceptrons, Backpropagation algorithm, Activation functions (ReLU, Sigmoid, Tanh). Introduction to Deep Learning, Convolutional Neural Networks (CNN), Recurrent Neural Networks (RNN), and Reinforcement Learning (Q-learning, Bellman equation).",
        "pagerank_score": 0.92,
    },
    {
        "url": "https://nptel.ac.in/courses/106/105/106105152/",
        "title": "NPTEL :: Computer Science and Engineering - Database Management Systems",
        "domain": "nptel.ac.in",
        "description": "Database Management Systems (DBMS) course by Prof. Partha Pratim Das, IIT Kharagpur. Covers relational algebra, SQL, normalization (1NF to BCNF), indexing, transaction management, ACID properties.",
        "body": "NPTEL Database Management Systems (DBMS) by Prof. Partha Pratim Das, IIT Kharagpur. Topics covered include: Entity-Relationship (ER) model and Extended ER features. Relational Model, Relational Algebra and Tuple Relational Calculus. Structured Query Language (SQL) queries, joins, subqueries, aggregation, views, and integrity constraints. Database Normalization: Functional Dependencies, First Normal Form (1NF), Second Normal Form (2NF), Third Normal Form (3NF), Boyce-Codd Normal Form (BCNF), and Multi-valued dependencies (4NF). Storage and Indexing: B+ Trees, Hashing, Query Processing, Query Optimization. Transaction Management: ACID properties (Atomicity, Consistency, Isolation, Durability), Serializability, Concurrency Control protocols (2PL, Timestamp ordering, MVCC), Deadlock detection and recovery.",
        "pagerank_score": 0.88,
    },
    {
        "url": "https://nptel.ac.in/courses/106/105/106105215/",
        "title": "NPTEL :: Computer Science and Engineering - Deep Learning",
        "domain": "nptel.ac.in",
        "description": "Deep Learning course by Prof. Prabir Kumar Biswas, IIT Kharagpur. Deep neural networks, backpropagation, CNN, RNN, LSTM, Autoencoders, GANs, PyTorch and TensorFlow.",
        "body": "NPTEL Deep Learning course by Prof. Prabir Kumar Biswas, Department of Electronics and Electrical Communication Engineering, IIT Kharagpur. Foundations of Deep Neural Networks: Optimization with SGD, Adam, RMSprop. Regularization techniques: Dropout, Batch Normalization, L1/L2 weight decay. Convolutional Neural Networks (CNN): Convolution, pooling layers, architectures (AlexNet, VGG, ResNet, DenseNet) for computer vision and object detection (YOLO, Faster R-CNN). Sequence Modeling: Recurrent Neural Networks (RNN), Long Short-Term Memory (LSTM), Gated Recurrent Units (GRU), Attention mechanisms, and Transformer architecture. Generative Models: Autoencoders, Variational Autoencoders (VAE), Generative Adversarial Networks (GAN). Practical implementation in PyTorch and TensorFlow for Indian college students.",
        "pagerank_score": 0.89,
    },
    {
        "url": "https://swayam.gov.in/courses/cs-python-programming",
        "title": "SWAYAM :: Programming, Data Structures and Algorithms using Python",
        "domain": "swayam.gov.in",
        "description": "Python Programming course on SWAYAM by Prof. Madhavan Mukund, Chennai Mathematical Institute (CMI). Covers Python syntax, control flow, functions, recursion, sorting, search algorithms.",
        "body": "SWAYAM Online Course: Programming, Data Structures and Algorithms using Python by Prof. Madhavan Mukund (Chennai Mathematical Institute). This course introduces computer programming and algorithmic thinking using Python 3. Core concepts: Variables, data types, control flow (if-else, loops), functions, recursion, lists, dictionaries, tuples, sets, file handling, and exception handling. Algorithmic concepts: Linear search, binary search, selection sort, insertion sort, merge sort, quick sort. Object Oriented Programming (OOP) in Python: classes, objects, inheritance, polymorphism. Applications to scientific computing with NumPy and Pandas. Free certificate examination for Indian university and college students.",
        "pagerank_score": 0.85,
    },
    {
        "url": "https://swayam.gov.in/courses/ai-artificial-intelligence",
        "title": "SWAYAM :: Artificial Intelligence Search Methods for Problem Solving",
        "domain": "swayam.gov.in",
        "description": "Artificial Intelligence course by Prof. Deepak Khemani, IIT Madras. State space search, heuristic search, A* algorithm, game playing, minimax, alpha-beta pruning, constraint satisfaction.",
        "body": "SWAYAM Artificial Intelligence Search Methods for Problem Solving by Prof. Deepak Khemani, Department of Computer Science and Engineering, IIT Madras. State Space Search representations. Uninformed search strategies: Breadth First Search (BFS), Depth First Search (DFS), Depth Limited Search, Iterative Deepening. Informed (Heuristic) Search: Best First Search, Greedy Search, A* algorithm with admissible and consistent heuristics, Iterative Deepening A* (IDA*), Memory bounded A* (SMA*). Adversarial Game Playing: Minimax algorithm, Alpha-Beta Pruning, evaluation functions. Constraint Satisfaction Problems (CSP): Forward checking, arc consistency (AC-3), backtracking search. Knowledge Representation and First-Order Logic.",
        "pagerank_score": 0.82,
    },
    {
        "url": "https://www.cse.iitd.ac.in/~kolin/col331/",
        "title": "IIT Delhi :: COL331 - Operating Systems Course Resources & Lecture Notes",
        "domain": "iitd.ac.in",
        "description": "Operating Systems course COL331 by Prof. Sorav Bansal, IIT Delhi. Process management, threads, concurrency, semaphores, virtual memory, paging, file systems, Pintos / xv6 OS assignments.",
        "body": "IIT Delhi Department of Computer Science and Engineering. Course COL331: Operating Systems. Instructors: Prof. Sorav Bansal and Prof. Smruti Sarangi. Course syllabus: Process Management: Process states, PCB, CPU scheduling algorithms (Round Robin, FCFS, Shortest Job First, Multi-level feedback queue). Concurrency & Synchronization: Critical section problem, Peterson's algorithm, mutex locks, semaphores, monitors, classic synchronization problems (Dining Philosophers, Producer-Consumer, Reader-Writer). Deadlocks: Conditions, prevention, avoidance (Banker's algorithm), detection and recovery. Memory Management: Paging, segmentation, translation lookaside buffer (TLB), page replacement algorithms (FIFO, LRU, Optimal). Storage & File Systems: Disk scheduling, inode structure, ext4 file system, directory management. xv6 / Pintos kernel coding labs and past semester exams.",
        "pagerank_score": 0.87,
    },
    {
        "url": "https://www.cse.iitb.ac.in/~cs347/",
        "title": "IIT Bombay :: CS347 - Operating Systems Lecture Notes and Lab Manuals",
        "domain": "iitb.ac.in",
        "description": "CS347 Operating Systems at IIT Bombay by Prof. Mythili Vutukuru. Virtualization, kernel architecture, memory allocation, multi-core OS, networking subsystem.",
        "body": "IIT Bombay CS347: Operating Systems course material, lecture slides and assignment handouts by Prof. Mythili Vutukuru. Topics: OS abstractions, system calls (fork, exec, wait, pipe), Unix process model. CPU virtualization: scheduling policies, fairness, multi-core scheduling. Memory virtualization: address spaces, hardware page tables, multi-level paging, page fault handling, copy-on-write (COW). Concurrency: POSIX pthreads, condition variables, spinlocks, lock-free data structures. Persistence: file system implementation, journaling, crash consistency, SSDs and Flash memory. Virtual machines and hypervisors. Includes lab assignments based on Linux kernel modules and Pintos OS.",
        "pagerank_score": 0.86,
    },
    {
        "url": "https://www.nitt.edu/home/academics/departments/cse/courses/cnet/",
        "title": "NIT Trichy :: Computer Networks Syllabus, Laboratory Manual and Notes",
        "domain": "nitt.edu.in",
        "description": "NIT Trichy Department of CSE Computer Networks course notes. OSI 7-layer model, TCP/IP protocol suite, routing protocols, flow control, congestion control, socket programming.",
        "body": "National Institute of Technology, Tiruchirappalli (NIT Trichy) - Department of Computer Science and Engineering. Course: Computer Networks (CSLR31). Unit 1: Introduction to Data Communication, Network Topologies, OSI Reference Model and TCP/IP Architecture. Unit 2: Physical and Data Link Layer: Framing, Error Detection (CRC, Checksum, Hamming Code), Sliding Window protocols (Stop-and-Wait, Go-Back-N, Selective Repeat), Medium Access Control (CSMA/CD, CSMA/CA, Ethernet, Wi-Fi IEEE 802.11). Unit 3: Network Layer: IPv4 and IPv6 addressing, Subnetting, CIDR, Routing Algorithms (Distance Vector Routing, Link State Routing, OSPF, BGP). Unit 4: Transport Layer: UDP, TCP connection establishment (3-way handshake), TCP Congestion Control (Slow Start, Congestion Avoidance, Fast Retransmit, Fast Recovery). Unit 5: Application Layer: DNS, HTTP/HTTPS, FTP, SMTP. Socket programming in C and Python.",
        "pagerank_score": 0.79,
    },
    {
        "url": "https://gate.iitk.ac.in/gate-cse-syllabus-and-previous-papers",
        "title": "GATE Computer Science (CS & IT) Official Syllabus and Previous Year Questions (PYQs)",
        "domain": "gate.iitk.ac.in",
        "description": "GATE Computer Science Engineering official syllabus, solved question papers from 2010-2025, subject-wise weightage, answer keys, and mock tests for Indian engineering graduates.",
        "body": "Graduate Aptitude Test in Engineering (GATE) - Computer Science and Information Technology (CS/IT). Comprehensive preparation resource and solved previous year papers. Section 1: Engineering Mathematics (Discrete Mathematics, Graph Theory, Combinatorics, Linear Algebra, Calculus, Probability and Statistics). Section 2: Digital Logic (Boolean algebra, combinational and sequential circuits, minimization). Section 3: Computer Organization and Architecture (Machine instructions, addressing modes, ALU, pipelining, cache memory, memory hierarchy). Section 4: Programming and Data Structures (C programming, recursion, arrays, stacks, queues, linked lists, trees, binary search trees, binary heaps, graphs). Section 5: Algorithms (Searching, sorting, hashing, asymptotic worst-case time and space complexity, algorithm design techniques: greedy, dynamic programming and divide-and-conquer, graph search, minimum spanning trees, shortest paths). Section 6: Theory of Computation (Regular expressions, finite automata, context-free grammars, pushdown automata, Turing machines, undecidability). Section 7: Compiler Design (Lexical analysis, parsing, syntax-directed translation, runtime environments, intermediate code generation). Section 8: Operating Systems (Processes, threads, inter-process communication, concurrency, synchronization, deadlocks, CPU scheduling, memory management, virtual memory, file systems). Section 9: Databases (ER-model, relational model, relational algebra, tuple calculus, SQL, integrity constraints, normal forms, transaction and concurrency control). Section 10: Computer Networks (Concept of layering: OSI and TCP/IP, flow and error control, routing, IP addressing, TCP/UDP, sockets, application layer).",
        "pagerank_score": 0.94,
    },
    {
        "url": "https://www.iitm.ac.in/notices/academic-calendar-2026",
        "title": "IIT Madras :: Academic Calendar, Semester Registration & Examination Notice",
        "domain": "iitm.ac.in",
        "description": "Official Academic Notice from IIT Madras covering semester enrollment dates, course add/drop deadlines, mid-semester exams, end-semester exams, convocation schedule, and fee submission.",
        "body": "Indian Institute of Technology Madras (IIT Madras) - Office of Academic Affairs. Official Notification for B.Tech, Dual Degree, M.Tech, and Ph.D. students. Key Dates: Semester Registration and Course Enrollment opens on January 5. Course Add/Drop period ends on January 19. Mid-Semester Examinations: February 20 to February 27. Course Feedback window: April 10 to April 20. End-Semester Final Examinations: April 25 to May 8. Declaration of Results and Grade Cards on Student Portal by May 22. Summer Internship registration deadline: June 1. Library and hostel clearance procedures for graduating batch. Convocation scheduled for July 15. All students must ensure minimum 85% attendance in theory and lab sessions.",
        "pagerank_score": 0.75,
    },
    {
        "url": "https://www.ugc.gov.in/notices/ai-curriculum-guidelines-2026",
        "title": "UGC & AICTE :: National Curriculum Guidelines for Artificial Intelligence & Data Science",
        "domain": "ugc.gov.in",
        "description": "University Grants Commission (UGC) and All India Council for Technical Education (AICTE) directives on integrating AI, Machine Learning, and Ethics in undergraduate engineering degrees.",
        "body": "University Grants Commission (UGC) and AICTE Circular: Implementation of AI and Emerging Technologies Curriculum in all Indian Universities, Autonomous Engineering Colleges, and Institutes of National Importance. Key Directives: 1. Mandatory introduction of Foundations of Artificial Intelligence and Data Science as core subjects in B.Tech/B.E. 2nd Year. 2. Inclusion of Ethics in AI, Data Privacy, and Intellectual Property Rights modules. 3. Promotion of open access courseware through SWAYAM, NPTEL, and National Digital Library of India (NDLI). 4. Industry-academia collaboration for hands-on project work and student internships in cloud computing, generative AI, and quantum algorithms.",
        "pagerank_score": 0.77,
    }
]

# Sample link relationships for link graph
SAMPLE_LINKS = [
    ("https://nptel.ac.in/courses/106/106/106106184/", "https://nptel.ac.in/courses/106/106/106106139/", "Machine Learning Course"),
    ("https://nptel.ac.in/courses/106/106/106106184/", "https://nptel.ac.in/courses/106/105/106105152/", "DBMS Course"),
    ("https://nptel.ac.in/courses/106/106/106106139/", "https://nptel.ac.in/courses/106/105/106105215/", "Deep Learning"),
    ("https://swayam.gov.in/courses/cs-python-programming", "https://nptel.ac.in/courses/106/106/106106184/", "Data Structures"),
    ("https://swayam.gov.in/courses/ai-artificial-intelligence", "https://nptel.ac.in/courses/106/106/106106139/", "Machine Learning"),
    ("https://gate.iitk.ac.in/gate-cse-syllabus-and-previous-papers", "https://nptel.ac.in/courses/106/106/106106184/", "NPTEL Algorithms"),
    ("https://gate.iitk.ac.in/gate-cse-syllabus-and-previous-papers", "https://nptel.ac.in/courses/106/105/106105152/", "NPTEL DBMS"),
    ("https://gate.iitk.ac.in/gate-cse-syllabus-and-previous-papers", "https://www.cse.iitd.ac.in/~kolin/col331/", "IIT Delhi OS"),
    ("https://www.cse.iitd.ac.in/~kolin/col331/", "https://www.cse.iitb.ac.in/~cs347/", "IIT Bombay OS"),
    ("https://www.cse.iitb.ac.in/~cs347/", "https://www.cse.iitd.ac.in/~kolin/col331/", "IIT Delhi OS"),
    ("https://www.nitt.edu/home/academics/departments/cse/courses/cnet/", "https://gate.iitk.ac.in/gate-cse-syllabus-and-previous-papers", "GATE Syllabus"),
    ("https://www.iitm.ac.in/notices/academic-calendar-2026", "https://nptel.ac.in/courses/106/106/106106139/", "NPTEL IIT Madras"),
    ("https://www.ugc.gov.in/notices/ai-curriculum-guidelines-2026", "https://swayam.gov.in/courses/ai-artificial-intelligence", "SWAYAM AI"),
]
