FREE_EMAIL_PROVIDERS = {"gmail.com", "yahoo.com", "outlook.com", "hotmail.com",
                        "aol.com", "icloud.com", "proton.me", "protonmail.com"}

SUSPICIOUS_TLDS = ['.xyz', '.top', '.click', '.icu', '.buzz', '.cfd', '.sbs', '.loan', '.work', '.online', '.site']

PENALTIES = {
    "suspicious_tld": -15,
    "salary_range_too_wide": -10,
}