from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from src.config.weights import SKILL_WEIGHTS, SKILL_SCORE_WEIGHT
from src.matching.evidence import find_skill_evidence
from src.matching.semantic import get_semantic_matcher
import re
from typing import Callable, Optional

def _clean_evidence(evidence_list: list[str]) -> str:
    """
    Remove line number prefixes (e.g., 'L1: ') from evidence strings
    and combine them into a single text block.
    """
    clean_text = []
    for line in evidence_list:
        # Remove "L<number>: " prefix
        text = re.sub(r"^L\d+:\s*", "", line)
        clean_text.append(text)
    return " ".join(clean_text)

JOB_EMBED_BATCH = 8
EMBED_PROGRESS_SHARE = 0.8

# Semantic score = weighted sum of (resume experience vs job text,
# resume full text vs job text, resume skills vs job skills).
SEMANTIC_COMPONENT_WEIGHTS = (0.5, 0.3, 0.2)


def resume_semantic_texts(resume_data: dict, resume_skills: list[str]) -> list[str]:
    """Return the [full text, experience section, skills text] embedded for a resume."""
    full = resume_data.get("text", "")
    experience = resume_data.get("sections", {}).get("experience", "")
    # Try specific skills section, fallback to joined list of extracted skills
    skills = resume_data.get("sections", {}).get("skills", "")
    if not skills and resume_skills:
        skills = " ".join(resume_skills)
    return [full, experience, skills]


def job_semantic_texts(job: dict) -> list[str]:
    """Return the [full text, skills text] embedded for a job."""
    return [job.get("text", ""), ", ".join(job.get("skills", []))]


def semantic_score_from_embeddings(semantic_matcher, resume_embs, job_emb_full, job_emb_skills) -> float:
    """
    Combine component similarities into a single semantic score.

    The full job text stands in for the job's requirements when compared
    with the resume's experience section. Negative similarities are clamped
    to 0 so they don't drag the score down.
    """
    res_full, res_exp, res_skills = resume_embs
    sims = [
        semantic_matcher.compute_similarity_score(res_exp, job_emb_full),
        semantic_matcher.compute_similarity_score(res_full, job_emb_full),
        semantic_matcher.compute_similarity_score(res_skills, job_emb_skills),
    ]
    return sum(w * max(0.0, s) for w, s in zip(SEMANTIC_COMPONENT_WEIGHTS, sims))

def match_resume_to_jobs(
    structured_jobs: list[dict], 
    resume: list[str], 
    resume_data: dict = None,
    progress_callback: Optional[Callable[[float], None]] = None,
    semantic: bool = True,
) -> list[dict]:
    """
    Match a resume against multiple job postings using weighted skill scoring and multi-factor semantic analysis.
    
    For each job, calculates a match score based on:
    1. Weighted overlap between the resume's skills and the job's required skills.
    2. Contextual verification: Reduces score if skill context in resume differs significantly from job.
    3. Semantic similarity using embeddings (Full Text, Experience section, Skills section).
    
    The semantic score is a weighted aggregate:
    - 50% Resume Experience vs Job Text (Requirements)
    - 30% Resume Full Text vs Job Full Text
    - 20% Resume Skills Text vs Job Skills List

    The final score blends the two: SKILL_SCORE_WEIGHT * skill score +
    (1 - SKILL_SCORE_WEIGHT) * semantic score. Without resume_data, the
    final score equals the skill score.
    
    Args:
        structured_jobs: List of job dictionaries with 'skills', 'text', etc.
        resume: List of skill strings from the resume (legacy/fallback).
        resume_data: Complete resume dictionary containing 'text' and 'sections'.
        semantic: Set False to skip embeddings and score skills only, while still
            using resume_data's full text for evidence and context checks.
        progress_callback: Optional function to report progress (0.0 to 1.0).
            When semantic matching runs, the first EMBED_PROGRESS_SHARE of
            progress covers batched job embedding and the rest covers scoring.
        
    Returns:
        List of match result dictionaries sorted by final_score (descending), each containing:
        - Basic job info (id, title, company)
        - Match metrics (final_score, score, semantic_score, matched_count, matched_weight, total_weight)
        - Skill breakdowns (matched_skills, missing_skills)
        - Evidence snippets showing where skills appear in job and resume
    """
    resume_set = set(resume)
    results = []

    semantic_matcher = None
    tfidf_vectorizer = TfidfVectorizer(stop_words='english')
    resume_embs = None

    # Determine source text for resume evidence
    # Prefer full text from resume_data to get actual context sentences
    resume_context_text = " ".join(resume) # Default fallback
    if resume_data and resume_data.get("text"):
        resume_context_text = resume_data.get("text")

    if resume_data and semantic:
        semantic_matcher = get_semantic_matcher()
        # Encode once
        resume_embs = semantic_matcher.encode_many(resume_semantic_texts(resume_data, resume))

    total_jobs = len(structured_jobs)
    score_progress_start = 0.0

    job_embs_full = []
    job_embs_skills = []
    if semantic_matcher:
        score_progress_start = EMBED_PROGRESS_SHARE
        for start in range(0, total_jobs, JOB_EMBED_BATCH):
            batch = structured_jobs[start:start + JOB_EMBED_BATCH]
            job_texts = [job_semantic_texts(job) for job in batch]
            texts = [full for full, _ in job_texts] + [skills for _, skills in job_texts]
            embs = semantic_matcher.encode_many(texts)
            job_embs_full.extend(embs[:len(batch)])
            job_embs_skills.extend(embs[len(batch):])
            if progress_callback:
                progress_callback(EMBED_PROGRESS_SHARE * (start + len(batch)) / total_jobs)
    
    for i, job in enumerate(structured_jobs):
        job_skills = job.get("skills", [])
        job_set = set(job_skills)

        matched = sorted(job_set & resume_set)

        job_text = job.get("text", "")
        
        # --- Semantic Matching ---
        semantic_score = 0.0
        if semantic_matcher:
            semantic_score = semantic_score_from_embeddings(
                semantic_matcher, resume_embs, job_embs_full[i], job_embs_skills[i]
            )

        # Gather Evidence
        job_evidence = find_skill_evidence(job_text, matched)
        resume_evidence = find_skill_evidence(resume_context_text, matched)

        missing = sorted(job_set - resume_set)

        # --- Weighted Score Calculation with Context Verification ---
        total_weight = sum(SKILL_WEIGHTS.get(s, 1.0) for s in job_set)
        matched_weight = 0.0

        for skill in matched:
            base_weight = SKILL_WEIGHTS.get(skill, 1.0)
            
            # Context Verification using TF-IDF
            j_ev_lines = job_evidence.get(skill, [])
            r_ev_lines = resume_evidence.get(skill, [])
            
            if j_ev_lines and r_ev_lines:
                j_ctx = _clean_evidence(j_ev_lines)
                r_ctx = _clean_evidence(r_ev_lines)
                
                # Only compare if we have meaningful text in both
                if j_ctx.strip() and r_ctx.strip():
                    try:
                        # Create a small corpus of just these two contexts
                        tfidf_matrix = tfidf_vectorizer.fit_transform([j_ctx, r_ctx])
                        # Calculate cosine similarity between the two
                        context_sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
                        
                        # Apply penalty if context is too dissimilar
                        if context_sim < 0.4:
                            # 20% penalty for poor context match
                            base_weight *= 0.8
                    except ValueError:
                        # Can happen if text contains only stop words
                        pass

            matched_weight += base_weight

        score = matched_weight / max(1e-9, total_weight)  # avoid divide-by-zero

        if semantic_matcher:
            final_score = SKILL_SCORE_WEIGHT * score + (1 - SKILL_SCORE_WEIGHT) * semantic_score
        else:
            final_score = score

        results.append({
            "job_id": job.get("id"),
            "title": job.get("title"),
            "company": job.get("company"),
            "final_score": round(final_score, 3),
            "score": round(score, 3),
            "semantic_score": round(semantic_score, 3),
            "matched_skills": matched,
            "missing_skills": missing,
            "job_skill_count": len(job_set),
            "matched_count": len(matched),
            "matched_weight": round(matched_weight, 2),
            "total_weight": round(total_weight, 2),
            "evidence": {
                "job": job_evidence,
                "resume": resume_evidence
            }
        })
        
        if progress_callback:
            progress_callback(score_progress_start + (1 - score_progress_start) * (i + 1) / total_jobs)

    results.sort(key=lambda x: (x["final_score"], x["score"], x["semantic_score"], x["matched_weight"]), reverse=True)
    return results
