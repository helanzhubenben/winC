from math import ceil

from django.db import transaction

from .models import Customer


def _score_total(customer):
    return (customer.score_x or 0) + (customer.score_y or 0) + (customer.score_z or 0)


def _has_zero_score(customer):
    return any((score or 0) == 0 for score in (customer.score_x, customer.score_y, customer.score_z))


def _ranked_level(position, total):
    top_10_cutoff = ceil(total * 0.10)
    top_25_cutoff = ceil(total * 0.25)
    top_60_cutoff = ceil(total * 0.60)

    if position <= top_10_cutoff:
        return 'A'
    if position <= top_25_cutoff:
        return 'B'
    if position <= top_60_cutoff:
        return 'C'
    return 'D'


@transaction.atomic
def recalculate_customer_levels():
    customers = list(Customer.objects.all())
    ranked_customers = [
        customer
        for customer in customers
        if not _has_zero_score(customer)
    ]
    ranked_customers.sort(
        key=lambda customer: (-_score_total(customer), customer.client_name.lower(), customer.id)
    )

    next_levels = {}
    total_ranked = len(ranked_customers)
    for index, customer in enumerate(ranked_customers, start=1):
        next_levels[customer.id] = _ranked_level(index, total_ranked)

    changed_customers = []
    for customer in customers:
        next_level = next_levels.get(customer.id, 'X')
        if customer.level != next_level:
            customer.level = next_level
            changed_customers.append(customer)

    if changed_customers:
        Customer.objects.bulk_update(changed_customers, ['level'])

    return len(changed_customers)
