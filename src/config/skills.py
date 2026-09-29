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
    "unit-test": "Unit Testing"
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
    "backend", "front end", "frontend", "platform", "embedded", "mlops"
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
    "REST API", "GraphQL", "Flask", "FastAPI", "Docker Compose", "Pip", "Conda", "Jupyter", "VSCode", "Linux", "FPGA", "Testing"
]


def _validate_canonical_names() -> None:
    """Fail fast if an alias maps to a skill that extraction would discard."""
    known = set(SOFT_ENG_SKILLS)
    unknown = (set(ALIASES.values()) | set(STRICT_SKILLS.values())) - known
    assert not unknown, f"Canonical skills missing from SOFT_ENG_SKILLS: {sorted(unknown)}"
    assert len(SOFT_ENG_SKILLS) == len(known), "SOFT_ENG_SKILLS contains duplicates"


_validate_canonical_names()
