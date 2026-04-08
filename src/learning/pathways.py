from src.config.weights import SKILL_WEIGHTS

PRIORITY_THRESHOLD = 2.0

RESOURCE_CATALOG = {
    "AWS": [
        {
            "title": "AWS Cloud Practitioner Essentials",
            "url": "https://aws.amazon.com/training/digital/aws-cloud-practitioner-essentials/",
            "type": "Course",
        },
        {
            "title": "AWS in 10 Minutes",
            "url": "https://www.youtube.com/watch?v=r4YIdn2eTm4",
            "type": "Video",
        },
    ],
    "Docker": [
        {
            "title": "Docker Getting Started Guide",
            "url": "https://docs.docker.com/get-started/",
            "type": "Documentation",
        },
        {
            "title": "Docker in 100 Seconds",
            "url": "https://www.youtube.com/watch?v=Gjnup-PuquQ",
            "type": "Video",
        },
    ],
    "Kubernetes": [
        {
            "title": "Kubernetes Basics Tutorial",
            "url": "https://kubernetes.io/docs/tutorials/kubernetes-basics/",
            "type": "Documentation",
        },
        {
            "title": "Kubernetes Crash Course for Beginners",
            "url": "https://www.youtube.com/watch?v=s_o8dwzRlu4",
            "type": "Video",
        },
    ],
    "CI/CD": [
        {
            "title": "GitHub Actions Quickstart",
            "url": "https://docs.github.com/en/actions/quickstart",
            "type": "Documentation",
        },
        {
            "title": "CI/CD Explained",
            "url": "https://www.youtube.com/watch?v=scEDHsr3APg",
            "type": "Video",
        },
    ],
    "Jenkins": [
        {
            "title": "Jenkins User Documentation",
            "url": "https://www.jenkins.io/doc/",
            "type": "Documentation",
        },
        {
            "title": "Jenkins Full Course for Beginners",
            "url": "https://www.youtube.com/watch?v=FX322RVNGj4",
            "type": "Video",
        },
    ],
    "Terraform": [
        {
            "title": "Terraform Getting Started",
            "url": "https://developer.hashicorp.com/terraform/tutorials/aws-get-started",
            "type": "Documentation",
        },
        {
            "title": "Terraform in 100 Seconds",
            "url": "https://www.youtube.com/watch?v=tomUWcQ0P3k",
            "type": "Video",
        },
    ],
    "Linux": [
        {
            "title": "Linux Command Line Basics",
            "url": "https://ubuntu.com/tutorials/command-line-for-beginners",
            "type": "Documentation",
        },
        {
            "title": "Linux in 100 Seconds",
            "url": "https://www.youtube.com/watch?v=rrB13utjYV4",
            "type": "Video",
        },
    ],
    "Python": [
        {
            "title": "The Python Tutorial",
            "url": "https://docs.python.org/3/tutorial/",
            "type": "Documentation",
        },
        {
            "title": "Python Full Course for Beginners",
            "url": "https://www.youtube.com/watch?v=XKHEtdqhLK8",
            "type": "Video",
        },
    ],
    "Java": [
        {
            "title": "Oracle Java Tutorials",
            "url": "https://docs.oracle.com/javase/tutorial/",
            "type": "Documentation",
        },
        {
            "title": "Java Full Course for Beginners",
            "url": "https://www.youtube.com/watch?v=xk4_1vDrzzo",
            "type": "Video",
        },
    ],
    "C++": [
        {
            "title": "Learn C++ (LearnCpp.com)",
            "url": "https://www.learncpp.com/",
            "type": "Documentation",
        },
        {
            "title": "C++ in 100 Seconds",
            "url": "https://www.youtube.com/watch?v=MNeX4EGtR5Y",
            "type": "Video",
        },
    ],
    "C": [
        {
            "title": "C Programming Tutorial (Programiz)",
            "url": "https://www.programiz.com/c-programming",
            "type": "Documentation",
        },
    ],
    "SQL": [
        {
            "title": "SQL Tutorial (W3Schools)",
            "url": "https://www.w3schools.com/sql/",
            "type": "Documentation",
        },
        {
            "title": "SQL in 100 Seconds",
            "url": "https://www.youtube.com/watch?v=zsjvFFKOm3c",
            "type": "Video",
        },
    ],
    "Git": [
        {
            "title": "Pro Git Book",
            "url": "https://git-scm.com/book/en/v2",
            "type": "Documentation",
        },
        {
            "title": "Git & GitHub Crash Course",
            "url": "https://www.youtube.com/watch?v=RGOj5yH7evk",
            "type": "Video",
        },
    ],
    "Version Control": [
        {
            "title": "Version Control with Git (Atlassian)",
            "url": "https://www.atlassian.com/git",
            "type": "Documentation",
        },
    ],
    "Unit Testing": [
        {
            "title": "Python Unit Testing with pytest",
            "url": "https://docs.pytest.org/en/stable/getting-started.html",
            "type": "Documentation",
        },
        {
            "title": "Unit Testing in Python",
            "url": "https://www.youtube.com/watch?v=6tNS--WetLI",
            "type": "Video",
        },
    ],
    "TensorFlow": [
        {
            "title": "TensorFlow Quickstart for Beginners",
            "url": "https://www.tensorflow.org/tutorials/quickstart/beginner",
            "type": "Documentation",
        },
        {
            "title": "TensorFlow in 100 Seconds",
            "url": "https://www.youtube.com/watch?v=i8NETqtGHms",
            "type": "Video",
        },
    ],
    "PyTorch": [
        {
            "title": "PyTorch 60 Minute Blitz",
            "url": "https://pytorch.org/tutorials/beginner/deep_learning_60min_blitz.html",
            "type": "Documentation",
        },
        {
            "title": "PyTorch in 100 Seconds",
            "url": "https://www.youtube.com/watch?v=ORMx45xqWkA",
            "type": "Video",
        },
    ],
    "MLflow": [
        {
            "title": "MLflow Quickstart",
            "url": "https://mlflow.org/docs/latest/getting-started/index.html",
            "type": "Documentation",
        },
    ],
    "Airflow": [
        {
            "title": "Apache Airflow Tutorial",
            "url": "https://airflow.apache.org/docs/apache-airflow/stable/tutorial/index.html",
            "type": "Documentation",
        },
        {
            "title": "Airflow Tutorial for Beginners",
            "url": "https://www.youtube.com/watch?v=K9AnJ9_ZAXE",
            "type": "Video",
        },
    ],
}


def get_priority_missing_skills(missing_skills):
    """Return missing skills whose weight meets or exceeds the priority threshold."""
    priority = []
    for skill in missing_skills:
        weight = SKILL_WEIGHTS.get(skill, 1.0)
        if weight >= PRIORITY_THRESHOLD:
            priority.append(skill)
    priority.sort(key=lambda s: SKILL_WEIGHTS.get(s, 1.0), reverse=True)
    return priority


def get_learning_resources(missing_skills):
    """
    Given a list of missing skills, return curated learning resources
    for skills whose weight meets the priority threshold.

    Returns a list of dicts: [{"skill", "title", "url", "type"}, ...].
    """
    priority_skills = get_priority_missing_skills(missing_skills)
    resources = []
    for skill in priority_skills:
        entries = RESOURCE_CATALOG.get(skill, [])
        for entry in entries:
            resources.append(
                {
                    "skill": skill,
                    "title": entry["title"],
                    "url": entry["url"],
                    "type": entry["type"],
                }
            )
    return resources
