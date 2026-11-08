import os
import json
from datetime import timedelta
from flask import Flask, render_template, request, jsonify, Response, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv
import cloudinary
from groq import Groq

from models import (
    db, User, KnowledgeItem, ReferenceDesign, Problem, SolutionItem,
    InnovationItem, StartupIdea, ProjectTask, RoadmapMilestone,
    JournalEntry, GoalHabit, OrganizationCRM
)

# Import all 3 Blueprints!
from advanced_routes import adv_bp
from chat_meeting_routes import chat_bp
from power_routes import power_bp

load_dotenv()

app = Flask(__name__)

# Strict + Localhost + Wildcard CORS Support for Vercel Frontend
CORS(
    app,
    resources={
        r"/*": {
            "origins": [
                "https://1bigknowledgefrontend.vercel.app",
                "http://localhost:3000",
                "http://localhost:5000",
                "http://127.0.0.1:5500",
                "*"
            ]
        }
    },
    methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-Requested-With"]
)

# Register Blueprints so /api/adv/*, /api/chat/*, and /api/power/* work!
app.register_blueprint(adv_bp)
app.register_blueprint(chat_bp)
app.register_blueprint(power_bp)

# Automatic SQLite / PostgreSQL Configuration
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

groq_api_key = os.environ.get("GROQ_API_KEY")
groq_client = Groq(api_key=groq_api_key) if groq_api_key else None

def safe_int(val, default=0):
    try:
        return int(val)
    except (ValueError, TypeError):
        return default

# Database Initialization
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

# Serve uploaded files cleanly
@app.route("/static/uploads/<path:filename>")
def serve_uploads(filename):
    upload_dir = os.path.join(os.getcwd(), "static", "uploads")
    return send_from_directory(upload_dir, filename)

@app.route("/")
def dashboard_home():
    try:
        return render_template("index.html")
    except Exception:
        return jsonify({
            "status": "live",
            "service": "BigKnowledge Backend API",
            "founder": "Mr. Vijay Mistry",
            "endpoints_active": ["core", "adv_bp", "chat_bp", "power_bp"]
        })

@app.route("/login")
def login_page():
    try:
        return render_template("login.html")
    except Exception:
        return jsonify({"status": "login_endpoint_active"})

@app.route("/api/bootstrap", methods=["GET"])
def api_bootstrap():
    return jsonify({
        "knowledge": [
            {
                "id": k.id,
                "title": k.title,
                "category": k.category,
                "content": k.content,
                "media_url": k.media_url,
                "tags": k.tags,
                "is_favorite": k.is_favorite,
                "created_at": k.created_at.strftime("%Y-%m-%d") if k.created_at else ""
            }
            for k in KnowledgeItem.query.order_by(KnowledgeItem.id.desc()).all()
        ],
        "problems": [
            {
                "id": p.id,
                "title": p.title,
                "source": p.source,
                "root_cause": p.root_cause,
                "solution": p.proposed_solution,
                "market_demand": p.market_demand,
                "competition_level": p.competition_level,
                "revenue_potential": p.revenue_potential,
                "opportunity_score": p.opportunity_score
            }
            for p in Problem.query.order_by(Problem.opportunity_score.desc()).all()
        ],
        "solutions": [
            {
                "id": s.id,
                "problem_title": s.problem_title,
                "solution_title": s.solution_title,
                "cost_estimate": s.cost_estimate,
                "benefits": s.benefits,
                "market_impact": s.market_impact,
                "difficulty": s.difficulty,
                "revenue_potential": s.revenue_potential
            }
            for s in SolutionItem.query.order_by(SolutionItem.id.desc()).all()
        ],
        "innovations": [
            {
                "id": i.id,
                "title": i.title,
                "category": i.category,
                "summary": i.summary,
                "opportunity_note": i.opportunity_note
            }
            for i in InnovationItem.query.order_by(InnovationItem.id.desc()).all()
        ],
        "startups": [
            {
                "id": st.id,
                "name": st.name,
                "description": st.description,
                "market": st.market,
                "industry": st.industry,
                "revenue_model": st.revenue_model,
                "competitors": st.competitors,
                "market_size": st.market_size,
                "validation_status": st.validation_status,
                "stage": st.stage,
                "priority": st.priority,
                "feasibility_score": st.feasibility_score,
                "progress": st.progress,
                "time_spent_hours": st.time_spent_hours
            }
            for st in StartupIdea.query.order_by(StartupIdea.id.desc()).all()
        ],
        "tasks": [
            {
                "id": t.id,
                "title": t.title,
                "project_name": t.project_name,
                "status": t.status,
                "kanban_stage": t.kanban_stage,
                "priority": t.priority,
                "deadline": t.deadline,
                "dependencies": t.dependencies,
                "assignee": t.assignee
            }
            for t in ProjectTask.query.order_by(ProjectTask.id.desc()).all()
        ],
        "roadmaps": [
            {
                "id": r.id,
                "roadmap_type": r.roadmap_type,
                "title": r.title,
                "dependencies": r.dependencies,
                "deadline": r.deadline,
                "progress": r.progress
            }
            for r in RoadmapMilestone.query.all()
        ],
        "journals": [
            {
                "id": j.id,
                "entry_type": j.entry_type,
                "category_tag": j.category_tag,
                "title": j.title,
                "details": j.details,
                "expected_outcome": j.expected_outcome,
                "actual_result": j.actual_result,
                "created_at": j.created_at.strftime("%Y-%m-%d") if j.created_at else ""
            }
            for j in JournalEntry.query.order_by(JournalEntry.id.desc()).all()
        ],
        "goals_habits": [
            {
                "id": g.id,
                "item_type": g.item_type,
                "title": g.title,
                "streak_or_progress": g.streak_or_progress,
                "completed_today": g.completed_today
            }
            for g in GoalHabit.query.all()
        ],
        "org_crm": [
            {
                "id": c.id,
                "entity_type": c.entity_type,
                "name": c.name,
                "role_or_segment": c.role_or_segment,
                "department_or_company": c.department_or_company,
                "details_or_strengths": c.details_or_strengths,
                "weaknesses_or_actions": c.weaknesses_or_actions,
                "tasks_completed": c.tasks_completed,
                "tasks_pending": c.tasks_pending,
                "work_hours": c.work_hours,
                "productivity_score": c.productivity_score
            }
            for c in OrganizationCRM.query.all()
        ]
    })

@app.route("/api/knowledge", methods=["POST", "DELETE"])
def manage_knowledge():
    if request.method == "DELETE":
        item = db.session.get(KnowledgeItem, safe_int(request.args.get("id")))
        if item:
            db.session.delete(item)
            db.session.commit()
        return jsonify({"status": "deleted"})

    d = request.get_json(silent=True) or {}
    item = KnowledgeItem(
        title=d.get("title") or "Untitled",
        category=d.get("category") or "Note",
        content=d.get("content") or "",
        media_url=d.get("media_url") or "",
        tags=d.get("tags") or "knowledge"
    )
    db.session.add(item)
    db.session.commit()
    return jsonify({"status": "success", "id": item.id})

@app.route("/api/problems", methods=["POST", "DELETE"])
def manage_problems():
    if request.method == "DELETE":
        p = db.session.get(Problem, safe_int(request.args.get("id")))
        if p:
            db.session.delete(p)
            db.session.commit()
        return jsonify({"status": "deleted"})

    d = request.get_json(silent=True) or {}
    demand = safe_int(d.get("market_demand"), 8)
    score = safe_int(d.get("opportunity_score"), min(100, demand * 10))
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

    if d.get("solution"):
        sol = SolutionItem(
            problem_title=p.title,
            solution_title=d.get("solution"),
            cost_estimate=d.get("cost_estimate") or "₹5,000 - ₹25,000",
            benefits=d.get("root_cause") or "",
            market_impact="High" if demand >= 8 else "Medium",
            revenue_potential=p.revenue_potential
        )
        db.session.add(sol)

    if d.get("auto_convert_startup"):
        st = StartupIdea(
            name=d.get("startup_name") or p.title[:30],
            description=d.get("solution") or p.root_cause or "Auto-converted from Problem Center",
            revenue_model=d.get("revenue_model") or "SaaS Subscription",
            market_size=p.revenue_potential,
            stage="Validation",
            priority="High",
            feasibility_score=score,
            progress=15
        )
        db.session.add(st)

    db.session.commit()
    return jsonify({"status": "success", "id": p.id})

@app.route("/api/startups", methods=["POST", "PUT", "DELETE"])
def manage_startups():
    if request.method == "DELETE":
        st = db.session.get(StartupIdea, safe_int(request.args.get("id")))
        if st:
            db.session.delete(st)
            db.session.commit()
        return jsonify({"status": "deleted"})

    d = request.get_json(silent=True) or {}
    if request.method == "PUT":
        st = db.session.get(StartupIdea, safe_int(d.get("id")))
        if st:
            if "progress" in d:
                st.progress = safe_int(d["progress"], st.progress)
            if "stage" in d:
                st.stage = d["stage"]
            if "feasibility_score" in d:
                st.feasibility_score = safe_int(d["feasibility_score"], st.feasibility_score)
            db.session.commit()
        return jsonify({"status": "updated"})

    st = StartupIdea(
        name=d.get("name") or "Untitled Venture",
        description=d.get("description") or "",
        market=d.get("market") or "India / Global",
        industry=d.get("industry") or "SaaS / Tech",
        revenue_model=d.get("revenue_model") or "Subscription",
        competitors=d.get("competitors") or "None",
        market_size=d.get("market_size") or "₹10Cr TAM",
        stage=d.get("stage") or "Idea",
        priority=d.get("priority") or "High",
        feasibility_score=safe_int(d.get("feasibility_score"), 85),
        progress=safe_int(d.get("progress"), 10)
    )
    db.session.add(st)
    db.session.commit()
    return jsonify({"status": "success", "id": st.id})

@app.route("/api/tasks", methods=["POST", "PUT", "DELETE"])
def handle_tasks():
    if request.method == "DELETE":
        t = db.session.get(ProjectTask, safe_int(request.args.get("id")))
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
        t = db.session.get(ProjectTask, safe_int(d.get("id")))
        if t:
            t.kanban_stage = d.get("kanban_stage", t.kanban_stage)
            t.status = "Completed" if t.kanban_stage == "Completed" else "In Progress"
            db.session.commit()
        return jsonify({"status": "updated"})

@app.route("/api/journals", methods=["POST", "DELETE"])
def create_journal():
    if request.method == "DELETE":
        j = db.session.get(JournalEntry, safe_int(request.args.get("id")))
        if j:
            db.session.delete(j)
            db.session.commit()
        return jsonify({"status": "deleted"})

    d = request.get_json(silent=True) or {}
    j = JournalEntry(
        entry_type=d.get("entry_type") or "Founder Journal",
        category_tag=d.get("category_tag") or "Daily Work",
        title=d.get("title") or "Untitled Entry",
        details=d.get("details") or "",
        expected_outcome=d.get("expected_outcome") or "",
        actual_result=d.get("actual_result") or ""
    )
    db.session.add(j)
    db.session.commit()
    return jsonify({"status": "success", "id": j.id})

@app.route("/api/export/json", methods=["GET"])
def export_json():
    payload = api_bootstrap().get_json()
    return Response(
        json.dumps(payload, indent=2),
        mimetype="application/json",
        headers={"Content-Disposition": "attachment;filename=bigknowledge_backup.json"}
    )

@app.route("/api/export/csv", methods=["GET"])
def export_csv():
    rows = ["ID,Startup Name,Stage,Industry,Revenue Model,Market Size,Feasibility Score,Progress"]
    for s in StartupIdea.query.all():
        safe_name = (s.name or "").replace('"', '""')
        safe_model = (s.revenue_model or "").replace('"', '""')
        safe_market = (s.market_size or "").replace('"', '""')
        rows.append(f'{s.id},"{safe_name}","{s.stage}","{s.industry}","{safe_model}","{safe_market}",{s.feasibility_score},{s.progress}')
    return Response(
        "\n".join(rows),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=bigknowledge_startups.csv"}
    )

# ==============================================================================
# 🤖 SUPER AI CO-FOUNDER ROUTE (WITH VALID GROQ MODEL & AUTOMATIC FALLBACK)
# ==============================================================================
@app.route("/api/ai-assistant", methods=["POST"])
def ai_assistant():
    d = request.get_json(silent=True) or {}
    user_query = d.get("query", "").strip()
    if not user_query:
        return jsonify({"error": "Query is empty"}), 400

    if not groq_client:
        return jsonify({
            "reply": "Vijay bhai, Render environment variables me GROQ_API_KEY set nahi hai. Kripya Render Dashboard -> Environment me GROQ_API_KEY add karein.",
            "action": "CHAT",
            "data": {"target": "dashboard"}
        }), 200

    system_prompt = """
    You are SUPER AI, the core assistant for Mr. Vijay Mistry's 'BigKnowledge' Founder OS.
    Your job is to understand what Vijay wants and return a STRICT JSON response.
    
    Website Map (Pages & What They Contain):
    1. "NAVIGATE": Use this action to open a page based on what Vijay is looking for.
       Pages available:
       - 'code-vault': Opens Developer Code & API Vault. Use this if Vijay asks for code, scripts, terminal commands, Python, or "git add .".
       - 'finance-ledger': Opens Finance & Cashflow. Use this for money, revenue, expenses, or burn tracker.
       - 'video-vault': Opens Video Vault. Use this for YouTube links, video notes.
       - 'kanban-board': Opens Kanban. Use this for execution, tasks, building, sprints.
       - 'startup-db': Opens Startup Ideas Database.
       - 'problem-center': Opens Problem Collection Center.
       - 'knowledge-vault': Opens Knowledge Vault for general text notes and research.
       - 'journals': Opens Founder Journals and logs.
       - 'dashboard': Opens Main Dashboard.
       
    2. "ADD_TASK": Use when Vijay explicitly says to add a new task.
    3. "SEARCH": Use when Vijay wants to search his past ideas in the database.
    4. "CHAT": Use for normal talk, coding help, or business advice.

    You MUST reply ONLY in this JSON format without any markdown or extra text:
    {
      "reply": "Your natural Hinglish reply (e.g., 'Vijay bhai, maine Code Vault open kar diya hai jahan aapke git commands hain.')",
      "action": "ACTION_NAME",
      "data": { "target": "page-name-from-the-list-above" }
    }
    """

    models_to_try = ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"]
    last_error = None

    for model_name in models_to_try:
        try:
            chat_completion = groq_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_query}
                ],
                model=model_name,
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            ai_response_text = chat_completion.choices[0].message.content
            ai_json = json.loads(ai_response_text)
            return jsonify(ai_json)
        except Exception as e:
            last_error = str(e)
            continue

    return jsonify({
        "reply": f"Sorry Vijay bhai, Groq AI model call me error aaya: {last_error}",
        "action": "ERROR",
        "data": {"error_details": last_error}
    }), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)