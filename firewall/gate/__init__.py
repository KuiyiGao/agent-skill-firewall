"""L0 static gate.

:mod:`firewall.gate.static_scanner` holds the built-in lightweight static
checks (hidden instructions in comments, suspicious frontmatter keys, shell
fetches, hostile host literals, and a file that matches both a configured
secret source and a configured network sink).

It emits :class:`Finding` records; the install policy
(``prescan``: only CRITICAL hard-blocks) is enforced by the L2 layer,
not here. See ``firewall.runtime.firewall`` invariants (2) and (3).
"""

from firewall.gate.static_scanner import Finding, scan_skill_dir

__all__ = ["Finding", "scan_skill_dir"]
