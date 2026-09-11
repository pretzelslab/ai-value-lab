from .models import Risk

RISK_PROFILES = {
    "General HR policy": (
        Risk(
            name="Reliability",
            category="Reliability",
            description=(
                "AI may provide an incorrect or inconsistent interpretation of general HR policy."
            ),
            likelihood="Medium",
            impact="Medium",
        ),
        Risk(
            name="Privacy",
            category="Privacy",
            description=(
                "General policy questions usually require limited employee-specific information."
            ),
            likelihood="Low",
            impact="Medium",
        ),
        Risk(
            name="Compliance",
            category="Compliance",
            description=(
                "Incorrect policy guidance may conflict with internal policy or applicable requirements."
            ),
            likelihood="Medium",
            impact="Medium",
        ),
        Risk(
            name="Operational Impact",
            category="Operational Impact",
            description=(
                "An incorrect response may create employee confusion or require additional HR handling."
            ),
            likelihood="Low",
            impact="Medium",
        ),
    ),
    "Benefits": (
        Risk(
            name="Reliability",
            category="Reliability",
            description=(
                "Incorrect or inconsistent benefits guidance may affect employee decisions or eligibility understanding."
            ),
            likelihood="Medium",
            impact="High",
        ),
        Risk(
            name="Privacy",
            category="Privacy",
            description=(
                "Benefits cases may contain personal, dependent, health, or eligibility-related information."
            ),
            likelihood="Medium",
            impact="High",
        ),
        Risk(
            name="Compliance",
            category="Compliance",
            description=(
                "Incorrect benefits guidance may create policy, regulatory, or administration exposure."
            ),
            likelihood="Medium",
            impact="High",
        ),
        Risk(
            name="Operational Impact",
            category="Operational Impact",
            description=(
                "Errors may require correction, escalation, or additional employee support."
            ),
            likelihood="Medium",
            impact="High",
        ),
    ),
    "Employee data": (
        Risk(
            name="Reliability",
            category="Reliability",
            description=(
                "AI handling employee data must produce dependable outputs and avoid incorrect interpretation."
            ),
            likelihood="Medium",
            impact="Medium",
        ),
        Risk(
            name="Privacy",
            category="Privacy",
            description=(
                "Employee data may contain personally identifiable or otherwise sensitive information."
            ),
            likelihood="High",
            impact="High",
        ),
        Risk(
            name="Compliance",
            category="Compliance",
            description=(
                "Improper handling of employee data may create privacy, retention, access, or governance exposure."
            ),
            likelihood="High",
            impact="High",
        ),
        Risk(
            name="Operational Impact",
            category="Operational Impact",
            description=(
                "Incorrect employee data handling may affect downstream HR processes and require remediation."
            ),
            likelihood="Medium",
            impact="High",
        ),
    ),
    "Payroll inquiry": (
        Risk(
            name="Reliability",
            category="Reliability",
            description=(
                "Incorrect payroll guidance may directly affect an employee's understanding of pay or deductions."
            ),
            likelihood="Medium",
            impact="High",
        ),
        Risk(
            name="Privacy",
            category="Privacy",
            description=(
                "Payroll cases commonly involve sensitive personal and financial information."
            ),
            likelihood="High",
            impact="High",
        ),
        Risk(
            name="Compliance",
            category="Compliance",
            description=(
                "Payroll errors may create statutory, policy, audit, or employment compliance exposure."
            ),
            likelihood="High",
            impact="High",
        ),
        Risk(
            name="Operational Impact",
            category="Operational Impact",
            description=(
                "Payroll errors may require urgent correction and can directly affect employees and payroll operations."
            ),
            likelihood="High",
            impact="High",
        ),
    ),
}


def get_risk_profile(case_category: str) -> tuple[Risk, ...]:
    try:
        return RISK_PROFILES[case_category]
    except KeyError as exc:
        raise ValueError(f"Unknown case category: {case_category}") from exc
