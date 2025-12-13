from typing import Optional

from sqlalchemy.orm import Session
from passlib.context import CryptContext
#from app.models.worker import Worker, WorkerRole
from app.schemas.worker import WorkerCreate, WorkerUpdate
from app.core.security import hash_password, verify_password

pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")


def get_worker_by_id(db: Session, worker_id: int) -> Optional[Worker]:
    return db.query(Worker).filter(Worker.id == worker_id).first()


def get_worker_by_login(db: Session, login: str) -> Optional[Worker]:
    return db.query(Worker).filter(Worker.login == login).first()


def get_all_workers(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Worker).offset(skip).limit(limit).all()


def get_workers_by_role(db: Session, role: WorkerRole):
    return db.query(Worker).filter(Worker.role == role).all()


def create_worker(db: Session, worker: WorkerCreate) -> Worker:
    hashed_password = hash_password(worker.password)
    db_worker = Worker(
        login=worker.login,
        password_hash=hashed_password,
        full_name=worker.full_name,
        phone_number=worker.phone_number,
        email=worker.email,
        role=worker.role
    )
    db.add(db_worker)
    db.commit()
    db.refresh(db_worker)
    return db_worker


def update_worker(db: Session, worker_id: int, worker_update: WorkerUpdate) -> Optional[Worker]:
    db_worker = get_worker_by_id(db, worker_id)
    if not db_worker:
        return None

    update_data = worker_update.dict(exclude_unset=True)

    if "password" in update_data:
        update_data["password_hash"] = pwd_context.hash(update_data["password"])
        del update_data["password"]

    for key, value in update_data.items():
        setattr(db_worker, key, value)

    db.commit()
    db.refresh(db_worker)
    return db_worker


def delete_worker(db: Session, worker_id: int) -> bool:
    db_worker = get_worker_by_id(db, worker_id)
    if not db_worker:
        return False

    db.delete(db_worker)
    db.commit()
    return True


def check_worker_password(db: Session, login: str, password: str) -> Optional[Worker]:
    worker = get_worker_by_login(db, login)
    if not worker:
        return None
    if not verify_password(password, worker.password_hash):
        return None
    return worker