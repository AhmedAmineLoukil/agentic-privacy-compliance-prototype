import asyncio
from dataclasses import dataclass, field
from typing import List

from typing_extensions import Never
from graph_rendering import save_graph_only

# Microsoft Agent Framework imports
from agent_framework import (
    Executor,
    Workflow,
    WorkflowBuilder,
    WorkflowContext,
    handler,
)


@dataclass
class ComplianceState:
    #Shared State Object
    
    request: str
    task_type: str = ""
    assigned_specialist: str = ""
    retrieved_material: List[str] = field(default_factory=list) #stores the documents and records retrieved by the retrieval layer
    specialist_notes: List[str] = field(default_factory=list)
    final_flags: List[str] = field(default_factory=list) #stores final warnings
    case_sensitivity: str = "unknown" #low/medium/high
    needs_human_review: bool = False
    audit_trail: List[str] = field(default_factory=list) #for logs


class ComplianceOfficerInterface(Executor):
    def __init__(self, id: str):
        super().__init__(id=id)

    @handler
    async def start(self, user_request: str, ctx: WorkflowContext[ComplianceState]) -> None:
        state = ComplianceState(
            request=user_request.strip(),
            audit_trail=["Compliance Officer Interface: request submitted"],
        )
        await ctx.send_message(state)


class IntakeTaskClassificationLayer(Executor):
    def __init__(self, id: str):
        super().__init__(id=id)

    @handler
    async def classify(self, state: ComplianceState, ctx: WorkflowContext[ComplianceState]) -> None:
        text = state.request.lower()

        # Data governance/mapping tasks
        if any(k in text for k in [
            "ropa", "record of processing", "data inventory", "data flow",
            "mapping", "retention", "erasure", "deletion", "minimization",
            "pii", "privacy by design"
        ]):
            state.task_type = "Data Governance & Mapping"
            state.assigned_specialist = "data_governance_mapping"

        # Transparency / notice / consent tasks
        elif any(k in text for k in [
            "privacy notice", "notice", "cookie", "cookies",
            "consent", "transparency", "banner", "policy notice"
        ]):
            state.task_type = "Transparency, Notice & Consent"
            state.assigned_specialist = "transparency_notice_consent"

        # Risk / security / incident tasks
        elif any(k in text for k in [
            "dpia", "impact assessment", "breach", "incident",
            "security", "vulnerability", "attack", "anomaly"
        ]):
            state.task_type = "Risk, Security & Incident"
            state.assigned_specialist = "risk_security_incident"

        # Legal analysis / governance tasks
        elif any(k in text for k in [
            "lawful basis", "legal analysis", "governance", "dpo",
            "supervisory authority", "authority reporting", "regulation"
        ]):
            state.task_type = "Legal Analysis & Governance"
            state.assigned_specialist = "legal_analysis_governance"

        # Vendor / processor / rights / DSAR tasks
        elif any(k in text for k in [
            "vendor", "processor", "article 28", "dpa",
            "dsar", "access request", "right to access",
            "right to erasure", "data subject request"
        ]):
            state.task_type = "Vendor, Processor & Rights"
            state.assigned_specialist = "vendor_processor_rights"

        else:
            state.task_type = "Legal Analysis & Governance"
            state.assigned_specialist = "legal_analysis_governance"

        state.audit_trail.append(
            f"Intake & Task Classification: task={state.task_type}, specialist={state.assigned_specialist}"
        )
        await ctx.send_message(state)


class OrchestratorAgent(Executor):
    def __init__(self, id: str):
        super().__init__(id=id)

    @handler
    async def orchestrate(self, state: ComplianceState, ctx: WorkflowContext[ComplianceState]) -> None:
        state.audit_trail.append(
            f"Orchestrator Agent: dispatching to retrieval layer for specialist={state.assigned_specialist}"
        )
        await ctx.send_message(state)


class RetrievalComplianceReasoningLayer(Executor):
    def __init__(self, id: str):
        super().__init__(id=id)

        #just a simple example of stored regulations..
        self.knowledge_map = {
            "data_governance_mapping": [
                "ROPA / processing inventory records",
                "Data-flow / system mapping entries",
                "Retention and erasure rules",
                "PII detection and data minimization policies",
            ],
            "transparency_notice_consent": [
                "Privacy notices and cookie disclosures",
                "Consent records and consent-state history",
                "Transparency obligations and notice templates",
                "Tracking and cookie policy checks",
            ],
            "risk_security_incident": [
                "DPIA templates and prior assessments",
                "Security logs / incidents / monitoring policies",
                "Breach notification playbooks",
                "Risk signals from anomaly-detection inputs",
            ],
            "legal_analysis_governance": [
                "Regulatory text and legal obligations",
                "Governance rules / lawful-basis references",
                "DPO guidance / authority reporting material",
                "Multi-regulation comparison notes",
            ],
            "vendor_processor_rights": [
                "Vendor contracts and DPA clauses",
                "Processor obligations / Article 28 checks",
                "DSAR workflow templates",
                "Rights handling checklists",
            ],
        }

    @handler
    async def retrieve(self, state: ComplianceState, ctx: WorkflowContext[ComplianceState]) -> None:
        state.retrieved_material.extend(self.knowledge_map.get(state.assigned_specialist, []))
        state.audit_trail.append(
            f"Retrieval & Compliance Reasoning Layer: retrieved {len(state.retrieved_material)} items"
        )
        await ctx.send_message(state)


class DataGovernanceMappingAgent(Executor):
    def __init__(self, id: str):
        super().__init__(id=id)

    @handler
    async def analyze(self, state: ComplianceState, ctx: WorkflowContext[ComplianceState]) -> None:
        state.specialist_notes.extend([
            "Mapped the request to RoPA / data inventory / minimization logic.",
            "Checked need for data-flow mapping, retention review, and erasure traceability.",
            "Flagged whether PII detection or privacy-by-design controls may be required.",
        ])
        state.audit_trail.append("Data Governance & Mapping Agent: analysis complete")
        await ctx.send_message(state)


class TransparencyNoticeConsentAgent(Executor):
    def __init__(self, id: str):
        super().__init__(id=id)

    @handler
    async def analyze(self, state: ComplianceState, ctx: WorkflowContext[ComplianceState]) -> None:
        state.specialist_notes.extend([
            "Checked notice / cookie / consent / transparency obligations.",
            "Prepared notice and consent validation points.",
            "Flagged possible tracking-detection and transparency-scoring needs.",
        ])
        state.audit_trail.append("Transparency, Notice & Consent Agent: analysis complete")
        await ctx.send_message(state)


class RiskSecurityIncidentAgent(Executor):
    def __init__(self, id: str):
        super().__init__(id=id)

    @handler
    async def analyze(self, state: ComplianceState, ctx: WorkflowContext[ComplianceState]) -> None:
        state.specialist_notes.extend([
            "Checked DPIA/security/incident/breach context.",
            "Flagged anomaly-detection, predictive-analytics, or behavior-monitoring relevance.",
            "Prepared breach-response and escalation cues.",
        ])
        state.audit_trail.append("Risk, Security & Incident Agent: analysis complete")
        await ctx.send_message(state)


class LegalAnalysisGovernanceAgent(Executor):
    def __init__(self, id: str):
        super().__init__(id=id)

    @handler
    async def analyze(self, state: ComplianceState, ctx: WorkflowContext[ComplianceState]) -> None:
        state.specialist_notes.extend([
            "Checked legal/governance/lawful-basis aspects.",
            "Prepared structured regulation-analysis points.",
            "Flagged whether multi-regulation comparison or authority preparation is needed.",
        ])
        state.audit_trail.append("Legal Analysis & Governance Agent: analysis complete")
        await ctx.send_message(state)


class VendorProcessorRightsAgent(Executor):
    def __init__(self, id: str):
        super().__init__(id=id)

    @handler
    async def analyze(self, state: ComplianceState, ctx: WorkflowContext[ComplianceState]) -> None:
        state.specialist_notes.extend([
            "Checked vendor/processor/rights workflow relevance.",
            "Prepared clause-review and checklist-audit points.",
            "Flagged DSAR or rights-handling steps if applicable.",
        ])
        state.audit_trail.append("Vendor, Processor & Rights Agent: analysis complete")
        await ctx.send_message(state)


class GuardrailPolicyEnforcementLayer(Executor):
    def __init__(self, id: str):
        super().__init__(id=id)

    @handler
    async def enforce(self, state: ComplianceState, ctx: WorkflowContext[ComplianceState]) -> None:
        text = state.request.lower()

        high_risk_markers = [
            "health data",
            "special category",
            "biometric",
            "children",
            "breach",
            "incident",
            "cross-border",
            "large-scale",
            "profiling",
            "supervisory authority",
        ]

        medium_risk_markers = [
            "consent",
            "cookie",
            "privacy notice",
            "vendor",
            "processor",
            "dsar",
            "retention",
            "erasure",
            "pii",
        ]

        if any(k in text for k in high_risk_markers):
            state.case_sensitivity = "high"
            state.needs_human_review = True
            state.final_flags.append("High-risk or legally sensitive case")
        elif any(k in text for k in medium_risk_markers):
            state.case_sensitivity = "medium"
            state.needs_human_review = False
            state.final_flags.append("Medium-risk case, guardrail-approved")
        else:
            state.case_sensitivity = "low"
            state.needs_human_review = False
            state.final_flags.append("Low-risk case, guardrail-approved")

       
        state.audit_trail.append(
            f"Guardrail / Policy Enforcement Layer: risk={state.case_sensitivity}, human_review={state.needs_human_review}"
        )
        await ctx.send_message(state)


class HumanReviewGate(Executor):
    
    def __init__(self, id: str):
        super().__init__(id=id)

    @handler
    async def review(self, state: ComplianceState, ctx: WorkflowContext[ComplianceState]) -> None:
        state.audit_trail.append("Human Review Gate: routed to DPO / legal / reviewer")
        state.final_flags.append("Human review required before release")
        await ctx.send_message(state)



class AuditLogReportingDashboard(Executor):
    def __init__(self, id: str):
        super().__init__(id=id)

    @handler
    async def finalize(self, state: ComplianceState, ctx: WorkflowContext[Never, str]) -> None:
        lines: List[str] = []
        lines.append("=== PRIVACY COMPLIANCE CASE SUMMARY ===")
        lines.append(f"Request: {state.request}")
        lines.append(f"Task type: {state.task_type}")
        lines.append(f"Assigned specialist: {state.assigned_specialist}")
        lines.append(f"Risk level: {state.case_sensitivity}")
        lines.append(f"Needs human review: {state.needs_human_review}")
        lines.append("")
        lines.append("Retrieved material:")
        for item in state.retrieved_material:
            lines.append(f"- {item}")
        lines.append("")
        lines.append("Specialist notes:")
        for item in state.specialist_notes:
            lines.append(f"- {item}")
        lines.append("")
        lines.append("Final flags:")
        for item in state.final_flags:
            lines.append(f"- {item}")
        lines.append("")
        lines.append("Audit trail:")
        for item in state.audit_trail:
            lines.append(f"- {item}")

        await ctx.yield_output("\n".join(lines))



def create_workflow() -> Workflow:

    #define all components
    interface= ComplianceOfficerInterface(id="compliance_officer_interface")
    intake= IntakeTaskClassificationLayer(id="intake_task_classification")
    orchestrator= OrchestratorAgent(id="orchestrator_agent")
    retrieval= RetrievalComplianceReasoningLayer(id="retrieval_compliance_reasoning")

    data_gov= DataGovernanceMappingAgent(id="data_governance_mapping")
    transparency= TransparencyNoticeConsentAgent(id="transparency_notice_consent")
    risk= RiskSecurityIncidentAgent(id="risk_security_incident")
    legal= LegalAnalysisGovernanceAgent(id="legal_analysis_governance")
    vendor= VendorProcessorRightsAgent(id="vendor_processor_rights")

    guardrail= GuardrailPolicyEnforcementLayer(id="guardrail_policy_enforcement")
    human_review= HumanReviewGate(id="human_review_gate")
    audit= AuditLogReportingDashboard(id="audit_log_reporting_dashboard")

    workflow = (
        WorkflowBuilder(start_executor=interface)

        # Main front-end pipeline
        .add_edge(interface, intake)
        .add_edge(intake, orchestrator)
        .add_edge(orchestrator, retrieval)

        # Specialist routing after retrieval
        .add_edge(
            retrieval,
            data_gov,
            condition=lambda s: s.assigned_specialist == "data_governance_mapping",
        )
        .add_edge(
            retrieval,
            transparency,
            condition=lambda s: s.assigned_specialist == "transparency_notice_consent",
        )
        .add_edge(
            retrieval,
            risk,
            condition=lambda s: s.assigned_specialist == "risk_security_incident",
        )
        .add_edge(
            retrieval,
            legal,
            condition=lambda s: s.assigned_specialist == "legal_analysis_governance",
        )
        .add_edge(
            retrieval,
            vendor,
            condition=lambda s: s.assigned_specialist == "vendor_processor_rights",
        )

        # All specialist agents flow into the guardrail
        .add_edge(data_gov, guardrail)
        .add_edge(transparency, guardrail)
        .add_edge(risk, guardrail)
        .add_edge(legal, guardrail)
        .add_edge(vendor, guardrail)

        # Guardrail decides whether human review is needed
        .add_edge(
            guardrail,
            human_review,
            condition=lambda s: s.needs_human_review is True,
        )
        .add_edge(
            guardrail,
            audit,
            condition=lambda s: s.needs_human_review is False,
        )

        # Human review eventually leads to final audit/reporting
        .add_edge(human_review, audit)

        .build()
    )

    return workflow



async def main():
    workflow = create_workflow()

    save_graph_only(
        svg_path="privacy_compliance_architecture.svg",
        png_path="privacy_compliance_architecture.png",
    )

    print("Generated:")
    print("privacy_compliance_architecture.svg")
    print("privacy_compliance_architecture.png")


if __name__ == "__main__":
    asyncio.run(main())
