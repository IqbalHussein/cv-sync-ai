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

def match_resume_to_jobs(
    structured_jobs: list[dict], 
    resume: list[str], 
    resume_data: dict = None,
    progress_callback: Optional[Callable[[float], None]] = None
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
    
    # Pre-compute resume embeddings if data is available
    res_emb_full = None
    res_emb_exp = None
    res_emb_skills = None

    # Determine source text for resume evidence
    # Prefer full text from resume_data to get actual context sentences
    resume_context_text = " ".join(resume) # Default fallback
    if resume_data and resume_data.get("text"):
        resume_context_text = resume_data.get("text")

    if resume_data:
        semantic_matcher = get_semantic_matcher()
        
        # Extract sections
        res_text_full = resume_data.get("text", "")
        res_text_exp = resume_data.get("sections", {}).get("experience", "")
        # Try specific skills section, fallback to joined list of extracted skills
        res_text_skills = resume_data.get("sections", {}).get("skills", "")
        if not res_text_skills and resume:
            res_text_skills = " ".join(resume)

        # Encode once
        res_emb_full, res_emb_exp, res_emb_skills = semantic_matcher.encode_many(
            [res_text_full, res_text_exp, res_text_skills]
        )

    total_jobs = len(structured_jobs)
    score_progress_start = 0.0

    job_embs_full = []
    job_embs_skills = []
    if semantic_matcher:
        score_progress_start = EMBED_PROGRESS_SHARE
        for start in range(0, total_jobs, JOB_EMBED_BATCH):
            batch = structured_jobs[start:start + JOB_EMBED_BATCH]
            texts = [job.get("text", "") for job in batch]
            texts += [", ".join(job.get("skills", [])) for job in batch]
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
        if semantic_matcher and res_emb_full is not None:
            # We treat the full job text as the "Requirements" for comparison with Experience
            job_emb_full = job_embs_full[i]
            job_emb_skills = job_embs_skills[i]
            
            # Calculate components
            # 1. Experience vs Job Requirements (Full Text) - 50%
            sim_exp = semantic_matcher.compute_similarity_score(res_emb_exp, job_emb_full)
            
            # 2. Full vs Full - 30%
            sim_full = semantic_matcher.compute_similarity_score(res_emb_full, job_emb_full)
            
            # 3. Skills vs Skills - 20%
            sim_skills = semantic_matcher.compute_similarity_score(res_emb_skills, job_emb_skills)
            
            # Weighted Aggregate
            # Ensure negative similarities don't drag down score too much
            sim_exp = max(0.0, sim_exp)
            sim_full = max(0.0, sim_full)
            sim_skills = max(0.0, sim_skills)
            
            semantic_score = (0.5 * sim_exp) + (0.3 * sim_full) + (0.2 * sim_skills)

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
