import itertools

def simulate_pack_distribution(packs, num_packs_needed, max_total_price):
    #------------------ Preliminary checks ------------------#
    if check_enough_packs(packs, num_packs_needed) is False:
        available_packs = sum(pack['quantity'] for pack in packs)
        raise ValueError(f"Not enough packs available for the draft. Available: {available_packs}, Required: {num_packs_needed}.")
    if check_min_price(packs, num_packs_needed, max_total_price) is False:
        min_price_per_player = sum(sorted(pack['price'] for pack in packs)[:num_packs_needed])
        raise ValueError(f"Entry fee is too low to cover the minimum possible pack prices. Minimum required: {min_price_per_player:.2f} per player.")
    
    #------------------ Limit Packs List ------------------#
    max_packs_quantity_hard_limit = 5
    max_packs_quantity = 1
    
    optimizations_done = False
    packs,saved_packs = use_one_of_each_pack(packs, num_packs_needed)
    num_packs_needed = num_packs_needed - sum(sp['quantity'] for sp in saved_packs)
    max_total_price = max_total_price - sum(sp['price'] * sp['quantity'] for sp in saved_packs)
    while optimizations_done is False:
        packs = set_max_packs_quantity_per_type(packs, max_packs_quantity)
        while check_min_price(packs, num_packs_needed, max_total_price) is False:
            saved_packs,removed_pack = remove_most_expensive(saved_packs)
            max_total_price += removed_pack['price']
            num_packs_needed += 1
            if check_enough_packs(packs, num_packs_needed) is False:
                max_packs_quantity += 1
                if max_packs_quantity > max_packs_quantity_hard_limit:
                    raise ValueError("Cannot find a valid distribution with the given constraints.")
            else:
                optimizations_done = True
        optimizations_done = True
    #------------------ Remove too expensive packs ------------------#           
    
                
    #------------------ Generate valid distributions ------------------#
    valid_distributions = []
    
    # Generator function to yield valid combinations
    def generate_combinations(packs, neededPacks):
        # Extract quantity limits from packs
        quantities = [pack['quantity'] for pack in packs]
        # Generate all possible distributions
        distributions = []
        if neededPacks == 0:
            distributions.append((0,) * len(packs))
            return distributions
        for distribution in itertools.product(*(range(q + 1) for q in quantities)):
            if sum(distribution) == neededPacks:
                distributions.append(distribution)

        return distributions
    # Use the generator to find valid distributions
    for counts in generate_combinations(packs, num_packs_needed):
        total_price = sum(count * pack['price'] for count, pack in zip(counts, packs))
        if total_price <= max_total_price:
            distribution = [{'name': pack['name'],
                             'price': pack['price'],
                             'quantity': count} for pack, count in zip(packs, counts) if count > 0]
            valid_distributions.append({'distribution': distribution,
                                        'total_price': total_price})
            
    # Add back any saved packs
    for dist in valid_distributions:
        for sp in saved_packs:
            found = False
            for d in dist['distribution']:
                if d['name'] == sp['name']:
                    d['quantity'] += sp['quantity']
                    found = True
                    break
            if not found:
                dist['distribution'].append(sp)
        dist['total_price'] += sum(sp['price'] * sp['quantity'] for sp in saved_packs)

    valid_distributions = score_pack_diversity(valid_distributions)
    valid_distributions = score_pack_dispersion(valid_distributions)
    valid_distributions = sorted(
        valid_distributions,
        key=lambda d: (d['diversity_score'], d['dispersion_score'], d['total_price']),
        reverse=True
    )
    return valid_distributions

def score_pack_diversity(distributions):
    """
    Adds a 'diversity_score' key to each distribution dict. The score is based on:
    - Number of different pack types included (more is better)
    """
    for dist in distributions:
        counts = [pack['quantity'] for pack in dist['distribution']]
        num_types = len(counts)
        dist['diversity_score'] = num_types
    return distributions

def score_pack_dispersion(distribution):
    """
    Adds a 'dispersion_score' key to each distribution dict. The score is based on:
    - Evenness of distribution (more even is better)
    """
    for dist in distribution:
        counts = [pack['quantity'] for pack in dist['distribution']]
        if len(counts) == 0:
            dist['dispersion_score'] = 0
            continue
        mean = sum(counts) / len(counts)
        variance = sum((x - mean) ** 2 for x in counts) / len(counts)
        dist['dispersion_score'] = 1 / (1 + variance) * 100 # Higher score for lower variance
    return distribution

def check_enough_packs(packs, num_packs_needed):
    total_available = sum(pack['quantity'] for pack in packs)
    return total_available >= num_packs_needed

def check_min_price(packs, num_packs_needed, max_total_price):
    sorted_packs = sorted(packs, key=lambda p: p['price'])
    total_price = 0
    packs_needed = num_packs_needed
    for pack in sorted_packs:
        if packs_needed <= 0:
            break
        take = min(pack['quantity'], packs_needed)
        total_price += pack['price'] * take
        packs_needed -= take
    return total_price <= max_total_price

def use_one_of_each_pack(packs, num_packs_needed):
    saved_packs = []
    while num_packs_needed >= len(packs):
        for pack in packs:
            num_packs_needed -= 1
            pack['quantity'] -= 1
            # Check if the pack already exists in saved_packs
            existing_pack = next((item for item in saved_packs if item['name'] == pack['name']), None)
            if existing_pack:
                existing_pack['quantity'] += 1  # Increment quantity if exists
            else:
                saved_packs.append({'name': pack['name'], 'price': pack['price'], 'quantity': 1})
        packs = list(filter(lambda p: p['quantity'] != 0, packs))
    return packs, saved_packs
            
def set_max_packs_quantity_per_type(packs, max_quantity):
    for pack in packs:
        if pack['quantity'] > max_quantity:
            pack['quantity'] = max_quantity
    return packs

def remove_most_expensive(packs):
    if not packs:
        return packs
    most_expensive = max(packs, key=lambda p: p['price'])
    if most_expensive['quantity'] > 1:
        most_expensive['quantity'] -= 1
    else:
        packs.remove(most_expensive)
    return packs, most_expensive

if __name__ == "__main__":  
    # Example usage:
    
    packs = [
        {'name': 'Ixalan', 'price': 8.99, 'quantity': 32},
        {'name': 'New Capena', 'price': 9.25, 'quantity': 15},
        {'name': 'Theros Beyond Death', 'price': 7.75, 'quantity': 20},
        {'name': 'Dark Ascension', 'price': 16.99, 'quantity': 6},
        {'name': 'Rival of Ixalan', 'price': 8.99, 'quantity': 30},
        {'name': 'Dominaria Remaster', 'price': 10.25, 'quantity': 3},
        {'name': 'Murder at Karlov Manor', 'price': 7.75, 'quantity': 36},
        {'name': 'Battle for Zendikar', 'price': 12.25, 'quantity': 20},
        {'name': 'Outlaw at Thunder Junction', 'price': 8.25, 'quantity': 25},
        {'name': 'Core Set 2020', 'price': 7.25, 'quantity': 18},
        {'name': 'Guilds of Ravnica', 'price': 8.75, 'quantity': 30},
        {'name': 'Ravnica Remaster', 'price': 9.99, 'quantity': 32},
        {'name': 'Phyrexia All Will Be One', 'price': 9.99, 'quantity': 6},
        {'name': 'Amonkhet', 'price': 16.99, 'quantity': 20},
        {'name': 'Strixhaven', 'price': 8.75, 'quantity': 20},
        {'name': 'Midnight Hunt', 'price': 8.75, 'quantity': 25},
        {'name': 'Bloomburrow', 'price': 8.25, 'quantity': 25},
        {'name': 'Innistrad Remaster', 'price': 9.5, 'quantity': 36},
        {'name': 'AetherDrift', 'price': 7.5, 'quantity': 36},
        {'name': 'Edge of Eternities', 'price': 9.5, 'quantity': 36},
        ]

    entry_fee = 19
    num_players = 11
    packs_per_player = 2
    
    max_total_price = entry_fee * num_players
    num_total_packs = num_players * packs_per_player

    result = simulate_pack_distribution(packs, num_total_packs, max_total_price)
    print(f"Found {len(result)} valid distributions.")
    top_3 = result[:3]
    for entry in top_3:
        pack_list = ", ".join([f"{pack['name']} (x{pack['quantity']})" for pack in entry['distribution']])
        price_per_player = f"{entry.get('total_price', 0)/num_players:.2f}"
        total_price = f"{entry.get('total_price', 0):.2f}"
        diversity = f"{entry.get('diversity_score', 0):.2f}"
        dispersion = f"{entry.get('dispersion_score', 0):.2f}"
        print(f"Diversity: {diversity}, Dispersion: {dispersion}, Price per Player: {price_per_player}, Total Price: {total_price}, Packs: {pack_list}")