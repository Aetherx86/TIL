import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from .types import SemanticType, TypeLattice

@dataclass
class TypeMismatch:
    variable: str
    expected_type: SemanticType
    actual_type: SemanticType
    actual_value_sample: str

@dataclass
class DriftReport:
    missing_in_target: List[str]
    undocumented_in_target: List[str]
    empty_in_target: List[str]
    type_mismatches: List[TypeMismatch]
    dependency_violations: List[str]

class EnvDriftChecker:
    """
    Audits environment variables against reference templates using
    semantic type lattices and cross-variable dependency constraints.
    """
    ENV_VAR_REGEX = re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)$")

    @classmethod
    def parse_env_file(cls, path: Path) -> Dict[str, str]:
        if not path.exists():
            return {}
        vars_dict = {}
        for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            m = cls.ENV_VAR_REGEX.match(line)
            if m:
                val = m.group(2).strip()
                if len(val) >= 2 and ((val[0] == '"' and val[-1] == '"') or (val[0] == chr(39) and val[-1] == chr(39))):
                    val = val[1:-1]
                vars_dict[m.group(1)] = val
        return vars_dict

    @classmethod
    def compare(
        cls,
        template_path: Path,
        target_path: Path,
        dependencies: Optional[Dict[str, List[str]]] = None,
    ) -> DriftReport:
        tpl = cls.parse_env_file(template_path)
        tgt = cls.parse_env_file(target_path)

        tpl_keys = set(tpl.keys())
        tgt_keys = set(tgt.keys())

        missing = sorted(list(tpl_keys - tgt_keys))
        undocumented = sorted(list(tgt_keys - tpl_keys))
        empty = sorted([k for k, v in tgt.items() if not v and k in tpl_keys])

        # Type lattice verification
        mismatches: List[TypeMismatch] = []
        for k in (tpl_keys & tgt_keys):
            tpl_val = tpl[k]
            tgt_val = tgt[k]
            if tpl_val and tgt_val:
                exp_type = TypeLattice.infer(tpl_val)
                act_type = TypeLattice.infer(tgt_val)
                if exp_type != act_type:
                    # Allow PORT to count as INTEGER
                    if exp_type == SemanticType.PORT and act_type == SemanticType.INTEGER:
                        continue
                    mismatches.append(TypeMismatch(k, exp_type, act_type, tgt_val))

        # Relational dependency check: if key X is truthy or present, keys [Y, Z] must be present
        dep_violations: List[str] = []
        if dependencies:
            for trigger, required_list in dependencies.items():
                if trigger in tgt and tgt[trigger].lower() in ("true", "1", "yes", "on"):
                    for req in required_list:
                        if req not in tgt or not tgt[req]:
                            dep_violations.append(f"Flag '{trigger}' is active, but required dependency '{req}' is missing.")

        return DriftReport(
            missing_in_target=missing,
            undocumented_in_target=undocumented,
            empty_in_target=empty,
            type_mismatches=mismatches,
            dependency_violations=dep_violations,
        )
