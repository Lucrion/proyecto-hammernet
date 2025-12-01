#!/usr/bin/env python
# -*- coding: utf-8 -*-

from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from config.database import get_db
from config.constants import API_PREFIX

router = APIRouter(prefix=f"{API_PREFIX}/analytics", tags=["Analytics"])

@router.post("/events")
async def collect_event(payload: dict, request: Request, db: Session = Depends(get_db)):
    try:
        name = str(payload.get("name") or "").strip() or "unknown"
        props = payload.get("properties") or {}
        url = payload.get("url") or None
        ts = payload.get("ts") or None
        print(f"[analytics] name={name} url={url} ts={ts} props={props}")
    except Exception as e:
        print(f"[analytics] error: {e}")
    return {"status": "ok"}
