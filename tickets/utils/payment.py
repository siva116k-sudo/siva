import random, time

def process_payment(card_number, card_name, expiry, cvv, amount):
    """
    Simulated payment gateway.
    Returns dict: { success: bool, transaction_id: str, message: str }
    Cards ending in 0000 → always fail (for testing failed.html).
    All others → succeed.
    """
    time.sleep(0.8)   # simulate network latency
    card_clean = card_number.replace(' ', '')

    if not card_clean.isdigit() or len(card_clean) != 16:
        return {'success': False, 'transaction_id': None,
                'message': 'Invalid card number.'}

    if len(cvv) != 3 or not cvv.isdigit():
        return {'success': False, 'transaction_id': None,
                'message': 'Invalid CVV.'}

    if card_clean.endswith('0000'):
        return {'success': False, 'transaction_id': None,
                'message': 'Payment declined by bank. Please try another card.'}

    txn_id = 'TXN' + str(int(time.time())) + str(random.randint(100, 999))
    return {'success': True, 'transaction_id': txn_id,
            'message': 'Payment successful.'}