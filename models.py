from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(50), default="Founder") # Founder, Co-Founder, Admin, Manager, Developer, etc.
    avatar_url = db.Column(db.String(500), default="https://ui-avatars.com/api/?name=Founder&background=7C3AED&color=fff")
    two_factor_enabled = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class KnowledgeItem(db.Model):
    __tablename__ = "knowledge_vault"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(80), nullable=False) # Note, Article, Blog, PDF, Course, Website, Research, Video, Image, Document
    content = db.Column(db.Text, nullable=False)
    media_url = db.Column(db.String(500), default="")
    tags = db.Column(db.String(255), default="general")
    is_favorite = db.Column(db.Boolean, default=False)
    is_archived = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ReferenceDesign(db.Model):
    __tablename__ = "reference_designs"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    ref_type = db.Column(db.String(80), default="Dashboard Reference") # Dashboard, UI, Wireframe, Screenshot, Website
    image_url = db.Column(db.String(500), nullable=False)
    extracted_palette = db.Column(db.String(200), default="#7C3AED, #0EA5E9, #10B981, #0F172A")
    notes = db.Column(db.Text, default="")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Problem(db.Model):
    __tablename__ = "problems"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    source = db.Column(db.String(100), nullable=False) # Play Store, App Store, YouTube, Reddit, Social Media, Customer, Observation
    root_cause = db.Column(db.Text, nullable=False)
    proposed_solution = db.Column(db.Text, default="")
    market_demand = db.Column(db.Integer, default=8) # 1-10
    competition_level = db.Column(db.String(50), default="Medium")
    revenue_potential = db.Column(db.String(100), default="$5M ARR")
    opportunity_score = db.Column(db.Integer, default=85)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class SolutionItem(db.Model):
    __tablename__ = "solutions"
    id = db.Column(db.Integer, primary_key=True)
    problem_title = db.Column(db.String(255), nullable=False)
    solution_title = db.Column(db.String(255), nullable=False)
    cost_estimate = db.Column(db.String(100), default="$1,500")
    benefits = db.Column(db.Text, default="")
    market_impact = db.Column(db.String(100), default="High")
    difficulty = db.Column(db.String(50), default="Medium")
    revenue_potential = db.Column(db.String(100), default="High")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class InnovationItem(db.Model):
    __tablename__ = "innovations"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(100), default="Technology") # Innovation, Technology, Research Paper, Future Trend, Discovery
    summary = db.Column(db.Text, nullable=False)
    opportunity_note = db.Column(db.Text, default="")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class StartupIdea(db.Model):
    __tablename__ = "startups"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    market = db.Column(db.String(120), default="Global B2B/B2C")
    industry = db.Column(db.String(100), default="SaaS / AI")
    revenue_model = db.Column(db.String(150), default="Tiered Subscription")
    competitors = db.Column(db.String(255), default="Notion, Linear, ClickUp")
    market_size = db.Column(db.String(100), default="$10B TAM")
    validation_status = db.Column(db.String(80), default="Validated")
    stage = db.Column(db.String(50), default="MVP") # Idea, Research, Validation, Planning, MVP, Development, Testing, Launch, Scaling
    priority = db.Column(db.String(50), default="High")
    feasibility_score = db.Column(db.Integer, default=90)
    progress = db.Column(db.Integer, default=65)
    time_spent_hours = db.Column(db.Integer, default=120)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ProjectTask(db.Model):
    __tablename__ = "project_tasks"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    project_name = db.Column(db.String(150), default="BIGKNOWLEDGE OS")
    subtasks_checklist = db.Column(db.Text, default="[]")
    status = db.Column(db.String(50), default="In Progress") # Todo, In Progress, Review, Completed
    kanban_stage = db.Column(db.String(50), default="Building") # Ideas, Researching, Planning, Building, Testing, Completed
    priority = db.Column(db.String(50), default="High")
    deadline = db.Column(db.String(50), default="2026-11-15")
    dependencies = db.Column(db.String(200), default="None")
    assignee = db.Column(db.String(100), default="Founder")

class RoadmapMilestone(db.Model):
    __tablename__ = "roadmaps"
    id = db.Column(db.Integer, primary_key=True)
    roadmap_type = db.Column(db.String(80), default="Startup Roadmap") # Startup Roadmap, Product Roadmap, Learning Roadmap
    title = db.Column(db.String(255), nullable=False)
    dependencies = db.Column(db.String(255), default="")
    deadline = db.Column(db.String(50), default="2026-12-31")
    progress = db.Column(db.Integer, default=50)

class JournalEntry(db.Model):
    __tablename__ = "journals"
    id = db.Column(db.Integer, primary_key=True)
    entry_type = db.Column(db.String(50), default="Founder Journal") # Founder Journal, Decision Journal
    category_tag = db.Column(db.String(80), default="Daily Work") # Daily Work, Thought, Lesson, Failure, Learning, Discovery, Decision
    title = db.Column(db.String(255), nullable=False)
    details = db.Column(db.Text, nullable=False)
    expected_outcome = db.Column(db.String(255), default="")
    actual_result = db.Column(db.String(255), default="")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class GoalHabit(db.Model):
    __tablename__ = "goals_habits"
    id = db.Column(db.Integer, primary_key=True)
    item_type = db.Column(db.String(50), default="Goal") # Life Goal, Yearly Goal, Monthly Goal, Weekly Goal, Daily Goal, Habit
    title = db.Column(db.String(255), nullable=False)
    streak_or_progress = db.Column(db.Integer, default=75)
    completed_today = db.Column(db.Boolean, default=True)

class OrganizationCRM(db.Model):
    __tablename__ = "org_crm"
    id = db.Column(db.Integer, primary_key=True)
    entity_type = db.Column(db.String(50), default="Team Member") # Team Member, Partner, Mentor, Investor, Candidate, Competitor, Meeting
    name = db.Column(db.String(150), nullable=False)
    role_or_segment = db.Column(db.String(100), default="Developer")
    department_or_company = db.Column(db.String(120), default="Core Engineering")
    details_or_strengths = db.Column(db.Text, default="")
    weaknesses_or_actions = db.Column(db.Text, default="")
    tasks_completed = db.Column(db.Integer, default=24)
    tasks_pending = db.Column(db.Integer, default=3)
    work_hours = db.Column(db.Integer, default=42)
    productivity_score = db.Column(db.Integer, default=95)
