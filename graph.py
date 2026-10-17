import os
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()

driver = GraphDatabase.driver(
    os.getenv("NEO4J_URI"),
    auth=(
        os.getenv("NEO4J_USER") or os.getenv("NEO4J_USERNAME"),
        os.getenv("NEO4J_PASSWORD"),
    ),
)


def run(query, **params):
    with driver.session() as s:
        return [r.data() for r in s.run(query, **params)]


def create_profile(name, role, skills: dict):
    # Reset any old skills/target for this person, then rebuild
    run("""
        MERGE (p:Person {name:$name})
        WITH p
        OPTIONAL MATCH (p)-[r:HAS_SKILL|TARGETS]->()
        DELETE r
    """, name=name)
    run("""
        MATCH (p:Person {name:$name}), (r:JobRole {name:$role})
        MERGE (p)-[:TARGETS]->(r)
    """, name=name, role=role)
    for skill, level in skills.items():
        run("""
            MATCH (p:Person {name:$name}), (s:Skill {name:$skill})
            MERGE (p)-[h:HAS_SKILL]->(s)
            SET h.level = $level
        """, name=name, skill=skill, level=level)


def skill_gap(name):
    return run("""
        MATCH (p:Person {name:$name})-[:TARGETS]->(r:JobRole)-[req:REQUIRES]->(s:Skill)
        OPTIONAL MATCH (p)-[h:HAS_SKILL]->(s)
        WITH s, req, coalesce(h.level, 0) AS have
        WHERE have < req.min_level
        OPTIONAL MATCH (res:LearningResource)-[:TEACHES]->(s)
        RETURN s.name AS skill, have, req.min_level AS needed,
               req.importance AS importance,
               collect(DISTINCT {title:res.title, url:res.url, hours:res.hours}) AS resources
        ORDER BY importance DESC
    """, name=name)


def missing_prereqs(name, skill):
    return run("""
        MATCH (p:Person {name:$name}), (target:Skill {name:$skill})
        MATCH (pre:Skill)-[:PREREQUISITE_OF*1..4]->(target)
        WHERE NOT (p)-[:HAS_SKILL]->(pre)
        RETURN DISTINCT pre.name AS prerequisite
    """, name=name, skill=skill)