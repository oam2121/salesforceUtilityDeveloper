# Optional utility functions

import pandas as pd

def export_to_csv(records, filename='salesforce_data.csv'):
    """Export records to CSV file."""
    df = pd.DataFrame(records)
    df.to_csv(filename, index=False)
    return filename
