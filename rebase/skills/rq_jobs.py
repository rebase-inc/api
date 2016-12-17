
from flask import current_app

from rebase.skills.ranking import compute_skills_ranking


def recompute_skills_ranking():
    current_app.default_queue(compute_skills_ranking)


