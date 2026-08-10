#!/usr/bin/env python3
"""
Phase H Week 2: Learning Dashboard
Visualize pattern discovery and optimization candidates
"""

import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List


@dataclass
class DashboardMetrics:
    """Dashboard display metrics"""
    total_patterns: int = 0
    patterns_by_type: Dict = None
    total_candidates: int = 0
    candidates_by_category: Dict = None
    candidates_by_score: Dict = None
    average_candidate_impact: float = 0.0
    learning_health: str = "unknown"
    patterns_detected_last_24h: int = 0
    candidates_generated_last_24h: int = 0
    top_candidates: List = None


class LearningDashboard:
    """Dashboard for Phase H learning progress"""

    def __init__(self, patterns_db: str = "control_plane/patterns.db",
                 optimizations_db: str = "control_plane/optimizations.db"):
        """Initialize dashboard"""
        self.patterns_db = patterns_db
        self.optimizations_db = optimizations_db

    def get_pattern_metrics(self) -> Dict:
        """Get pattern discovery metrics"""
        metrics = {
            'total': 0,
            'by_type': {},
            'by_confidence': {'high': 0, 'medium': 0, 'low': 0},
            'average_confidence': 0.0,
            'recent': [],
        }

        if not Path(self.patterns_db).exists():
            return metrics

        try:
            conn = sqlite3.connect(self.patterns_db)
            c = conn.cursor()

            # Get all patterns
            c.execute('''
                SELECT id, pattern_type, name, confidence, last_detected, occurrence_count
                FROM patterns
                ORDER BY confidence DESC
            ''')

            patterns = c.fetchall()
            metrics['total'] = len(patterns)

            confidences = []
            for pattern_id, pattern_type, name, confidence, last_detected, occurrence_count in patterns:
                # Count by type
                if pattern_type not in metrics['by_type']:
                    metrics['by_type'][pattern_type] = 0
                metrics['by_type'][pattern_type] += 1

                # Count by confidence level
                if confidence >= 0.8:
                    metrics['by_confidence']['high'] += 1
                elif confidence >= 0.6:
                    metrics['by_confidence']['medium'] += 1
                else:
                    metrics['by_confidence']['low'] += 1

                confidences.append(confidence)

                # Recent patterns (top 5)
                if len(metrics['recent']) < 5:
                    metrics['recent'].append({
                        'name': name,
                        'type': pattern_type,
                        'confidence': round(confidence, 2),
                        'detected': last_detected,
                        'occurrences': occurrence_count,
                    })

            if confidences:
                metrics['average_confidence'] = round(sum(confidences) / len(confidences), 2)

            conn.close()
        except Exception as e:
            print(f"Error getting pattern metrics: {e}")

        return metrics

    def get_candidate_metrics(self) -> Dict:
        """Get optimization candidate metrics"""
        metrics = {
            'total': 0,
            'by_category': {},
            'by_score': {'high': 0, 'medium': 0, 'low': 0},
            'average_impact': 0.0,
            'average_score': 0.0,
            'ready_for_approval': 0,
            'top_candidates': [],
        }

        if not Path(self.optimizations_db).exists():
            return metrics

        try:
            conn = sqlite3.connect(self.optimizations_db)
            c = conn.cursor()

            # Get all candidates
            c.execute('''
                SELECT id, category, name, expected_impact_pct, composite_score,
                       confidence, safety_score, implementation_effort
                FROM candidates
                ORDER BY composite_score DESC
            ''')

            candidates = c.fetchall()
            metrics['total'] = len(candidates)

            impacts = []
            scores = []
            for (candidate_id, category, name, impact, score,
                 confidence, safety, effort) in candidates:

                # Count by category
                if category not in metrics['by_category']:
                    metrics['by_category'][category] = 0
                metrics['by_category'][category] += 1

                # Count by score
                if score >= 0.80:
                    metrics['by_score']['high'] += 1
                elif score >= 0.60:
                    metrics['by_score']['medium'] += 1
                else:
                    metrics['by_score']['low'] += 1

                # Ready for approval (confidence >= 70% and safety >= 75%)
                if confidence >= 0.70 and safety >= 0.75:
                    metrics['ready_for_approval'] += 1

                impacts.append(impact if impact else 0)
                scores.append(score if score else 0)

                # Top candidates
                if len(metrics['top_candidates']) < 5:
                    metrics['top_candidates'].append({
                        'name': name,
                        'category': category,
                        'impact': round(impact, 1) if impact else 0,
                        'score': round(score, 2) if score else 0,
                        'effort': effort,
                    })

            if impacts:
                metrics['average_impact'] = round(sum(impacts) / len(impacts), 1)
            if scores:
                metrics['average_score'] = round(sum(scores) / len(scores), 2)

            conn.close()
        except Exception as e:
            print(f"Error getting candidate metrics: {e}")

        return metrics

    def get_learning_health_status(self) -> Dict:
        """Compute learning health status"""
        health = {
            'status': 'initializing',
            'pattern_discovery_rate': 'unknown',
            'candidate_generation_rate': 'unknown',
            'quality_score': 0.0,
            'readiness_for_optimization': 'not_ready',
            'recommendations': [],
        }

        patterns = self.get_pattern_metrics()
        candidates = self.get_candidate_metrics()

        # Pattern discovery rate
        if patterns['total'] >= 3:
            health['pattern_discovery_rate'] = 'healthy'
            health['recommendations'].append(f"✓ Detected {patterns['total']} patterns")
        elif patterns['total'] > 0:
            health['pattern_discovery_rate'] = 'emerging'
            health['recommendations'].append(f"⚠ Only {patterns['total']} patterns detected, need more")
        else:
            health['pattern_discovery_rate'] = 'none'
            health['recommendations'].append("⚠ No patterns detected yet")

        # Candidate generation
        if candidates['total'] >= 5:
            health['candidate_generation_rate'] = 'healthy'
            health['recommendations'].append(f"✓ Generated {candidates['total']} candidates")
        elif candidates['total'] > 0:
            health['candidate_generation_rate'] = 'emerging'
            health['recommendations'].append(f"⚠ Only {candidates['total']} candidates, need more")
        else:
            health['candidate_generation_rate'] = 'none'
            health['recommendations'].append("⚠ No candidates generated yet")

        # Quality score (0-1)
        pattern_quality = min(patterns['average_confidence'], 1.0) if patterns['average_confidence'] > 0 else 0
        candidate_quality = min(candidates['average_score'], 1.0) if candidates['average_score'] > 0 else 0
        health['quality_score'] = round((pattern_quality + candidate_quality) / 2, 2)

        # Readiness for optimization
        if candidates['ready_for_approval'] >= 3 and health['quality_score'] >= 0.7:
            health['readiness_for_optimization'] = 'ready'
            health['status'] = 'healthy'
        elif candidates['total'] > 0 and health['quality_score'] >= 0.5:
            health['readiness_for_optimization'] = 'partial'
            health['status'] = 'emerging'
        else:
            health['readiness_for_optimization'] = 'not_ready'
            health['status'] = 'initializing'

        return health

    def get_improvement_projections(self) -> Dict:
        """Calculate expected improvements from candidates"""
        projections = {
            'total_potential_improvement': 0.0,
            'high_confidence_improvement': 0.0,
            'candidates_needed_for_5pct': 0,
            'candidates_needed_for_10pct': 0,
            'timeline': 'unknown',
        }

        if not Path(self.optimizations_db).exists():
            return projections

        try:
            conn = sqlite3.connect(self.optimizations_db)
            c = conn.cursor()

            # Get all high-quality candidates
            c.execute('''
                SELECT expected_impact_pct, confidence
                FROM candidates
                WHERE confidence >= 0.70 AND composite_score >= 0.60
                ORDER BY composite_score DESC
            ''')

            candidates = c.fetchall()

            # Calculate cumulative improvement (conservative: multiply by confidence)
            total_improvement = 0.0
            high_confidence_improvement = 0.0

            for impact, confidence in candidates:
                if impact:
                    weighted_impact = impact * confidence
                    total_improvement += weighted_impact
                    if confidence >= 0.85:
                        high_confidence_improvement += weighted_impact

            projections['total_potential_improvement'] = round(total_improvement, 1)
            projections['high_confidence_improvement'] = round(high_confidence_improvement, 1)

            # Estimate candidates needed
            for threshold, key in [(5.0, 'candidates_needed_for_5pct'),
                                    (10.0, 'candidates_needed_for_10pct')]:
                running_total = 0.0
                count = 0
                for impact, confidence in candidates:
                    if impact and running_total < threshold:
                        running_total += impact * confidence
                        count += 1
                projections[key] = count

            # Estimate timeline
            if len(candidates) >= 3:
                projections['timeline'] = '1-2 weeks (with implementation)'
            elif len(candidates) > 0:
                projections['timeline'] = '2-4 weeks (need more candidates)'
            else:
                projections['timeline'] = 'unknown (no candidates yet)'

            conn.close()
        except Exception as e:
            print(f"Error calculating projections: {e}")

        return projections

    def get_dashboard_display(self, mode: str = 'full') -> str:
        """Get formatted dashboard for display"""
        output = []

        output.append("\n" + "="*70)
        output.append("PHASE H WEEK 2: LEARNING DASHBOARD")
        output.append("="*70)

        # Patterns section
        patterns = self.get_pattern_metrics()
        output.append("\n📊 PATTERN DISCOVERY")
        output.append(f"  Total patterns: {patterns['total']}")
        output.append(f"  Average confidence: {patterns['average_confidence']:.0%}")
        for ptype, count in patterns['by_type'].items():
            output.append(f"    • {ptype}: {count}")

        # Candidates section
        candidates = self.get_candidate_metrics()
        output.append("\n🎯 OPTIMIZATION CANDIDATES")
        output.append(f"  Total candidates: {candidates['total']}")
        output.append(f"  Average impact: {candidates['average_impact']:.1f}%")
        output.append(f"  Average score: {candidates['average_score']:.0%}")
        output.append(f"  Ready for approval: {candidates['ready_for_approval']}")

        # Health status
        health = self.get_learning_health_status()
        output.append(f"\n💚 LEARNING HEALTH: {health['status'].upper()}")
        output.append(f"  Quality score: {health['quality_score']:.0%}")
        output.append(f"  Pattern discovery: {health['pattern_discovery_rate']}")
        output.append(f"  Candidate generation: {health['candidate_generation_rate']}")
        output.append(f"  Ready for optimization: {health['readiness_for_optimization']}")

        # Projections
        projections = self.get_improvement_projections()
        output.append("\n📈 IMPROVEMENT PROJECTIONS")
        output.append(f"  Total potential: {projections['total_potential_improvement']:.1f}%")
        output.append(f"  High confidence: {projections['high_confidence_improvement']:.1f}%")
        output.append(f"  Timeline: {projections['timeline']}")

        # Top candidates
        if candidates['top_candidates']:
            output.append("\n⭐ TOP CANDIDATES")
            for i, c in enumerate(candidates['top_candidates'], 1):
                output.append(f"  {i}. {c['name']}")
                output.append(f"     Impact: {c['impact']:.0f}% | Score: {c['score']:.0%} | Effort: {c['effort']}")

        # Recommendations
        if health['recommendations']:
            output.append("\n💡 RECOMMENDATIONS")
            for rec in health['recommendations']:
                output.append(f"  {rec}")

        output.append("\n" + "="*70 + "\n")

        return "\n".join(output)

    def get_json_export(self) -> Dict:
        """Export dashboard data as JSON"""
        return {
            'timestamp': datetime.now().isoformat(),
            'patterns': self.get_pattern_metrics(),
            'candidates': self.get_candidate_metrics(),
            'health': self.get_learning_health_status(),
            'projections': self.get_improvement_projections(),
        }


if __name__ == '__main__':
    dashboard = LearningDashboard()

    # Display dashboard
    print(dashboard.get_dashboard_display())

    # Export data
    data = dashboard.get_json_export()
    print("\nJSON Export:")
    print(json.dumps(data, indent=2))
