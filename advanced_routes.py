import os
import json
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import Blueprint, request, jsonify
import cloudinary.uploader
from models import (
    db, KeyValueStore, KnowledgeItem, ReferenceDesign, Problem, SolutionItem,
    InnovationItem, StartupIdea, ProjectTask, RoadmapMilestone,
    JournalEntry, GoalHabit, OrganizationCRM
)

adv_bp = Blueprint("adv_bp", __name__)

UPLOAD_DIR = os.path.join(os.getcwd(), "static", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

STORE_KEY = "interactive_store"

def safe_int(val, default=0):
    try:
        return int(val)
    except (ValueError, TypeError):
        return default

def get_default_store():
    return {
        "graph_nodes": [
            {"id": 1, "label": "Problem: Local Catalogs", "group": "Problem", "x": 180, "y": 220, "color": "#F59E0B"},
            {"id": 2, "label": "Solution: 1-Click SaaS", "group": "Solution", "x": 450, "y": 150, "color": "#0EA5E9"},
            {"id": 3, "label": "Startup: B2Conecter", "group": "Startup", "x": 750, "y": 220, "color": "#7C3AED"},
            {"id": 4, "label": "Revenue: Tiered Plan", "group": "Revenue", "x": 1000, "y": 220, "color": "#10B981"}
        ],
        "graph_links": [[1, 2], [2, 3], [3, 4]],
        "mindmap_nodes": [
            {"id": 101, "label": "BIGKNOWLEDGE BRAIN", "parent": 0, "x": 550, "y": 240, "color": "#7C3AED", "img": ""},
            {"id": 102, "label": "Startup Ideas", "parent": 101, "x": 250, "y": 120, "color": "#0EA5E9", "img": ""},
            {"id": 103, "label": "Research & Vault", "parent": 101, "x": 850, "y": 120, "color": "#10B981", "img": ""},
            {"id": 104, "label": "Execution & Team", "parent": 101, "x": 550, "y": 400, "color": "#F59E0B", "img": ""}
        ],
        "bmc": {
            "partners": "Cloud Providers, Incubators, Local Merchant Guilds",
            "activities": "Full-Stack Product Engineering, Problem Validation",
            "value": "Lifelong Second Brain + Startup Execution OS",
            "relationships": "Self-serve SaaS, Community & Automated Reports",
            "segments": "Startup Founders, Researchers, SMB Owners",
            "resources": "Knowledge Graph Engine, PostgreSQL Vault",
            "channels": "Direct SaaS Onboarding, Hackathons, Communities",
            "costs": "Cloud Hosting, Database Compute, Storage CDN",
            "revenue": "Tiered Subscriptions (₹199 / ₹299 / ₹399 / ₹799)"
        },
        "active_workspace": {
            "startup_name": "B2Conecter & BIGKNOWLEDGE OS",
            "goal": "Onboard 100 Active Users & Complete Cloud Persistence",
            "problem": "Fragmented tools for founders & local businesses",
            "solution": "Unified Founder OS + Hyperlocal Storefront Engine",
            "milestones": "Database Ready, UI Ready, Media Vaults Active",
            "progress": 82,
            "hours": 350
        }
    }

def load_custom_store():
    record = KeyValueStore.query.get(STORE_KEY)
    if not record:
        default_data = get_default_store()
        save_custom_store(default_data)
        return default_data
    try:
        return json.loads(record.value_json)
    except Exception:
        return get_default_store()

def save_custom_store(data):
    record = KeyValueStore.query.get(STORE_KEY)
    if not record:
        record = KeyValueStore(key=STORE_KEY, value_json=json.dumps(data))
        db.session.add(record)
    else:
        record.value_json = json.dumps(data)
    db.session.commit()

# 1. File Upload API (Cloudinary first, Full Render URL fallback)
@adv_bp.route("/api/adv/upload_file", methods=["POST"])
def upload_real_file():
    if "file" not in request.files:
        return jsonify({"error": "No file selected"}), 400
    f = request.files["file"]
    if not f or f.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    # Try Cloudinary if configured in environment
    if os.environ.get("CLOUDINARY_URL"):
        try:
            upload_res = cloudinary.uploader.upload(f, resource_type="auto")
            return jsonify({
                "status": "success",
                "url": upload_res.get("secure_url"),
                "filename": f.filename
            })
        except Exception as e:
            print("Cloudinary upload fallback to local:", e)
            f.seek(0)

    safe_name = f"{int(datetime.utcnow().timestamp())}_{secure_filename(f.filename)}"
    save_path = os.path.join(UPLOAD_DIR, safe_name)
    f.save(save_path)
    base_url = request.host_url.rstrip("/")
    file_url = f"{base_url}/static/uploads/{safe_name}"
    return jsonify({"status": "success", "url": file_url, "filename": f.filename})

# 2. Universal Delete API
@adv_bp.route("/api/adv/delete", methods=["POST"])
def universal_delete():
    d = request.get_json(silent=True) or {}
    model_map = {
        "knowledge": KnowledgeItem,
        "reference": ReferenceDesign,
        "problem": Problem,
        "solution": SolutionItem,
        "innovation": InnovationItem,
        "startup": StartupIdea,
        "task": ProjectTask,
        "roadmap": RoadmapMilestone,
        "journal": JournalEntry,
        "goal": GoalHabit,
        "crm": OrganizationCRM
    }
    model = model_map.get(d.get("module"))
    if model and d.get("id") is not None:
        obj = db.session.get(model, safe_int(d.get("id")))
        if obj:
            db.session.delete(obj)
            db.session.commit()
            return jsonify({"status": "deleted"})
    return jsonify({"status": "not_found"}), 404

# 3. Universal Create API
@adv_bp.route("/api/adv/create", methods=["POST"])
def universal_create():
    d = request.get_json(silent=True) or {}
    mod = d.get("module")
    item = None

    if mod == "solution":
        item = SolutionItem(
            problem_title=d.get("problem_title", "General Problem"),
            solution_title=d.get("solution_title") or d.get("title", "New Solution"),
            cost_estimate=d.get("cost_estimate", "$1,000"),
            benefits=d.get("benefits", ""),
            market_impact=d.get("market_impact", "High"),
            difficulty=d.get("difficulty", "Medium"),
            revenue_potential=d.get("revenue_potential", "High")
        )
    elif mod == "innovation":
        item = InnovationItem(
            title=d.get("title", "Untitled Innovation"),
            category=d.get("category", "Technology"),
            summary=d.get("summary", ""),
            opportunity_note=d.get("opportunity_note", "")
        )
    elif mod == "roadmap":
        item = RoadmapMilestone(
            roadmap_type=d.get("roadmap_type", "Startup Roadmap"),
            title=d.get("title", "New Milestone"),
            dependencies=d.get("dependencies", "None"),
            deadline=d.get("deadline", "2026-12-31"),
            progress=safe_int(d.get("progress"), 50)
        )
    elif mod == "goal":
        item = GoalHabit(
            item_type=d.get("item_type", "Goal"),
            title=d.get("title", "New Goal"),
            streak_or_progress=safe_int(d.get("streak_or_progress"), 1),
            completed_today=bool(d.get("completed_today", True))
        )
    elif mod == "crm":
        item = OrganizationCRM(
            entity_type=d.get("entity_type", "Team Member"),
            name=d.get("name") or d.get("title", "New Contact"),
            role_or_segment=d.get("role_or_segment", "Developer"),
            department_or_company=d.get("department_or_company", "Core Team"),
            details_or_strengths=d.get("details_or_strengths", ""),
            weaknesses_or_actions=d.get("weaknesses_or_actions", ""),
            tasks_completed=safe_int(d.get("tasks_completed"), 10),
            tasks_pending=safe_int(d.get("tasks_pending"), 2),
            work_hours=safe_int(d.get("work_hours"), 40),
            productivity_score=safe_int(d.get("productivity_score"), 95)
        )
    elif mod == "reference":
        item = ReferenceDesign(
            title=d.get("title", "UI Reference"),
            ref_type=d.get("ref_type", "Dashboard Reference"),
            image_url=d.get("image_url", ""),
            extracted_palette=d.get("extracted_palette", "#7C3AED, #0EA5E9, #10B981"),
            notes=d.get("notes", "")
        )
    else:
        return jsonify({"error": f"Unknown module: {mod}"}), 400

    db.session.add(item)
    db.session.commit()
    return jsonify({"status": "created", "id": item.id})

# 4. Get & Save Interactive Store
@adv_bp.route("/api/adv/store", methods=["GET", "POST"])
def handle_custom_store():
    store = load_custom_store()
    if request.method == "POST":
        incoming = request.get_json(silent=True) or {}
        for k, v in incoming.items():
            store[k] = v
        save_custom_store(store)
        return jsonify({"status": "saved", "store": store})

    refs = [
        {
            "id": r.id,
            "title": r.title,
            "ref_type": r.ref_type,
            "image_url": r.image_url,
            "palette": r.extracted_palette,
            "notes": r.notes
        }
        for r in ReferenceDesign.query.order_by(ReferenceDesign.id.desc()).all()
    ]
    store["references"] = refs
    return jsonify(store)