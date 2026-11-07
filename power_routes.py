import os
import json
import base64
from datetime import datetime
from flask import Blueprint, request, jsonify
from models import (
    db, KnowledgeItem, Problem, SolutionItem,
    StartupIdea, ProjectTask, JournalEntry
)

power_bp = Blueprint("power_bp", __name__)

UPLOAD_DIR = os.path.join(os.getcwd(), "static", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# 1. AI Co-Founder Smart Analyzer & Pitch Deck Generator API
@power_bp.route("/api/power/ai_cofounder", methods=["POST"])
def ai_cofounder_engine():
    d = request.json
    prompt = (d.get("prompt") or "").lower()
    startup_name = d.get("startup_name", "BIGKNOWLEDGE Venture")

    # Fetch live database stats for intelligent context
    total_probs = Problem.query.count()
    total_startups = StartupIdea.query.count()
    total_notes = KnowledgeItem.query.count()
    total_tasks = ProjectTask.query.count()

    if "pitch" in prompt or "deck" in prompt:
        reply = (
            f"📊 **AUTO-GENERATED 7-SLIDE PITCH DECK FOR {startup_name.upper()}**\n\n"
            f"1. **The Hook & Vision:** Empowering founders and businesses with next-gen automation.\n"
            f"2. **The Validated Problem:** Backed by {total_probs} real-world problems logged in your Problem Center.\n"
            f"3. **The Proprietary Solution:** Full-stack cloud architecture with instant workflow execution.\n"
            f"4. **Market Opportunity (TAM/SAM/SOM):** $12B Global TAM | ₹850Cr India Serviceable Market.\n"
            f"5. **Business & Revenue Model:** Tiered SaaS Subscriptions (₹199 / ₹299 / ₹399 / ₹799 per month).\n"
            f"6. **Traction & Execution:** {total_startups} active ventures in pipeline, {total_tasks} execution tasks tracked.\n"
            f"7. **Valuation & Seed Ask:** Pre-Money Valuation ₹4.5Cr ($550K) | Raising ₹50L for 10,000 user scale."
        )
    elif "audit" in prompt or "status" in prompt or "analyze" in prompt:
        reply = (
            f"🧠 **SECOND BRAIN DIAGNOSTIC REPORT:**\n"
            f"• **Knowledge Base:** {total_notes} items indexed.\n"
            f"• **Problem-to-Startup Ratio:** {total_probs} Problems → {total_startups} Startups.\n"
            f"• **Execution Health:** {total_tasks} tasks in Kanban.\n"
            f"• **Next Strategic Move:** Convert your highest-scoring problem into a paid MVP landing page this week and onboard 10 local beta users."
        )
    else:
        reply = (
            f"⚡ **JARVIS Co-Founder Response:**\n"
            f"Maine aapka command *'{d.get('prompt')}'* analyze kiya. Aapke Second Brain me is waqt **{total_notes} Notes**, **{total_probs} Problems**, aur **{total_startups} Startups** active hain.\n\n"
            f"**Actionable Blueprint:**\n"
            f"1. Isko **Problem Collection Center** me root-cause ke saath link karein.\n"
            f"2. **SaaS Revenue Calculator** me ₹299/mo plan par 500 users ka projection check karein (₹1.49 Lakh/Month MRR).\n"
            f"3. **Kanban Board** me iske liye 3 din ki deadline set karein."
        )

    return jsonify({"status": "success", "reply": reply})

# 2. Save Whiteboard Sketch directly to Image Vault as HD PNG
@power_bp.route("/api/power/save_sketch", methods=["POST"])
def save_whiteboard_sketch():
    d = request.json
    img_data = d.get("image_base64", "")
    title = d.get("title", f"Architecture Sketch {datetime.now().strftime('%H:%M')}")
    if "," in img_data:
        img_data = img_data.split(",")[1]
    
    filename = f"sketch_{int(datetime.utcnow().timestamp())}.png"
    filepath = os.path.join(UPLOAD_DIR, filename)
    with open(filepath, "wb") as f:
        f.write(base64.b64decode(img_data))

    file_url = f"/static/uploads/{filename}"
    item = KnowledgeItem(
        title=title,
        category="Image",
        content="Created in Interactive Architecture Whiteboard Sketchpad",
        media_url=file_url,
        tags="whiteboard,architecture,diagram"
    )
    db.session.add(item)
    db.session.commit()
    return jsonify({"status": "saved", "url": file_url})

# 3. Full JSON Backup Restore Engine (1-Click Restore)
@power_bp.route("/api/power/restore_backup", methods=["POST"])
def restore_full_backup():
    if "file" not in request.files:
        return jsonify({"error": "No backup file provided"}), 400
    f = request.files["file"]
    data = json.load(f)
    restored_count = 0

    for k in data.get("knowledge", []):
        if not KnowledgeItem.query.filter_by(title=k.get("title")).first():
            db.session.add(KnowledgeItem(
                title=k.get("title", "Restored Note"),
                category=k.get("category", "Note"),
                content=k.get("content", ""),
                media_url=k.get("media_url", ""),
                tags=k.get("tags", "restored")
            ))
            restored_count += 1

    for st in data.get("startups", []):
        if not StartupIdea.query.filter_by(name=st.get("name")).first():
            db.session.add(StartupIdea(
                name=st.get("name", "Restored Startup"),
                description=st.get("description", ""),
                revenue_model=st.get("revenue_model", "Subscription"),
                stage=st.get("stage", "MVP"),
                feasibility_score=int(st.get("feasibility_score", 85)),
                progress=int(st.get("progress", 50))
            ))
            restored_count += 1

    db.session.commit()
    return jsonify({"status": "restored", "restored_items": restored_count})