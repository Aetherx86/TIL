import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Set, Tuple
from .graph import DocumentationGraph

@dataclass
class LinkFinding:
    source_file: str
    target_link: str
    line_number: int
    is_broken: bool
    reason: str

@dataclass
class CorpusAuditReport:
    broken_links: List[LinkFinding]
    cycles: List[List[str]]
    orphaned_files: List[str]
    total_files: int
    total_links: int

class MarkdownLinkAuditor:
    """
    Analyzes markdown documents for dead links, missing header anchors,
    cyclic reference clusters, and unreachable documentation islands.
    """
    LINK_REGEX = re.compile(r"\[([^\]]+)\]\(([^\)]+)\)")
    HEADER_REGEX = re.compile(r"^#{1,6}\s+(.+)$", re.MULTILINE)

    @classmethod
    def slugify_header(cls, header: str) -> str:
        s = re.sub(r"^#+\s*", "", header.strip()).lower()
        s = re.sub(r"[^a-z0-9\s-]", "", s)
        return re.sub(r"[\s]+", "-", s).strip("-")

    def extract_file_headers(self, path: Path) -> Set[str]:
        content = path.read_text(encoding="utf-8", errors="ignore")
        return {self.slugify_header(h) for h in self.HEADER_REGEX.findall(content)}

    def audit_directory(self, root_dir: Path, entrypoints: List[str] = ["README.md"]) -> CorpusAuditReport:
        doc_graph = DocumentationGraph()
        broken: List[LinkFinding] = []
        md_files = list(root_dir.rglob("*.md"))
        total_links = 0

        # Map file -> valid headers
        headers_cache: Dict[str, Set[str]] = {}
        for f in md_files:
            rel = str(f.relative_to(root_dir))
            headers_cache[rel] = self.extract_file_headers(f)
            doc_graph.all_nodes.add(rel)

        for md_path in md_files:
            rel_src = str(md_path.relative_to(root_dir))
            content = md_path.read_text(encoding="utf-8", errors="ignore")

            for line_idx, line in enumerate(content.splitlines(), start=1):
                for m in self.LINK_REGEX.finditer(line):
                    total_links += 1
                    url = m.group(2).strip()

                    if url.startswith("#"):
                        anchor = url[1:].lower()
                        if anchor not in headers_cache.get(rel_src, set()):
                            broken.append(LinkFinding(rel_src, url, line_idx, True, f"Anchor #{anchor} not found in current file"))
                    elif not (url.startswith("http://") or url.startswith("https://") or url.startswith("mailto:")):
                        # Local file reference
                        parts = url.split("#", 1)
                        file_part = parts[0]
                        anchor_part = parts[1].lower() if len(parts) > 1 else None

                        target_path = (md_path.parent / file_part).resolve()
                        if not target_path.exists():
                            broken.append(LinkFinding(rel_src, url, line_idx, True, f"File {file_part} does not exist"))
                        else:
                            try:
                                rel_target = str(target_path.relative_to(root_dir.resolve()))
                                doc_graph.add_edge(rel_src, rel_target)
                                if anchor_part and anchor_part not in headers_cache.get(rel_target, set()):
                                    broken.append(LinkFinding(rel_src, url, line_idx, True, f"Anchor #{anchor_part} not found in {rel_target}"))
                            except ValueError:
                                pass

        cycles = doc_graph.find_cycles()
        orphans = doc_graph.find_orphans(entrypoints)

        return CorpusAuditReport(
            broken_links=broken,
            cycles=cycles,
            orphaned_files=orphans,
            total_files=len(md_files),
            total_links=total_links,
        )
