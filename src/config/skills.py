ALIASES = {
    # ML / frameworks
    "torch": "PyTorch",
    "pytorch": "PyTorch",
    "huggingface": "HuggingFace",
    "hugging face": "HuggingFace",
    "mlflow": "MLflow",
    "ml flow": "MLflow",
    "scikit learn": "scikit-learn",
    "sklearn": "scikit-learn",
    "scikit-learn": "scikit-learn",

    # Dev practices
    "cicd": "CI/CD",
    "ci cd": "CI/CD",
    "ci/cd": "CI/CD",
    "test driven development": "Test Driven Development",
    "tdd": "Test Driven Development",
    "unit tests": "Unit Testing",
    "unit-tests": "Unit Testing",
    "unit-test": "Unit Testing",

    # Software (extended)
    "nodejs": "Node.js",
    "node js": "Node.js",
    "react.js": "React",
    "reactjs": "React",
    "google cloud": "GCP",
    "google cloud platform": "GCP",
    "microsoft azure": "Azure",
    "asp.net": ".NET",
    "dotnet": ".NET",

    # Office / business tools
    "microsoft excel": "Excel",
    "ms excel": "Excel",
    "microsoft office": "Microsoft Office",
    "ms office": "Microsoft Office",
    "office 365": "Microsoft Office",
    "microsoft 365": "Microsoft Office",
    "microsoft word": "Microsoft Word",
    "ms word": "Microsoft Word",
    "microsoft outlook": "Outlook",
    "ms outlook": "Outlook",
    "microsoft access": "Microsoft Access",
    "ms access": "Microsoft Access",
    "microsoft project": "Microsoft Project",
    "ms project": "Microsoft Project",
    "powerbi": "Power BI",
    "power bi": "Power BI",
    "lean six sigma": "Six Sigma",
    "pivot table": "Pivot Tables",
    "vlookups": "VLOOKUP",

    # Accounting & finance
    "a/p": "Accounts Payable",
    "a/r": "Accounts Receivable",
    "gl": "General Ledger",
    "month end close": "Month-End Close",
    "month-end closing": "Month-End Close",
    "month end closing": "Month-End Close",
    "account reconciliations": "Account Reconciliation",
    "account reconciliation": "Account Reconciliation",
    "balance sheet reconciliations": "Account Reconciliation",
    "bank reconciliations": "Bank Reconciliation",
    "sarbanes-oxley": "SOX Compliance",
    "sarbanes oxley": "SOX Compliance",
    "sox": "SOX Compliance",
    "certified public accountant": "CPA",
    "anti-money laundering": "AML",
    "anti money laundering": "AML",

    # Sales, marketing & service
    "customer relationship management": "CRM",
    "search engine optimization": "SEO",
    "point of sale": "POS",
    "b2b": "B2B Sales",
    "social media": "Social Media Marketing",

    # HR
    "talent acquisition": "Recruiting",
    "full cycle recruiting": "Recruiting",
    "hris": "HRIS",

    # Healthcare
    "electronic health records": "EHR",
    "electronic medical records": "EHR",
    "emr": "EHR",
    "icd-10": "Medical Coding",
    "icd 10": "Medical Coding",
    "basic life support": "BLS",

    # Design & engineering
    "photoshop": "Adobe Photoshop",
    "illustrator": "Adobe Illustrator",
    "indesign": "Adobe InDesign",
    "adobe creative suite": "Adobe Creative Suite",
    "adobe creative cloud": "Adobe Creative Suite",
    "ux": "UX Design",
    "ui design": "UX Design",
}

# Single words that are also ordinary English ("you will excel", "outlook is
# positive"); matched only when capitalized and not tagged as a verb.
PROPER_NOUN_SKILLS = {
    "Excel": "Excel",
    "Outlook": "Outlook",
}

# Skills that are risky to match by substring
STRICT_SKILLS = {
    "go": "Go",
    "sql": "SQL",
    "c++": "C++",
    "c#": "C#",
    "c": "C"
}

TITLE_KEYWORDS = (
    "engineer", "developer", "software", "full stack", "full-stack",
    "backend", "front end", "frontend", "platform", "embedded", "mlops",
    # Non-technical roles
    "accountant", "analyst", "manager", "specialist", "coordinator", "consultant",
    "administrator", "assistant", "associate", "representative", "director",
    "designer", "technician", "nurse", "teacher", "recruiter", "supervisor",
    "architect", "scientist", "clerk", "controller", "auditor", "bookkeeper",
    "paralegal", "attorney", "chef", "cashier", "intern", "advisor", "officer",
)

NOISE_SUBSTRINGS = [
    "profile insights",
    "here’s how the job qualifications align with your profile",
    "job details",
    "full job description",
    "pulled from the full job description",
    "show more",
    "promoted by hirer",
    "responses managed off linkedin",
    "matches your job preferences",
    "&nbsp;",
]

NOISE_EXACT_LINES = {
    "apply", "apply now", "easy apply", "save",
    "benefits", "perks & benefits",
}

META_SUBSTRINGS = [
    "reposted", "clicked apply", "applicants"
]

SOFT_ENG_SKILLS = [
    #Languages
    "Python", "Java", "C++", "C#", "JavaScript", "TypeScript", "Go", "SQL", "Shell", "Bash", "C", "Verilog",

    #ML Frameworks
    "TensorFlow", "PyTorch", "Keras", "scikit-learn", "XGBoost", "LightGBM",

    #Data Frameworks
    "NumPy", "Pandas", "Matplotlib", "Seaborn", "Plotly", "SQLAlchemy", "Spark",

    #Natural Language Processing
    "spaCy", "NLTK", "Transformers", "HuggingFace", "BERT", "GPT", "Word2Vec",

    #Work Practices
    "Test Driven Development", "CI/CD", "Git", "Version Control", "Unit Testing", "Code Review", "Agile", "Scrum", "Paired Programming",

    #Databases
    "PostgreSQL", "MySQL", "MongoDB", "NoSQL", "Redis", "SQLite",

    #Cloud/DevOps/MLOps
    "AWS", "EC2", "S3", "Lambda", "VPC", "Docker", "Kubernetes", "Terraform", "Jenkins", "MLflow", "Kubeflow", "Airflow", "Tecton", "Luigi",

    #Misc
    "REST API", "GraphQL", "Flask", "FastAPI", "Docker Compose", "Pip", "Conda", "Jupyter", "VSCode", "Linux", "FPGA", "Testing",

    #Web / Cloud / Data (extended)
    "React", "Angular", "Node.js", "HTML", "CSS", "PHP", "Ruby", "Kotlin", "Swift", "Scala", "Rust", ".NET",
    "Azure", "GCP", "Snowflake", "Kafka", "Hadoop", "Databricks", "ETL", "Selenium", "Microservices",
    "Machine Learning", "Deep Learning",
]

# Skills for non-software roles, grouped by domain. Deliberately excludes
# generic soft skills ("communication", "teamwork") that appear in nearly
# every posting and so carry no matching signal.
DOMAIN_SKILLS = {
    "Software & Data": SOFT_ENG_SKILLS,
    "Accounting & Finance": [
        "Accounts Payable", "Accounts Receivable", "General Ledger", "Journal Entries",
        "Account Reconciliation", "Bank Reconciliation", "Month-End Close", "Financial Reporting",
        "Financial Statements", "Financial Analysis", "Financial Modeling", "Budgeting", "Forecasting",
        "Variance Analysis", "GAAP", "IFRS", "Auditing", "Internal Controls", "SOX Compliance",
        "Tax Preparation", "Payroll", "Bookkeeping", "Cost Accounting", "Fixed Assets", "Billing",
        "Invoicing", "CPA", "QuickBooks", "SAP", "NetSuite", "ERP", "Xero", "Underwriting",
        "Credit Analysis", "AML", "KYC", "Risk Management",
    ],
    "Business & Analytics": [
        "Excel", "Microsoft Office", "Microsoft Word", "Outlook", "Microsoft Access", "Pivot Tables",
        "VLOOKUP", "Tableau", "Power BI", "Looker", "Data Analysis", "Data Visualization",
        "Business Intelligence", "Business Analysis", "Requirements Gathering", "Gap Analysis",
        "User Acceptance Testing", "Process Improvement", "Stakeholder Management", "Statistics",
        "Market Research", "Jira", "Confluence", "Visio", "SharePoint",
    ],
    "Project & Operations Management": [
        "Project Management", "Program Management", "PMP", "Waterfall", "Kanban", "Six Sigma",
        "Change Management", "Vendor Management", "Microsoft Project", "Inventory Management",
        "Supply Chain", "Logistics", "Procurement", "Purchasing", "Quality Assurance",
        "Quality Control", "Operations Management",
    ],
    "Sales, Marketing & Service": [
        "Salesforce", "CRM", "HubSpot", "Lead Generation", "Cold Calling", "Account Management",
        "Business Development", "B2B Sales", "Negotiation", "Customer Retention", "Customer Service",
        "Customer Support", "Call Center", "POS", "Retail Sales", "Upselling", "Merchandising",
        "Digital Marketing", "SEO", "SEM", "Social Media Marketing", "Content Marketing",
        "Email Marketing", "Google Analytics", "Brand Management", "Public Relations",
    ],
    "Human Resources": [
        "Recruiting", "Onboarding", "Employee Relations", "Benefits Administration", "HRIS",
        "Performance Management", "Training and Development", "ADP",
    ],
    "Healthcare": [
        "Patient Care", "EHR", "HIPAA", "Medical Billing", "Medical Coding", "CPR", "BLS",
        "Phlebotomy", "Vital Signs", "Medication Administration", "Nursing", "Clinical Research",
        "Case Management",
    ],
    "Legal & Compliance": [
        "Regulatory Compliance", "Contract Management", "Contract Negotiation", "Legal Research",
        "Litigation", "Due Diligence",
    ],
    "Education": [
        "Curriculum Development", "Lesson Planning", "Classroom Management", "Tutoring",
        "Instructional Design", "Special Education",
    ],
    "Design & Engineering": [
        "Adobe Photoshop", "Adobe Illustrator", "Adobe InDesign", "Adobe Creative Suite", "Figma",
        "Graphic Design", "UX Design", "Video Editing", "Copywriting", "AutoCAD", "SolidWorks",
        "MATLAB", "Revit", "PLC", "HVAC", "Circuit Design", "OSHA", "Food Safety",
    ],
}

ALL_SKILLS = [skill for skills in DOMAIN_SKILLS.values() for skill in skills]

SKILL_DOMAIN = {skill: domain for domain, skills in DOMAIN_SKILLS.items() for skill in skills}


def _validate_canonical_names() -> None:
    """Fail fast if an alias maps to a skill that extraction would discard."""
    known = set(ALL_SKILLS)
    unknown = (set(ALIASES.values()) | set(STRICT_SKILLS.values()) | set(PROPER_NOUN_SKILLS.values())) - known
    assert not unknown, f"Canonical skills missing from DOMAIN_SKILLS: {sorted(unknown)}"
    assert len(ALL_SKILLS) == len(known), "DOMAIN_SKILLS contains duplicates"


_validate_canonical_names()
