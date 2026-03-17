def retention_strategy(prob):

    if prob > 0.7:
        return "🔥 High Risk: Offer premium benefits + personal call"

    elif prob > 0.5:
        return "⚠ Medium Risk: Give discounts & engagement offers"

    elif prob > 0.3:
        return "📊 Monitor customer behavior"

    else:
        return "✅ Customer stable"