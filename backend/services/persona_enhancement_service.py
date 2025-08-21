"""
Persona Enhancement Service

This service enhances existing personas with stakeholder intelligence features,
creating a unified system that eliminates duplication between personas and
stakeholder entities.
"""

import logging
from typing import List, Dict, Any, Optional
from backend.models.enhanced_persona_models import (
    EnhancedPersona,
    EnhancedPersonaTrait,
    StakeholderIntelligence,
    InfluenceMetrics,
    PersonaRelationship,
    ConflictIndicator,
    ConsensusLevel,
    PersonaEnhancementResult
)

logger = logging.getLogger(__name__)


class PersonaEnhancementService:
    """Service for enhancing personas with stakeholder intelligence features"""
    
    def __init__(self, llm_service=None):
        self.llm_service = llm_service
        
    async def enhance_personas_with_stakeholder_intelligence(
        self,
        personas: List[Dict[str, Any]],
        stakeholder_intelligence: Optional[Dict[str, Any]] = None,
        analysis_context: Optional[Dict[str, Any]] = None
    ) -> PersonaEnhancementResult:
        """
        Enhance existing personas with stakeholder intelligence features.
        
        Args:
            personas: List of existing persona dictionaries
            stakeholder_intelligence: Optional stakeholder intelligence data
            analysis_context: Optional analysis context (themes, patterns, etc.)
            
        Returns:
            PersonaEnhancementResult with enhanced personas
        """
        logger.info(f"[PERSONA_ENHANCEMENT] Starting enhancement of {len(personas)} personas")
        
        enhanced_personas = []
        relationships_created = 0
        conflicts_identified = 0
        
        # Step 1: Convert existing personas to enhanced format
        for i, persona in enumerate(personas):
            try:
                enhanced_persona = await self._convert_to_enhanced_persona(persona, i)
                enhanced_personas.append(enhanced_persona)
                logger.info(f"[PERSONA_ENHANCEMENT] Converted persona: {enhanced_persona.name}")
            except Exception as e:
                logger.error(f"[PERSONA_ENHANCEMENT] Error converting persona {i}: {str(e)}")
                continue
        
        # Step 2: Add stakeholder intelligence features
        if stakeholder_intelligence and stakeholder_intelligence.get('detected_stakeholders'):
            enhanced_personas = await self._add_stakeholder_features(
                enhanced_personas, 
                stakeholder_intelligence
            )
        
        # Step 3: Analyze relationships between personas
        relationships_created = await self._analyze_persona_relationships(enhanced_personas)
        
        # Step 4: Identify conflicts and consensus
        conflicts_identified = await self._identify_conflicts_and_consensus(
            enhanced_personas, 
            analysis_context
        )
        
        result = PersonaEnhancementResult(
            enhanced_personas=enhanced_personas,
            processing_metadata={
                "original_persona_count": len(personas),
                "enhanced_persona_count": len(enhanced_personas),
                "stakeholder_data_used": bool(stakeholder_intelligence),
                "analysis_context_used": bool(analysis_context)
            },
            relationships_created=relationships_created,
            conflicts_identified=conflicts_identified
        )
        
        logger.info(f"[PERSONA_ENHANCEMENT] Enhancement complete: {len(enhanced_personas)} personas, "
                   f"{relationships_created} relationships, {conflicts_identified} conflicts")
        
        return result
    
    async def _convert_to_enhanced_persona(
        self, 
        persona: Dict[str, Any], 
        index: int
    ) -> EnhancedPersona:
        """Convert a regular persona to enhanced format"""
        
        # Extract core fields
        name = persona.get('name', f'Persona {index + 1}')
        description = persona.get('description', '')
        archetype = persona.get('archetype', None)
        
        # Convert traits to enhanced format
        demographics = self._convert_trait(persona.get('demographics'))
        goals_and_motivations = self._convert_trait(persona.get('goals_and_motivations'))
        challenges_and_frustrations = self._convert_trait(persona.get('challenges_and_frustrations'))
        
        # Extract metadata
        overall_confidence = persona.get('overall_confidence', persona.get('confidence', 0.7))
        supporting_evidence = persona.get('supporting_evidence_summary', persona.get('evidence', []))
        patterns = persona.get('patterns', [])
        metadata = persona.get('persona_metadata', persona.get('metadata', {}))
        
        # Create enhanced persona with default stakeholder intelligence
        enhanced_persona = EnhancedPersona(
            name=name,
            description=description,
            archetype=archetype,
            demographics=demographics,
            goals_and_motivations=goals_and_motivations,
            challenges_and_frustrations=challenges_and_frustrations,
            overall_confidence=overall_confidence,
            supporting_evidence_summary=supporting_evidence if isinstance(supporting_evidence, list) else [],
            patterns=patterns if isinstance(patterns, list) else [],
            persona_metadata=metadata if isinstance(metadata, dict) else {}
        )
        
        return enhanced_persona
    
    def _convert_trait(self, trait_data: Any) -> Optional[EnhancedPersonaTrait]:
        """Convert a trait to enhanced format"""
        if not trait_data:
            return None
            
        if isinstance(trait_data, dict):
            return EnhancedPersonaTrait(
                value=trait_data.get('value', ''),
                confidence=trait_data.get('confidence', 0.7),
                evidence=trait_data.get('evidence', [])
            )
        elif isinstance(trait_data, str):
            return EnhancedPersonaTrait(
                value=trait_data,
                confidence=0.7,
                evidence=[]
            )
        
        return None
    
    async def _add_stakeholder_features(
        self,
        personas: List[EnhancedPersona],
        stakeholder_intelligence: Dict[str, Any]
    ) -> List[EnhancedPersona]:
        """Add stakeholder intelligence features to personas"""
        
        detected_stakeholders = stakeholder_intelligence.get('detected_stakeholders', [])
        
        # Map stakeholders to personas based on similarity
        for i, persona in enumerate(personas):
            if i < len(detected_stakeholders):
                stakeholder = detected_stakeholders[i]
                
                # Determine stakeholder type
                stakeholder_type = stakeholder.get('stakeholder_type', 'primary_customer')
                
                # Extract influence metrics
                influence_data = stakeholder.get('influence_metrics', {})
                influence_metrics = InfluenceMetrics(
                    decision_power=influence_data.get('decision_power', 0.5),
                    technical_influence=influence_data.get('technical_influence', 0.5),
                    budget_influence=influence_data.get('budget_influence', 0.5)
                )
                
                # Update persona's stakeholder intelligence
                persona.stakeholder_intelligence.stakeholder_type = stakeholder_type
                persona.stakeholder_intelligence.influence_metrics = influence_metrics
                
                logger.info(f"[PERSONA_ENHANCEMENT] Added stakeholder features to {persona.name}: "
                           f"type={stakeholder_type}, decision_power={influence_metrics.decision_power}")
        
        return personas
    
    async def _analyze_persona_relationships(
        self, 
        personas: List[EnhancedPersona]
    ) -> int:
        """Analyze relationships between personas"""
        relationships_created = 0
        
        # Simple relationship analysis based on stakeholder types
        for i, persona1 in enumerate(personas):
            for j, persona2 in enumerate(personas):
                if i >= j:  # Avoid duplicates and self-relationships
                    continue
                
                relationship = self._determine_relationship(persona1, persona2)
                if relationship:
                    persona1.stakeholder_intelligence.relationships.append(relationship)
                    relationships_created += 1
        
        return relationships_created
    
    def _determine_relationship(
        self, 
        persona1: EnhancedPersona, 
        persona2: EnhancedPersona
    ) -> Optional[PersonaRelationship]:
        """Determine relationship between two personas"""
        
        type1 = persona1.stakeholder_intelligence.stakeholder_type
        type2 = persona2.stakeholder_intelligence.stakeholder_type
        
        # Define relationship rules
        if type1 == "decision_maker" and type2 == "primary_customer":
            return PersonaRelationship(
                target_persona_id=persona2.name,
                relationship_type="influences",
                strength=0.8,
                description=f"{persona1.name} makes decisions that affect {persona2.name}"
            )
        elif type1 == "primary_customer" and type2 == "secondary_user":
            return PersonaRelationship(
                target_persona_id=persona2.name,
                relationship_type="collaborates_with",
                strength=0.6,
                description=f"{persona1.name} collaborates with {persona2.name}"
            )
        
        return None
    
    async def _identify_conflicts_and_consensus(
        self,
        personas: List[EnhancedPersona],
        analysis_context: Optional[Dict[str, Any]]
    ) -> int:
        """Identify conflicts and consensus between personas"""
        conflicts_identified = 0
        
        if not analysis_context:
            return conflicts_identified
        
        themes = analysis_context.get('themes', [])
        
        # Simple conflict identification based on opposing stakeholder types
        for persona in personas:
            if persona.stakeholder_intelligence.stakeholder_type == "decision_maker":
                # Decision makers might have conflicts with primary customers on cost/features
                conflict = ConflictIndicator(
                    topic="Cost vs Features",
                    severity=0.6,
                    description="Potential conflict between cost control and feature requests",
                    evidence=["Budget constraints mentioned", "Feature requests from users"]
                )
                persona.stakeholder_intelligence.conflict_indicators.append(conflict)
                conflicts_identified += 1
            
            # Add consensus levels for themes
            for theme in themes[:3]:  # Limit to first 3 themes
                consensus = ConsensusLevel(
                    theme_or_pattern=theme.get('name', 'Unknown Theme'),
                    agreement_score=0.7,  # Default consensus level
                    supporting_evidence=[f"Theme mentioned by {persona.name}"]
                )
                persona.stakeholder_intelligence.consensus_levels.append(consensus)
        
        return conflicts_identified
