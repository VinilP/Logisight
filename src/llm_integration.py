"""
LLM Integration Module for the Logistics Insight System.
Provides optional LLM integration with multiple approaches:
- OPTION A: OpenAI API integration (requires API key)
- OPTION B: Local LLM using Ollama (no API key needed)
- OPTION C: Advanced rule-based approach with templates (fallback)

Implements graceful fallback to basic functionality when LLM is not available.
Includes usage monitoring and cost estimation for API-based approaches.
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from enum import Enum
import time

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # python-dotenv not installed, environment variables must be set manually
    pass

logger = logging.getLogger(__name__)


class LLMProvider(Enum):
    """Enumeration of supported LLM providers."""
    OPENAI = "openai"
    OLLAMA = "ollama"
    RULE_BASED = "rule_based"


class LLMIntegration:
    """
    Manages LLM integration with multiple provider options and graceful fallback.
    Provides enhanced natural language processing capabilities for query understanding
    and response generation.
    """
    
    def __init__(self, preferred_provider: Optional[str] = None):
        """
        Initialize LLM integration with preferred provider.
        
        Args:
            preferred_provider: Preferred LLM provider ("openai", "ollama", or "rule_based")
        """
        self.preferred_provider = preferred_provider
        self.active_provider = None
        self.usage_stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'total_tokens': 0,
            'estimated_cost': 0.0,
            'provider_usage': {}
        }
        
        # Initialize providers
        self._initialize_providers()
        
        # Set up cost estimation (OpenAI pricing as of 2024)
        self.cost_per_token = {
            'gpt-3.5-turbo': 0.0015 / 1000,  # $0.0015 per 1K tokens
            'gpt-4': 0.03 / 1000,            # $0.03 per 1K tokens
            'gpt-4-turbo': 0.01 / 1000       # $0.01 per 1K tokens
        }
    
    def _initialize_providers(self):
        """Initialize available LLM providers based on configuration and availability."""
        self.providers = {}
        
        # Try to initialize OpenAI
        if self._initialize_openai():
            self.providers[LLMProvider.OPENAI] = True
            logger.info("OpenAI provider initialized successfully")
        else:
            self.providers[LLMProvider.OPENAI] = False
            logger.info("OpenAI provider not available")
        
        # Try to initialize Ollama
        if self._initialize_ollama():
            self.providers[LLMProvider.OLLAMA] = True
            logger.info("Ollama provider initialized successfully")
        else:
            self.providers[LLMProvider.OLLAMA] = False
            logger.info("Ollama provider not available")
        
        # Rule-based is always available as fallback
        self.providers[LLMProvider.RULE_BASED] = True
        
        # Set active provider based on preference and availability
        self._set_active_provider()
    
    def _initialize_openai(self) -> bool:
        """
        Initialize OpenAI provider if API key is available.
        
        Returns:
            True if OpenAI is available, False otherwise
        """
        try:
            # Check for API key
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                logger.info("OpenAI API key not found in environment variables")
                return False
            
            # Try to import OpenAI
            import openai
            self.openai_client = openai.OpenAI(api_key=api_key)
            
            # Test connection with a minimal request
            try:
                response = self.openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": "Hello"}],
                    max_tokens=5
                )
                return True
            except Exception as e:
                logger.warning(f"OpenAI API test failed: {str(e)}")
                return False
                
        except ImportError:
            logger.info("OpenAI library not installed. Install with: pip install openai")
            return False
        except Exception as e:
            logger.warning(f"Failed to initialize OpenAI: {str(e)}")
            return False
    
    def _initialize_ollama(self) -> bool:
        """
        Initialize Ollama provider if available locally.
        
        Returns:
            True if Ollama is available, False otherwise
        """
        try:
            # Try to import ollama
            import ollama
            self.ollama_client = ollama
            
            # Test connection by listing models
            try:
                models = self.ollama_client.list()
                if models and len(models.get('models', [])) > 0:
                    # Find a suitable model (prefer llama2, mistral, or any available)
                    available_models = [m['name'] for m in models['models']]
                    
                    # Preferred models in order
                    preferred_models = ['llama2', 'mistral', 'codellama', 'llama2:7b', 'mistral:7b']
                    
                    self.ollama_model = None
                    for model in preferred_models:
                        if model in available_models:
                            self.ollama_model = model
                            break
                    
                    # If no preferred model, use the first available
                    if not self.ollama_model and available_models:
                        self.ollama_model = available_models[0]
                    
                    if self.ollama_model:
                        logger.info(f"Ollama initialized with model: {self.ollama_model}")
                        return True
                    else:
                        logger.info("No suitable Ollama models found")
                        return False
                else:
                    logger.info("No Ollama models available. Install a model with: ollama pull llama2")
                    return False
                    
            except Exception as e:
                logger.warning(f"Ollama connection test failed: {str(e)}")
                return False
                
        except ImportError:
            logger.info("Ollama library not installed. Install with: pip install ollama")
            return False
        except Exception as e:
            logger.warning(f"Failed to initialize Ollama: {str(e)}")
            return False
    
    def _set_active_provider(self):
        """Set the active provider based on preference and availability."""
        # If preferred provider is specified and available, use it
        if self.preferred_provider:
            try:
                preferred_enum = LLMProvider(self.preferred_provider.lower())
                if self.providers.get(preferred_enum, False):
                    self.active_provider = preferred_enum
                    logger.info(f"Using preferred provider: {preferred_enum.value}")
                    return
            except ValueError:
                logger.warning(f"Invalid preferred provider: {self.preferred_provider}")
        
        # Otherwise, use priority order: OpenAI -> Ollama -> Rule-based
        if self.providers.get(LLMProvider.OPENAI, False):
            self.active_provider = LLMProvider.OPENAI
            logger.info("Using OpenAI provider")
        elif self.providers.get(LLMProvider.OLLAMA, False):
            self.active_provider = LLMProvider.OLLAMA
            logger.info("Using Ollama provider")
        else:
            self.active_provider = LLMProvider.RULE_BASED
            logger.info("Using rule-based provider (fallback)")
    
    def enhance_query_understanding(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Enhance query understanding using LLM capabilities.
        
        Args:
            query: Natural language query string
            context: Optional context information
            
        Returns:
            Enhanced query understanding with extracted intent, entities, and parameters
        """
        start_time = time.time()
        
        try:
            if self.active_provider == LLMProvider.OPENAI:
                result = self._enhance_query_openai(query, context)
            elif self.active_provider == LLMProvider.OLLAMA:
                result = self._enhance_query_ollama(query, context)
            else:
                result = self._enhance_query_rule_based(query, context)
            
            # Update usage stats
            self._update_usage_stats(True, time.time() - start_time, result.get('tokens_used', 0))
            
            return result
            
        except Exception as e:
            logger.error(f"Error enhancing query understanding: {str(e)}")
            self._update_usage_stats(False, time.time() - start_time, 0)
            
            # Fallback to rule-based approach
            return self._enhance_query_rule_based(query, context)
    
    def enhance_response_generation(self, analysis_result: str, query_context: Dict[str, Any]) -> str:
        """
        Enhance response generation using LLM capabilities.
        
        Args:
            analysis_result: Raw analysis result from insight generator
            query_context: Context information about the query
            
        Returns:
            Enhanced, more natural response text
        """
        start_time = time.time()
        
        try:
            if self.active_provider == LLMProvider.OPENAI:
                result = self._enhance_response_openai(analysis_result, query_context)
            elif self.active_provider == LLMProvider.OLLAMA:
                result = self._enhance_response_ollama(analysis_result, query_context)
            else:
                result = self._enhance_response_rule_based(analysis_result, query_context)
            
            # Update usage stats
            tokens_used = len(result.split()) * 1.3  # Rough token estimation
            self._update_usage_stats(True, time.time() - start_time, tokens_used)
            
            return result
            
        except Exception as e:
            logger.error(f"Error enhancing response generation: {str(e)}")
            self._update_usage_stats(False, time.time() - start_time, 0)
            
            # Fallback to rule-based approach
            return self._enhance_response_rule_based(analysis_result, query_context)
    
    def _enhance_query_openai(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Enhance query understanding using OpenAI API."""
        system_prompt = """You are a logistics analytics assistant. Analyze the user's query and extract:
1. Query intent (city_delay_analysis, client_failure_analysis, warehouse_failure_analysis, city_comparison, festival_period_analysis, capacity_impact_analysis)
2. Key entities (cities, clients, warehouses, dates, numbers)
3. Parameters needed for analysis

Respond in JSON format with: {"intent": "...", "entities": {...}, "parameters": {...}, "confidence": 0.0-1.0}"""
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Query: {query}\nContext: {json.dumps(context) if context else 'None'}"}
                ],
                max_tokens=300,
                temperature=0.1
            )
            
            result_text = response.choices[0].message.content
            tokens_used = response.usage.total_tokens
            
            # Parse JSON response
            try:
                result = json.loads(result_text)
                result['tokens_used'] = tokens_used
                result['provider'] = 'openai'
                return result
            except json.JSONDecodeError:
                logger.warning("Failed to parse OpenAI JSON response, using fallback")
                return self._enhance_query_rule_based(query, context)
                
        except Exception as e:
            logger.error(f"OpenAI query enhancement failed: {str(e)}")
            return self._enhance_query_rule_based(query, context)
    
    def _enhance_query_ollama(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Enhance query understanding using Ollama local LLM."""
        prompt = f"""Analyze this logistics query and extract key information:

Query: {query}
Context: {json.dumps(context) if context else 'None'}

Extract:
1. Intent: What type of analysis is requested?
2. Entities: Cities, clients, warehouses, dates mentioned
3. Parameters: Specific values needed for analysis

Respond in JSON format."""
        
        try:
            response = self.ollama_client.generate(
                model=self.ollama_model,
                prompt=prompt,
                options={'temperature': 0.1, 'num_predict': 200}
            )
            
            result_text = response['response']
            
            # Try to extract JSON from response
            try:
                # Look for JSON in the response
                import re
                json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group())
                    result['provider'] = 'ollama'
                    result['tokens_used'] = len(result_text.split())
                    return result
                else:
                    logger.warning("No JSON found in Ollama response, using fallback")
                    return self._enhance_query_rule_based(query, context)
            except json.JSONDecodeError:
                logger.warning("Failed to parse Ollama JSON response, using fallback")
                return self._enhance_query_rule_based(query, context)
                
        except Exception as e:
            logger.error(f"Ollama query enhancement failed: {str(e)}")
            return self._enhance_query_rule_based(query, context)
    
    def _enhance_query_rule_based(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Enhance query understanding using advanced rule-based approach."""
        # This is the fallback method using sophisticated pattern matching
        query_lower = query.lower()
        
        # Determine intent based on keywords
        intent_keywords = {
            'city_delay_analysis': ['delayed', 'delay', 'city', 'yesterday', 'late'],
            'client_failure_analysis': ['client', 'customer', 'orders fail', 'failure'],
            'warehouse_failure_analysis': ['warehouse', 'facility', 'dispatch', 'picking'],
            'city_comparison': ['compare', 'between', 'vs', 'versus', 'difference'],
            'festival_period_analysis': ['festival', 'holiday', 'seasonal', 'peak period'],
            'capacity_impact_analysis': ['onboard', 'capacity', 'additional orders', 'extra orders']
        }
        
        intent_scores = {}
        for intent, keywords in intent_keywords.items():
            score = sum(1 for keyword in keywords if keyword in query_lower)
            if score > 0:
                intent_scores[intent] = score / len(keywords)
        
        # Get the highest scoring intent
        best_intent = max(intent_scores.items(), key=lambda x: x[1]) if intent_scores else ('unknown', 0.0)
        
        # Extract entities using regex patterns
        entities = {}
        
        # Extract cities
        import re
        city_patterns = [
            r'(?:in|for|from)\s+([A-Z][a-zA-Z\s]+?)(?:\s+yesterday|\s+on|\s+and|\s*\?|$)',
            r'city\s+([A-Z][a-zA-Z\s]+?)(?:\s+yesterday|\s+on|\s+and|\s*\?|$)'
        ]
        
        for pattern in city_patterns:
            matches = re.findall(pattern, query)
            if matches:
                entities['cities'] = [city.strip() for city in matches]
                break
        
        # Extract client names
        client_match = re.search(r'client\s+([A-Z][a-zA-Z0-9\s]+?)(?:\s|\'s|\?|$)', query)
        if client_match:
            entities['client'] = client_match.group(1).strip()
        
        # Extract warehouse names
        warehouse_match = re.search(r'warehouse\s+([A-Z][a-zA-Z0-9\s]+?)(?:\s|\'s|\?|$)', query)
        if warehouse_match:
            entities['warehouse'] = warehouse_match.group(1).strip()
        
        # Extract numbers (order volumes, etc.)
        number_matches = re.findall(r'([0-9,]+)', query)
        if number_matches:
            entities['numbers'] = [int(num.replace(',', '')) for num in number_matches]
        
        # Extract time references
        time_patterns = [
            r'yesterday', r'last week', r'past week', r'last month', r'past month',
            r'in\s+([A-Z][a-z]+)', r'during\s+([A-Z][a-z]+)'
        ]
        
        for pattern in time_patterns:
            match = re.search(pattern, query)
            if match:
                if match.groups():
                    entities['time_reference'] = match.group(1)
                else:
                    entities['time_reference'] = match.group(0)
                break
        
        return {
            'intent': best_intent[0],
            'confidence': best_intent[1],
            'entities': entities,
            'parameters': entities,  # For compatibility
            'provider': 'rule_based',
            'tokens_used': 0
        }
    
    def _enhance_response_openai(self, analysis_result: str, query_context: Dict[str, Any]) -> str:
        """Enhance response generation using OpenAI API."""
        system_prompt = """You are a logistics operations expert. Take the technical analysis and rewrite it as a clear, actionable business report. 
Make it professional but accessible, with specific recommendations. Keep the same factual content but improve clarity and business relevance."""
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Analysis: {analysis_result}\n\nQuery Context: {json.dumps(query_context)}"}
                ],
                max_tokens=800,
                temperature=0.3
            )
            
            enhanced_response = response.choices[0].message.content
            
            # Update cost tracking
            tokens_used = response.usage.total_tokens
            model_used = "gpt-3.5-turbo"
            cost = tokens_used * self.cost_per_token.get(model_used, 0)
            self.usage_stats['estimated_cost'] += cost
            
            return enhanced_response
            
        except Exception as e:
            logger.error(f"OpenAI response enhancement failed: {str(e)}")
            return self._enhance_response_rule_based(analysis_result, query_context)
    
    def _enhance_response_ollama(self, analysis_result: str, query_context: Dict[str, Any]) -> str:
        """Enhance response generation using Ollama local LLM."""
        prompt = f"""Rewrite this logistics analysis as a clear, professional business report:

Analysis: {analysis_result}

Make it:
- Clear and actionable for operations managers
- Professional but accessible
- Include specific recommendations
- Keep all factual content

Enhanced Report:"""
        
        try:
            response = self.ollama_client.generate(
                model=self.ollama_model,
                prompt=prompt,
                options={'temperature': 0.3, 'num_predict': 500}
            )
            
            return response['response']
            
        except Exception as e:
            logger.error(f"Ollama response enhancement failed: {str(e)}")
            return self._enhance_response_rule_based(analysis_result, query_context)
    
    def _enhance_response_rule_based(self, analysis_result: str, query_context: Dict[str, Any]) -> str:
        """Enhance response generation using advanced rule-based templates."""
        # This is the sophisticated fallback that improves the basic analysis
        
        # Add professional formatting
        enhanced_lines = []
        lines = analysis_result.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                enhanced_lines.append('')
                continue
            
            # Enhance bullet points
            if line.startswith('- '):
                enhanced_lines.append(f"• {line[2:]}")
            # Enhance headers
            elif line.isupper() or (line.startswith('Analysis') or line.startswith('Summary')):
                enhanced_lines.append(f"\n**{line}**\n")
            # Enhance recommendations
            elif 'recommend' in line.lower() or 'suggest' in line.lower():
                enhanced_lines.append(f"💡 **Recommendation:** {line}")
            # Enhance metrics
            elif any(metric in line.lower() for metric in ['rate', 'percentage', 'average', 'total']):
                enhanced_lines.append(f"📊 {line}")
            else:
                enhanced_lines.append(line)
        
        # Add business context footer
        enhanced_lines.extend([
            '',
            '---',
            '**Business Impact Assessment:**',
            'This analysis provides actionable insights for operational improvements.',
            'Implement recommendations in priority order for maximum impact.',
            '',
            f'*Report generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*'
        ])
        
        return '\n'.join(enhanced_lines)
    
    def _update_usage_stats(self, success: bool, processing_time: float, tokens_used: int):
        """Update usage statistics for monitoring and cost estimation."""
        self.usage_stats['total_requests'] += 1
        
        if success:
            self.usage_stats['successful_requests'] += 1
        else:
            self.usage_stats['failed_requests'] += 1
        
        self.usage_stats['total_tokens'] += tokens_used
        
        # Track provider usage
        provider_key = self.active_provider.value if self.active_provider else 'unknown'
        if provider_key not in self.usage_stats['provider_usage']:
            self.usage_stats['provider_usage'][provider_key] = {
                'requests': 0,
                'tokens': 0,
                'avg_processing_time': 0.0
            }
        
        provider_stats = self.usage_stats['provider_usage'][provider_key]
        provider_stats['requests'] += 1
        provider_stats['tokens'] += tokens_used
        
        # Update average processing time
        current_avg = provider_stats['avg_processing_time']
        new_avg = (current_avg * (provider_stats['requests'] - 1) + processing_time) / provider_stats['requests']
        provider_stats['avg_processing_time'] = new_avg
    
    def get_usage_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive usage statistics and cost estimation.
        
        Returns:
            Dictionary containing usage stats, cost estimates, and performance metrics
        """
        stats = self.usage_stats.copy()
        
        # Calculate success rate
        if stats['total_requests'] > 0:
            stats['success_rate'] = (stats['successful_requests'] / stats['total_requests']) * 100
        else:
            stats['success_rate'] = 0.0
        
        # Add provider availability
        stats['available_providers'] = {
            provider.value: available 
            for provider, available in self.providers.items()
        }
        
        stats['active_provider'] = self.active_provider.value if self.active_provider else None
        
        # Add cost breakdown by model (for OpenAI)
        if self.active_provider == LLMProvider.OPENAI:
            stats['cost_breakdown'] = {
                'total_estimated_cost': stats['estimated_cost'],
                'cost_per_request': stats['estimated_cost'] / max(stats['total_requests'], 1),
                'tokens_per_request': stats['total_tokens'] / max(stats['total_requests'], 1)
            }
        
        return stats
    
    def get_provider_status(self) -> Dict[str, Any]:
        """
        Get current status of all LLM providers.
        
        Returns:
            Dictionary containing provider availability and configuration status
        """
        status = {
            'providers': {},
            'active_provider': self.active_provider.value if self.active_provider else None,
            'fallback_available': True  # Rule-based is always available
        }
        
        # OpenAI status
        status['providers']['openai'] = {
            'available': self.providers.get(LLMProvider.OPENAI, False),
            'api_key_configured': bool(os.getenv('OPENAI_API_KEY')),
            'library_installed': self._check_library_installed('openai')
        }
        
        # Ollama status
        status['providers']['ollama'] = {
            'available': self.providers.get(LLMProvider.OLLAMA, False),
            'library_installed': self._check_library_installed('ollama'),
            'model_available': hasattr(self, 'ollama_model') and self.ollama_model is not None,
            'model_name': getattr(self, 'ollama_model', None)
        }
        
        # Rule-based status
        status['providers']['rule_based'] = {
            'available': True,
            'description': 'Advanced pattern matching and template-based approach'
        }
        
        return status
    
    def _check_library_installed(self, library_name: str) -> bool:
        """Check if a Python library is installed."""
        try:
            __import__(library_name)
            return True
        except ImportError:
            return False
    
    def switch_provider(self, provider_name: str) -> bool:
        """
        Switch to a different LLM provider if available.
        
        Args:
            provider_name: Name of provider to switch to
            
        Returns:
            True if switch was successful, False otherwise
        """
        try:
            provider_enum = LLMProvider(provider_name.lower())
            if self.providers.get(provider_enum, False):
                self.active_provider = provider_enum
                logger.info(f"Switched to provider: {provider_name}")
                return True
            else:
                logger.warning(f"Provider {provider_name} is not available")
                return False
        except ValueError:
            logger.error(f"Invalid provider name: {provider_name}")
            return False