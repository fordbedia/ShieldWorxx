def make_finding(
        name: str = "suspicious_tld",
        penalty: int = 0,
        reason: str = "",
        **extra
)-> dict:
    findings = {
        "name": name,
        "penalty": penalty,
        "reason": reason,
        **extra
    }

    return findings