"""
Hand-labeled benchmark dataset for CVSyncAI.

Contents
--------
RESUMES   6 candidate resumes, one per role family.
JOBS      30 software job postings, 5 per role family. Each carries `gold_skills`:
          the skills from ALL_SKILLS a human reader would say the posting asks
          for (labeled by hand, independent of the extractor's output).
NON_TECH_POSTINGS
          12 non-software postings labeled the same way; used for extraction only.
EXTRACTION_CASES
          Short sentences targeting known hard cases for keyword extraction
          (aliases, ambiguous words like "go"/"C", skills inside other words).

Relevance for ranking is derived from role families: a posting in the same
family as the resume is relevant (grade 2), an adjacent family is partially
relevant (grade 1), anything else is irrelevant (grade 0).
"""

FAMILIES = ["ml", "devops", "backend", "embedded", "data_eng", "systems"]

ADJACENT = {
    frozenset({"ml", "data_eng"}),
    frozenset({"devops", "backend"}),
    frozenset({"devops", "systems"}),
    frozenset({"backend", "data_eng"}),
    frozenset({"embedded", "systems"}),
}


def relevance(resume_family: str, job_family: str) -> int:
    if resume_family == job_family:
        return 2
    if frozenset({resume_family, job_family}) in ADJACENT:
        return 1
    return 0


RESUMES = [
    {
        "id": "r_ml",
        "family": "ml",
        "text": """Priya Raman
SUMMARY
Machine learning engineer with three years building NLP and recommendation models.
SKILLS
Python, PyTorch, TensorFlow, scikit-learn, Pandas, NumPy, HuggingFace, MLflow, SQL, Git
EXPERIENCE
Machine Learning Engineer, Larkspur Analytics
- Fine-tuned BERT classifiers with HuggingFace Transformers to route 40k support tickets a week.
- Built feature pipelines in Pandas and trained gradient boosted models with XGBoost.
- Tracked experiments and model versions in MLflow; served models behind a FastAPI endpoint.
Data Science Intern, Northwind Health
- Trained PyTorch models to predict patient readmission and evaluated them with scikit-learn.
PROJECTS
- Word2Vec embeddings for product search, visualized with Matplotlib in Jupyter notebooks.
EDUCATION
B.Sc. Computer Science
""",
    },
    {
        "id": "r_devops",
        "family": "devops",
        "text": """Marcus Bell
SUMMARY
Platform engineer focused on cloud infrastructure, automation and reliability.
SKILLS
AWS, Terraform, Kubernetes, Docker, Jenkins, Linux, Bash, Python, CI/CD, Git
EXPERIENCE
DevOps Engineer, Copperline Logistics
- Managed AWS infrastructure (EC2, S3, VPC, Lambda) entirely as code with Terraform.
- Migrated 30 services from VMs to Kubernetes and containerized them with Docker.
- Owned Jenkins CI/CD pipelines and cut average deploy time from 40 to 8 minutes.
Systems Administrator, Halcyon College
- Maintained Linux servers and automated patching with Bash and Python scripts.
EDUCATION
Diploma, Computer Systems Technology
""",
    },
    {
        "id": "r_backend",
        "family": "backend",
        "text": """Elena Fischer
SUMMARY
Backend developer who builds reliable web APIs and data models.
SKILLS
Python, Flask, FastAPI, PostgreSQL, Redis, Docker, REST API, GraphQL, Git, Unit Testing
EXPERIENCE
Software Developer, Brightpath Payments
- Designed REST API endpoints in FastAPI serving 2M requests per day.
- Modeled billing data in PostgreSQL with SQLAlchemy and cached hot reads in Redis.
- Practiced test driven development with unit tests on every pull request and code review.
Junior Developer, Maple Street Media
- Built a GraphQL API with Flask and shipped features in two-week Agile sprints.
EDUCATION
B.Eng. Software Engineering
""",
    },
    {
        "id": "r_embedded",
        "family": "embedded",
        "text": """Tomás Ortega
SUMMARY
Embedded engineer working close to the hardware.
SKILLS
C, C++, Verilog, FPGA, Linux, Python, Git
EXPERIENCE
Firmware Engineer, Quillon Devices
- Wrote firmware in C for ARM microcontrollers driving motor controllers and sensors.
- Implemented signal processing blocks in Verilog and validated them on Xilinx FPGA boards.
- Built Python test fixtures that exercise hardware over serial and log results.
Hardware Co-op, Ridgeway Robotics
- Ported C++ drivers to embedded Linux and debugged timing issues with an oscilloscope.
EDUCATION
B.Eng. Electrical Engineering
""",
    },
    {
        "id": "r_data_eng",
        "family": "data_eng",
        "text": """Aisha Mensah
SUMMARY
Data engineer building batch and streaming pipelines.
SKILLS
Python, SQL, Spark, Airflow, AWS, S3, PostgreSQL, Docker, Pandas, Git
EXPERIENCE
Data Engineer, Tidewater Retail
- Orchestrated 120 daily ETL jobs in Airflow loading data from S3 into a warehouse.
- Rewrote slow Pandas jobs in Spark, reducing nightly runtime by 70%.
- Modeled reporting tables in PostgreSQL and wrote SQL data quality checks.
Analytics Intern, Pinecrest Insurance
- Automated weekly reports with Python and scheduled them with Luigi.
EDUCATION
B.Sc. Statistics
""",
    },
    {
        "id": "r_systems",
        "family": "systems",
        "text": """Daniel Kowalski
SUMMARY
Systems programmer interested in performance, concurrency and distributed systems.
SKILLS
C++, Go, Linux, Bash, Git, Docker, Unit Testing
EXPERIENCE
Software Engineer, Ironbark Networks
- Built a low-latency packet router in C++ with lock-free queues on Linux.
- Wrote Go microservices for cluster membership and health checking.
- Profiled hot paths and reduced p99 latency by 35%; added unit tests and code review gates.
Teaching Assistant, Operating Systems
- Helped students debug kernel modules and Bash tooling.
EDUCATION
B.Sc. Computer Science
""",
    },
]


JOBS = [
    # ---------------- ML ----------------
    {
        "id": "j_ml_1", "family": "ml",
        "title": "Machine Learning Engineer", "company": "Orchard AI",
        "text": """Machine Learning Engineer
Orchard AI
We are looking for an engineer to train and deploy deep learning models for document understanding.
You will fine-tune transformer models such as BERT using PyTorch and the HuggingFace ecosystem,
build evaluation datasets, and ship models to production.
Requirements: strong Python, experience with PyTorch, familiarity with MLflow for experiment tracking,
and comfort with Git based workflows.""",
        "gold_skills": ["Python", "PyTorch", "BERT", "HuggingFace", "MLflow", "Git", "Transformers",
                        "Machine Learning", "Deep Learning"],
    },
    {
        "id": "j_ml_2", "family": "ml",
        "title": "Data Scientist", "company": "Fernhill Bank",
        "text": """Data Scientist
Fernhill Bank
Join our risk team to build credit models. Day to day you will explore data in Jupyter,
engineer features with Pandas and NumPy, and train models with scikit-learn, XGBoost and LightGBM.
You will present findings with Matplotlib and Seaborn charts. SQL is required to pull data from our warehouse.""",
        "gold_skills": ["Jupyter", "Pandas", "NumPy", "scikit-learn", "XGBoost", "LightGBM", "Matplotlib", "Seaborn", "SQL"],
    },
    {
        "id": "j_ml_3", "family": "ml",
        "title": "NLP Engineer", "company": "Lexica Labs",
        "text": """NLP Engineer
Lexica Labs
Build language understanding features for our legal search product: entity extraction,
classification and semantic retrieval. You should know spaCy and NLTK, have trained neural networks
in TensorFlow or Keras, and understand embeddings such as Word2Vec and modern GPT style models.
Python is our primary language.""",
        "gold_skills": ["spaCy", "NLTK", "TensorFlow", "Keras", "Word2Vec", "GPT", "Python"],
    },
    {
        "id": "j_ml_4", "family": "ml",
        "title": "Applied Scientist, Recommendations", "company": "Streamwise",
        "text": """Applied Scientist, Recommendations
Streamwise
Improve how millions of listeners discover music. You will design ranking models, run offline
experiments and online A/B tests, and partner with engineers to productionize them.
We value a strong grasp of statistics and deep learning. Most of our modeling is done in Python
with PyTorch; experience with Kubeflow pipelines is a plus.""",
        "gold_skills": ["Python", "PyTorch", "Kubeflow", "Statistics", "Deep Learning"],
    },
    {
        "id": "j_ml_5", "family": "ml",
        "title": "Computer Vision Engineer", "company": "Kestrel Robotics",
        "text": """Computer Vision Engineer
Kestrel Robotics
Develop perception models that let our warehouse robots recognize packages. Train and optimize
convolutional networks, curate labeled image datasets and measure model accuracy in the field.
Experience with TensorFlow or PyTorch, NumPy and Python is required. Bonus: C++ for deploying models on device.""",
        "gold_skills": ["TensorFlow", "PyTorch", "NumPy", "Python", "C++"],
    },
    # ---------------- DevOps ----------------
    {
        "id": "j_devops_1", "family": "devops",
        "title": "DevOps Engineer", "company": "Cobalt Cloud",
        "text": """DevOps Engineer
Cobalt Cloud
Own our AWS footprint and the pipelines that ship code to it. You will write Terraform modules,
run workloads on Kubernetes, and keep Jenkins CI/CD healthy. Strong Linux and Bash skills expected;
Python for tooling is a plus.""",
        "gold_skills": ["AWS", "Terraform", "Kubernetes", "Jenkins", "CI/CD", "Linux", "Bash", "Python"],
    },
    {
        "id": "j_devops_2", "family": "devops",
        "title": "Site Reliability Engineer", "company": "Harborview Health",
        "text": """Site Reliability Engineer
Harborview Health
Keep our patient-facing services available around the clock. You will define SLOs, build monitoring
and alerting, lead incident response and automate toil away. We run containerized services with Docker
on Kubernetes in AWS. Experience scripting in Python or Go and deep Linux troubleshooting skills are essential.""",
        "gold_skills": ["Docker", "Kubernetes", "AWS", "Python", "Go", "Linux"],
    },
    {
        "id": "j_devops_3", "family": "devops",
        "title": "Cloud Infrastructure Engineer", "company": "Summit Freight",
        "text": """Cloud Infrastructure Engineer
Summit Freight
Design secure network topologies on AWS including VPC peering, IAM policies and EC2 autoscaling groups.
Store artifacts in S3 and run event driven jobs with Lambda. Infrastructure is managed in Terraform
and deployed through a CI/CD pipeline.""",
        "gold_skills": ["AWS", "VPC", "EC2", "S3", "Lambda", "Terraform", "CI/CD"],
    },
    {
        "id": "j_devops_4", "family": "devops",
        "title": "Platform Engineer", "company": "Gridline Energy",
        "text": """Platform Engineer
Gridline Energy
Build the internal developer platform our 200 engineers deploy to. You will maintain Kubernetes clusters,
write Helm charts, build golden-path templates and improve build and release automation.
Docker, Git and a scripting language such as Bash or Python are required.""",
        "gold_skills": ["Kubernetes", "Docker", "Git", "Bash", "Python"],
    },
    {
        "id": "j_devops_5", "family": "devops",
        "title": "Release Engineer", "company": "Quartzite Games",
        "text": """Release Engineer
Quartzite Games
Own the build farm that compiles and packages our games for every platform. Maintain Jenkins jobs,
manage version control branching strategy in Git, and automate release steps with shell scripts.
Linux administration experience required.""",
        "gold_skills": ["Jenkins", "Version Control", "Git", "Shell", "Linux"],
    },
    # ---------------- Backend ----------------
    {
        "id": "j_backend_1", "family": "backend",
        "title": "Backend Developer (Python)", "company": "Ledgerly",
        "text": """Backend Developer (Python)
Ledgerly
Build the APIs behind our accounting product. You will design REST API endpoints in FastAPI,
model data in PostgreSQL with SQLAlchemy, and write unit tests for everything you ship.
Docker and Git are part of the daily workflow.""",
        "gold_skills": ["REST API", "FastAPI", "PostgreSQL", "SQLAlchemy", "Unit Testing", "Docker", "Git", "Python"],
    },
    {
        "id": "j_backend_2", "family": "backend",
        "title": "Software Engineer, API Platform", "company": "Vantage Travel",
        "text": """Software Engineer, API Platform
Vantage Travel
Our public GraphQL gateway serves partners around the world. Help us scale it: design schemas,
optimize resolvers, and add caching with Redis. Our services are written in TypeScript and Python
and store data in PostgreSQL and MongoDB.""",
        "gold_skills": ["GraphQL", "Redis", "TypeScript", "Python", "PostgreSQL", "MongoDB"],
    },
    {
        "id": "j_backend_3", "family": "backend",
        "title": "Python Web Developer", "company": "Greenleaf Grocers",
        "text": """Python Web Developer
Greenleaf Grocers
Maintain and extend our ordering platform built on Flask and MySQL. You will fix bugs, add features
from our Scrum backlog, take part in code review, and practice test driven development.""",
        "gold_skills": ["Python", "Flask", "MySQL", "Scrum", "Code Review", "Test Driven Development"],
    },
    {
        "id": "j_backend_4", "family": "backend",
        "title": "Backend Engineer, Payments", "company": "Coinwell",
        "text": """Backend Engineer, Payments
Coinwell
Move money safely. You will build idempotent payment services, reconcile ledgers and design
database schemas that stay correct under concurrency. We use Java and SQL heavily, run services in Docker,
and expect thorough unit testing and careful code review.""",
        "gold_skills": ["Java", "SQL", "Docker", "Unit Testing", "Code Review"],
    },
    {
        "id": "j_backend_5", "family": "backend",
        "title": "Full Stack Developer", "company": "Brightside Learning",
        "text": """Full Stack Developer
Brightside Learning
Ship features end to end for our tutoring app: REST API endpoints in Node and Python on the server,
JavaScript on the client, and data in PostgreSQL. We work in Agile sprints and deploy with CI/CD.""",
        "gold_skills": ["REST API", "Python", "JavaScript", "PostgreSQL", "Agile", "CI/CD"],
    },
    # ---------------- Embedded ----------------
    {
        "id": "j_embedded_1", "family": "embedded",
        "title": "Firmware Engineer", "company": "Pulse Medical",
        "text": """Firmware Engineer
Pulse Medical
Develop firmware for wearable heart monitors. Write C for low power microcontrollers, bring up new boards,
and debug with JTAG and logic analyzers. Python for test automation is a plus.""",
        "gold_skills": ["C", "Python"],
    },
    {
        "id": "j_embedded_2", "family": "embedded",
        "title": "FPGA Design Engineer", "company": "Signalcraft",
        "text": """FPGA Design Engineer
Signalcraft
Design high speed digital logic for our radio products. You will write RTL in Verilog, run simulation and
timing closure, and verify designs on FPGA hardware in the lab.""",
        "gold_skills": ["Verilog", "FPGA"],
    },
    {
        "id": "j_embedded_3", "family": "embedded",
        "title": "Embedded Software Engineer", "company": "Northstar Automotive",
        "text": """Embedded Software Engineer
Northstar Automotive
Build software for vehicle electronic control units. Modern C++ on embedded Linux, CAN bus communication,
and real time constraints. Experience with Git and unit testing on target hardware is desired.""",
        "gold_skills": ["C++", "Linux", "Git", "Unit Testing"],
    },
    {
        "id": "j_embedded_4", "family": "embedded",
        "title": "Hardware Verification Engineer", "company": "Tessellate Semiconductor",
        "text": """Hardware Verification Engineer
Tessellate Semiconductor
Write testbenches that verify our next generation accelerator chips. Strong Verilog skills,
Python or Bash scripting for regressions, and a solid understanding of digital design.""",
        "gold_skills": ["Verilog", "Python", "Bash"],
    },
    {
        "id": "j_embedded_5", "family": "embedded",
        "title": "IoT Device Engineer", "company": "Hearthsense",
        "text": """IoT Device Engineer
Hearthsense
Our smart thermostats need firmware that never crashes. Write C and C++ drivers for sensors,
implement over the air updates, and squeeze performance out of devices with 256KB of RAM.""",
        "gold_skills": ["C", "C++"],
    },
    # ---------------- Data engineering ----------------
    {
        "id": "j_data_eng_1", "family": "data_eng",
        "title": "Data Engineer", "company": "Meridian Media",
        "text": """Data Engineer
Meridian Media
Build the pipelines that power our audience analytics. Orchestrate jobs in Airflow, process event data
with Spark, and land curated tables from S3 into our warehouse. Strong SQL and Python required.""",
        "gold_skills": ["Airflow", "Spark", "S3", "SQL", "Python"],
    },
    {
        "id": "j_data_eng_2", "family": "data_eng",
        "title": "Analytics Engineer", "company": "Fairway Insurance",
        "text": """Analytics Engineer
Fairway Insurance
Turn raw policy and claims data into trusted models for analysts. You will write modular SQL transformations,
define metrics, add data tests, and document lineage. Python and Git experience is a plus.""",
        "gold_skills": ["SQL", "Python", "Git"],
    },
    {
        "id": "j_data_eng_3", "family": "data_eng",
        "title": "Big Data Engineer", "company": "Atlas Telecom",
        "text": """Big Data Engineer
Atlas Telecom
Process billions of network events per day. Write Spark jobs, tune cluster performance on AWS,
and schedule workflows with Airflow or Luigi. Familiarity with NoSQL stores is a bonus.""",
        "gold_skills": ["Spark", "AWS", "Airflow", "Luigi", "NoSQL"],
    },
    {
        "id": "j_data_eng_4", "family": "data_eng",
        "title": "ETL Developer", "company": "Crescent Health Network",
        "text": """ETL Developer
Crescent Health Network
Integrate data from hospital systems into a central reporting database. Build extract, transform and load
processes with Python and Pandas, write PostgreSQL stored procedures, and monitor data quality.""",
        "gold_skills": ["Python", "Pandas", "PostgreSQL", "ETL"],
    },
    {
        "id": "j_data_eng_5", "family": "data_eng",
        "title": "Data Platform Engineer", "company": "Riverbend Capital",
        "text": """Data Platform Engineer
Riverbend Capital
Run the infrastructure our quants depend on: a lakehouse on AWS S3, Spark clusters and Airflow scheduling.
You will containerize jobs with Docker and manage access controls. Python and SQL are daily tools.""",
        "gold_skills": ["AWS", "S3", "Spark", "Airflow", "Docker", "Python", "SQL"],
    },
    # ---------------- Systems ----------------
    {
        "id": "j_systems_1", "family": "systems",
        "title": "Systems Software Engineer", "company": "Helix Storage",
        "text": """Systems Software Engineer
Helix Storage
Build the storage engine behind our distributed database. Write high performance C++ on Linux,
reason about concurrency, memory and disk IO, and profile everything.""",
        "gold_skills": ["C++", "Linux"],
    },
    {
        "id": "j_systems_2", "family": "systems",
        "title": "Distributed Systems Engineer (Go)", "company": "Relay Mesh",
        "text": """Distributed Systems Engineer (Go)
Relay Mesh
Develop our service mesh control plane in Go. You will work on consensus, service discovery and
networking, run everything in Docker containers on Linux, and write thorough unit tests.""",
        "gold_skills": ["Go", "Docker", "Linux", "Unit Testing"],
    },
    {
        "id": "j_systems_3", "family": "systems",
        "title": "Performance Engineer", "company": "Tachyon Trading",
        "text": """Performance Engineer
Tachyon Trading
Shave microseconds off our trading systems. Profile C++ services, tune the Linux kernel network stack,
and build benchmarks that catch regressions before release.""",
        "gold_skills": ["C++", "Linux"],
    },
    {
        "id": "j_systems_4", "family": "systems",
        "title": "Compiler Engineer", "company": "Lattice Languages",
        "text": """Compiler Engineer
Lattice Languages
Work on optimization passes and code generation for our language toolchain. Strong C++ and knowledge of
compiler internals required. You will review code, write tests and maintain the project in Git.""",
        "gold_skills": ["C++", "Code Review", "Testing", "Git"],
    },
    {
        "id": "j_systems_5", "family": "systems",
        "title": "Operating Systems Engineer", "company": "Kernelworks",
        "text": """Operating Systems Engineer
Kernelworks
Develop and maintain kernel drivers and low level system services. C programming on Linux,
Bash for tooling, and comfort reading assembly are required.""",
        "gold_skills": ["C", "Linux", "Bash"],
    },
]


# Short sentences for hard extraction cases. `gold` is the full set of skills
# expected; an empty list means nothing should be extracted.
EXTRACTION_CASES = [
    {"text": "We will go to the office on Mondays and go over the roadmap.", "gold": []},
    {"text": "Backend services are written in Golang.", "gold": ["Go"]},
    {"text": "Experience with Go and Kubernetes operators.", "gold": ["Go", "Kubernetes"]},
    {"text": "Account manager for a large accounting firm.", "gold": []},
    {"text": "Proficient in C and C++, some C# exposure.", "gold": ["C", "C++", "C#"]},
    {"text": "Report to the C-suite on quarterly budgets.", "gold": []},
    {"text": "Built models with sklearn and torch, tracked runs in ml flow.", "gold": ["scikit-learn", "PyTorch", "MLflow"]},
    {"text": "We practice TDD and keep CICD green.", "gold": ["Test Driven Development", "CI/CD"]},
    {"text": "Pipelines use hugging face models and spacy.", "gold": ["HuggingFace", "spaCy"]},
    {"text": "Writing unit tests is part of every story.", "gold": ["Unit Testing"]},
    {"text": "Comfortable in the terminal with Bash and Linux.", "gold": ["Bash", "Linux"]},
    {"text": "Our sparkling office has a great view.", "gold": []},
    {"text": "Expert in javascript and typescript.", "gold": ["JavaScript", "TypeScript"]},
    {"text": "Store blobs in S3 and trigger Lambda functions.", "gold": ["S3", "Lambda"]},
    {"text": "Please take a rest after your interview.", "gold": []},
    {"text": "Strong SQL; experience with PostgreSQL or MySQL.", "gold": ["SQL", "PostgreSQL", "MySQL"]},
    {"text": "Familiar with numpy, pandas and matplotlib.", "gold": ["NumPy", "Pandas", "Matplotlib"]},
    {"text": "Dockerized the app and wrote a docker compose file.", "gold": ["Docker", "Docker Compose"]},
    {"text": "The candidate must be a self starter with grit.", "gold": []},
    {"text": "Deployed with Jenkins and Terraform on AWS.", "gold": ["Jenkins", "Terraform", "AWS"]},
]


NON_TECH_POSTINGS = [
    {
        "title": "Staff Accountant", "domain": "Accounting & Finance",
        "text": """Staff Accountant
Pinewood Manufacturing
Support the controller with month end close: prepare journal entries, perform account reconciliations
and maintain the general ledger. Process accounts payable and assist with the annual audit.
Requirements: degree in accounting, working knowledge of GAAP, advanced Excel (pivot tables, VLOOKUP)
and experience with QuickBooks or NetSuite. CPA candidates preferred.""",
        "gold": ["Month-End Close", "Journal Entries", "Account Reconciliation", "General Ledger",
                 "Accounts Payable", "Auditing", "GAAP", "Excel", "Pivot Tables", "VLOOKUP",
                 "QuickBooks", "NetSuite", "CPA"],
    },
    {
        "title": "Financial Analyst", "domain": "Accounting & Finance",
        "text": """Financial Analyst
Harbor Point Hotels
Own budgeting and forecasting for our 12 properties. Build financial models, run variance analysis against plan,
and present financial reporting packages to leadership. Strong Excel and Power BI skills; SAP experience is a plus.""",
        "gold": ["Budgeting", "Forecasting", "Financial Modeling", "Variance Analysis", "Financial Reporting",
                 "Excel", "Power BI", "SAP"],
    },
    {
        "title": "Payroll Specialist", "domain": "Accounting & Finance",
        "text": """Payroll Specialist
Cedar Health Partners
Run bi-weekly payroll for 900 employees in ADP, reconcile payroll to the general ledger and answer employee
questions. Familiarity with benefits administration and Microsoft Office required.""",
        "gold": ["Payroll", "ADP", "General Ledger", "Benefits Administration", "Microsoft Office"],
    },
    {
        "title": "Account Executive", "domain": "Sales, Marketing & Service",
        "text": """Account Executive
Northbeam Software
Own the full sales cycle for mid-market B2B accounts: lead generation, cold calling, discovery, negotiation and close.
Keep your pipeline current in Salesforce and partner with account management on renewals and upselling.""",
        "gold": ["B2B Sales", "Lead Generation", "Cold Calling", "Negotiation", "Salesforce",
                 "Account Management", "Upselling"],
    },
    {
        "title": "Digital Marketing Coordinator", "domain": "Sales, Marketing & Service",
        "text": """Digital Marketing Coordinator
Willow & Pine Apparel
Plan and execute email marketing campaigns, manage our social media calendar and improve organic traffic through SEO.
Report on campaign results with Google Analytics. HubSpot experience and an eye for content marketing are a plus.""",
        "gold": ["Digital Marketing", "Email Marketing", "Social Media Marketing", "SEO", "Google Analytics",
                 "HubSpot", "Content Marketing"],
    },
    {
        "title": "Customer Service Representative", "domain": "Sales, Marketing & Service",
        "text": """Customer Service Representative
Brightline Utilities
Answer inbound calls in a busy call center, resolve billing questions and update accounts in our CRM.
Previous customer service experience and basic computer skills required.""",
        "gold": ["Call Center", "Billing", "CRM", "Customer Service"],
    },
    {
        "title": "HR Generalist", "domain": "Human Resources",
        "text": """HR Generalist
Granite Construction Group
Partner with site managers on recruiting, onboarding and employee relations. Maintain records in our HRIS,
support the annual performance management cycle and help track OSHA safety training completion.""",
        "gold": ["Recruiting", "Onboarding", "Employee Relations", "HRIS", "Performance Management", "OSHA"],
    },
    {
        "title": "Registered Nurse", "domain": "Healthcare",
        "text": """Registered Nurse, Medical-Surgical
St. Brendan's Hospital
Provide direct patient care for up to five patients per shift: monitor vital signs, handle medication administration
and document care in the EHR. Current BLS certification required; knowledge of HIPAA expected.""",
        "gold": ["Patient Care", "Vital Signs", "Medication Administration", "EHR", "BLS", "HIPAA"],
    },
    {
        "title": "Business Analyst", "domain": "Business & Analytics",
        "text": """Business Analyst
Keystone Insurance
Lead requirements gathering with underwriting and claims teams, perform gap analysis on current workflows and
write user stories in Jira. Coordinate user acceptance testing and document processes in Confluence and Visio.
SQL and Tableau experience preferred.""",
        "gold": ["Requirements Gathering", "Underwriting", "Gap Analysis", "Jira", "User Acceptance Testing",
                 "Confluence", "Visio", "SQL", "Tableau"],
    },
    {
        "title": "Operations Manager", "domain": "Project & Operations Management",
        "text": """Operations Manager
Riverside Distribution
Run day to day warehouse operations: inventory management, vendor management and procurement of supplies.
Drive process improvement using Six Sigma methods and track KPIs in Excel. PMP is a plus.""",
        "gold": ["Inventory Management", "Vendor Management", "Procurement", "Process Improvement", "Six Sigma",
                 "Excel", "PMP"],
    },
    {
        "title": "Middle School Teacher", "domain": "Education",
        "text": """Grade 7 Science Teacher
Oakridge Public Schools
Deliver engaging science lessons, contribute to curriculum development and maintain a positive learning environment
through strong classroom management. Lesson planning and experience supporting special education students required.""",
        "gold": ["Curriculum Development", "Classroom Management", "Lesson Planning", "Special Education"],
    },
    {
        "title": "Graphic Designer", "domain": "Design & Engineering",
        "text": """Graphic Designer
Lumen Creative Agency
Create brand assets, packaging and campaign visuals. Expert in Adobe Photoshop, Illustrator and InDesign;
Figma for web mockups. Some video editing and copywriting experience is a bonus.""",
        "gold": ["Adobe Photoshop", "Adobe Illustrator", "Adobe InDesign", "Figma", "Video Editing", "Copywriting"],
    },
]

EXTRACTION_CASES += [
    {"text": "You will excel in a fast-paced, collaborative environment.", "gold": []},
    {"text": "Employees may purchase company stock at a discount.", "gold": []},
    {"text": "Please send your resume to Bill in the hiring office.", "gold": []},
    {"text": "The outlook for this team is very positive.", "gold": []},
    {"text": "We value strong communication and teamwork.", "gold": []},
    {"text": "Reconciled A/R and A/P weekly in QuickBooks.", "gold": ["Accounts Receivable", "Accounts Payable", "QuickBooks"]},
    {"text": "Built dashboards in PowerBI and MS Excel.", "gold": ["Power BI", "Excel"]},
    {"text": "Certified Public Accountant with Sarbanes-Oxley experience.", "gold": ["CPA", "SOX Compliance"]},
    {"text": "Maintained electronic medical records and performed phlebotomy.", "gold": ["EHR", "Phlebotomy"]},
    {"text": "Led talent acquisition and onboarding for 40 new hires.", "gold": ["Recruiting", "Onboarding"]},
]
