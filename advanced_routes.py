import os
import json
import base64
import threading
import urllib.request
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import Blueprint, request, jsonify, current_app
import cloudinary.uploader
from models import (
    db, KnowledgeItem, ReferenceDesign, Problem, SolutionItem,
    InnovationItem, StartupIdea, ProjectTask, RoadmapMilestone,
    JournalEntry, GoalHabit, OrganizationCRM
)

adv_bp = Blueprint("adv_bp", __name__)

UPLOAD_DIR = os.path.join(os.getcwd(), "static", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

CUSTOM_STORE_FILE = os.path.join(UPLOAD_DIR, "interactive_store.json")

DEFAULT_STORE_DATA = {
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
        "resources": "Knowledge Graph Engine, 5TB Google Drive Vault",
        "channels": "Direct SaaS Onboarding, Hackathons, Communities",
        "costs": "Cloud Hosting, Database Compute, Storage CDN",
        "revenue": "Tiered Subscriptions (₹199 / ₹299 / ₹399 / ₹799)"
    },
    "active_workspace": {
        "startup_name": "B2Conecter & BIGKNOWLEDGE OS",
        "goal": "Onboard 100 Active Users & Complete Cloud Persistence",
        "problem": "Fragmented tools for founders & local businesses",
        "solution": "Unified Founder OS + Hyperlocal Storefront Engine",
        "milestones": "Database Ready, UI Ready, 5TB Drive Vault Active",
        "progress": 85,
        "hours": 350
    }
}

def upload_to_5tb_gdrive(file_bytes, filename, mime_type="application/octet-stream", sub_folder="Uploaded_Files"):
    """Uploads file to 5TB Google Drive using standard urllib (Zero extra dependencies)"""
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
        req = urllib.request.Request(
            webhook_url,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=45) as resp:
            res_json = json.loads(resp.read().decode("utf-8"))
            if res_json.get("status") == "success":
                file_id = res_json.get("file_id")
                if file_id and mime_type.startswith("image/"):
                    return f"https://drive.google.com/thumbnail?id={file_id}&sz=w2000"
                return res_json.get("url")
    except Exception as e:
        print("🚨 5TB Google Drive Upload Error:", str(e))
    return None

def load_custom_store():
    if not os.path.exists(CUSTOM_STORE_FILE):
        save_custom_store(DEFAULT_STORE_DATA)
        return dict(DEFAULT_STORE_DATA)
    try:
        with open(CUSTOM_STORE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        save_custom_store(DEFAULT_STORE_DATA)
        return dict(DEFAULT_STORE_DATA)

def save_custom_store(data):
    with open(CUSTOM_STORE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

# 1. SUPERFAST INSTANT UPLOAD API (0.5 Second Response + Background 5TB Drive Sync)
@adv_bp.route("/api/adv/upload_file", methods=["POST"])
def upload_real_file():
    if "file" not in request.files:
        return jsonify({"error": "No file selected"}), 400
    f = request.files["file"]
    if not f or f.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    safe_name = f"{int(datetime.utcnow().timestamp())}_{secure_filename(f.filename)}"
    mime_type = f.mimetype or "application/octet-stream"
    file_bytes = f.read()

    # STEP A: Turant (0.2 second me) Render par save karo taaki website bilkul wait na kare!
    save_path = os.path.join(UPLOAD_DIR, safe_name)
    with open(save_path, "wb") as out_file:
        out_file.write(file_bytes)

    base_url = request.host_url.rstrip("/")
    instant_url = f"{base_url}/static/uploads/{safe_name}"

    # STEP B: Background me chupchap 5TB Google Drive me bhejo aur Database link update kar do!
    app_obj = current_app._get_current_object()

    def background_5tb_sync(app_context, b_data, s_name, m_type, temp_url):
        with app_context.app_context():
            drive_url = upload_to_5tb_gdrive(b_data, s_name, m_type, sub_folder="Uploaded_Files")
            if drive_url:
                try:
                    # Knowledge Vault ya Reference Design me jahan bhi temp_url save hua ho, usko permanent 5TB Drive URL bana do
                    for k_item in KnowledgeItem.query.filter_by(media_url=temp_url).all():
                        k_item.media_url = drive_url
                    for r_item in ReferenceDesign.query.filter_by(image_url=temp_url).all():
                        r_item.image_url = drive_url
                    db.session.commit()
                    print(f"✅ Background 5TB Drive Sync Complete: {drive_url}")
                except Exception as db_err:
                    print("DB URL update error:", db_err)

    threading.Thread(
        target=background_5tb_sync,
        args=(app_obj, file_bytes, safe_name, mime_type, instant_url),
        daemon=True
    ).start()

    # User ko bina ruke 0.5 second me response mil jayega!
    return jsonify({
        "status": "success",
        "url": instant_url,
        "filename": f.filename,
        "storage_engine": "Instant_Speed_5TB_Background_Sync"
    })

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
    rec_id = d.get("id")
    if model and rec_id is not None:
        obj = db.session.get(model, int(rec_id))
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

    if mod == "solution":
        item = SolutionItem(
            problem_title=d.get("problem_title") or "General Problem",
            solution_title=d.get("solution_title") or "Proposed Solution",
            cost_estimate=d.get("cost_estimate") or "$1,000",
            benefits=d.get("benefits") or "",
            market_impact=d.get("market_impact") or "High",
            difficulty=d.get("difficulty") or "Medium",
            revenue_potential=d.get("revenue_potential") or "High"
        )
        db.session.add(item)

    elif mod == "innovation":
        item = InnovationItem(
            title=d.get("title") or "New Innovation",
            category=d.get("category") or "Technology",
            summary=d.get("summary") or "",
            opportunity_note=d.get("opportunity_note") or ""
        )
        db.session.add(item)

    elif mod == "roadmap":
        item = RoadmapMilestone(
            roadmap_type=d.get("roadmap_type") or "Startup Roadmap",
            title=d.get("title") or "Milestone",
            dependencies=d.get("dependencies") or "None",
            deadline=d.get("deadline") or "2026-12-31",
            progress=int(d.get("progress") or 50)
        )
        db.session.add(item)

    elif mod == "goal":
        item = GoalHabit(
            item_type=d.get("item_type") or "Goal",
            title=d.get("title") or "Daily Goal",
            streak_or_progress=int(d.get("streak_or_progress") or 1),
            completed_today=True
        )
        db.session.add(item)

    elif mod == "crm":
        item = OrganizationCRM(
            entity_type=d.get("entity_type") or "Team Member",
            name=d.get("name") or "Member",
            role_or_segment=d.get("role_or_segment") or "Developer",
            department_or_company=d.get("department_or_company") or "Core Team",
            details_or_strengths=d.get("details_or_strengths") or "",
            weaknesses_or_actions=d.get("weaknesses_or_actions") or "",
            tasks_completed=int(d.get("tasks_completed") or 10),
            tasks_pending=int(d.get("tasks_pending") or 2),
            work_hours=int(d.get("work_hours") or 40),
            productivity_score=int(d.get("productivity_score") or 95)
        )
        db.session.add(item)

    elif mod == "reference":
        item = ReferenceDesign(
            title=d.get("title") or "UI Reference",
            ref_type=d.get("ref_type") or "Dashboard Reference",
            image_url=d.get("image_url") or "",
            extracted_palette=d.get("extracted_palette") or "#7C3AED, #0EA5E9, #10B981",
            notes=d.get("notes") or ""
        )
        db.session.add(item)
    else:
        return jsonify({"error": f"Unknown module: {mod}"}), 400

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
