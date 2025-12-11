from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
from .nsw_core import solve_nsw_allocation, NSWAllocationError
from .data_loader import load_firms_from_csv



app = FastAPI(
    title="NSW Carbon Credit Allocation API",
    version="0.1.0",
    description="Backend for fair carbon credit allocation using Nash Social Welfare."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class FirmInput(BaseModel):
    id: str
    name: Optional[str] = None
    sector: Optional[str] = None
    demand_d: float = Field(..., ge=0, description="Demand for credits (Scope 2)")
    responsibility_r: float = Field(..., ge=0, description="Responsibility (Total emissions)")


class AllocationRequest(BaseModel):
    cap: float = Field(..., gt=0, description="Total available carbon credits C")
    alpha: float = Field(0.6, ge=0, le=1, description="Need vs responsibility weight")
    beta: float = Field(0.1, ge=0, le=0.9, description="Equity floor fraction")
    epsilon: float = Field(1e-6, gt=0, description="Small value for log")
    firms: List[FirmInput]


@app.get("/")
def root():
    return {"message": "NSW Carbon Credit Allocation API is running"}

@app.post("/allocate")
def allocate(req: AllocationRequest):
    try:
        result = solve_nsw_allocation(
            firms=[f.dict() for f in req.firms],
            cap=req.cap,
            alpha=req.alpha,
            beta=req.beta,
            epsilon=req.epsilon,
        )
        return result
    except NSWAllocationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {e}")

@app.get("/allocate-from-csv")
def allocate_from_csv(
    cap: float = Query(1_000_000.0),
    alpha: float = Query(0.6),
    beta: float = Query(0.1),
    epsilon: float = Query(1e-6),
    path: str = Query("Extracted_Dataset - Sheet1.csv"),
):
    """
    Convenience endpoint: load firms from CSV and run allocation.
    """
    try:
        firms = load_firms_from_csv(path)
        result = solve_nsw_allocation(
            firms=firms,
            cap=cap,
            alpha=alpha,
            beta=beta,
            epsilon=epsilon,
        )
        return result
    except NSWAllocationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"CSV file not found at {path}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {e}")