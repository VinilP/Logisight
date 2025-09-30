"""
Comprehensive test runner for the Logistics Insight System.
Runs all unit tests, integration tests, and performance benchmarks.
"""

import unittest
import sys
import os
import time
from io import StringIO

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class ComprehensiveTestRunner:
    """Comprehensive test runner with detailed reporting."""
    
    def __init__(self):
        self.test_results = {}
        self.total_start_time = None
        self.total_end_time = None
    
    def run_test_suite(self, test_module_name, suite_name):
        """Run a specific test suite and capture results."""
        print(f"\n{'='*60}")
        print(f"Running {suite_name}")
        print(f"{'='*60}")
        
        # Capture test output
        test_output = StringIO()
        
        # Load and run the test suite
        try:
            loader = unittest.TestLoader()
            suite = loader.loadTestsFromName(test_module_name)
            
            runner = unittest.TextTestRunner(
                stream=test_output,
                verbosity=2,
                buffer=True
            )
            
            start_time = time.time()
            result = runner.run(suite)
            end_time = time.time()
            
            # Store results
            self.test_results[suite_name] = {
                'tests_run': result.testsRun,
                'failures': len(result.failures),
                'errors': len(result.errors),
                'skipped': len(result.skipped) if hasattr(result, 'skipped') else 0,
                'success_rate': ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100) if result.testsRun > 0 else 0,
                'duration': end_time - start_time,
                'output': test_output.getvalue(),
                'result': result
            }
            
            # Print summary
            print(f"\n{suite_name} Results:")
            print(f"  Tests Run: {result.testsRun}")
            print(f"  Failures: {len(result.failures)}")
            print(f"  Errors: {len(result.errors)}")
            print(f"  Skipped: {len(result.skipped) if hasattr(result, 'skipped') else 0}")
            print(f"  Success Rate: {self.test_results[suite_name]['success_rate']:.1f}%")
            print(f"  Duration: {self.test_results[suite_name]['duration']:.2f}s")
            
            # Print failures and errors if any
            if result.failures:
                print(f"\nFailures in {suite_name}:")
                for test, traceback in result.failures:
                    print(f"  - {test}: {traceback.split('AssertionError:')[-1].strip() if 'AssertionError:' in traceback else 'See details above'}")
            
            if result.errors:
                print(f"\nErrors in {suite_name}:")
                for test, traceback in result.errors:
                    print(f"  - {test}: {traceback.split('Exception:')[-1].strip() if 'Exception:' in traceback else 'See details above'}")
            
            return result.wasSuccessful()
            
        except Exception as e:
            print(f"Failed to run {suite_name}: {e}")
            self.test_results[suite_name] = {
                'tests_run': 0,
                'failures': 0,
                'errors': 1,
                'skipped': 0,
                'success_rate': 0,
                'duration': 0,
                'output': str(e),
                'result': None
            }
            return False
    
    def run_all_tests(self):
        """Run all test suites."""
        self.total_start_time = time.time()
        
        print("Starting Comprehensive Test Suite for Logistics Insight System")
        print(f"Start Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Define test suites to run
        test_suites = [
            ('test_data_loader', 'Data Loader Unit Tests'),
            ('test_data_aggregator', 'Data Aggregator Unit Tests'),
            ('test_correlation_engine', 'Correlation Engine Unit Tests'),
            ('test_insight_generator', 'Insight Generator Unit Tests'),
            ('test_query_processor', 'Query Processor Unit Tests'),
            ('test_response_generator', 'Response Generator Unit Tests'),
            ('test_natural_language_interface', 'Natural Language Interface Unit Tests'),
            ('test_integration_aggregation_correlation', 'Aggregation-Correlation Integration Tests'),
            ('test_insight_integration', 'Insight Generation Integration Tests'),
            ('test_end_to_end_workflows', 'End-to-End Workflow Tests'),
            ('test_performance_benchmarks', 'Performance Benchmark Tests'),
        ]
        
        successful_suites = 0
        total_suites = len(test_suites)
        
        # Run each test suite
        for module_name, suite_name in test_suites:
            try:
                success = self.run_test_suite(module_name, suite_name)
                if success:
                    successful_suites += 1
            except KeyboardInterrupt:
                print("\nTest execution interrupted by user")
                break
            except Exception as e:
                print(f"Unexpected error running {suite_name}: {e}")
        
        self.total_end_time = time.time()
        
        # Generate final report
        self.generate_final_report(successful_suites, total_suites)
    
    def generate_final_report(self, successful_suites, total_suites):
        """Generate comprehensive final report."""
        total_duration = self.total_end_time - self.total_start_time
        
        print(f"\n{'='*80}")
        print("COMPREHENSIVE TEST REPORT")
        print(f"{'='*80}")
        print(f"Total Duration: {total_duration:.2f} seconds")
        print(f"End Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Successful Test Suites: {successful_suites}/{total_suites}")
        
        # Calculate overall statistics
        total_tests = sum(result['tests_run'] for result in self.test_results.values())
        total_failures = sum(result['failures'] for result in self.test_results.values())
        total_errors = sum(result['errors'] for result in self.test_results.values())
        total_skipped = sum(result['skipped'] for result in self.test_results.values())
        
        overall_success_rate = ((total_tests - total_failures - total_errors) / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\nOverall Statistics:")
        print(f"  Total Tests: {total_tests}")
        print(f"  Passed: {total_tests - total_failures - total_errors}")
        print(f"  Failed: {total_failures}")
        print(f"  Errors: {total_errors}")
        print(f"  Skipped: {total_skipped}")
        print(f"  Overall Success Rate: {overall_success_rate:.1f}%")
        
        # Detailed breakdown by test suite
        print(f"\nDetailed Breakdown:")
        print(f"{'Suite Name':<40} {'Tests':<8} {'Pass':<8} {'Fail':<8} {'Error':<8} {'Skip':<8} {'Rate':<8} {'Time':<8}")
        print(f"{'-'*40} {'-'*7} {'-'*7} {'-'*7} {'-'*7} {'-'*7} {'-'*7} {'-'*7}")
        
        for suite_name, result in self.test_results.items():
            passed = result['tests_run'] - result['failures'] - result['errors']
            print(f"{suite_name:<40} {result['tests_run']:<8} {passed:<8} {result['failures']:<8} {result['errors']:<8} {result['skipped']:<8} {result['success_rate']:<7.1f}% {result['duration']:<7.2f}s")
        
        # Performance summary (if performance tests were run)
        if 'Performance Benchmark Tests' in self.test_results:
            perf_result = self.test_results['Performance Benchmark Tests']
            if perf_result['tests_run'] > 0:
                print(f"\nPerformance Summary:")
                print(f"  Performance tests completed: {perf_result['tests_run']}")
                print(f"  Performance success rate: {perf_result['success_rate']:.1f}%")
                if perf_result['failures'] > 0 or perf_result['errors'] > 0:
                    print(f"  ⚠️  Some performance benchmarks failed - check detailed output above")
                else:
                    print(f"  ✅ All performance benchmarks passed")
        
        # System readiness assessment
        print(f"\nSystem Readiness Assessment:")
        
        # Core functionality tests
        core_suites = [
            'Data Loader Unit Tests',
            'Data Aggregator Unit Tests', 
            'Correlation Engine Unit Tests',
            'Insight Generator Unit Tests'
        ]
        
        core_success = all(
            self.test_results.get(suite, {}).get('success_rate', 0) >= 90
            for suite in core_suites
        )
        
        # Integration tests
        integration_suites = [
            'Aggregation-Correlation Integration Tests',
            'Insight Generation Integration Tests',
            'End-to-End Workflow Tests'
        ]
        
        integration_success = all(
            self.test_results.get(suite, {}).get('success_rate', 0) >= 80
            for suite in integration_suites
        )
        
        # Overall assessment
        if overall_success_rate >= 90 and core_success and integration_success:
            print(f"  🟢 SYSTEM READY FOR PRODUCTION")
            print(f"     - All core components functioning correctly")
            print(f"     - Integration tests passing")
            print(f"     - Overall success rate: {overall_success_rate:.1f}%")
        elif overall_success_rate >= 75 and core_success:
            print(f"  🟡 SYSTEM READY FOR DEMO/TESTING")
            print(f"     - Core functionality working")
            print(f"     - Some integration issues may exist")
            print(f"     - Overall success rate: {overall_success_rate:.1f}%")
        else:
            print(f"  🔴 SYSTEM NOT READY")
            print(f"     - Critical issues detected")
            print(f"     - Overall success rate: {overall_success_rate:.1f}%")
            print(f"     - Review failed tests above")
        
        # Recommendations
        print(f"\nRecommendations:")
        if total_failures > 0:
            print(f"  - Address {total_failures} test failures")
        if total_errors > 0:
            print(f"  - Fix {total_errors} test errors")
        if total_skipped > 0:
            print(f"  - Review {total_skipped} skipped tests (may indicate missing dependencies)")
        
        if overall_success_rate < 90:
            print(f"  - Improve test coverage and fix failing tests")
        
        if 'Performance Benchmark Tests' in self.test_results:
            perf_result = self.test_results['Performance Benchmark Tests']
            if perf_result['success_rate'] < 100:
                print(f"  - Optimize system performance (some benchmarks failed)")
        
        print(f"\n{'='*80}")


def main():
    """Main function to run comprehensive tests."""
    runner = ComprehensiveTestRunner()
    
    try:
        runner.run_all_tests()
    except KeyboardInterrupt:
        print("\n\nTest execution interrupted by user")
        return 1
    except Exception as e:
        print(f"\nUnexpected error during test execution: {e}")
        return 1
    
    # Return appropriate exit code
    overall_success_rate = 0
    if runner.test_results:
        total_tests = sum(result['tests_run'] for result in runner.test_results.values())
        total_failures = sum(result['failures'] for result in runner.test_results.values())
        total_errors = sum(result['errors'] for result in runner.test_results.values())
        
        if total_tests > 0:
            overall_success_rate = ((total_tests - total_failures - total_errors) / total_tests * 100)
    
    # Return 0 if success rate is good, 1 otherwise
    return 0 if overall_success_rate >= 80 else 1


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)