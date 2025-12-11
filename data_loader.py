import pandas as pd
from typing import List, Dict, Any

def load_firms_from_csv(path: str) -> List[Dict[str, Any]]:
    """
    Load firms from CSV and return list of dicts:
    {
      'id': 'firm_0',
      'name': 'Company ABC',
      'sector': 'Energy',
      'demand_d': <float>,           # Scope 2
      'responsibility_r': <float>    # Scope1 + Scope2 (Total emissions)
    }
    """
    df = pd.read_csv(path)

    # Normalization
    cols = {c.lower().strip(): c for c in df.columns}
    def col_lookup(name_variants):
        for v in name_variants:
            k = v.lower()
            if k in cols:
                return cols[k]
        return None

    col_scope1 = col_lookup(['Scope 1 Emissions', 'scope 1', 'scope1', 'scope_1_emissions'])
    col_scope2 = col_lookup(['Scope 2 Emissions', 'scope 2', 'scope2', 'scope_2_emissions'])
    col_name   = col_lookup(['Company_name', 'company_name', 'company', 'name'])
    col_total  = col_lookup(['Total emissions', 'total_emissions', 'total'])


    if col_scope1 is None and col_scope2 is None and col_total is None:
        raise FileNotFoundError("CSV does not contain recognizable emissions columns (scope1/scope2/total).")

    
    def to_float_series(col):
        if col is None:
            return pd.Series([0.0] * len(df), index=df.index)
        s = df[col].astype(str).str.replace(',', '').replace(['', 'nan', 'NaN'], '0')
        return pd.to_numeric(s, errors='coerce').fillna(0.0)

    s1 = to_float_series(col_scope1)
    s2 = to_float_series(col_scope2)
    if col_total is not None:
        tot = to_float_series(col_total)
    else:
        tot = s1 + s2

    firms = []
    for i, row in df.iterrows():
        name = row[col_name] if (col_name in df.columns) else f"firm_{i}"
        sector = row.get('Sector') if 'Sector' in df.columns else None
        demand_d = float(s2.iloc[i])    # use Scope 2 as 'demand'
        responsibility_r = float(tot.iloc[i])
        firms.append({
            'id': f'firm_{i}',
            'name': str(name),
            'sector': str(sector) if sector is not None else None,
            'demand_d': demand_d,
            'responsibility_r': responsibility_r,
        })

    return firms
