import itertools

def simulate_pack_distribution(packs, entry_fee, num_players, packs_per_player):
    """
    packs: list of dicts, each with 'name', 'price', and 'quantity' keys
    entry_fee: int or float, fee per player
    num_players: int
    packs_per_player: int
    """
    total_packs_needed = num_players * packs_per_player
    max_packs_price = entry_fee * num_players
    
    if sum(pack['quantity'] for pack in packs) < total_packs_needed:
        raise ValueError("Not enough packs available for the draft.")
    
    # Check if the max_packs_price is smaller than the total price of the cheapest packs
    sorted_packs_by_price = sorted(packs, key=lambda p: p['price'])
    # Select the cheapest packs, taking as many as possible from each until reaching total_packs_needed
    min_price_packs = 0
    packs_needed = total_packs_needed
    for pack in sorted_packs_by_price:
        if packs_needed <= 0:
            break
        take = min(pack['quantity'], packs_needed)
        min_price_packs += pack['price'] * take
        packs_needed -= take
    if max_packs_price < min_price_packs:
        min_price_per_player = min_price_packs / num_players
        raise ValueError(f"Entry fee is too low to cover the minimum possible pack prices. Minimum required: {min_price_per_player:.2f} per player.")
   
    valid_distributions = []
    # Generate all possible combinations of packs to distribute
    # Each distribution is a list of pack counts, one per pack type, summing to total_packs_needed
    # Each pack count cannot exceed the available quantity for that pack
    for counts in itertools.product(*(range(min(pack['quantity'], total_packs_needed) + 1) for pack in packs)):
        if sum(counts) != total_packs_needed:
            continue
        total_price = sum(count * pack['price'] for count, pack in zip(counts, packs))
        if total_price <= max_packs_price:
            price_per_player = total_price / num_players
            distribution = {pack['name']: count for pack, count in zip(packs, counts) if count > 0}
            valid_distributions.append({'distribution': distribution,
                                        'price_per_player': price_per_player,
                                        'total_price': total_price})

    valid_distributions = score_pack_diversity(valid_distributions)
    valid_distributions = score_pack_dispersion(valid_distributions)
    valid_distributions = sorted(
        valid_distributions,
        key=lambda d: (d['diversity_score'], d['dispersion_score'], d['price_per_player']),
        reverse=True
    )
    return valid_distributions

def score_pack_diversity(distributions):
    """
    Adds a 'diversity_score' key to each distribution dict. The score is based on:
    - Number of different pack types included (more is better)
    """
    for dist in distributions:
        counts = list(dist['distribution'].values())
        num_types = len(counts)
        dist['diversity_score'] = num_types
    return distributions

def score_pack_dispersion(distribution):
    """
    Adds a 'dispersion_score' key to each distribution dict. The score is based on:
    - Evenness of distribution (more even is better)
    """
    for dist in distribution:
        counts = list(dist['distribution'].values())
        if len(counts) == 0:
            dist['dispersion_score'] = 0
            continue
        mean = sum(counts) / len(counts)
        variance = sum((x - mean) ** 2 for x in counts) / len(counts)
        dist['dispersion_score'] = 1 / (1 + variance) * 100 # Higher score for lower variance
    return distribution

if __name__ == "__main__":  
    # Example usage:
    packs = [
        {'name': 'Edge of Eternities',          'price': 5, 'quantity': 8},
        {'name': 'Tarkir: Dragonstorm',         'price': 7, 'quantity': 8},
        {'name': 'Aetherdrift',                 'price': 14, 'quantity': 8},
        {'name': 'Mystery Booster',             'price': 10, 'quantity': 8},
        {'name': 'Modern Horizons 2',           'price': 12, 'quantity': 8},
        {'name': 'Innistrad: Midnight Hunt',    'price': 8, 'quantity': 8},
        {'name': 'Innistrad: Crimson Vow',      'price': 9, 'quantity': 8},
        {'name': 'Strixhaven: School of Mages', 'price': 11, 'quantity': 8},
        {'name': 'Kaldheim',                    'price': 10, 'quantity': 8},
        {'name': "Adventures in the Forgotten Realms", 'price': 13, 'quantity': 8},
    ]

    entry_fee = 19
    num_players = 10
    packs_per_player = 2

    result = simulate_pack_distribution(packs, entry_fee, num_players, packs_per_player)
    print(f"Found {len(result)} valid distributions.")
    top_20 = result[:20]
    for dist in top_20:
        print(dist)