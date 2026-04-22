"""Anya Omega - Intent Compiler for Camelot CLI.

Analyzes directives through a 5-stage pipeline:
  1. Tokenize  2. Classify Intent  3. Detect Domain
  4. Assess Complexity  5. Compile Output
"""

import re

INTENT_PATTERNS = {
    "PLAN": [r"//PLAN", r"\bplan\b", r"\barchitect\b", r"\bdesign system\b", r"\bstructure\b"],
    "CREATE": [r"//FORGE", r"\bcreate\b", r"\bbuild\b", r"\bgenerate\b", r"\bimplement\b",
               r"\bwrite\b", r"\bmake\b", r"\badd\b", r"\bscaffold\b"],
    "RESEARCH": [r"\bresearch\b", r"\banalyze\b", r"\bcompare\b", r"\binvestigate\b",
                 r"\bfind\b", r"\blook up\b", r"\bexplain\b"],
    "DEBUG": [r"//HEAL", r"\bdebug\b", r"\bfix\b", r"\bdiagnose\b", r"\btroubleshoot\b",
              r"\berror\b", r"\bbug\b", r"\boptimize\b", r"\bperformance\b"],
    "AUDIT": [r"\baudit\b", r"\bscan\b", r"\bsweep\b", r"\bforensic\b",
              r"\btailscale\b", r"\btailscape\b", r"\bsentinel\b", r"\binventory\b",
              r"\bcve\b", r"\btrivy\b", r"\bmiri\b", r"\bcargo audit\b"],
    "SECURE": [r"\bsecurity\b", r"\bvulnerab\b", r"\bharden\b",
               r"\bpermission\b", r"\bauth\b", r"\bencrypt\b"],
    "DESIGN": [r"\bdesign\b", r"\bui\b", r"\bux\b", r"\bstyle\b", r"\blayout\b",
               r"\btheme\b", r"\bmockup\b", r"\bwireframe\b"],
    "EVOLVE": [r"//EVOLVE", r"//Evolve", r"\bevolve\b", r"\bself-improvement\b", r"\bupgrade internal\b"],
}

DOMAIN_PATTERNS = {
    "ENGINEERING": [r"\bapi\b", r"\broute\b", r"\bserver\b", r"\bdatabase\b", r"\bbackend\b",
                    r"\bfrontend\b", r"\bcomponent\b", r"\bfunction\b", r"\bclass\b",
                    r"\bnext\.?js\b", r"\breact\b", r"\bnode\b", r"\btypescript\b",
                    r"\bpython\b", r"\brust\b", r"\bgo\b", r"\bdocker\b"],
    "INFRASTRUCTURE": [r"\bdeploy\b", r"\bci\b", r"\bcd\b", r"\bpipeline\b", r"\bcloud\b",
                       r"\baws\b", r"\bkubernetes\b", r"\bterraform\b", r"\bnginx\b"],
    "DATA": [r"\bdata\b", r"\bsql\b", r"\bquery\b", r"\bschema\b", r"\bmigration\b",
             r"\banalytics\b", r"\bml\b", r"\bmodel\b"],
    "SECURITY": [r"\bsecurity\b", r"\bauth\b", r"\bcrypto\b", r"\bssl\b", r"\bcert\b"],
    "DESIGN": [r"\bui\b", r"\bux\b", r"\bcss\b", r"\bstyle\b", r"\bfigma\b", r"\bcolor\b"],
    "GENERAL": [],
}

COMPLEXITY_SIGNALS = {
    "high": [r"\bfull\b", r"\bentire\b", r"\bcomplete\b", r"\bsystem\b", r"\barchitecture\b",
             r"\bmulti", r"\bintegrat", r"\bscalable\b", r"\bmicroservice\b"],
    "medium": [r"\bwith\b.*\band\b", r"\bincluding\b", r"\bfeature\b", r"\bmodule\b"],
}


MAX_DIRECTIVE_LEN = 2000


def compile_intent(directive: str) -> dict:
    """5-stage intent compilation pipeline."""
    if len(directive) > MAX_DIRECTIVE_LEN:
        directive = directive[:MAX_DIRECTIVE_LEN]
    text = directive.lower().strip()

    # Stage 1: Tokenize
    tokens = re.findall(r'\w+|//\w+', text)

    # Stage 2: Classify intent
    intent = "CREATE"  # default
    best_score = 0
    for intent_type, patterns in INTENT_PATTERNS.items():
        score = sum(1 for p in patterns if re.search(p, text, re.I))
        if score > best_score:
            best_score = score
            intent = intent_type

    # Stage 3: Detect domain
    domain = "GENERAL"
    best_score = 0
    for dom, patterns in DOMAIN_PATTERNS.items():
        score = sum(1 for p in patterns if re.search(p, text, re.I))
        if score > best_score:
            best_score = score
            domain = dom

    # Stage 4: Assess complexity (1-5)
    complexity = 2
    if any(re.search(p, text, re.I) for p in COMPLEXITY_SIGNALS["high"]):
        complexity = 4
    elif any(re.search(p, text, re.I) for p in COMPLEXITY_SIGNALS["medium"]):
        complexity = 3
    if len(tokens) > 20:
        complexity = min(complexity + 1, 5)

    # Stage 5: Compile
    return {
        "directive": directive,
        "intent": intent,
        "domain": domain,
        "complexity": complexity,
        "tokens": tokens,
        "runic": directive.strip().startswith("//"),
    }
