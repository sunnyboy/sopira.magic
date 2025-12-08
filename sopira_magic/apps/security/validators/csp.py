"""CSP validator - generovanie Content-Security-Policy headeru."""

from typing import Dict, List


class CspValidator:
    """ConfigDriven CSP validator - SSOT pre Content-Security-Policy."""

    @staticmethod
    def build_csp_header(csp_config: Dict[str, List[str]]) -> str:
        """Zostav CSP header zo slovníka direktív.

        Prázdne alebo chýbajúce direktívy sú ignorované.
        """

        if not csp_config:
            return ""

        parts: List[str] = []

        mapping = {
            "default_src": "default-src",
            "script_src": "script-src",
            "style_src": "style-src",
            "img_src": "img-src",
            "connect_src": "connect-src",
            "font_src": "font-src",
            "object_src": "object-src",
            "media_src": "media-src",
            "frame_src": "frame-src",
            "sandbox": "sandbox",
        }

        for key, directive in mapping.items():
            values = csp_config.get(key)
            if not values:
                continue

            # sandbox bez hodnôt je platná direktíva
            if key == "sandbox" and values == [""]:
                parts.append("sandbox")
                continue

            value_str = " ".join(values)
            parts.append(f"{directive} {value_str}")

        report_uri = csp_config.get("report_uri")
        if report_uri:
            parts.append(f"report-uri {report_uri}")

        return "; ".join(parts)
