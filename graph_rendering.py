from html import escape
from graphviz import Digraph


def card_label(title: str, comment: str, tools: str, header_color: str, body_color: str) -> str:
    """
    Builds a modern HTML-like label for Graphviz.
    """
    title = escape(title)
    comment = escape(comment)
    tools = escape(tools)

    return f"""<
<TABLE BORDER="1" CELLBORDER="0" CELLSPACING="0" CELLPADDING="8" COLOR="{header_color}" BGCOLOR="{body_color}">
    <TR>
        <TD BGCOLOR="{header_color}" ALIGN="CENTER">
            <FONT COLOR="white" FACE="Helvetica"><B>{title}</B></FONT>
        </TD>
    </TR>
    <TR>
        <TD ALIGN="LEFT">
            <FONT FACE="Helvetica" POINT-SIZE="11">{comment}</FONT><BR ALIGN="LEFT"/>
            <FONT FACE="Helvetica" POINT-SIZE="10" COLOR="#334155"><B>Tools:</B> {tools}</FONT>
        </TD>
    </TR>
</TABLE>
>"""


def build_architecture_graph() -> Digraph:
    """
    Builds the styled architecture diagram.
    """

    dot = Digraph("PrivacyComplianceArchitecture")
    dot.attr(
        rankdir="TB",
        splines="ortho",
        pad="0.3",
        nodesep="0.45",
        ranksep="0.65",
        bgcolor="white",
        fontname="Helvetica",
        labelloc="t",
        label="Agentic AI Privacy Compliance Architecture",
        fontsize="20",
    )

    dot.attr("node", shape="plain", fontname="Helvetica")
    dot.attr("edge", fontname="Helvetica", fontsize="10", color="#5B7C99", penwidth="1.5")

    dot.node(
        "interface",
        card_label(
            "Compliance Officer Interface",
            "Entry point for DPO/legal/internal requests and final report return.",
            "Forms · case queue · result viewer",
            "#334155",
            "#F8FAFC",
        ),
    )

    dot.node(
        "intake",
        card_label(
            "Intake & Task Classification Layer",
            "Classifies the request and routes it to the correct workflow.",
            "spaCy/Tint · TF-IDF · NER · SVM/RF/XGBoost",
            "#2563EB",
            "#EFF6FF",
        ),
    )

    dot.node(
        "orchestrator",
        card_label(
            "Orchestrator Agent",
            "Coordinates which specialist agent(s) run and in what order.",
            "Workflow rules · task router · state store",
            "#1D4ED8",
            "#DBEAFE",
        ),
    )

    dot.node(
        "shared_knowledge",
        card_label(
            "Shared Compliance Knowledge Layer",
            "Stores regulations, policies, notices, contracts, RoPA, consent, DPIA, and logs.",
            "KG/ontology · CSM-ROPA · GraphDB · SPARQL · DPV/PROV-O",
            "#0F766E",
            "#ECFEFF",
        ),
    )

    dot.node(
        "retrieval",
        card_label(
            "Retrieval & Compliance Reasoning Layer",
            "Retrieves and structures legal/organizational evidence before specialist analysis.",
            "ARC tuples · SRL · benepar · spaCy · ARCBert queries",
            "#2563EB",
            "#EFF6FF",
        ),
    )

    dot.node(
        "data_gov",
        card_label(
            "Data Governance & Mapping Agent",
            "RoPA, data inventory, data-flow mapping, PII, minimization, retention, erasure.",
            "CSM-ROPA · KG · data-flow map · PII NER · TF-IDF · SVM/RF",
            "#15803D",
            "#F0FDF4",
        ),
    )

    dot.node(
        "transparency",
        card_label(
            "Transparency, Notice & Consent Agent",
            "Privacy notices, cookie compliance, consent monitoring, transparency checks.",
            "BeautifulSoup · Selenium · transparency scoring · tracking detection · consent KG",
            "#1E40AF",
            "#EFF6FF",
        ),
    )

    dot.node(
        "risk",
        card_label(
            "Risk, Security & Incident Agent",
            "DPIA support, anomaly monitoring, breach support, security-oriented compliance analysis.",
            "SVM · decision trees · CNN/RNN · SIEM logs · anomaly detection",
            "#DC2626",
            "#FEF2F2",
        ),
    )

    dot.node(
        "legal",
        card_label(
            "Legal Analysis & Governance Agent",
            "Lawful-basis assessment, regulation analysis, governance checks, DPO support.",
            "spaCy · SRL · benepar · ARC tuples · ARCBert",
            "#0F3D3E",
            "#F0FDFA",
        ),
    )

    dot.node(
        "vendor",
        card_label(
            "Vendor, Processor & Rights Agent",
            "Vendor/DPA review, processor compliance, DSAR and rights-handling support.",
            "NER · clause extraction · rights tuples · checklist audit",
            "#C2410C",
            "#FFF7ED",
        ),
    )

    dot.node(
        "guardrail",
        card_label(
            "Guardrail / Policy Enforcement Layer",
            "Validates completeness, evidence, and policy compliance before release.",
            "SDM/TOM rules · policy checks · role-based access · JWT",
            "#475569",
            "#F8FAFC",
        ),
    )

    dot.node(
        "human_review",
        card_label(
            "Human Review Gate",
            "Escalates high-risk or legally sensitive cases to DPO/legal/security review.",
            "DPO review · legal review · approval queue · XAI notes",
            "#64748B",
            "#F8FAFC",
        ),
    )

    dot.node(
        "audit",
        card_label(
            "Audit Log & Reporting Dashboard",
            "Records execution, evidence, flags, and generates audit-ready reports.",
            "Decision logs · provenance · full audit · report templates",
            "#CBD5E1",
            "#F8FAFC",
        ),
    )

    with dot.subgraph() as s:
        s.attr(rank="same")
        s.node("data_gov")
        s.node("transparency")
        s.node("risk")
        s.node("legal")
        s.node("vendor")

    with dot.subgraph() as s:
        s.attr(rank="same")
        s.node("shared_knowledge")
        s.node("data_gov")

    dot.edge("shared_knowledge", "data_gov", style="invis")
    dot.edge("data_gov", "transparency", style="invis")
    dot.edge("transparency", "risk", style="invis")
    dot.edge("risk", "legal", style="invis")
    dot.edge("legal", "vendor", style="invis")

    dot.edge("interface", "intake", label="submit request")
    dot.edge("intake", "orchestrator", label="classified task")
    dot.edge("orchestrator", "retrieval", label="prepare context")

    dot.edge("orchestrator", "data_gov", label="dispatch", color="#93C5FD")
    dot.edge("orchestrator", "transparency", label="dispatch", color="#93C5FD")
    dot.edge("orchestrator", "risk", label="dispatch", color="#93C5FD")
    dot.edge("orchestrator", "legal", label="dispatch", color="#93C5FD")
    dot.edge("orchestrator", "vendor", label="dispatch", color="#93C5FD")

    dot.edge("retrieval", "data_gov", label="grounded evidence")
    dot.edge("retrieval", "transparency", label="grounded evidence")
    dot.edge("retrieval", "risk", label="grounded evidence")
    dot.edge("retrieval", "legal", label="grounded evidence")
    dot.edge("retrieval", "vendor", label="grounded evidence")

    dot.edge("shared_knowledge", "retrieval", label="regulations / records", color="#0F766E")
    dot.edge("shared_knowledge", "data_gov", style="dashed", color="#94A3B8")
    dot.edge("shared_knowledge", "transparency", style="dashed", color="#94A3B8")
    dot.edge("shared_knowledge", "risk", style="dashed", color="#94A3B8")
    dot.edge("shared_knowledge", "legal", style="dashed", color="#94A3B8")
    dot.edge("shared_knowledge", "vendor", style="dashed", color="#94A3B8")

    dot.edge("data_gov", "guardrail")
    dot.edge("transparency", "guardrail")
    dot.edge("risk", "guardrail")
    dot.edge("legal", "guardrail")
    dot.edge("vendor", "guardrail")

    dot.edge("guardrail", "human_review", label="high-risk / sensitive")
    dot.edge("guardrail", "audit", label="approved result")
    dot.edge("human_review", "audit", label="reviewed result")
    dot.edge("audit", "interface", label="reports / flags / draft actions")

    return dot


def save_graph_only(svg_path: str, png_path: str) -> None:
    """
    Renders the diagram directly to SVG and PNG bytes.
    """
    graph = build_architecture_graph()

    svg_bytes = graph.pipe(format="svg")
    with open(svg_path, "wb") as f:
        f.write(svg_bytes)

    png_bytes = graph.pipe(format="png")
    with open(png_path, "wb") as f:
        f.write(png_bytes)
