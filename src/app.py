"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
from pathlib import Path

import src.db as db


app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")


@app.on_event("startup")
def startup_event():
    # Initialize database and seed defaults if empty
    db.init_db()


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    return db.get_activities()


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity"""
    try:
        db.signup_for_activity(activity_name, email)
    except ValueError as e:
        code = str(e)
        if code == "not_found":
            raise HTTPException(status_code=404, detail="Activity not found")
        if code == "already_signed_up":
            raise HTTPException(status_code=400, detail="Student is already signed up")
        if code == "full":
            raise HTTPException(status_code=400, detail="Activity is full")
        raise HTTPException(status_code=400, detail="Unable to sign up")
    return {"message": f"Signed up {email} for {activity_name}"}


@app.delete("/activities/{activity_name}/unregister")
def unregister_from_activity(activity_name: str, email: str):
    """Unregister a student from an activity"""
    try:
        db.unregister_from_activity(activity_name, email)
    except ValueError as e:
        code = str(e)
        if code == "not_found":
            raise HTTPException(status_code=404, detail="Activity not found")
        if code == "not_signed_up":
            raise HTTPException(status_code=400, detail="Student is not signed up for this activity")
        raise HTTPException(status_code=400, detail="Unable to unregister")
    return {"message": f"Unregistered {email} from {activity_name}"}
