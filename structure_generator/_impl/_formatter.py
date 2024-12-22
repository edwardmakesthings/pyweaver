"""Private implementation of structure formatting.

Handles formatting directory structure into various output formats
including tree-style, plain listing, and markdown.

Path: tools/project_tools/structure_generator/_impl/_formatter.py
"""

from pathlib import Path
from typing import List, Optional
import logging

from ..generator import StructureConfig, OutputFormat
from _generator import DirectoryNode

logger = logging.getLogger(__name__)

class StructureFormatter:
    """Formats directory structure into various outputs."""

    def __init__(self, config: StructureConfig):
        self.config = config
        self._formatters = {
            OutputFormat.TREE: self._format_tree,
            OutputFormat.PLAIN: self._format_plain,
            OutputFormat.MARKDOWN: self._format_markdown
        }

    def format_structure(self, structure: DirectoryNode) -> str:
        """Format directory structure according to configuration.

        Args:
            structure: Root node of structure to format

        Returns:
            Formatted string representation
        """
        # Get appropriate formatter
        formatter = self._formatters.get(self.config.format)
        if not formatter:
            raise ValueError(f"Unsupported format: {self.config.format}")

        # Build header
        lines = [
            f"# Project Structure: {structure.path.name}",
            f"# Generated by structure_gen"
        ]

        # Add structure
        lines.extend(formatter(structure))
        return "\n".join(lines)

    def _format_tree(self, node: DirectoryNode, prefix: str = "", is_last: bool = True) -> List[str]:
        """Format structure as tree with connectors.

        Args:
            node: Node to format
            prefix: Current line prefix
            is_last: Whether this is the last item at this level

        Returns:
            List of formatted lines
        """
        lines = []

        # Add current node
        connector = "└── " if is_last else "├── "
        name = self._format_name(node)
        lines.append(f"{prefix}{connector}{name}")

        # Add children
        if node.children:
            children = sorted(node.children, key=lambda n: (not n.is_dir, n.path.name))
            for i, child in enumerate(children):
                is_last_child = i == len(children) - 1
                extension = "    " if is_last else "│   "
                lines.extend(self._format_tree(
                    child,
                    prefix + extension,
                    is_last_child
                ))

        return lines

    def _format_plain(self, node: DirectoryNode) -> List[str]:
        """Format structure as plain file listing.

        Args:
            node: Node to format

        Returns:
            List of formatted lines
        """
        lines = []

        # Add files in directory
        if not node.is_dir:
            lines.append(str(node.rel_path))
        elif node.children:
            for child in sorted(node.children, key=lambda n: str(n.rel_path)):
                lines.extend(self._format_plain(child))

        return lines

    def _format_markdown(self, node: DirectoryNode, depth: int = 0) -> List[str]:
        """Format structure as markdown with indentation.

        Args:
            node: Node to format
            depth: Current depth level

        Returns:
            List of formatted lines
        """
        lines = []
        indent = "  " * depth

        # Add current node
        marker = "📁" if node.is_dir else "📄"
        name = self._format_name(node)
        lines.append(f"{indent}- {marker} {name}")

        # Add children
        if node.children:
            children = sorted(node.children, key=lambda n: (not n.is_dir, n.path.name))
            for child in children:
                lines.extend(self._format_markdown(child, depth + 1))

        return lines

    def _format_name(self, node: DirectoryNode) -> str:
        """Format node name with optional size.

        Args:
            node: Node to format name for

        Returns:
            Formatted name string
        """
        name = str(node.path.name)

        if self.config.show_size and node.size is not None:
            size = self._format_size(node.size)
            return f"{name} ({size})"

        return name

    def _format_size(self, size: int) -> str:
        """Format file size in human readable format.

        Args:
            size: Size in bytes

        Returns:
            Formatted size string
        """
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} PB"