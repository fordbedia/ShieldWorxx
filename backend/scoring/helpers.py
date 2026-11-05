import ssl, socket
from datetime import datetime, timezone
from .findings import make_finding
from .rules import FREE_EMAIL_PROVIDERS, SUSPICIOUS_TLDS, PENALTIES


def check_ssl_status(hostname: str, port: int, index: int):
    context = ssl.create_default_context()
    try:
        # Establish a network connection and wrap it with SSL
        with socket.create_connection((hostname, port), timeout=5) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                # If wrap_socket succeeds, the SSL certificate is VALID
                # Now extract metadata like the expiration date
                cert = ssock.getpeercert()

                # Parse the expiration date string (e.g., 'Jan 24 12:00:00 2027 GMT')
                expiry_str = cert["notAfter"]
                expiry_date = datetime.strptime(
                    expiry_str, "%b %d %H:%M:%S %Y %Z"
                ).replace(tzinfo=timezone.utc)
                current_time = datetime.now(timezone.utc)
                days_left = (expiry_date - current_time).days

                if days_left <= 0:
                    return make_finding(
                        name=f"ssl_validity_check_{index}",
                        hostname=hostname,
                        reason=f"Company website's SSL certificate has expired.",
                        penalty=PENALTIES['expired_ssl'],
                    )

                return make_finding(
                    name=f"ssl_validity_check_{index}",
                    hostname=hostname,
                    reason=f"Company website has a valid SSL certificate.",
                    evidence=[f"Expires on: {expiry_str} ({days_left} days left)",
                              f"SSL Issued to: {dict(cert['subject'][-1])['commonName']}"],
                    penalty=0
                )

    except ssl.SSLCertVerificationError as e:
        # Expired
        if e.verify_code == 10:
            return make_finding(
                name=f"ssl_validity_check_{index}",
                hostname=hostname,
                reason=f"Company website's SSL certificate has expired.",
                penalty=PENALTIES['expired_ssl'],
            )
        # Hostname mismatch
        if e.verify_code == 62:
            return make_finding(
                name=f"ssl_validity_check_{index}",
                hostname=hostname,
                reason=f"SSL certificate doesn't match the company domain.",
                penalty=PENALTIES['hostname_mismatch'],
            )
        # Self-signed
        if e.verify_code == 18:
            return make_finding(
                name=f"ssl_validity_check_{index}",
                hostname=hostname,
                reason=f"Company website uses a self-signed SSL certificate.",
                penalty=PENALTIES['self_signed_or_untrusted_ca'],
            )
        # Untrusted issuer: 20, 21, 2
        return make_finding(
            name=f"ssl_validity_check_{index}",
            hostname=hostname,
            reason=f"SSL certificate isn't from a trusted issuer.",
            penalty=PENALTIES['self_signed_or_untrusted_ca'],
        )
    except socket.timeout:
        return make_finding(
            name=f"ssl_validity_check_{index}",
            hostname=hostname,
            reason=f"Couldn't check SSL certificate ({hostname} didn't respond).",
            penalty=0
        )
    except Exception as e:
        return make_finding(
            name=f"ssl_validity_check_{index}",
            hostname=hostname,
            reason=f"Couldn't check SSL certificate.",
            penalty=0
        )
