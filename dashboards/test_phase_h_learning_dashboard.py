#!/usr/bin/env python3
"""
Phase H Week 2: Learning Dashboard Tests
Verify visualization and metrics accuracy
"""

import json
import sqlite3
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

from phase_h_learning_dashboard import LearningDashboard


class TestLearningDashboard(unittest.TestCase):
    """Test learning dashboard functionality"""

    def setUp(self):
        """Create temporary databases"""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.patterns_db = str(Path(self.temp_dir.name) / "test_patterns.db")
        self.optimizations_db = str(Path(self.temp_dir.name) / "test_optimizations.db")

        # Create test databases
        self._create_test_databases()

        self.dashboard = LearningDashboard(
            patterns_db=self.patterns_db,
            optimizations_db=self.optimizations_db
        )

    def tearDown(self):
        """Clean up"""
        import gc
        gc.collect()
        try:
            self.temp_dir.cleanup()
        except Exception:
            pass

    def _create_test_databases(self):
        """Create test pattern and candidate databases"""
        # Patterns database
        conn = sqlite3.connect(self.patterns_db)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE patterns (
                id INTEGER PRIMARY KEY,
                pattern_type TEXT,
                name TEXT,
                metrics TEXT,
                confidence REAL,
                last_detected TIMESTAMP,
                occurrence_count INTEGER,
                created_at TIMESTAMP
            )
        ''')

        # Add test patterns
        patterns_data = [
            (1, 'temporal', 'Morning Spike', json.dumps({}), 0.92, datetime.now().isoformat(), 5),
            (2, 'load', 'Load Correlation', json.dumps({}), 0.88, datetime.now().isoformat(), 8),
            (3, 'error', 'Error Spike', json.dumps({}), 0.85, datetime.now().isoformat(), 3),
            (4, 'resource', 'Memory Creep', json.dumps({}), 0.80, datetime.now().isoformat(), 2),
        ]

        for pattern_data in patterns_data:
            c.execute('''
                INSERT INTO patterns
                VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))
            ''', pattern_data)

        conn.commit()
        conn.close()

        # Optimizations database
        conn = sqlite3.connect(self.optimizations_db)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE candidates (
                id INTEGER PRIMARY KEY,
                pattern_id INTEGER,
                category TEXT,
                name TEXT,
                description TEXT,
                current_value TEXT,
                suggested_value TEXT,
                expected_impact_pct REAL,
                confidence REAL,
                safety_score REAL,
                composite_score REAL,
                rationale TEXT,
                implementation_effort TEXT,
                accepted INTEGER,
                applied_at TIMESTAMP,
                result_impact_pct REAL,
                created_at TIMESTAMP
            )
        ''')

        # Add test candidates
        candidates_data = [
            (1, 1, 'parameter_tuning', 'Increase Pool', 'Desc', 'curr', 'sugg', 8.0, 0.92, 0.95, 0.82, 'rat', 'low'),
            (2, 2, 'resource_allocation', 'Add Indexes', 'Desc', 'curr', 'sugg', 12.0, 0.90, 0.88, 0.80, 'rat', 'med'),
            (3, 3, 'parameter_tuning', 'Timeout', 'Desc', 'curr', 'sugg', 25.0, 0.92, 0.92, 0.89, 'rat', 'low'),
            (4, 4, 'compression', 'Compression', 'Desc', 'curr', 'sugg', 20.0, 0.85, 0.80, 0.78, 'rat', 'med'),
            (5, 1, 'caching', 'Cache TTL', 'Desc', 'curr', 'sugg', 10.0, 0.80, 0.75, 0.71, 'rat', 'low'),
        ]

        for candidate_data in candidates_data:
            c.execute('''
                INSERT INTO candidates
                (id, pattern_id, category, name, description, current_value, suggested_value,
                 expected_impact_pct, confidence, safety_score, composite_score, rationale,
                 implementation_effort, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
            ''', candidate_data)

        conn.commit()
        conn.close()

    def test_dashboard_initialization(self):
        """Test dashboard initializes correctly"""
        self.assertIsNotNone(self.dashboard)
        self.assertEqual(self.dashboard.patterns_db, self.patterns_db)

    def test_pattern_metrics_extraction(self):
        """Test pattern metrics are extracted correctly"""
        metrics = self.dashboard.get_pattern_metrics()

        self.assertEqual(metrics['total'], 4)
        self.assertGreater(metrics['average_confidence'], 0)
        self.assertIn('temporal', metrics['by_type'])
        self.assertEqual(metrics['by_type']['temporal'], 1)
        self.assertEqual(metrics['by_confidence']['high'], 4)

    def test_candidate_metrics_extraction(self):
        """Test candidate metrics are extracted correctly"""
        metrics = self.dashboard.get_candidate_metrics()

        self.assertEqual(metrics['total'], 5)
        self.assertGreater(metrics['average_impact'], 0)
        self.assertGreater(metrics['average_score'], 0)
        self.assertIn('parameter_tuning', metrics['by_category'])

    def test_learning_health_status(self):
        """Test learning health status computation"""
        health = self.dashboard.get_learning_health_status()

        self.assertIn('status', health)
        self.assertIn('quality_score', health)
        self.assertIn('readiness_for_optimization', health)
        self.assertGreaterEqual(health['quality_score'], 0)
        self.assertLessEqual(health['quality_score'], 1.0)

        # Should be healthy with 4 patterns and 5 candidates
        self.assertEqual(health['status'], 'healthy')
        self.assertEqual(health['pattern_discovery_rate'], 'healthy')
        self.assertEqual(health['candidate_generation_rate'], 'healthy')

    def test_improvement_projections(self):
        """Test improvement projections calculation"""
        projections = self.dashboard.get_improvement_projections()

        self.assertIn('total_potential_improvement', projections)
        self.assertIn('timeline', projections)
        self.assertGreater(projections['total_potential_improvement'], 0)

    def test_top_candidates_display(self):
        """Test top candidates are displayed correctly"""
        candidates = self.dashboard.get_candidate_metrics()

        self.assertEqual(len(candidates['top_candidates']), 5)

        # Should be sorted by score (descending)
        if len(candidates['top_candidates']) > 1:
            self.assertGreaterEqual(
                candidates['top_candidates'][0]['score'],
                candidates['top_candidates'][1]['score']
            )

    def test_dashboard_display_formatting(self):
        """Test dashboard display formats correctly"""
        display = self.dashboard.get_dashboard_display()

        self.assertIn('PATTERN DISCOVERY', display)
        self.assertIn('OPTIMIZATION CANDIDATES', display)
        self.assertIn('LEARNING HEALTH', display)
        self.assertIn('IMPROVEMENT PROJECTIONS', display)
        self.assertIn('TOP CANDIDATES', display)

    def test_json_export(self):
        """Test JSON export structure"""
        data = self.dashboard.get_json_export()

        self.assertIn('timestamp', data)
        self.assertIn('patterns', data)
        self.assertIn('candidates', data)
        self.assertIn('health', data)
        self.assertIn('projections', data)

        # Verify structure
        self.assertIsInstance(data['patterns'], dict)
        self.assertIsInstance(data['candidates'], dict)
        self.assertIsInstance(data['health'], dict)
        self.assertIsInstance(data['projections'], dict)

    def test_empty_database_handling(self):
        """Test dashboard handles empty databases"""
        empty_dashboard = LearningDashboard(
            patterns_db=str(Path(self.temp_dir.name) / "empty_patterns.db"),
            optimizations_db=str(Path(self.temp_dir.name) / "empty_optimizations.db")
        )

        patterns = empty_dashboard.get_pattern_metrics()
        self.assertEqual(patterns['total'], 0)

        candidates = empty_dashboard.get_candidate_metrics()
        self.assertEqual(candidates['total'], 0)

        health = empty_dashboard.get_learning_health_status()
        self.assertEqual(health['status'], 'initializing')


class TestDashboardMetrics(unittest.TestCase):
    """Test specific metrics calculations"""

    def setUp(self):
        """Create test dashboard"""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.patterns_db = str(Path(self.temp_dir.name) / "metrics_patterns.db")
        self.optimizations_db = str(Path(self.temp_dir.name) / "metrics_optimizations.db")

        self._create_simple_databases()
        self.dashboard = LearningDashboard(
            patterns_db=self.patterns_db,
            optimizations_db=self.optimizations_db
        )

    def tearDown(self):
        """Clean up"""
        import gc
        gc.collect()
        try:
            self.temp_dir.cleanup()
        except Exception:
            pass

    def _create_simple_databases(self):
        """Create minimal test databases"""
        # Patterns
        conn = sqlite3.connect(self.patterns_db)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE patterns (
                id INTEGER PRIMARY KEY,
                pattern_type TEXT,
                name TEXT,
                metrics TEXT,
                confidence REAL,
                last_detected TIMESTAMP,
                occurrence_count INTEGER,
                created_at TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()

        # Optimizations
        conn = sqlite3.connect(self.optimizations_db)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE candidates (
                id INTEGER PRIMARY KEY,
                pattern_id INTEGER,
                category TEXT,
                name TEXT,
                description TEXT,
                current_value TEXT,
                suggested_value TEXT,
                expected_impact_pct REAL,
                confidence REAL,
                safety_score REAL,
                composite_score REAL,
                rationale TEXT,
                implementation_effort TEXT,
                accepted INTEGER,
                applied_at TIMESTAMP,
                result_impact_pct REAL,
                created_at TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()

    def test_zero_patterns_health(self):
        """Test health status with zero patterns"""
        health = self.dashboard.get_learning_health_status()

        self.assertEqual(health['pattern_discovery_rate'], 'none')
        self.assertIn('No patterns detected', ' '.join(health['recommendations']))

    def test_average_confidence_calculation(self):
        """Test average confidence is calculated correctly"""
        # Add specific patterns
        conn = sqlite3.connect(self.patterns_db)
        c = conn.cursor()

        # Add 3 patterns with known confidences: 0.8, 0.9, 0.7
        c.execute('''
            INSERT INTO patterns
            VALUES (1, 'temporal', 'P1', '{}', 0.8, datetime('now'), 1, datetime('now'))
        ''')
        c.execute('''
            INSERT INTO patterns
            VALUES (2, 'load', 'P2', '{}', 0.9, datetime('now'), 1, datetime('now'))
        ''')
        c.execute('''
            INSERT INTO patterns
            VALUES (3, 'error', 'P3', '{}', 0.7, datetime('now'), 1, datetime('now'))
        ''')

        conn.commit()
        conn.close()

        metrics = self.dashboard.get_pattern_metrics()

        # Average should be (0.8 + 0.9 + 0.7) / 3 = 0.8
        self.assertAlmostEqual(metrics['average_confidence'], 0.8, places=1)


class TestDashboardDisplay(unittest.TestCase):
    """Test dashboard display and formatting"""

    def setUp(self):
        """Create test dashboard"""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.patterns_db = str(Path(self.temp_dir.name) / "disp_patterns.db")
        self.optimizations_db = str(Path(self.temp_dir.name) / "disp_optimizations.db")

        # Create empty databases
        for db_path in [self.patterns_db, self.optimizations_db]:
            conn = sqlite3.connect(db_path)
            c = conn.cursor()
            if 'patterns' in db_path:
                c.execute('''
                    CREATE TABLE patterns (
                        id INTEGER PRIMARY KEY, pattern_type TEXT, name TEXT, metrics TEXT,
                        confidence REAL, last_detected TIMESTAMP, occurrence_count INTEGER,
                        created_at TIMESTAMP
                    )
                ''')
            else:
                c.execute('''
                    CREATE TABLE candidates (
                        id INTEGER PRIMARY KEY, pattern_id INTEGER, category TEXT, name TEXT,
                        description TEXT, current_value TEXT, suggested_value TEXT,
                        expected_impact_pct REAL, confidence REAL, safety_score REAL,
                        composite_score REAL, rationale TEXT, implementation_effort TEXT,
                        accepted INTEGER, applied_at TIMESTAMP, result_impact_pct REAL,
                        created_at TIMESTAMP
                    )
                ''')
            conn.commit()
            conn.close()

        self.dashboard = LearningDashboard(
            patterns_db=self.patterns_db,
            optimizations_db=self.optimizations_db
        )

    def tearDown(self):
        """Clean up"""
        import gc
        gc.collect()
        try:
            self.temp_dir.cleanup()
        except Exception:
            pass

    def test_display_contains_all_sections(self):
        """Test display contains all required sections"""
        display = self.dashboard.get_dashboard_display()

        required_sections = [
            'PATTERN DISCOVERY',
            'OPTIMIZATION CANDIDATES',
            'LEARNING HEALTH',
            'IMPROVEMENT PROJECTIONS',
        ]

        for section in required_sections:
            self.assertIn(section, display, f"Missing section: {section}")

    def test_display_readability(self):
        """Test display is readable with proper formatting"""
        display = self.dashboard.get_dashboard_display()

        # Should have structure
        self.assertGreater(len(display), 100)
        self.assertIn('\n', display)  # Multiline output

        # Should not crash with empty data
        self.assertIsNotNone(display)
        self.assertIsInstance(display, str)


if __name__ == '__main__':
    unittest.main(verbosity=2)
