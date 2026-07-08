def normalize_area_text(value):
    """Normalize customer area values copied from spreadsheet cells or forms."""
    if value is None:
        return ''

    lines = [line.strip() for line in str(value).replace('\r\n', '\n').replace('\r', '\n').split('\n')]
    first_line = next((line for line in lines if line), '')
    return ' '.join(first_line.split())
