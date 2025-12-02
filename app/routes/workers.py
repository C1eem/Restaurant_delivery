from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.crud import worker as crud
from app.schemas.worker import WorkerCreate, WorkerResponse, WorkerUpdate, WorkerLogin, WorkerRole
from app.dependencies import get_db

router = APIRouter(prefix="/workers", tags=["workers"])

@router.post("/", response_model=WorkerResponse, status_code=status.HTTP_201_CREATED)
def create_worker(worker: WorkerCreate, db: Session = Depends(get_db)):
    if crud.get_worker_by_login(db, worker.login):
        raise HTTPException(status_code=400, detail="Работник с таким логином уже существует")
    return crud.create_worker(db, worker)

@router.get("/", response_model=List[WorkerResponse])
def read_workers(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    workers = crud.get_all_workers(db, skip=skip, limit=limit)
    return workers

@router.get("/{worker_id}", response_model=WorkerResponse)
def read_worker(worker_id: int, db: Session = Depends(get_db)):
    worker = crud.get_worker_by_id(db, worker_id)
    if not worker:
        raise HTTPException(status_code=404, detail="Работник не найден")
    return worker

@router.get("/role/{role}", response_model=List[WorkerResponse])
def read_workers_by_role(role: WorkerRole, db: Session = Depends(get_db)):
    workers = crud.get_workers_by_role(db, role)
    return workers

@router.put("/{worker_id}", response_model=WorkerResponse)
def update_worker(
    worker_id: int,
    worker_update: WorkerUpdate,
    db: Session = Depends(get_db)
):
    worker = crud.update_worker(db, worker_id, worker_update)
    if not worker:
        raise HTTPException(status_code=404, detail="Работник не найден")
    return worker

@router.delete("/{worker_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_worker(worker_id: int, db: Session = Depends(get_db)):
    success = crud.delete_worker(db, worker_id)
    if not success:
        raise HTTPException(status_code=404, detail="Работник не найден")

@router.post("/login/")
def login_worker(credentials: WorkerLogin, db: Session = Depends(get_db)):
    worker = crud.check_worker_password(db, credentials.login, credentials.password)
    if not worker:
        raise HTTPException(status_code=401, detail="Неверный логин или пароль")
    return {"message": "Успешный вход", "worker_id": worker.id, "role": worker.role}