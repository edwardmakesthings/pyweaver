"""Private implementation of init file generator.

Coordinates the collection, formatting and writing of init files.

Path: pyweaver/init_generator/_impl/_generator.py
"""

from pathlib import Path
from typing import Dict
import logging

from pyweaver.common.type_definitions import GeneratorResult, ProcessingError
from pyweaver.init_generator.generator import InitGeneratorConfig
from pyweaver.init_generator._impl._collector import ModuleCollector
from pyweaver.init_generator._impl._formatter import ContentFormatter
from pyweaver.init_generator._impl._writer import InitWriter

logger = logging.getLogger(__name__)

class InitGeneratorImpl:
    """Internal implementation of init file generator."""

    def __init__(self, config: InitGeneratorConfig):
        self.config = config
        self._collector = ModuleCollector(config)
        self._formatter = ContentFormatter(config)
        self._writer = InitWriter(config)

    def preview_files(self) -> Dict[Path, str]:
        """Generate preview of init files."""
        try:
            # Collect and format module content
            module_contents = self._collector.collect_modules()
            return {
                path: self._formatter.format_content(content)
                for path, content in module_contents.items()
            }
        except Exception as e:
            logger.error("Error generating preview: %s", e)
            raise ProcessingError(f"Failed to generate preview: {str(e)}")

    def write_files(self) -> GeneratorResult:
        """Write init files to disk."""
        try:
            # Get formatted content
            files = self.preview_files()
            return self._writer.write_files(files)
        except Exception as e:
            logger.error("Error writing files: %s", e)
            raise ProcessingError(f"Failed to write files: {str(e)}")

    def generate_combined(self, output_path: Path) -> Path:
        """Generate combined output file."""
        try:
            files = self.preview_files()
            return self._writer.write_combined(files, output_path)
        except Exception as e:
            logger.error("Error generating combined output: %s", e)
            raise ProcessingError(f"Failed to generate combined output: {str(e)}")


