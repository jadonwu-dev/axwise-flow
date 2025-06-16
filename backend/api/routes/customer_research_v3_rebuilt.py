"""
V3 Customer Research Service - Rebuilt with V1 Reliability

Architecture:
- V1 Core (100% reliable foundation)
- V3 Enhancement Layers (fail-safe additions)
- Circuit breaker pattern for unreliable enhancements
- Always fall back to working V1 behavior

Philosophy: Never replace what works, only enhance it safely.
"""

import logging
import time
from typing import Dict, List, Any, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.api.routes.customer_research import (
    ChatRequest, ChatResponse, GenerateQuestionsRequest, ResearchQuestions,
    Message, ResearchContext
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/research/v3-rebuilt", tags=["research-v3-rebuilt"])


class EnhancementMonitor:
    """Monitor and manage V3 enhancement reliability"""

    def __init__(self):
        self.failure_counts = {}
        self.disabled_enhancements = set()
        self.success_counts = {}

    def record_success(self, enhancement_name: str):
        """Record successful enhancement"""
        self.success_counts[enhancement_name] = self.success_counts.get(enhancement_name, 0) + 1

    def record_failure(self, enhancement_name: str):
        """Record failed enhancement and potentially disable it"""
        self.failure_counts[enhancement_name] = self.failure_counts.get(enhancement_name, 0) + 1

        # Circuit breaker: disable if failure rate too high
        total_attempts = self.failure_counts[enhancement_name] + self.success_counts.get(enhancement_name, 0)
        if total_attempts >= 10 and self.failure_counts[enhancement_name] / total_attempts > 0.3:
            self.disabled_enhancements.add(enhancement_name)
            logger.warning(f"🔴 Circuit breaker: disabled unreliable enhancement '{enhancement_name}'")

    def is_enabled(self, enhancement_name: str) -> bool:
        """Check if enhancement is enabled"""
        return enhancement_name not in self.disabled_enhancements


class UXResearchMethodology:
    """UX Research methodology enhancements for V1 responses"""

    def enhance_suggestions(self, v1_suggestions: List[str], conversation_stage: str = "discovery") -> List[str]:
        """Add UX research special options to V1's proven suggestions"""

        try:
            # Only skip enhancement for explicit confirmation phase
            if conversation_stage == 'confirmation':
                # Don't modify confirmation phase - V1 handles this perfectly
                return v1_suggestions

            # For discovery phase: Add special options AFTER first 3 contextual suggestions
            if v1_suggestions and len(v1_suggestions) >= 1:
                # Filter out any existing special options to avoid duplicates
                filtered_suggestions = [s for s in v1_suggestions if s not in ["All of the above", "I don't know"]]

                # Take first 3 contextual suggestions, then add special options
                contextual_suggestions = filtered_suggestions[:3]
                enhanced = contextual_suggestions + ["All of the above", "I don't know"]
                return enhanced[:5]  # Limit to 5 total
            else:
                # Fallback with special options at the end
                return ["Tell me more", "Continue", "What else?", "All of the above", "I don't know"]

        except Exception as e:
            logger.error(f"UX methodology enhancement failed: {e}")
            return v1_suggestions  # Always return V1 suggestions if enhancement fails

    def validate_response_methodology(self, response_content: str) -> bool:
        """Validate that response follows UX research methodology"""

        try:
            # Check for UX research best practices
            content_lower = response_content.lower()

            # Good: Single focused question
            question_count = content_lower.count('?')
            if question_count > 2:
                return False  # Too many questions at once

            # Good: Builds on previous answers
            if any(phrase in content_lower for phrase in ['you mentioned', 'you said', 'you shared']):
                return True

            # Good: Professional tone
            if any(phrase in content_lower for phrase in ['understand', 'help me', 'could you']):
                return True

            return True  # Default to accepting V1's proven responses

        except Exception:
            return True  # Default to accepting V1 responses


class IndustryClassifier:
    """LLM-based intelligent industry classification for enhanced context"""

    def __init__(self):
        self.llm_service = None

    async def classify(self, business_context: Dict[str, Any], llm_service=None) -> Dict[str, Any]:
        """Classify industry using LLM-based semantic analysis"""

        try:
            if llm_service is None:
                from backend.services.llm import LLMServiceFactory
                llm_service = LLMServiceFactory.create("gemini")

            business_idea = business_context.get('businessIdea', '') or business_context.get('business_idea', '')
            target_customer = business_context.get('targetCustomer', '') or business_context.get('target_customer', '')
            problem = business_context.get('problem', '')

            prompt = f"""Analyze this business and provide detailed industry classification for customer research context.

Business Idea: {business_idea}
Target Customer: {target_customer}
Problem: {problem}

Provide comprehensive industry analysis:

Return ONLY valid JSON:
{{
  "industry": "Primary industry category",
  "sub_industry": "Specific sub-category",
  "confidence": 0.0-1.0,
  "characteristics": ["key", "business", "characteristics"],
  "context_for_questions": "specific focus area for research questions",
  "business_model": "description of likely business model",
  "key_success_factors": ["critical", "success", "factors"],
  "typical_challenges": ["common", "industry", "challenges"],
  "research_focus_areas": ["areas", "to", "focus", "research", "on"]
}}

Consider factors like:
- Business model (B2B, B2C, marketplace, service, product)
- Industry dynamics and competition
- Customer behavior patterns
- Regulatory considerations
- Technology requirements
- Scalability factors"""

            response = await llm_service.generate_text(
                prompt=prompt,
                temperature=0.3,
                max_tokens=1200
            )

            # Parse JSON response
            import json
            response_clean = response.strip()
            if response_clean.startswith('```json'):
                response_clean = response_clean[7:]
            if response_clean.endswith('```'):
                response_clean = response_clean[:-3]
            response_clean = response_clean.strip()

            analysis = json.loads(response_clean)

            logger.info(f"🏢 LLM Industry Classification: {analysis.get('industry')}/{analysis.get('sub_industry')} (confidence: {analysis.get('confidence', 0):.2f})")

            return analysis

        except Exception as e:
            logger.error(f"LLM industry classification failed: {e}")
            # Fallback to simple classification
            return {
                'industry': 'General Business',
                'sub_industry': 'General',
                'confidence': 0.5,
                'characteristics': ['customer-centric'],
                'context_for_questions': 'general business focused',
                'business_model': 'unknown',
                'key_success_factors': ['customer satisfaction'],
                'typical_challenges': ['market competition'],
                'research_focus_areas': ['customer needs', 'market validation']
            }


class CustomerResearchServiceV3Rebuilt:
    """
    V3 Rebuilt: V1 Core + Strategic Enhancements

    Design Philosophy:
    - V1 handles ALL core functionality (proven & reliable)
    - V3 adds enhancements as optional layers
    - Fail gracefully to V1 behavior always
    - Monitor enhancement reliability
    """

    def __init__(self):
        # V1 Core Service (Proven & Reliable)
        self.v1_core = None  # Will import V1 functions as needed

        # V3 Enhancement Layers (Optional & Fail-Safe)
        self.ux_methodology = UXResearchMethodology()
        self.industry_classifier = IndustryClassifier()
        self.enhancement_monitor = EnhancementMonitor()

        # V3 Performance Optimization: Simple response cache
        self._response_cache = {}
        self._cache_max_size = 100

        logger.info("🏗️ V3 Rebuilt service initialized with V1 core + fail-safe enhancements")

    def _get_cache_key(self, request: ChatRequest) -> str:
        """Generate cache key for request"""
        try:
            # Create a simple cache key based on recent conversation
            recent_messages = request.messages[-3:] if len(request.messages) > 3 else request.messages
            message_content = " ".join([msg.content for msg in recent_messages])
            cache_content = f"{message_content} {request.input}".lower().strip()

            # Simple hash for cache key
            import hashlib
            return hashlib.md5(cache_content.encode()).hexdigest()[:16]
        except:
            return None

    def _get_from_cache(self, cache_key: str) -> Dict[str, Any]:
        """Get response from cache if available"""
        if cache_key and cache_key in self._response_cache:
            cached_response = self._response_cache[cache_key].copy()
            cached_response['from_cache'] = True
            logger.info(f"🚀 V3 Cache hit for key: {cache_key}")
            return cached_response
        return None

    def _store_in_cache(self, cache_key: str, response: Dict[str, Any]):
        """Store response in cache"""
        if cache_key and len(self._response_cache) < self._cache_max_size:
            # Don't cache the cache flag itself
            cache_response = response.copy()
            cache_response.pop('from_cache', None)
            self._response_cache[cache_key] = cache_response
            logger.info(f"💾 V3 Cached response for key: {cache_key}")

    async def process_chat(self, request: ChatRequest) -> Dict[str, Any]:
        """
        Main orchestration: V1 first, V3 enhancements second

        Flow:
        1. Use V1 core for reliable foundation
        2. Apply V3 enhancements safely
        3. Fall back to V1 if any enhancement fails
        """

        start_time = time.time()
        logger.info(f"🎯 V3 Rebuilt processing chat request")

        # V3 Performance: Check cache first
        cache_key = self._get_cache_key(request)
        cached_response = self._get_from_cache(cache_key)
        if cached_response:
            cached_response['processing_time_ms'] = int((time.time() - start_time) * 1000)
            return cached_response

        try:
            # Step 1: ALWAYS use V1 core for reliability
            v1_response = await self._process_with_v1_core(request)
            logger.info("✅ V1 core processing completed successfully")

            # Step 2: Apply V3 enhancements safely
            enhanced_response = await self._apply_v3_enhancements(v1_response, request)

            # Step 3: Add V3 metadata
            enhanced_response['api_version'] = 'v3-rebuilt'
            enhanced_response['processing_time_ms'] = int((time.time() - start_time) * 1000)
            enhanced_response['v1_core_used'] = True
            enhanced_response['enhancements_applied'] = self._get_applied_enhancements()

            # V3 Performance: Store in cache for future requests
            self._store_in_cache(cache_key, enhanced_response)

            logger.info(f"🎉 V3 Rebuilt completed successfully in {enhanced_response['processing_time_ms']}ms")
            return enhanced_response

        except Exception as e:
            logger.error(f"🔴 V3 Rebuilt failed, attempting V1 fallback: {e}")

            # Ultimate fallback: Pure V1 response
            try:
                v1_fallback = await self._process_with_v1_core(request)
                v1_fallback['api_version'] = 'v3-rebuilt-v1-fallback'
                v1_fallback['processing_time_ms'] = int((time.time() - start_time) * 1000)
                v1_fallback['fallback_used'] = True
                return v1_fallback
            except Exception as fallback_error:
                logger.error(f"🔴 Even V1 fallback failed: {fallback_error}")
                raise HTTPException(status_code=500, detail="Service temporarily unavailable")

    async def _process_with_v1_core(self, request: ChatRequest) -> Dict[str, Any]:
        """Process request using V1's proven core functionality"""

        try:
            # Import V1 proven functions
            from backend.api.routes.customer_research import (
                generate_research_response_with_retry,
                generate_contextual_suggestions,
                extract_context_with_llm,
                analyze_user_intent_with_llm,
                validate_business_readiness_with_llm,
                generate_research_questions,
                Message as V1Message
            )
            from backend.services.llm import LLMServiceFactory

            # Create V1-compatible LLM service
            llm_service = LLMServiceFactory.create("gemini")

            # Convert V3 messages to V1 format
            v1_messages = []
            for msg in request.messages:
                v1_messages.append(V1Message(
                    id=msg.id or f'msg_{int(time.time())}',
                    content=msg.content,
                    role=msg.role,
                    timestamp=msg.timestamp or datetime.now().isoformat(),
                    metadata=msg.metadata
                ))

            # Build conversation context (V1 pattern)
            conversation_context = ""
            for msg in request.messages:
                conversation_context += f"{msg.role}: {msg.content}\n"
            if request.input:
                conversation_context += f"user: {request.input}\n"

            # V3 Optimized Analysis Pipeline - Parallel execution for better performance
            import asyncio

            # Execute context and intent analysis in parallel to reduce latency
            context_task = extract_context_with_llm(
                llm_service=llm_service,
                conversation_context=conversation_context,
                latest_input=request.input
            )

            intent_task = analyze_user_intent_with_llm(
                llm_service=llm_service,
                conversation_context=conversation_context,
                latest_input=request.input,
                messages=v1_messages
            )

            # Run context and intent analysis in parallel
            context_analysis, intent_analysis = await asyncio.gather(context_task, intent_task)

            # Only run business validation if we don't have obvious continuation intent
            if intent_analysis.get('intent') in ['confirmation', 'question_request']:
                # Skip expensive business validation for obvious cases
                business_validation = {
                    'ready_for_questions': True,
                    'confidence': 0.9,
                    'reasoning': f"User intent is {intent_analysis.get('intent')}, skipping detailed validation",
                    'conversation_quality': 'high'
                }
            else:
                # Run business validation only when needed
                business_validation = await validate_business_readiness_with_llm(
                    llm_service=llm_service,
                    conversation_context=conversation_context,
                    latest_input=request.input
                )

            # V3 Rebuilt Enhancement: LLM-based intelligent validation for better UX
            ready_for_questions = await self._enhanced_business_readiness_check(
                business_validation, context_analysis, intent_analysis, v1_messages, llm_service
            )

            # V3 Fix: LLM-based user confirmation detection
            user_confirmed = await self._check_user_confirmation_with_llm(
                llm_service, intent_analysis, request.input, v1_messages
            )

            if ready_for_questions and user_confirmed:
                # Generate questions using V1's proven method
                questions = await generate_research_questions(
                    llm_service=llm_service,
                    context=request.context,
                    conversation_history=request.messages
                )

                return {
                    "content": "COMPREHENSIVE_QUESTIONS_COMPONENT",
                    "questions": questions,
                    "suggestions": ["Yes, that's right", "Generate research questions", "Let me clarify something"],
                    "metadata": {
                        "extracted_context": context_analysis,
                        "user_intent": intent_analysis,
                        "business_readiness": business_validation,
                        "questions_generated": True,
                        "v1_core": True
                    }
                }
            elif ready_for_questions and not user_confirmed:
                # Show confirmation summary before generating questions
                return await self._generate_confirmation_summary(
                    llm_service, context_analysis, intent_analysis, business_validation, v1_messages, request
                )
            else:
                # Generate response using V1's proven method
                context_obj = type('Context', (), {
                    'businessIdea': context_analysis.get('businessIdea'),
                    'targetCustomer': context_analysis.get('targetCustomer'),
                    'problem': context_analysis.get('problem'),
                    'stage': context_analysis.get('stage')
                })()

                # V3 Optimization: Generate response and suggestions in parallel
                response_task = generate_research_response_with_retry(
                    llm_service=llm_service,
                    messages=v1_messages,
                    user_input=request.input,
                    context=context_obj,
                    conversation_context=conversation_context
                )

                # Start response generation
                response_content = await response_task

                # Generate suggestions using V1's proven method (but optimized)
                suggestions = await generate_contextual_suggestions(
                    llm_service=llm_service,
                    messages=v1_messages,
                    user_input=request.input,
                    assistant_response=response_content,
                    conversation_context=conversation_context
                )

                return {
                    "content": response_content,
                    "questions": None,
                    "suggestions": suggestions,
                    "metadata": {
                        "extracted_context": context_analysis,
                        "user_intent": intent_analysis,
                        "business_readiness": business_validation,
                        "questions_generated": False,
                        "v1_core": True
                    }
                }

        except Exception as e:
            logger.error(f"V1 core processing failed: {e}")
            raise

    async def _apply_v3_enhancements(self, v1_response: Dict[str, Any], request: ChatRequest) -> Dict[str, Any]:
        """Apply V3 enhancements to V1 response safely"""

        enhanced_response = v1_response.copy()
        applied_enhancements = []

        # Enhancement 1: UX Research Methodology (Special Options)
        if self.enhancement_monitor.is_enabled('ux_methodology'):
            try:
                conversation_stage = self._determine_conversation_stage(v1_response)
                logger.info(f"🔍 Conversation stage determined: {conversation_stage}")

                if enhanced_response.get('suggestions'):
                    original_suggestions = enhanced_response['suggestions']
                    logger.info(f"🔍 Original suggestions: {original_suggestions}")

                    enhanced_suggestions = self.ux_methodology.enhance_suggestions(
                        original_suggestions, conversation_stage
                    )
                    enhanced_response['suggestions'] = enhanced_suggestions
                    applied_enhancements.append('ux_methodology')
                    self.enhancement_monitor.record_success('ux_methodology')

                    logger.info(f"✅ UX methodology: {original_suggestions} → {enhanced_suggestions}")
                else:
                    logger.warning(f"🔍 No suggestions found in enhanced_response for UX enhancement")

            except Exception as e:
                logger.warning(f"UX methodology enhancement failed: {e}")
                self.enhancement_monitor.record_failure('ux_methodology')

        # Enhancement 2: LLM-based Industry Classification
        if self.enhancement_monitor.is_enabled('industry_classification'):
            try:
                context_data = enhanced_response.get('metadata', {}).get('extracted_context', {})

                # Use LLM-based classification
                from backend.services.llm import LLMServiceFactory
                llm_service = LLMServiceFactory.create("gemini")
                industry_data = await self.industry_classifier.classify(context_data, llm_service)

                if not enhanced_response.get('metadata'):
                    enhanced_response['metadata'] = {}
                enhanced_response['metadata']['industry_analysis'] = industry_data
                applied_enhancements.append('industry_classification')
                self.enhancement_monitor.record_success('industry_classification')

                logger.info(f"✅ Industry classified: {industry_data.get('industry')}/{industry_data.get('sub_industry')}")

            except Exception as e:
                logger.warning(f"Industry classification enhancement failed: {e}")
                self.enhancement_monitor.record_failure('industry_classification')

        # Enhancement 3: Response Methodology Validation
        if self.enhancement_monitor.is_enabled('response_validation'):
            try:
                response_content = enhanced_response.get('content', '')
                is_valid = self.ux_methodology.validate_response_methodology(response_content)

                if not enhanced_response.get('metadata'):
                    enhanced_response['metadata'] = {}
                enhanced_response['metadata']['ux_methodology_compliant'] = is_valid
                applied_enhancements.append('response_validation')
                self.enhancement_monitor.record_success('response_validation')

            except Exception as e:
                logger.warning(f"Response validation enhancement failed: {e}")
                self.enhancement_monitor.record_failure('response_validation')

        # Store applied enhancements for monitoring
        enhanced_response['v3_enhancements'] = applied_enhancements

        return enhanced_response

    async def _enhanced_business_readiness_check(
        self,
        business_validation: Dict[str, Any],
        context_analysis: Dict[str, Any],
        intent_analysis: Dict[str, Any],
        messages: List[Any],
        llm_service
    ) -> bool:
        """Enhanced business readiness check using LLM-based intelligent analysis"""

        try:
            # V3 Enhancement: LLM-based analysis takes precedence over V1 assumptions
            business_idea = context_analysis.get('business_idea', '') or context_analysis.get('businessIdea', '')
            target_customer = context_analysis.get('target_customer', '') or context_analysis.get('targetCustomer', '')
            problem = context_analysis.get('problem', '')

            # Handle None values safely
            business_idea = business_idea or ''
            target_customer = target_customer or ''
            problem = problem or ''

            # Basic length checks (still useful)
            has_business_idea = len(business_idea.strip()) > 10
            has_target_customer = len(target_customer.strip()) > 5

            # Check conversation depth
            user_message_count = len([msg for msg in messages if hasattr(msg, 'role') and msg.role == 'user'])
            has_sufficient_depth = user_message_count >= 3

            # LLM-based problem context analysis (this is the critical check)
            has_problem_context = await self._analyze_problem_context_with_llm(
                llm_service, business_idea, target_customer, problem, messages
            )

            # LLM-based business type analysis (replaces hardcoded industry patterns)
            business_type_analysis = await self._analyze_business_type_with_llm(
                llm_service, business_idea, target_customer
            )

            # V3 Enhanced Logic: LLM analysis is authoritative for problem context
            # Don't rely on V1's assumptions about "implied" problems
            v3_ready = (
                has_business_idea and
                has_target_customer and
                has_problem_context and  # This must be explicitly validated by LLM
                has_sufficient_depth
            )

            # Use LLM analysis for business-specific thresholds
            if business_type_analysis.get('requires_lower_threshold', False) and has_problem_context:
                # For certain business types, be more lenient with conversation depth
                # BUT still require explicit problem context
                v3_ready = (
                    has_business_idea and
                    has_target_customer and
                    has_problem_context and  # Still required even for lenient validation
                    user_message_count >= 2
                )
                if v3_ready:
                    logger.info(f"🎯 V3 Enhanced: {business_type_analysis.get('business_type')} detected, using lenient validation")
                    return True

            if v3_ready:
                logger.info("🎯 V3 Enhanced: LLM analysis confirms sufficient context for question generation")
                return True

            # Log detailed reasoning for debugging
            logger.info(f"🔍 V3 Enhanced: Not ready - business_idea: {has_business_idea}, customer: {has_target_customer}, problem_context: {has_problem_context}, depth: {has_sufficient_depth}")

            # If LLM says no problem context, don't generate questions regardless of V1's opinion
            if not has_problem_context:
                logger.info("🚫 V3 Enhanced: LLM analysis indicates insufficient problem context - overriding V1 validation")
                return False

            return False

        except Exception as e:
            logger.error(f"Enhanced business readiness check failed: {e}")
            # Fallback to V1 logic
            return business_validation.get('ready_for_questions', False)

    async def _analyze_problem_context_with_llm(
        self,
        llm_service,
        business_idea: str,
        target_customer: str,
        problem: str,
        messages: List[Any]
    ) -> bool:
        """Use LLM to analyze if conversation contains sufficient problem context"""

        try:
            # Build conversation context
            conversation_text = ""
            for msg in messages[-5:]:  # Last 5 messages for context
                if hasattr(msg, 'role') and hasattr(msg, 'content'):
                    conversation_text += f"{msg.role}: {msg.content}\n"

            prompt = f"""Analyze this customer research conversation to determine if there is sufficient PROBLEM CONTEXT for generating research questions.

Business Idea: {business_idea}
Target Customer: {target_customer}
Explicit Problem: {problem}

Recent Conversation:
{conversation_text}

Evaluate whether the conversation contains enough information about:
1. What specific problem or pain point the business is trying to solve
2. Why customers would need this solution
3. What challenges or frustrations the target customers currently face

Important distinctions:
- Describing business OFFERINGS (e.g., "community hub", "pickup service") is NOT the same as identifying customer PROBLEMS
- Mentioning service features is NOT the same as explaining why customers need those features
- A business idea can be clear without the underlying customer problem being articulated

Return ONLY valid JSON:
{{
  "has_problem_context": true/false,
  "confidence": 0.0-1.0,
  "reasoning": "Detailed explanation of why problem context is sufficient or insufficient",
  "problem_indicators": ["list", "of", "specific", "problem", "indicators", "found"],
  "missing_elements": ["what", "problem", "context", "is", "still", "needed"]
}}

Be conservative - only return true if there's clear evidence of customer problems or pain points, not just business features."""

            response = await llm_service.generate_text(
                prompt=prompt,
                temperature=0.2,
                max_tokens=1000
            )

            # Parse JSON response
            import json
            response_clean = response.strip()
            if response_clean.startswith('```json'):
                response_clean = response_clean[7:]
            if response_clean.endswith('```'):
                response_clean = response_clean[:-3]
            response_clean = response_clean.strip()

            analysis = json.loads(response_clean)

            has_context = analysis.get('has_problem_context', False)
            confidence = analysis.get('confidence', 0.0)

            logger.info(f"🧠 LLM Problem Analysis: has_context={has_context}, confidence={confidence:.2f}")
            logger.info(f"🧠 Reasoning: {analysis.get('reasoning', 'No reasoning provided')}")

            return has_context and confidence >= 0.7  # Require high confidence

        except Exception as e:
            logger.error(f"LLM problem context analysis failed: {e}")
            # Conservative fallback - require explicit problem statement
            return len(problem.strip()) > 10

    async def _analyze_business_type_with_llm(
        self,
        llm_service,
        business_idea: str,
        target_customer: str
    ) -> Dict[str, Any]:
        """Use LLM to analyze business type and determine appropriate validation thresholds"""

        try:
            prompt = f"""Analyze this business idea and determine the appropriate validation approach for customer research.

Business Idea: {business_idea}
Target Customer: {target_customer}

Classify the business and determine if it should have more lenient validation requirements:

Return ONLY valid JSON:
{{
  "business_type": "specific business category",
  "industry": "industry classification",
  "requires_lower_threshold": true/false,
  "reasoning": "why this business type needs different validation",
  "characteristics": ["list", "of", "business", "characteristics"],
  "validation_complexity": "low/medium/high"
}}

Guidelines for requires_lower_threshold:
- true: Simple service businesses where the problem is often obvious (laundry, food, basic services)
- false: Complex businesses requiring detailed problem articulation (SaaS, B2B tools, innovative products)"""

            response = await llm_service.generate_text(
                prompt=prompt,
                temperature=0.3,
                max_tokens=800
            )

            # Parse JSON response
            import json
            response_clean = response.strip()
            if response_clean.startswith('```json'):
                response_clean = response_clean[7:]
            if response_clean.endswith('```'):
                response_clean = response_clean[:-3]
            response_clean = response_clean.strip()

            analysis = json.loads(response_clean)

            logger.info(f"🏢 LLM Business Type Analysis: {analysis.get('business_type')} - Lower threshold: {analysis.get('requires_lower_threshold')}")

            return analysis

        except Exception as e:
            logger.error(f"LLM business type analysis failed: {e}")
            # Conservative fallback
            return {
                "business_type": "unknown",
                "industry": "general",
                "requires_lower_threshold": False,
                "reasoning": "LLM analysis failed, using conservative approach",
                "characteristics": [],
                "validation_complexity": "high"
            }

    async def _check_user_confirmation_with_llm(
        self,
        llm_service,
        intent_analysis: Dict[str, Any],
        user_input: str,
        messages: List[Any]
    ) -> bool:
        """Use LLM to detect if user is explicitly confirming their business summary"""

        try:
            # Build recent conversation context
            conversation_text = ""
            for msg in messages[-3:]:  # Last 3 messages for context
                if hasattr(msg, 'role') and hasattr(msg, 'content'):
                    conversation_text += f"{msg.role}: {msg.content}\n"

            prompt = f"""Analyze this user input to determine if they are explicitly CONFIRMING their business summary or just CONTINUING to provide more information.

Recent Conversation:
{conversation_text}

Latest User Input: "{user_input}"

Intent Analysis: {intent_analysis.get('intent', 'unknown')}

Determine if the user is:
1. CONFIRMING: Explicitly agreeing that their business summary is correct and ready for questions
2. CONTINUING: Still providing more details, clarifications, or additional information

Return ONLY valid JSON:
{{
  "is_confirmation": true/false,
  "confidence": 0.0-1.0,
  "reasoning": "Detailed explanation of why this is confirmation or continuation",
  "confirmation_indicators": ["specific", "phrases", "that", "indicate", "confirmation"],
  "continuation_indicators": ["specific", "phrases", "that", "indicate", "continuation"]
}}

Examples of CONFIRMATION:
- "Yes, that's correct"
- "That sounds right"
- "Generate the questions"
- "Let's proceed"
- "That's exactly what I meant"

Examples of CONTINUATION:
- Providing new details about the business
- Clarifying or correcting previous information
- Adding more features or services
- Describing additional aspects of the business"""

            response = await llm_service.generate_text(
                prompt=prompt,
                temperature=0.2,
                max_tokens=800
            )

            # Parse JSON response
            import json
            response_clean = response.strip()
            if response_clean.startswith('```json'):
                response_clean = response_clean[7:]
            if response_clean.endswith('```'):
                response_clean = response_clean[:-3]
            response_clean = response_clean.strip()

            analysis = json.loads(response_clean)

            is_confirmation = analysis.get('is_confirmation', False)
            confidence = analysis.get('confidence', 0.0)

            logger.info(f"🤝 LLM Confirmation Analysis: is_confirmation={is_confirmation}, confidence={confidence:.2f}")
            logger.info(f"🤝 Reasoning: {analysis.get('reasoning', 'No reasoning provided')}")

            return is_confirmation and confidence >= 0.8  # Require high confidence for confirmation

        except Exception as e:
            logger.error(f"LLM user confirmation analysis failed: {e}")
            # Conservative fallback - assume continuation unless explicit confirmation phrases
            confirmation_phrases = ['yes', 'correct', 'right', 'generate', 'proceed', 'ready']
            return any(phrase in user_input.lower() for phrase in confirmation_phrases)

    async def _generate_confirmation_summary(
        self,
        llm_service,
        context_analysis: Dict[str, Any],
        intent_analysis: Dict[str, Any],
        business_validation: Dict[str, Any],
        messages: List[Any],
        request
    ) -> Dict[str, Any]:
        """Generate a confirmation summary before question generation"""

        try:
            business_idea = context_analysis.get('business_idea', '') or context_analysis.get('businessIdea', '')
            target_customer = context_analysis.get('target_customer', '') or context_analysis.get('targetCustomer', '')
            problem = context_analysis.get('problem', '')

            # Generate confirmation summary using LLM
            prompt = f"""Create a clear, concise confirmation summary for this business idea before generating research questions.

Business Idea: {business_idea}
Target Customer: {target_customer}
Problem: {problem}

Create a professional summary that:
1. Clearly states what the business does
2. Identifies who the target customers are
3. Explains what problem it solves (if identified)
4. Asks for user confirmation before proceeding

Format as a conversational response that ends with asking the user to confirm if this summary is accurate."""

            summary_content = await llm_service.generate_text(
                prompt=prompt,
                temperature=0.3,
                max_tokens=500
            )

            return {
                "content": summary_content,
                "questions": None,
                "suggestions": ["Yes, that's correct", "Let me clarify something", "Generate questions anyway"],
                "metadata": {
                    "extracted_context": context_analysis,
                    "user_intent": intent_analysis,
                    "business_readiness": business_validation,
                    "questions_generated": False,
                    "confirmation_needed": True,
                    "v1_core": True
                }
            }

        except Exception as e:
            logger.error(f"Confirmation summary generation failed: {e}")
            # Fallback to simple confirmation
            return {
                "content": "I have enough information about your business idea. Would you like me to generate research questions now?",
                "questions": None,
                "suggestions": ["Yes, generate questions", "Let me add more details", "Show me what you understand"],
                "metadata": {
                    "extracted_context": context_analysis,
                    "user_intent": intent_analysis,
                    "business_readiness": business_validation,
                    "questions_generated": False,
                    "confirmation_needed": True,
                    "v1_core": True
                }
            }

    def _determine_conversation_stage(self, v1_response: Dict[str, Any]) -> str:
        """Determine conversation stage from V1 response"""

        try:
            metadata = v1_response.get('metadata', {})

            # Only return ready_for_questions if user explicitly confirmed
            # Don't skip UX enhancements just because questions were generated
            if metadata.get('questionCategory') == 'confirmation' and metadata.get('needs_confirmation'):
                return 'confirmation'

            # Check business readiness for confirmation phase
            business_readiness = metadata.get('business_readiness', {})
            if business_readiness.get('ready_for_questions') and not v1_response.get('questions'):
                return 'confirmation'

            # Always use discovery phase for UX enhancements unless explicitly in confirmation
            # This ensures "All of the above" and "I don't know" are added to suggestions
            return 'discovery'

        except Exception:
            return 'discovery'

    def _get_applied_enhancements(self) -> List[str]:
        """Get list of currently enabled enhancements"""

        all_enhancements = ['ux_methodology', 'industry_classification', 'response_validation']
        return [e for e in all_enhancements if self.enhancement_monitor.is_enabled(e)]


# Global service instance
v3_rebuilt_service = CustomerResearchServiceV3Rebuilt()


@router.post("/chat", response_model=ChatResponse)
async def chat_v3_rebuilt(
    request: ChatRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    V3 Rebuilt Chat Endpoint

    Uses V1 core for reliability + V3 enhancements for improved UX
    Automatically falls back to V1 behavior if enhancements fail
    """

    try:
        logger.info(f"🎯 V3 Rebuilt chat request: {request.input}")

        # Process with V3 Rebuilt service
        result = await v3_rebuilt_service.process_chat(request)

        # Convert to ChatResponse format
        response = ChatResponse(
            content=result.get('content', ''),
            metadata=result.get('metadata', {}),
            questions=result.get('questions'),
            suggestions=result.get('suggestions', []),
            session_id=request.session_id
        )

        logger.info(f"✅ V3 Rebuilt chat completed successfully")
        return response

    except Exception as e:
        logger.error(f"🔴 V3 Rebuilt chat failed: {e}")
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {str(e)}")


@router.post("/questions", response_model=ResearchQuestions)
async def generate_questions_v3_rebuilt(
    request: GenerateQuestionsRequest,
    db: Session = Depends(get_db)
):
    """
    V3 Rebuilt Question Generation

    Uses V1's proven question generation with V3 enhancements
    """

    try:
        logger.info(f"🎯 V3 Rebuilt question generation request")

        # Use V1's proven question generation directly
        from backend.api.routes.customer_research import generate_research_questions
        from backend.services.llm import LLMServiceFactory

        llm_service = LLMServiceFactory.create("gemini")

        # Generate questions using V1's proven method
        questions = await generate_research_questions(
            llm_service=llm_service,
            context=request.context,
            conversation_history=request.conversation_history
        )

        # Apply V3 enhancements to questions if enabled
        if v3_rebuilt_service.enhancement_monitor.is_enabled('industry_classification'):
            try:
                # Add industry context to questions metadata using LLM analysis
                context_dict = {
                    'businessIdea': request.context.businessIdea,
                    'targetCustomer': request.context.targetCustomer,
                    'problem': request.context.problem
                }
                industry_data = await v3_rebuilt_service.industry_classifier.classify(context_dict, llm_service)

                # Enhance questions with industry context (if questions object supports it)
                if hasattr(questions, 'metadata'):
                    questions.metadata = questions.metadata or {}
                    questions.metadata['industry_analysis'] = industry_data

            except Exception as e:
                logger.warning(f"Question enhancement failed: {e}")

        logger.info(f"✅ V3 Rebuilt questions generated successfully")
        return questions

    except Exception as e:
        logger.error(f"🔴 V3 Rebuilt question generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Question generation failed: {str(e)}")


@router.get("/health")
async def health_check_v3_rebuilt():
    """Health check for V3 Rebuilt service"""

    return {
        "status": "healthy",
        "service": "customer-research-v3-rebuilt",
        "version": "1.0.0",
        "architecture": "v1-core-with-v3-enhancements",
        "enabled_enhancements": v3_rebuilt_service._get_applied_enhancements(),
        "disabled_enhancements": list(v3_rebuilt_service.enhancement_monitor.disabled_enhancements),
        "enhancement_stats": {
            "success_counts": v3_rebuilt_service.enhancement_monitor.success_counts,
            "failure_counts": v3_rebuilt_service.enhancement_monitor.failure_counts
        }
    }


@router.get("/thinking-progress/{request_id}")
async def get_thinking_progress_v3_rebuilt(request_id: str):
    """
    Thinking Progress for V3 Rebuilt

    V3 Rebuilt processes faster than V3 Simple, so thinking progress
    is typically completed immediately. This endpoint provides compatibility
    with frontend components that expect thinking progress.
    """

    try:
        # V3 Rebuilt is designed for fast processing with V1 core
        # Most requests complete quickly, so we return completed state
        return {
            "request_id": request_id,
            "thinking_process": [
                {
                    "step": "context_analysis",
                    "description": "Analyzing business context using V1 proven methods",
                    "status": "completed",
                    "timestamp": datetime.now().isoformat()
                },
                {
                    "step": "intent_analysis",
                    "description": "Understanding user intent with V1 reliability",
                    "status": "completed",
                    "timestamp": datetime.now().isoformat()
                },
                {
                    "step": "response_generation",
                    "description": "Generating response using V1 core + V3 enhancements",
                    "status": "completed",
                    "timestamp": datetime.now().isoformat()
                },
                {
                    "step": "enhancement_application",
                    "description": "Applying UX methodology and industry classification",
                    "status": "completed",
                    "timestamp": datetime.now().isoformat()
                }
            ],
            "is_complete": True,
            "total_steps": 4,
            "completed_steps": 4,
            "processing_time_ms": 0,  # V3 Rebuilt is fast
            "service_version": "v3-rebuilt"
        }

    except Exception as e:
        logger.error(f"Thinking progress error: {e}")
        return {
            "request_id": request_id,
            "thinking_process": [],
            "is_complete": True,
            "total_steps": 0,
            "completed_steps": 0,
            "error": "V3 Rebuilt processes quickly - thinking progress not needed"
        }
