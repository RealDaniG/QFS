"""
PolicyEngine.py - Minimal policy engine for translating AEGIS advisories into client-facing policy hints

This module provides a deterministic, functional policy engine that takes AEGIS advisory data
and translates it into client-consumable policy hints such as visibility levels and warning banners.
"""
import json
import hashlib
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum

class VisibilityLevel(Enum):
    """Visibility levels for content"""
    VISIBLE = 'visible'
    WARNED = 'warned'
    HIDDEN = 'hidden'

class WarningBannerType(Enum):
    """Types of warning banners"""
    NONE = 'none'
    GENERAL = 'general'
    SAFETY = 'safety'
    ECONOMIC = 'economic'

@dataclass
class PolicyHints:
    """Policy hints for client consumption"""
    visibility_level: VisibilityLevel
    warning_banner: WarningBannerType
    warning_message: Optional[str] = None
    requires_click_through: bool = False
    client_tags: List[str] = field(default_factory=list)

@dataclass
class PolicyConfiguration:
    """Configuration for policy engine rules"""
    info_visibility: VisibilityLevel = VisibilityLevel.VISIBLE
    warning_visibility: VisibilityLevel = VisibilityLevel.WARNED
    critical_visibility: VisibilityLevel = VisibilityLevel.HIDDEN
    info_banner: WarningBannerType = WarningBannerType.NONE
    warning_banner: WarningBannerType = WarningBannerType.GENERAL
    critical_banner: WarningBannerType = WarningBannerType.SAFETY
    require_click_through_for_warning: bool = False
    require_click_through_for_critical: bool = True

class PolicyEngine:
    """
    Minimal policy engine that translates AEGIS advisories into client-facing policy hints.
    
    This engine is purely functional and deterministic with no I/O or state.
    It takes AEGIS advisory data and configuration rules to produce policy hints.
    """

    def __init__(self, config: Optional[PolicyConfiguration]=None):
        """
        Initialize the policy engine.
        
        Args:
            config: Policy configuration with rules and thresholds
        """
        self.config = config or PolicyConfiguration()

    def generate_policy_hints(self, aegis_advisory: Dict[str, Any]) -> PolicyHints:
        """
        Generate policy hints from AEGIS advisory data.
        
        Args:
            aegis_advisory: AEGIS advisory data with block_suggested and severity fields
            
        Returns:
            PolicyHints: Client-facing policy hints
        """
        block_suggested = aegis_advisory.get('block_suggested', False)
        severity = aegis_advisory.get('severity', 'info')
        visibility_level = self._determine_visibility_level(severity, block_suggested)
        warning_banner, warning_message = self._determine_warning_banner(severity)
        requires_click_through = self._determine_click_through_requirement(severity)
        client_tags = self._generate_client_tags(aegis_advisory)
        return PolicyHints(visibility_level=visibility_level, warning_banner=warning_banner, warning_message=warning_message, requires_click_through=requires_click_through, client_tags=client_tags)

    def _determine_visibility_level(self, severity: str, block_suggested: bool) -> VisibilityLevel:
        """Determine visibility level based on severity and block suggestion."""
        if block_suggested:
            if severity == 'critical':
                return self.config.critical_visibility
            elif severity == 'warning':
                return self.config.warning_visibility
            else:
                return self.config.info_visibility
        else:
            return VisibilityLevel.VISIBLE

    def _determine_warning_banner(self, severity: str) -> tuple[WarningBannerType, Optional[str]]:
        """Determine warning banner type and message based on severity."""
        if severity == 'critical':
            banner_type = self.config.critical_banner
            message = 'This content has been flagged for safety concerns'
        elif severity == 'warning':
            banner_type = self.config.warning_banner
            message = 'This content may be inappropriate for some audiences'
        else:
            banner_type = self.config.info_banner
            message = None
        return (banner_type, message)

    def _determine_click_through_requirement(self, severity: str) -> bool:
        """Determine if click-through is required based on severity."""
        if severity == 'critical':
            return self.config.require_click_through_for_critical
        elif severity == 'warning':
            return self.config.require_click_through_for_warning
        else:
            return False

    def _generate_client_tags(self, aegis_advisory: Dict[str, Any]) -> List[str]:
        """Generate client tags based on advisory data."""
        tags = []
        severity = aegis_advisory.get('severity', 'info')
        if severity != 'info':
            tags.append(f'aegis_severity_{severity}')
        if aegis_advisory.get('block_suggested', False):
            tags.append('aegis_block_suggested')
        return tags