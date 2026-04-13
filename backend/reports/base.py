from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import os


class BaseReportGenerator(ABC):
    """Abstract base class for all report generators."""
    
    @property
    @abstractmethod
    def id(self) -> str:
        """Unique identifier for the report type."""
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable name of the report."""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Description of what the report does."""
        pass
    
    @property
    def params_schema(self) -> Optional[Dict[str, Any]]:
        """JSON Schema for report parameters (optional)."""
        return None
    
    @abstractmethod
    async def generate(self, params: Dict[str, Any], output_path: str) -> str:
        """
        Generate the report and save it to output_path.
        Returns the file path of the generated report.
        
        Args:
            params: Report generation parameters
            output_path: Where to save the generated file
            
        Returns:
            Path to the generated file
        """
        pass
