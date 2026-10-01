from src.config.skills import ALL_SKILLS

SKILL_WEIGHTS = {
    # Cloud / DevOps
    "AWS": 3.0,
    "Docker": 3.0,
    "Kubernetes": 3.0,
    "CI/CD": 2.5,
    "Jenkins": 2.0,
    "Terraform": 2.5,
    "Linux": 2.5,

    # Core SWE
    "Python": 2.5,
    "Java": 2.5,
    "C++": 2.5,
    "C": 2.0,
    "SQL": 2.0,
    "Git": 2.0,
    "Version Control": 2.0,
    "Unit Testing": 2.0,
    "Code Review": 1.8,

    # Data/ML
    "TensorFlow": 2.0,
    "PyTorch": 2.0,
    "MLflow": 2.0,
    "Airflow": 2.0,

    # Process
    "Agile": 1.0,
    "Scrum": 1.0,
    "Shell": 1.2,
    "Bash": 1.2,

    # Embedded/Hardware
    "Verilog": 1.8,
    "FPGA": 1.8,
    "NoSQL": 1.5,
    "Pip": 1.0,
}

# Tuned on the resume/JD fit benchmark train split (see benchmarks/FIT_RESULTS.md):
# semantic similarity carries most of the signal; a small skill share breaks ties.
SKILL_SCORE_WEIGHT = 0.1

_unknown = set(SKILL_WEIGHTS) - set(ALL_SKILLS)
assert not _unknown, f"SKILL_WEIGHTS keys missing from ALL_SKILLS: {sorted(_unknown)}"
