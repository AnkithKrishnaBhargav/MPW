#To check dataset and compute minimum feasible CAP
import pandas as pd

path = "api/assets/dataset.csv"
beta = 0.1

df = pd.read_csv(path)

# auto detect scope2 column
candidates = [c for c in df.columns if "scope" in c.lower() and "2" in c.lower()]
if not candidates:
    print("Could not find scope2 column. Columns:", df.columns.tolist())
    raise SystemExit

col = candidates[0]

# clean numeric
d = pd.to_numeric(df[col].astype(str).str.replace(',', ''), errors='coerce').fillna(0.0)

sum_d = d.sum()
required_min_cap = beta * sum_d

print("\n--- Dataset Analysis ---")
print("Detected Scope-2 column:", col)
print("Number of firms:", len(d))
print("sum(d) =", sum_d)
print("beta =", beta)
print("beta * sum(d) (minimum feasible CAP) =", required_min_cap)


#expected output
#--- Dataset Analysis --- 
#Detected Scope-2 column: Scope 2 Emissions
#Number of firms: 1231
#sum(d) = 27285628853.199997
#beta = 0.1
#beta * sum(d) (minimum feasible CAP) = 2728562885.3199997