import os
import json
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import Blueprint, request, jsonify, send_from_directory
from models import (
    db, KnowledgeItem, ReferenceDesign, Problem, SolutionItem,
    InnovationItem, StartupIdea, ProjectTask, RoadmapMilestone,
    JournalEntry, GoalHabit, OrganizationCRM
)

adv_bp = Blueprint("adv_bp", __name__)

# Upload folder banana jahan HD Images, Videos, PPTX, PDF save honge
UPLOAD_DIR = os.path.join(os.getcwd(), "static", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Custom JSON Store for Graph Nodes, MindMap Nodes & Business Model Canvas
CUSTOM_STORE_FILE = os.path.join(UPLOAD_DIR, "interactive_store.json")

def load_custom_store():
    if not os.path.exists(CUSTOM_STORE_FILE):
        default_data = {
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
        save_custom_store(default_data)
    with open(CUSTOM_STORE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_custom_store(data):
    with open(CUSTOM_STORE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

# 1. File Upload API (For Video MP4, HD Images, PDF, PPTX, DOCX, Graph JSON)
@adv_bp.route("/api/adv/upload_file", methods=["POST"])
def upload_real_file():
    if "file" not in request.files:
        return jsonify({"error": "No file selected"}), 400
    f = request.files["file"]
    if f.filename == "":
        return jsonify({"error": "Empty filename"}), 400
    safe_name = f"{int(datetime.utcnow().timestamp())}_{secure_filename(f.filename)}"
    save_path = os.path.join(UPLOAD_DIR, safe_name)
    f.save(save_path)
    file_url = f"/static/uploads/{safe_name}"
    return jsonify({"status": "success", "url": file_url, "filename": f.filename})

# 2. Universal Universal Delete API (Delete any record from any module)
@adv_bp.route("/api/adv/delete", methods=["POST"])
def universal_delete():
    d = request.json
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
    if model:
        obj = model.query.get(d.get("id"))
        if obj:
            db.session.delete(obj)
            db.session.commit()
            return jsonify({"status": "deleted"})
    return jsonify({"status": "not_found"}), 404

# 3. Universal Create API for All Remaining Modules (Solutions, Innovations, Roadmaps, Goals, CRM, References)
@adv_bp.route("/api/adv/create", methods=["POST"])
def universal_create():
    d = request.json
    mod = d.get("module")

    if mod == "solution":
        item = SolutionItem(
            problem_title=d.get("problem_title", ""),
            solution_title=d.get("solution_title", ""),
            cost_estimate=d.get("cost_estimate", "$1,000"),
            benefits=d.get("benefits", ""),
            market_impact=d.get("market_impact", "High"),
            difficulty=d.get("difficulty", "Medium"),
            revenue_potential=d.get("revenue_potential", "High")
        )
        db.session.add(item)

    elif mod == "innovation":
        item = InnovationItem(
            title=d.get("title", ""),
            category=d.get("category", "Technology"),
            summary=d.get("summary", ""),
            opportunity_note=d.get("opportunity_note", "")
        )
        db.session.add(item)

    elif mod == "roadmap":
        item = RoadmapMilestone(
            roadmap_type=d.get("roadmap_type", "Startup Roadmap"),
            title=d.get("title", ""),
            dependencies=d.get("dependencies", "None"),
            deadline=d.get("deadline", "2026-12-31"),
            progress=int(d.get("progress", 50))
        )
        db.session.add(item)

    elif mod == "goal":
        item = GoalHabit(
            item_type=d.get("item_type", "Goal"),
            title=d.get("title", ""),
            streak_or_progress=int(d.get("streak_or_progress", 1)),
            completed_today=True
        )
        db.session.add(item)

    elif mod == "crm":
        item = OrganizationCRM(
            entity_type=d.get("entity_type", "Team Member"),
            name=d.get("name", ""),
            role_or_segment=d.get("role_or_segment", "Developer"),
            department_or_company=d.get("department_or_company", "Core Team"),
            details_or_strengths=d.get("details_or_strengths", ""),
            weaknesses_or_actions=d.get("weaknesses_or_actions", ""),
            tasks_completed=int(d.get("tasks_completed", 10)),
            tasks_pending=int(d.get("tasks_pending", 2)),
            work_hours=int(d.get("work_hours", 40)),
            productivity_score=int(d.get("productivity_score", 95))
        )
        db.session.add(item)

    elif mod == "reference":
        item = ReferenceDesign(
            title=d.get("title", "UI Reference"),
            ref_type=d.get("ref_type", "Dashboard Reference"),
            image_url=d.get("image_url", ""),
            extracted_palette=d.get("extracted_palette", "#7C3AED, #0EA5E9, #10B981"),
            notes=d.get("notes", "")
        )
        db.session.add(item)

    db.session.commit()
    return jsonify({"status": "created"})

# 4. Get & Save Interactive Store (Knowledge Graph, Mind Map, BMC, Active Startup, Reference List)
@adv_bp.route("/api/adv/store", methods=["GET", "POST"])
def handle_custom_store():
    store = load_custom_store()
    if request.method == "POST":
        incoming = request.json
        for k, v in incoming.items():
            store[k] = v
        save_custom_store(store)
        return jsonify({"status": "saved", "store": store})
    
    refs = [
        {"id": r.id, "title": r.title, "ref_type": r.ref_type, "image_url": r.image_url, "palette": r.extracted_palette, "notes": r.notes}
        for r in ReferenceDesign.query.order_by(ReferenceDesign.id.desc()).all()
    ]
    store["references"] = refs
    return jsonify(store)