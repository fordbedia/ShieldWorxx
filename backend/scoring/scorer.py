
def score(findings):
    total = 100
    # value = [sum(max(total, f['penalty'])) for f in findings]
    # or
    total = max(total + sum(f['penalty'] for f in findings), 0)
    # print('value', value)
    # for f in findings:
    #     total += f["penalty"]
    if total >= 80:
        return {
            "verdict": "Looks legitimate.",
            "summary": "No major red flags found. Still confirm the employer on their official website before sharing personal information.",
            "total": total
        }
    elif total >= 50:
        return {
            "verdict": "Proceed with caution.",
            "summary": "This posting shows some warning signs. Review the flagged items below and confirm the employer independently before applying.",
            "total": total
        }
    else:
        return {
            "verdict": "High risk. Verify the employer before you proceed.",
            "summary": "This posting shows several signs common in job scams. Don’t share personal information or pay any fees until you’ve confirmed the employer through official channels.",
            "total": total
        }
