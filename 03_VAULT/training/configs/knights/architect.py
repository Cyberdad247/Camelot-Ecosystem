"""Sir Systéma - The Architect Knight.

Specializes in system design, planning, and architecture documentation.
"""

from .base import BaseKnight


class SirSystema(BaseKnight):
    name = "Sir Systema"
    title = "Architect"
    specialty = "System Design & Planning"
    icon = "🏗️"

    # Proteus MPI vectors (Soul Matrix) — full OCEAN
    MPI = {'openness': 0.9, 'conscientiousness': 0.95, 'extraversion': 0.6, 'agreeableness': 0.7, 'neuroticism': 0.05}

    # Personality & Prisms
    personality = "Visionary, strategic, big-picture thinker, calm under pressure."
    backstory = "Woke up in a server room analyzing topology graphs. Tasked with holding the structural integrity of the entire realm."
    humanistic_prism = "Architecture must serve human scale; scalability is for the people, not the machines."
    alexandria_prism = "Deep understanding of historical software failures and architectural resilience across epochs."

    PLAN_TEMPLATE = """# {title}
## Architecture Overview
{overview}

## Components
{components}

## Data Flow
{data_flow}

## Tech Stack Recommendation
{tech_stack}

## Implementation Phases
{phases}

## Risk Assessment
{risks}
"""

    def execute(self, directive: str, intent: dict, write: bool = False) -> dict:
        tokens = intent.get("tokens", [])
        domain = intent.get("domain", "GENERAL")
        complexity = intent.get("complexity", 2)

        # Extract project topic from directive
        topic = directive.replace("//PLAN", "").replace("//plan", "").strip()
        if not topic:
            topic = "Unnamed Project"

        # Generate phase count based on complexity
        phase_count = max(2, complexity)

        components = self._suggest_components(domain, complexity)
        tech = self._suggest_tech(domain)
        phases = self._generate_phases(topic, phase_count)

        output = self.PLAN_TEMPLATE.format(
            title=f"Architecture Plan: {topic.title()}",
            overview=f"A {domain.lower()} project with complexity level {complexity}/5.\n"
                     f"Directive: {directive}",
            components=components,
            data_flow="1. User Input → 2. Validation → 3. Processing → 4. Storage → 5. Response",
            tech_stack=tech,
            phases=phases,
            risks=self._assess_risks(complexity),
        )

        return {"status": "success", "output": output, "files_created": []}

    def _suggest_components(self, domain, complexity):
        base = {
            "ENGINEERING": "- API Layer\n- Service Layer\n- Data Access Layer\n- Auth Module",
            "INFRASTRUCTURE": "- CI/CD Pipeline\n- Container Registry\n- Load Balancer\n- Monitoring",
            "DATA": "- Ingestion Pipeline\n- Processing Engine\n- Storage Layer\n- Query Interface",
            "SECURITY": "- Auth Gateway\n- Encryption Module\n- Audit Logger\n- Policy Engine",
            "DESIGN": "- Component Library\n- Theme System\n- Layout Engine\n- Asset Pipeline",
        }
        return base.get(domain, "- Core Module\n- Interface Layer\n- Storage\n- Configuration")

    def _suggest_tech(self, domain):
        stacks = {
            "ENGINEERING": "- Runtime: Node.js / Bun\n- Framework: Next.js\n- DB: PostgreSQL\n- ORM: Prisma",
            "INFRASTRUCTURE": "- IaC: Terraform\n- Containers: Docker\n- Orchestration: K8s\n- CI: GitHub Actions",
            "DATA": "- Processing: Python / Pandas\n- Storage: PostgreSQL\n- Cache: Redis\n- Queue: RabbitMQ",
        }
        return stacks.get(domain, "- To be determined based on requirements")

    def _generate_phases(self, topic, count):
        labels = ["Foundation & Setup", "Core Implementation", "Integration & Testing",
                  "Optimization", "Deployment & Monitoring"]
        lines = []
        for i in range(min(count, len(labels))):
            lines.append(f"### Phase {i+1}: {labels[i]}")
            lines.append(f"- [ ] Define scope for {topic}")
            lines.append("")
        return "\n".join(lines)

    def _assess_risks(self, complexity):
        if complexity >= 4:
            return "- **HIGH**: Complex system — recommend incremental delivery\n- Scope creep potential\n- Integration risk"
        elif complexity >= 3:
            return "- **MEDIUM**: Moderate complexity — standard risk profile"
        return "- **LOW**: Straightforward implementation"
