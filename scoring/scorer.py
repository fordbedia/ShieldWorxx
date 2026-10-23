
def score(findings):
    total = 100
    # value = [sum(max(total, f['penalty'])) for f in findings]
    # or
    total = max(total + sum(f['penalty'] for f in findings), 0)
    # print('value', value)
    # for f in findings:
    #     total += f["penalty"]
    if total >= 80:
        return {"label": "Looks legit", "total": total}
    elif total >= 50:
        return {"label": "Use caution", "total": total}
    else:
        return {"label": "High risk", "total": total}
