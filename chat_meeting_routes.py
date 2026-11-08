import json
from datetime import datetime
from flask import Blueprint, request, jsonify
from models import db, KeyValueStore, ProjectTask, KnowledgeItem

chat_bp = Blueprint("chat_bp", __name__)

CHAT_STORE_KEY = "enterprise_chat_meetings"

def safe_int(val, default=0):
    try:
        return int(val)
    except (ValueError, TypeError):
        return default

def get_initial_chat_data():
    return {
        "channels": [
            {"id": "core-architecture", "name": "core-architecture", "type": "public", "topic": "System Design, Flask APIs & Database Scaling"},
            {"id": "b2conecter-dev", "name": "b2conecter-dev", "type": "public", "topic": "Hyperlocal Multi-Vendor Storefront & Billing"},
            {"id": "honey-chain-iot", "name": "honey-chain-iot", "type": "public", "topic": "SIH Smart Beekeeping & Blockchain Ledger"},
            {"id": "announcements", "name": "announcements", "type": "public", "topic": "Important Founder & Milestone Broadcasts"}
        ],
        "messages": [
            {
                "id": 1001,
                "channel": "core-architecture",
                "sender": "Mr. Vijay Mistry",
                "role": "Founder & CTO",
                "avatar": "VM",
                "text": "Welcome to BIGKNOWLEDGE Enterprise Team Hub! Yahan aap Code, Files, Voice Notes, Polls aur Website previews share kar sakte hain.",
                "msg_type": "text",
                "media_url": "",
                "link_url": "https://github.com",
                "code_snippet": "",
                "poll_data": None,
                "pinned": True,
                "reactions": {"🔥": 3, "🚀": 4, "👍": 2},
                "timestamp": datetime.now().strftime("%I:%M %p | %d %b")
            },
            {
                "id": 1002,
                "channel": "core-architecture",
                "sender": "AI Co-Founder",
                "role": "System Bot",
                "avatar": "AI",
                "text": "PostgreSQL + SQLite fallback aur Cloudinary media pipeline 100% active hai. Kisi bhi message ko 'Convert to Task' button se sidha Kanban Board me bhej sakte hain.",
                "msg_type": "code",
                "media_url": "",
                "link_url": "",
                "code_snippet": "@app.route('/api/chat/bootstrap')\ndef status():\n    return {'engine': 'BIGKNOWLEDGE_PRO', 'uptime': '99.99%'}",
                "poll_data": None,
                "pinned": False,
                "reactions": {"🚀": 2},
                "timestamp": datetime.now().strftime("%I:%M %p | %d %b")
            }
        ],
        "meetings": [
            {
                "id": 501,
                "title": "B2Conecter & BIGKNOWLEDGE Sprint Architecture Sync",
                "date": "2026-11-08",
                "time": "10:30 AM",
                "host": "Mr. Vijay Mistry",
                "attendees": "Founder, Core Dev, UI Lead",
                "meet_link": "https://meet.google.com/new",
                "status": "Scheduled",
                "agenda": "Review subscription tiers (₹199-₹799), database indexing, and UI polish.",
                "notes": "1. Multi-vendor onboarding flow finalized.\n2. Kanban & Knowledge Graph drag-and-drop verified.",
                "decisions": "Use Database KV Store + JSON backup for zero data loss.",
                "action_items": [
                    {"id": 1, "task": "Deploy updated build to Render cloud", "owner": "Mr. Vijay Mistry", "done": True},
                    {"id": 2, "task": "Test mobile responsiveness on 5G", "owner": "UI Lead", "done": False}
                ]
            }
        ]
    }

def load_chat_db():
    record = KeyValueStore.query.get(CHAT_STORE_KEY)
    if not record:
        initial = get_initial_chat_data()
        save_chat_db(initial)
        return initial
    try:
        return json.loads(record.value_json)
    except Exception:
        return get_initial_chat_data()

def save_chat_db(data):
    record = KeyValueStore.query.get(CHAT_STORE_KEY)
    if not record:
        record = KeyValueStore(key=CHAT_STORE_KEY, value_json=json.dumps(data))
        db.session.add(record)
    else:
        record.value_json = json.dumps(data)
    db.session.commit()

@chat_bp.route("/api/chat/bootstrap", methods=["GET"])
def get_chat_bootstrap():
    return jsonify(load_chat_db())

@chat_bp.route("/api/chat/channels", methods=["POST", "DELETE"])
def manage_channels():
    store = load_chat_db()
    if request.method == "DELETE":
        cid = request.args.get("id")
        if cid and cid != "core-architecture":
            store["channels"] = [c for c in store["channels"] if c["id"] != cid]
            store["messages"] = [m for m in store["messages"] if m["channel"] != cid]
            save_chat_db(store)
        return jsonify({"status": "deleted", "channels": store["channels"]})

    d = request.get_json(silent=True) or {}
    raw_name = (d.get("name") or "new-channel").lower().strip().replace(" ", "-")
    if not any(c["id"] == raw_name for c in store["channels"]):
        store["channels"].append({
            "id": raw_name,
            "name": raw_name,
            "type": d.get("type", "public"),
            "topic": d.get("topic", "Team Discussion & Execution")
        })
        save_chat_db(store)
    return jsonify({"status": "created", "channels": store["channels"]})

@chat_bp.route("/api/chat/messages", methods=["POST", "DELETE"])
def manage_messages():
    store = load_chat_db()
    if request.method == "DELETE":
        mid = safe_int(request.args.get("id"), 0)
        store["messages"] = [m for m in store["messages"] if m["id"] != mid]
        save_chat_db(store)
        return jsonify({"status": "deleted"})

    d = request.get_json(silent=True) or {}
    sender_name = d.get("sender", "Mr. Vijay Mistry")
    avatar_initials = "".join([w[0] for w in sender_name.split()[:2]]).upper() or "VM"

    new_msg = {
        "id": int(datetime.utcnow().timestamp() * 1000),
        "channel": d.get("channel", "core-architecture"),
        "sender": sender_name,
        "role": d.get("role", "Founder"),
        "avatar": avatar_initials,
        "text": d.get("text", ""),
        "msg_type": d.get("msg_type", "text"),
        "media_url": d.get("media_url", ""),
        "link_url": d.get("link_url", ""),
        "code_snippet": d.get("code_snippet", ""),
        "poll_data": d.get("poll_data", None),
        "pinned": False,
        "reactions": {},
        "timestamp": datetime.now().strftime("%I:%M %p | %d %b")
    }
    store["messages"].append(new_msg)

    user_text = (d.get("text") or "").lower()
    if "@ai" in user_text or user_text.startswith("/ai"):
        bot_reply = {
            "id": int(datetime.utcnow().timestamp() * 1000) + 1,
            "channel": new_msg["channel"],
            "sender": "JARVIS AI Bot",
            "role": "Neural Assistant",
            "avatar": "AI",
            "text": f"🤖 Maine aapka message analyze kiya: '{d.get('text')}'. Kya main isko Kanban Task ya Meeting Agenda me convert kar doon?",
            "msg_type": "text",
            "media_url": "",
            "link_url": "",
            "code_snippet": "",
            "poll_data": None,
            "pinned": False,
            "reactions": {"⚡": 1},
            "timestamp": datetime.now().strftime("%I:%M %p | %d %b")
        }
        store["messages"].append(bot_reply)

    save_chat_db(store)
    return jsonify({"status": "sent", "message": new_msg})

@chat_bp.route("/api/chat/interact", methods=["POST"])
def interact_message():
    store = load_chat_db()
    d = request.get_json(silent=True) or {}
    mid = safe_int(d.get("id"), 0)
    action = d.get("action")

    for m in store["messages"]:
        if m["id"] == mid:
            if action == "react":
                emoji = d.get("emoji", "🔥")
                m.setdefault("reactions", {})
                m["reactions"][emoji] = m["reactions"].get(emoji, 0) + 1
            elif action == "pin":
                m["pinned"] = not m.get("pinned", False)
            elif action == "vote" and m.get("poll_data"):
                opt_idx = safe_int(d.get("option_index"), 0)
                options = m["poll_data"].get("options", [])
                if 0 <= opt_idx < len(options):
                    options[opt_idx]["votes"] = safe_int(options[opt_idx].get("votes"), 0) + 1
            break

    save_chat_db(store)
    return jsonify({"status": "updated"})

@chat_bp.route("/api/chat/convert_to_task", methods=["POST"])
def convert_chat_to_task():
    d = request.get_json(silent=True) or {}
    t = ProjectTask(
        title=(d.get("title") or "Team Chat Action Item")[:240],
        project_name=d.get("project_name", "Team Collaboration"),
        status="Todo",
        kanban_stage="Planning",
        priority="High",
        deadline=datetime.now().strftime("%Y-%m-%d"),
        assignee=d.get("assignee", "Mr. Vijay Mistry")
    )
    db.session.add(t)
    db.session.commit()
    return jsonify({"status": "converted", "task_id": t.id})

@chat_bp.route("/api/chat/meetings", methods=["POST", "PUT", "DELETE"])
def manage_meetings():
    store = load_chat_db()
    if request.method == "DELETE":
        mt_id = safe_int(request.args.get("id"), 0)
        store["meetings"] = [m for m in store["meetings"] if m["id"] != mt_id]
        save_chat_db(store)
        return jsonify({"status": "deleted"})

    d = request.get_json(silent=True) or {}
    if request.method == "POST":
        new_mt = {
            "id": int(datetime.utcnow().timestamp() * 1000),
            "title": d.get("title", "Startup Strategy Sync"),
            "date": d.get("date", datetime.now().strftime("%Y-%m-%d")),
            "time": d.get("time", "11:00 AM"),
            "host": d.get("host", "Mr. Vijay Mistry"),
            "attendees": d.get("attendees", "Core Team"),
            "meet_link": d.get("meet_link", "https://meet.google.com/new"),
            "status": d.get("status", "Scheduled"),
            "agenda": d.get("agenda", ""),
            "notes": d.get("notes", ""),
            "decisions": d.get("decisions", ""),
            "action_items": d.get("action_items", [])
        }
        store["meetings"].insert(0, new_mt)
        save_chat_db(store)
        return jsonify({"status": "created", "meeting": new_mt})

    if request.method == "PUT":
        mt_id = safe_int(d.get("id"), 0)
        for m in store["meetings"]:
            if m["id"] == mt_id:
                for key in ["title", "status", "agenda", "notes", "decisions", "action_items", "meet_link", "date", "time", "attendees"]:
                    if key in d:
                        m[key] = d[key]
                if d.get("save_to_vault"):
                    kv = KnowledgeItem(
                        title=f"Meeting Minutes: {m['title']} ({m['date']})",
                        category="Note",
                        content=f"Attendees: {m['attendees']}\n\nAgenda:\n{m['agenda']}\n\nNotes:\n{m['notes']}\n\nDecisions:\n{m['decisions']}",
                        tags="meeting,minutes,decisions"
                    )
                    db.session.add(kv)
                    db.session.commit()
                break
        save_chat_db(store)
        return jsonify({"status": "updated"})