import os
from dotenv import load_dotenv
load_dotenv()

for key in ["NEO4J_URI", "NEO4J_USER", "NEO4J_PASSWORD"]:
    v = os.getenv(key)
    print(key, "->", repr(v) if key != "NEO4J_PASSWORD" else f"length {len(v) if v else None}")