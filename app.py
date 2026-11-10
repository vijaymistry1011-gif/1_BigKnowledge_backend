import os
import json
import base64
import urllib.request
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, Response, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv
import cloudinary
import cloudinary.uploader

from models import (
    db, User, KnowledgeItem, ReferenceDesign, Problem, SolutionItem,
    InnovationItem, StartupIdea, ProjectTask, RoadmapMilestone,
    JournalEntry, GoalHabit, OrganizationCRM
)

load_dotenv()

app = Flask(__name__, static_folder="static", static_url_path="/static")

CORS(
    app,
    resources={r"/*": {"origins": "*"}},
    methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-Requested-With"]
)

# Safe Blueprint Registration (Agar files repo me hain to jud jayengi, nahi hain to crash nahi hoga!)
try:
    from advanced_routes import adv_bp
    app.register_blueprint(adv_bp)
except Exception as e:
    print("adv_bp warning:", e)

try:
    from chat_meeting_routes import chat_bp
    app.register_blueprint(chat_bp)
except Exception as e:
    print("chat_bp warning:", e)

try:
    from power_routes import power_bp
    app.register_blueprint(power_bp)
except Exception as e:
    print("power_bp warning:", e)

db_url = os.environ.get("DATABASE_URL", "sqlite:///bigknowledge.db")
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = db_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "bigknowledge-secret-2026")
app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY", "bigknowledge-jwt-2026")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=7)

if os.environ.get("CLOUDINARY_URL"):
    cloudinary.config(cloudinary_url=os.environ.get("CLOUDINARY_URL"))

db.init_app(app)
jwt = JWTManager(app)

with app.app_context():
    db.create_all()
    if User.query.count() == 0:
        founder = User(
            name="Mr. Vijay Mistry",
            email="founder@bigknowledge.io",
            password_hash=generate_password_hash("admin123"),
            role="Founder"
        )
        db.session.add(founder)
        db.session.commit()

# Zero-dependency 5TB Google Drive Uploader (Works even without 'requests' library!)
def upload_to_5tb_drive(file_bytes, filename, mime_type="image/png", sub_folder="Uploaded_Files"):
    webhook_url = os.environ.get("GDRIVE_WEBHOOK_URL")
    if not webhook_url:
        return None
    try:
        payload = json.dumps({
            "filename": filename,
            "mime_type": mime_type,
            "file_base64": base64.b64encode(file_bytes).decode("utf-8"),
            "sub_folder": sub_folder
        }).encode("utf-8")
        req = urllib.request.Request(webhook_url, data=payload, headers={"Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(req, timeout=45) as resp:
            res_json = json.loads(resp.read().decode("utf-8"))
            if res_json.get("status") == "success":
                fid = res_json.get("file_id")
                if fid and mime_type.startswith("image/"):
                    return f"https://drive.google.com/thumbnail?id={fid}&sz=w2000"
                return res_json.get("url")
    except Exception as e:
        print("Drive upload error:", e)
    return None

@app.route("/")
def dashboard_home():
    return jsonify({
        "status": "live",
        "service": "BigKnowledge Backend API (5TB Drive Ready)",
        "founder": "Mr. Vijay Mistry",
        "gdrive_5tb_connected": bool(os.environ.get("GDRIVE_WEBHOOK_URL"))
    })

@app.route("/login")
def login_page():
    return jsonify({"status": "login_endpoint_active"})

@app.route("/static/uploads/<path:filename>")
def serve_uploads(filename):
    upload_dir = os.path.join(os.getcwd(), "static", "uploads")
    return send_from_directory(upload_dir, filename)

@app.route("/api/bootstrap", methods=["GET"])
def api_bootstrap():
    return jsonify({
        "knowledge": [
            {"id": k.id, "title": k.title, "category": k.category, "content": k.content, "media_url": k.media_url, "tags": k.tags, "is_favorite": k.is_favorite, "created_at": k.created_at.strftime("%Y-%m-%d") if k.created_at else ""}
            for k in KnowledgeItem.query.order_by(KnowledgeItem.id.desc()).all()
        ],
        "problems": [
            {"id": p.id, "title": p.title, "source": p.source, "root_cause": p.root_cause, "solution": p.proposed_solution, "market_demand": p.market_demand, "competition_level": p.competition_level, "revenue_potential": p.revenue_potential, "opportunity_score": p.opportunity_score}
            for p in Problem.query.order_by(Problem.opportunity_score.desc()).all()
        ],
        "solutions": [
            {"id": s.id, "problem_title": s.problem_title, "solution_title": s.solution_title, "cost_estimate": s.cost_estimate, "benefits": s.benefits, "market_impact": s.market_impact, "difficulty": s.difficulty, "revenue_potential": s.revenue_potential}
            for s in SolutionItem.query.order_by(SolutionItem.id.desc()).all()
        ],
        "innovations": [
            {"id": i.id, "title": i.title, "category": i.category, "summary": i.summary, "opportunity_note": i.opportunity_note}
            for i in InnovationItem.query.order_by(InnovationItem.id.desc()).all()
        ],
        "startups": [
            {"id": st.id, "name": st.name, "description": st.description, "market": st.market, "industry": st.industry, "revenue_model": st.revenue_model, "competitors": st.competitors, "market_size": st.market_size, "validation_status": st.validation_status, "stage": st.stage, "priority": st.priority, "feasibility_score": st.feasibility_score, "progress": st.progress, "time_spent_hours": st.time_spent_hours}
            for st in StartupIdea.query.order_by(StartupIdea.id.desc()).all()
        ],
        "tasks": [
            {"id": t.id, "title": t.title, "project_name": t.project_name, "status": t.status, "kanban_stage": t.kanban_stage, "priority": t.priority, "deadline": t.deadline, "dependencies": t.dependencies, "assignee": t.assignee}
            for t in ProjectTask.query.order_by(ProjectTask.id.desc()).all()
        ],
        "roadmaps": [
            {"id": r.id, "roadmap_type": r.roadmap_type, "title": r.title, "dependencies": r.dependencies, "deadline": r.deadline, "progress": r.progress}
            for r in RoadmapMilestone.query.all()
        ],
        "journals": [
            {"id": j.id, "entry_type": j.entry_type, "category_tag": j.category_tag, "title": j.title, "details": j.details, "expected_outcome": j.expected_outcome, "actual_result": j.actual_result, "created_at": j.created_at.strftime("%Y-%m-%d") if j.created_at else ""}
            for j in JournalEntry.query.order_by(JournalEntry.id.desc()).all()
        ],
        "goals_habits": [
            {"id": g.id, "item_type": g.item_type, "title": g.title, "streak_or_progress": g.streak_or_progress, "completed_today": g.completed_today}
            for g in GoalHabit.query.all()
        ],
        "org_crm": [
            {"id": c.id, "entity_type": c.entity_type, "name": c.name, "role_or_segment": c.role_or_segment, "department_or_company": c.department_or_company, "details_or_strengths": c.details_or_strengths, "weaknesses_or_actions": c.weaknesses_or_actions, "tasks_completed": c.tasks_completed, "tasks_pending": c.tasks_pending, "work_hours": c.work_hours, "productivity_score": c.productivity_score}
            for c in OrganizationCRM.query.all()
        ]
    })

@app.route("/api/knowledge", methods=["POST", "DELETE"])
def manage_knowledge():
    if request.method == "DELETE":
        item_id = request.args.get("id")
        if item_id:
            item = db.session.get(KnowledgeItem, int(item_id))
            if item:
                db.session.delete(item)
                db.session.commit()
        return jsonify({"status": "deleted"})

    d = request.get_json(silent=True) or {}
    media_url = d.get("media_url") or ""
    if media_url.startswith("data:"):
        try:
            header, b64_data = media_url.split(",", 1)
            mime_type = header.split(";")[0].replace("data:", "")
            ext = mime_type.split("/")[-1] if "/" in mime_type else "bin"
            fname = f"vault_{int(datetime.utcnow().timestamp())}.{ext}"
            drive_link = upload_to_5tb_drive(base64.b64decode(b64_data), fname, mime_type)
            if drive_link:
                media_url = drive_link
        except Exception as e:
            print("Base64 upload error:", e)

    item = KnowledgeItem(
        title=d.get("title") or "Untitled",
        category=d.get("category") or "Note",
        content=d.get("content") or "",
        media_url=media_url,
        tags=d.get("tags") or "knowledge"
    )
    db.session.add(item)
    db.session.commit()
    return jsonify({"status": "success", "id": item.id, "media_url": media_url})

@app.route("/api/problems", methods=["POST", "DELETE"])
def manage_problems():
    if request.method == "DELETE":
        prob_id = request.args.get("id")
        if prob_id:
            p = db.session.get(Problem, int(prob_id))
            if p:
                db.session.delete(p)
                db.session.commit()
        return jsonify({"status": "deleted"})

    d = request.get_json(silent=True) or {}
    demand = int(d.get("market_demand") or 8)
    score = int(d.get("opportunity_score") or min(100, demand * 10))
    p = Problem(
        title=d.get("title") or "Untitled Problem",
        source=d.get("source") or "Real World Observation",
        root_cause=d.get("root_cause") or "",
        proposed_solution=d.get("solution") or "",
        market_demand=demand,
        competition_level=d.get("competition_level") or "Medium",
        revenue_potential=d.get("revenue_potential") or "₹10L - ₹1Cr",
        opportunity_score=score
    )
    db.session.add(p)
    db.session.commit()
    return jsonify({"status": "success", "id": p.id})

@app.route("/api/startups", methods=["POST", "PUT", "DELETE"])
def manage_startups():
    if request.method == "DELETE":
        st_id = request.args.get("id")
        if st_id:
            st = db.session.get(StartupIdea, int(st_id))
            if st:
                db.session.delete(st)
                db.session.commit()
        return jsonify({"status": "deleted"})

    d = request.get_json(silent=True) or {}
    if request.method == "PUT":
        st_id = d.get("id")
        if st_id:
            st = db.session.get(StartupIdea, int(st_id))
            if st:
                if "progress" in d and d["progress"] is not None:
                    st.progress = int(d["progress"])
                if "stage" in d:
                    st.stage = d["stage"]
                db.session.commit()
        return jsonify({"status": "updated"})

    st = StartupIdea(
        name=d.get("name") or "New Venture",
        description=d.get("description") or "",
        revenue_model=d.get("revenue_model") or "Subscription",
        market_size=d.get("market_size") or "₹10Cr TAM",
        stage=d.get("stage") or "Idea",
        feasibility_score=int(d.get("feasibility_score") or 85),
        progress=int(d.get("progress") or 10)
    )
    db.session.add(st)
    db.session.commit()
    return jsonify({"status": "success", "id": st.id})

@app.route("/api/tasks", methods=["POST", "PUT", "DELETE"])
def handle_tasks():
    if request.method == "DELETE":
        t_id = request.args.get("id")
        if t_id:
            t = db.session.get(ProjectTask, int(t_id))
            if t:
                db.session.delete(t)
                db.session.commit()
        return jsonify({"status": "deleted"})

    d = request.get_json(silent=True) or {}
    if request.method == "POST":
        t = ProjectTask(
            title=d.get("title") or "Untitled Task",
            project_name=d.get("project_name") or "Main Startup",
            status="Todo",
            kanban_stage=d.get("kanban_stage") or "Ideas",
            priority=d.get("priority") or "High",
            deadline=d.get("deadline") or "2026-11-30",
            dependencies=d.get("dependencies") or "None",
            assignee=d.get("assignee") or "Mr. Vijay Mistry"
        )
        db.session.add(t)
        db.session.commit()
        return jsonify({"status": "success", "id": t.id})
    else:
        t_id = d.get("id")
        if t_id:
            t = db.session.get(ProjectTask, int(t_id))
            if t:
                t.kanban_stage = d.get("kanban_stage", t.kanban_stage)
                t.status = "Completed" if t.kanban_stage == "Completed" else "In Progress"
                db.session.commit()
        return jsonify({"status": "updated"})

@app.route("/api/journals", methods=["POST", "DELETE"])
def create_journal():
    d = request.get_json(silent=True) or {}
    j = JournalEntry(
        entry_type=d.get("entry_type") or "Founder Journal",
        category_tag=d.get("category_tag") or "Daily Work",
        title=d.get("title") or "Untitled Log",
        details=d.get("details") or ""
    )
    db.session.add(j)
    db.session.commit()
    return jsonify({"status": "success", "id": j.id})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)