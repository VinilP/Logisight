#!/usr/bin/env python3
"""
Logistics Insight System - Main Command-Line Interface and Demo Program

This is the main entry point for the Logistics Insight System that provides:
1. Command-line interface for interactive queries
2. Demo mode with all six sample use cases
3. Help and usage instructions
4. System validation and status reporting

Requirements fulfilled: 6.1, 6.2, 6.4, 8.2
"""

import sys
import os
import argparse
from datetime import datetime, timedelta

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # python-dotenv not installed, environment variables must be set manually
    pass

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from natural_language_interface import NaturalLanguageInterface
from data_aggregator import DataAggregator
from correlation_engine import CorrelationEngine
from data_loader import DataLoader


class LogisticsInsightCLI:
    """Main command-line interface for the Logistics Insight System."""
    
    def __init__(self):
        """Initialize the CLI with system components."""
        self.nl_interface = None
        self.system_ready = False
        
    def initialize_system(self):
        """Initialize all system components and validate readiness."""
        try:
            print("🚚 Logistics Insight System")
            print("=" * 50)
            print("📊 Initializing system components...")
            
            # Initialize core components
            data_loader = DataLoader('sample-data-set')
            data_aggregator = DataAggregator(data_loader)
            correlation_engine = CorrelationEngine(data_aggregator)
            self.nl_interface = NaturalLanguageInterface(data_aggregator, correlation_engine)
            
            # Validate system readiness
            print("🔍 Validating system readiness...")
            readiness = self.nl_interface.validate_system_readiness()
            
            # Check LLM integration status
            llm_status = self.nl_interface.get_llm_status()
            if llm_status['enabled']:
                provider = llm_status['active_provider']
                print(f"🤖 LLM Integration: ✅ Active ({provider})")
            else:
                print("🤖 LLM Integration: ⚠️ Using rule-based approach")
            
            if readiness['ready']:
                print("✅ System initialized successfully!")
                self.system_ready = True
            else:
                print("⚠️ System initialized with warnings:")
                for issue in readiness['issues']:
                    print(f"   - {issue}")
                print("Some queries may not work properly.")
                self.system_ready = True  # Continue with warnings
            
            print()
            return True
            
        except Exception as e:
            print(f"❌ Failed to initialize system: {str(e)}")
            return False
    
    def show_help(self):
        """Display comprehensive help information."""
        help_text = """
🚚 LOGISTICS INSIGHT SYSTEM - HELP

DESCRIPTION:
    The Logistics Insight System analyzes delivery performance, identifies failure
    patterns, and provides actionable recommendations for logistics operations.

USAGE:
    python main.py [OPTIONS]

OPTIONS:
    -h, --help          Show this help message
    -i, --interactive   Start interactive query mode
    -d, --demo          Run demonstration with all sample use cases
    -q, --query TEXT    Process a single query and exit
    -s, --stats         Show system statistics
    --validate          Validate system components and exit

SUPPORTED QUERY TYPES:

1. City Delay Analysis
   Example: "Why were deliveries delayed in Mumbai yesterday?"
   Purpose: Analyze delivery delays in a specific city for a given date

2. Client Failure Analysis
   Example: "Why did Client Mann Group's orders fail in the past week?"
   Purpose: Examine order failure patterns for a specific client

3. Warehouse Failure Analysis
   Example: "Explain top reasons for delivery failures linked to Warehouse B in August?"
   Purpose: Analyze warehouse-related delivery failures and operational issues

4. City Comparison
   Example: "Compare delivery failure causes between Delhi and Mumbai last month?"
   Purpose: Compare delivery performance between two cities

5. Festival Period Analysis
   Example: "What are the likely causes of delivery failures during the festival period?"
   Purpose: Analyze seasonal delivery risks and preparation strategies

6. Capacity Impact Analysis
   Example: "If we onboard Client XYZ with 20,000 extra monthly orders, what risks should we expect?"
   Purpose: Evaluate capacity impact from onboarding high-volume clients

INTERACTIVE COMMANDS:
    help    - Show query examples and usage
    stats   - Display query processing statistics
    quit    - Exit the application

EXAMPLES:
    # Start interactive mode
    python main.py --interactive
    
    # Run full demonstration
    python main.py --demo
    
    # Process single query
    python main.py --query "Why were deliveries delayed in Mumbai yesterday?"
    
    # Validate system
    python main.py --validate

DATA REQUIREMENTS:
    The system requires CSV files in the 'sample-data-set' directory:
    - orders.csv, clients.csv, warehouses.csv, drivers.csv
    - fleet_logs.csv, external_factors.csv, feedback.csv, warehouse_logs.csv

For more information, see QUERY_USAGE.md or README.md
"""
        print(help_text)
    
    def run_interactive_mode(self):
        """Run interactive query mode."""
        if not self.system_ready:
            print("❌ System not ready for interactive mode.")
            return False
        
        print("🔍 INTERACTIVE QUERY MODE")
        print("=" * 40)
        print("Ask questions about delivery performance and logistics operations.")
        print("Type 'help' for examples, 'stats' for statistics, 'llm' for LLM status, or 'quit' to exit.")
        print()
        
        while True:
            try:
                # Get user input
                query = input("🔍 Your question: ").strip()
                
                if not query:
                    continue
                
                # Handle commands
                if query.lower() == 'quit':
                    print("👋 Goodbye!")
                    break
                elif query.lower() == 'help':
                    self._show_interactive_help()
                    continue
                elif query.lower() == 'stats':
                    self._show_stats()
                    continue
                elif query.lower() == 'llm':
                    self._show_llm_status()
                    continue
                
                # Process the query
                print("⏳ Processing your query...")
                start_time = datetime.now()
                
                result = self.nl_interface.process_query(query, include_executive_summary=True)
                
                processing_time = (datetime.now() - start_time).total_seconds()
                print(f"⏱️ Processed in {processing_time:.3f} seconds")
                print()
                
                if result['success']:
                    # Show executive summary first
                    if result.get('executive_summary'):
                        print("📋 Executive Summary:")
                        print(result['executive_summary'])
                        print()
                    
                    # Ask if user wants to see full response
                    show_full = input("📄 Show full detailed response? (y/n): ").strip().lower()
                    if show_full in ['y', 'yes']:
                        print()
                        print("📄 Full Response:")
                        print("-" * 50)
                        print(result['formatted_response'])
                        print("-" * 50)
                    
                else:
                    print(f"❌ Error: {result['error']}")
                    
                    if 'supported_queries' in result:
                        print("\n💡 Try one of these supported query formats:")
                        for example in result['supported_queries'][:3]:
                            print(f"   - {example}")
                
                print()
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ An error occurred: {str(e)}")
                print("Please try again with a different query.")
                print()
        
        return True
    
    def run_demo_mode(self):
        """Run demonstration with all six sample use cases."""
        if not self.system_ready:
            print("❌ System not ready for demo mode.")
            return False
        
        print("🎯 DEMONSTRATION MODE - All Six Use Cases")
        print("=" * 50)
        print("This demo showcases all supported query types with sample data.")
        print()
        
        # Define the six sample use cases as specified in requirements
        demo_queries = [
            {
                'title': '1. City Delay Analysis',
                'query': 'Why were deliveries delayed in Mumbai yesterday?',
                'description': 'Analyzes delivery delays in a specific city for a given date'
            },
            {
                'title': '2. Client Failure Analysis', 
                'query': 'Why did Client Mann Group\'s orders fail in the past week?',
                'description': 'Examines order failure patterns for a specific client over time'
            },
            {
                'title': '3. Warehouse Failure Analysis',
                'query': 'Explain top reasons for delivery failures linked to Warehouse B in August?',
                'description': 'Analyzes warehouse-related delivery failures and operational issues'
            },
            {
                'title': '4. City Comparison',
                'query': 'Compare delivery failure causes between Delhi and Mumbai last month?',
                'description': 'Compares delivery performance and failure patterns between cities'
            },
            {
                'title': '5. Festival Period Analysis',
                'query': 'What are the likely causes of delivery failures during the festival period?',
                'description': 'Analyzes seasonal delivery risks and preparation strategies'
            },
            {
                'title': '6. Capacity Impact Analysis',
                'query': 'If we onboard Client XYZ with 20,000 extra monthly orders, what new failure risks should we expect?',
                'description': 'Evaluates capacity impact and risks from onboarding high-volume clients'
            }
        ]
        
        successful_queries = 0
        total_processing_time = 0
        
        for i, demo in enumerate(demo_queries, 1):
            print(f"{demo['title']}")
            print(f"Query: {demo['query']}")
            print(f"Purpose: {demo['description']}")
            print("-" * 60)
            
            try:
                # Process the query
                start_time = datetime.now()
                result = self.nl_interface.process_query(demo['query'], include_executive_summary=True)
                processing_time = (datetime.now() - start_time).total_seconds()
                total_processing_time += processing_time
                
                if result['success']:
                    successful_queries += 1
                    print(f"✅ Query Type: {result['query_type']}")
                    print(f"⏱️ Processing Time: {processing_time:.3f} seconds")
                    print()
                    
                    # Show executive summary
                    if result.get('executive_summary'):
                        print("📋 Executive Summary:")
                        print(result['executive_summary'])
                        print()
                    
                    # Show preview of full response
                    response_lines = result['formatted_response'].split('\n')
                    print("📄 Response Preview (first 8 lines):")
                    for line in response_lines[:8]:
                        print(line)
                    if len(response_lines) > 8:
                        print("... (truncated for demo)")
                    print()
                    
                else:
                    print(f"❌ Error: {result['error']}")
                    print()
                
            except Exception as e:
                print(f"❌ Error processing query: {str(e)}")
                print()
            
            print("=" * 60)
            print()
            
            # Pause between queries for readability
            if i < len(demo_queries):
                input("Press Enter to continue to next demo query...")
                print()
        
        # Show demo summary
        print("🎉 DEMO SUMMARY")
        print("=" * 30)
        print(f"✅ Successful Queries: {successful_queries}/{len(demo_queries)}")
        print(f"⏱️ Total Processing Time: {total_processing_time:.3f} seconds")
        print(f"📊 Average Time per Query: {total_processing_time/len(demo_queries):.3f} seconds")
        
        if successful_queries == len(demo_queries):
            print("🎯 All use cases demonstrated successfully!")
        else:
            print(f"⚠️ {len(demo_queries) - successful_queries} queries had issues")
        
        print()
        return True
    
    def process_single_query(self, query):
        """Process a single query and display results."""
        if not self.system_ready:
            print("❌ System not ready for query processing.")
            return False
        
        print(f"🔍 Processing Query: {query}")
        print("=" * 50)
        
        try:
            start_time = datetime.now()
            result = self.nl_interface.process_query(query, include_executive_summary=True)
            processing_time = (datetime.now() - start_time).total_seconds()
            
            if result['success']:
                print(f"✅ Query Type: {result['query_type']}")
                print(f"⏱️ Processing Time: {processing_time:.3f} seconds")
                print()
                
                # Show executive summary
                if result.get('executive_summary'):
                    print("📋 Executive Summary:")
                    print(result['executive_summary'])
                    print()
                
                # Show full response
                print("📄 Full Response:")
                print("-" * 50)
                print(result['formatted_response'])
                print("-" * 50)
                
                return True
                
            else:
                print(f"❌ Error: {result['error']}")
                
                if 'supported_queries' in result:
                    print("\n💡 Try one of these supported query formats:")
                    for example in result['supported_queries']:
                        print(f"   - {example}")
                
                return False
                
        except Exception as e:
            print(f"❌ Error processing query: {str(e)}")
            return False
    
    def validate_system(self):
        """Validate system components and display status."""
        print("🔍 SYSTEM VALIDATION")
        print("=" * 30)
        
        try:
            if not self.nl_interface:
                if not self.initialize_system():
                    return False
            
            readiness = self.nl_interface.validate_system_readiness()
            
            print("Component Status:")
            for component, status in readiness['components'].items():
                status_icon = "✅" if status else "❌"
                print(f"   {status_icon} {component}")
            
            if readiness['issues']:
                print("\nIssues Detected:")
                for issue in readiness['issues']:
                    print(f"   ⚠️ {issue}")
            
            print(f"\nOverall Status: {'✅ Ready' if readiness['ready'] else '❌ Not Ready'}")
            
            # Show data statistics
            try:
                stats = self.nl_interface.get_query_statistics()
                print(f"\nQuery Processing Statistics:")
                print(f"   Total Queries Processed: {stats['total_queries']}")
                print(f"   Success Rate: {stats['success_rate']}%")
            except:
                print("\nQuery statistics not available yet.")
            
            return readiness['ready']
            
        except Exception as e:
            print(f"❌ Validation failed: {str(e)}")
            return False
    
    def _show_interactive_help(self):
        """Show help for interactive mode."""
        print("💡 Interactive Mode Help:")
        print()
        
        examples = self.nl_interface.get_supported_query_examples()
        for i, example in enumerate(examples, 1):
            print(f"{i}. {example['type']}")
            print(f"   Example: {example['example']}")
            print(f"   Purpose: {example['description']}")
            print()
        
        print("Commands:")
        print("   help  - Show this help message")
        print("   stats - Show query processing statistics")
        print("   llm   - Show LLM integration status and usage")
        print("   quit  - Exit the application")
        print()
    
    def _show_stats(self):
        """Show query processing statistics."""
        stats = self.nl_interface.get_query_statistics()
        
        print("📈 Query Processing Statistics:")
        print(f"   Total Queries: {stats['total_queries']}")
        print(f"   Successful Queries: {stats['successful_queries']}")
        print(f"   Success Rate: {stats['success_rate']}%")
        
        if stats['query_types']:
            print("   Query Types Processed:")
            for query_type, count in stats['query_types'].items():
                print(f"     - {query_type}: {count}")
        
        if stats['recent_queries']:
            print("   Recent Queries:")
            for query in stats['recent_queries'][-3:]:  # Show last 3
                status = "✅" if query['success'] else "❌"
                print(f"     {status} {query['query'][:50]}...")
        
        print()
    
    def _show_llm_status(self):
        """Show LLM integration status and usage statistics."""
        llm_status = self.nl_interface.get_llm_status()
        
        print("🤖 LLM Integration Status:")
        print(f"   Enabled: {'✅ Yes' if llm_status['enabled'] else '❌ No'}")
        
        if llm_status['enabled']:
            print(f"   Active Provider: {llm_status['active_provider']}")
            
            # Show provider availability
            print("   Provider Availability:")
            for provider, info in llm_status['providers'].items():
                available = info.get('available', False)
                status_icon = "✅" if available else "❌"
                print(f"     {status_icon} {provider}")
                
                # Show additional info for specific providers
                if provider == 'openai' and info.get('api_key_configured'):
                    print(f"         API Key: {'✅ Configured' if info['api_key_configured'] else '❌ Missing'}")
                elif provider == 'ollama' and info.get('model_name'):
                    print(f"         Model: {info['model_name']}")
            
            # Show usage statistics
            usage_stats = llm_status.get('usage_stats', {})
            if usage_stats.get('total_requests', 0) > 0:
                print("   Usage Statistics:")
                print(f"     Total Requests: {usage_stats['total_requests']}")
                print(f"     Success Rate: {usage_stats['success_rate']:.1f}%")
                print(f"     Total Tokens: {usage_stats['total_tokens']:,}")
                
                if usage_stats.get('estimated_cost', 0) > 0:
                    print(f"     Estimated Cost: ${usage_stats['estimated_cost']:.4f}")
        else:
            print("   Reason: Using rule-based approach (advanced pattern matching)")
            print("   Setup: Run 'python llm_setup.py' to configure LLM integration")
        
        print()


def main():
    """Main function with argument parsing."""
    parser = argparse.ArgumentParser(
        description='Logistics Insight System - Analyze delivery performance and generate actionable insights',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --interactive                    # Start interactive mode
  python main.py --demo                          # Run full demonstration
  python main.py --query "Why were deliveries delayed in Mumbai yesterday?"
  python main.py --validate                      # Validate system components
        """
    )
    
    parser.add_argument('-i', '--interactive', action='store_true',
                       help='Start interactive query mode')
    parser.add_argument('-d', '--demo', action='store_true',
                       help='Run demonstration with all sample use cases')
    parser.add_argument('-q', '--query', type=str,
                       help='Process a single query and exit')
    parser.add_argument('-s', '--stats', action='store_true',
                       help='Show system statistics')
    parser.add_argument('--validate', action='store_true',
                       help='Validate system components and exit')
    
    args = parser.parse_args()
    
    # Create CLI instance
    cli = LogisticsInsightCLI()
    
    # Handle different modes
    if args.validate:
        success = cli.validate_system()
        return 0 if success else 1
    
    elif args.query:
        if not cli.initialize_system():
            return 1
        success = cli.process_single_query(args.query)
        return 0 if success else 1
    
    elif args.demo:
        if not cli.initialize_system():
            return 1
        success = cli.run_demo_mode()
        return 0 if success else 1
    
    elif args.interactive:
        if not cli.initialize_system():
            return 1
        success = cli.run_interactive_mode()
        return 0 if success else 1
    
    elif args.stats:
        if not cli.initialize_system():
            return 1
        cli._show_stats()
        return 0
    
    else:
        # No arguments provided - show help and offer options
        print("🚚 Logistics Insight System")
        print("=" * 40)
        print("No mode specified. Choose an option:")
        print()
        print("1. Interactive Mode  - Ask questions interactively")
        print("2. Demo Mode        - See all use cases demonstrated")
        print("3. Single Query     - Process one query")
        print("4. Help             - Show detailed help")
        print("5. Validate         - Check system status")
        print()
        
        try:
            choice = input("Enter your choice (1-5): ").strip()
            
            if choice == '1':
                if cli.initialize_system():
                    cli.run_interactive_mode()
            elif choice == '2':
                if cli.initialize_system():
                    cli.run_demo_mode()
            elif choice == '3':
                query = input("Enter your query: ").strip()
                if query and cli.initialize_system():
                    cli.process_single_query(query)
            elif choice == '4':
                cli.show_help()
            elif choice == '5':
                cli.validate_system()
            else:
                print("Invalid choice. Use --help for usage information.")
                return 1
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            return 0
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())