"""
Fallback question bank used when Groq is unavailable or returns malformed
output. Sector-keyed so we always serve a relevant challenge.
"""
from typing import Any, Dict

FALLBACK_QUESTIONS: Dict[str, list] = {
    "web_dev": [
        {"id": 1, "question": "Pointing to a photograph, a man said, 'I have no brother, and that man's father is my father's son.' Whose photograph was it?", "options": ["His son", "His own", "His father", "His nephew"], "correct": 0},
        {"id": 2, "question": "A is the mother of B and C. If D is the husband of C, what is A to D?", "options": ["Mother", "Sister", "Aunt", "Mother-in-law"], "correct": 3},
        {"id": 3, "question": "If 'A + B' means A is the brother of B; 'A x B' means A is the father of B. Which of the following means C is the son of M?", "options": ["M x N + C", "F x C + N", "N + M x C", "M x C + N"], "correct": 3},
        {"id": 4, "question": "Look at this series: 2, 1, (1/2), (1/4)... What number should come next?", "options": ["(1/3)", "(1/8)", "(2/8)", "(1/16)"], "correct": 1},
        {"id": 5, "question": "SCD, TEF, UGH, ____, WKL", "options": ["CMN", "UJI", "VIJ", "IJT"], "correct": 2},
    ],
    "data_ai": [
        {"id": 1, "question": "Introducing a boy, a girl said, 'He is the son of the daughter of the father of my uncle.' How is the boy related to the girl?", "options": ["Brother", "Nephew", "Uncle", "Son-in-law"], "correct": 0},
        {"id": 2, "question": "Look at this series: 7, 10, 8, 11, 9, 12, ... What number should come next?", "options": ["7", "10", "12", "13"], "correct": 1},
        {"id": 3, "question": "If South-East becomes North, North-East becomes West and so on. What will West become?", "options": ["North-East", "North-West", "South-East", "South-West"], "correct": 2},
        {"id": 4, "question": "A man walks 5 km toward south and then turns to the right. After walking 3 km he turns to the left and walks 5 km. Now in which direction is he from the starting place?", "options": ["West", "South", "North-East", "South-West"], "correct": 3},
        {"id": 5, "question": "QAR, RAS, SAT, TAU, _____", "options": ["UAV", "UAT", "TAS", "TAT"], "correct": 0},
    ],
    "cloud_devops": [
        {"id": 1, "question": "Pointing to a photograph, a woman says, 'This man's son's sister is my mother-in-law.' How is the woman's husband related to the man in the photograph?", "options": ["Grandson", "Son", "Nephew", "Son-in-law"], "correct": 0},
        {"id": 2, "question": "FAG, GAF, HAI, IAH, _____", "options": ["JAK", "HAL", "HAK", "JAI"], "correct": 0},
        {"id": 3, "question": "Which word does not belong with the others?", "options": ["Tulip", "Rose", "Bud", "Daisy"], "correct": 2},
        {"id": 4, "question": "Odometer is to mileage as compass is to:", "options": ["Speed", "Hiking", "Needle", "Direction"], "correct": 3},
        {"id": 5, "question": "If A is the brother of B; B is the sister of C; and C is the father of D, how D is related to A?", "options": ["Brother", "Sister", "Nephew", "Cannot be determined"], "correct": 3},
    ],
    "cybersecurity": [
        {"id": 1, "question": "A is B's sister. C is B's mother. D is C's father. E is D's mother. Then, how is A related to D?", "options": ["Grandfather", "Grandmother", "Daughter", "Granddaughter"], "correct": 3},
        {"id": 2, "question": "Look at this series: 36, 34, 30, 28, 24, ... What number should come next?", "options": ["20", "22", "23", "26"], "correct": 1},
        {"id": 3, "question": "Which word does not belong with the others?", "options": ["Index", "Glossary", "Chapter", "Book"], "correct": 3},
        {"id": 4, "question": "Marathon is to race as hibernation is to:", "options": ["Winter", "Bear", "Dream", "Sleep"], "correct": 3},
        {"id": 5, "question": "A man said to a lady, 'Your mother's husband's sister is my aunt.' How is the lady related to the man?", "options": ["Daughter", "Granddaughter", "Mother", "Sister"], "correct": 3},
    ],
    "mobile_dev": [
        {"id": 1, "question": "A girl introduced a boy as the son of the daughter of the father of her uncle. The boy is girl's:", "options": ["Brother", "Son", "Uncle", "Son-in-law"], "correct": 0},
        {"id": 2, "question": "CMM, EOO, GQQ, _____, KUU", "options": ["GRR", "GSS", "ISS", "ITT"], "correct": 2},
        {"id": 3, "question": "Look at this series: 22, 21, 23, 22, 24, 23, ... What number should come next?", "options": ["22", "24", "25", "26"], "correct": 2},
        {"id": 4, "question": "Yard is to inch as quart is to:", "options": ["Gallon", "Ounce", "Milk", "Liquid"], "correct": 1},
        {"id": 5, "question": "Pointing to a man in a photograph, a woman said, 'His brother's father is the only son of my grandfather.' How is the woman related to the man?", "options": ["Mother", "Aunt", "Sister", "Daughter"], "correct": 2},
    ],
}


def get_fallback_challenge(sector: str, problem_description: str) -> Dict[str, Any]:
    """Return a complete challenge dict when Groq is unavailable."""
    sector_key = sector if sector in FALLBACK_QUESTIONS else "web_dev"
    return {
        "title": f"{sector.replace('_', ' ').title()} Skills Assessment",
        "round1_questions": FALLBACK_QUESTIONS[sector_key],
        "round2_problem": (
            f"Implement a solution for: {problem_description}. "
            "Handle edge cases and follow best practices."
        ),
        "round3_scenario": (
            f"You've joined a team working on: {problem_description}. "
            "Describe your approach, architecture decisions, and potential pitfalls."
        ),
    }
