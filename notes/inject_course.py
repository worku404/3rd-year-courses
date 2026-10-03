r"""
Course Content Injector for University 3rd-Year Courses
Location: C:\class\3rdYearCourse\notes\inject_course.py

Features:
- Injects 3rd-year university courses (e.g. ObjectOrientedProgramming) into Django.
- Strictly verifies all YouTube video URLs via YouTube oEmbed API (rejects dead/404 videos).
- Auto-syncs assets from notes/<Course>/assets to media/notes/<course_lower>/
- Auto-copies chapter PDFs from <Course>units/ to media/<Course>units/
- Fully idempotent: can be re-run safely without creating duplicate blocks.
- Supports CLI filters: e.g. python inject_course.py --oop u1

Usage:
  # Inject all 3rd-year courses and units:
  python inject_course.py

  # Inject specific unit:
  python inject_course.py --oop u1
  python inject_course.py --objectorientedprogramming u1
"""

import os
import sys
import json
import re
import shutil
import subprocess

# Ensure stdout supports UTF-8 on Windows terminal
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# ----------------- CONFIGURATION & DJANGO BOOTSTRAP -------------------------
NOTES_DIR = os.path.dirname(os.path.abspath(__file__))      # .../3rdYearCourse/notes
COURSE_ROOT = os.path.dirname(NOTES_DIR)                    # .../3rdYearCourse

# Early CLI parsing for bootstrap options
edu_dir_arg = None
settings_arg = None
instructor_arg = None

clean_argv = []
skip_next = False
for i, arg in enumerate(sys.argv[1:], start=1):
    if skip_next:
        skip_next = False
        continue
    if arg == "--edu-dir" and i < len(sys.argv) - 1:
        edu_dir_arg = sys.argv[i + 1]
        skip_next = True
    elif arg == "--settings" and i < len(sys.argv) - 1:
        settings_arg = sys.argv[i + 1]
        skip_next = True
    elif arg == "--instructor" and i < len(sys.argv) - 1:
        instructor_arg = sys.argv[i + 1]
        skip_next = True
    else:
        clean_argv.append(arg)

sys.argv = [sys.argv[0]] + clean_argv

# 1. Determine Edu Project Directory (Cross-Platform)
candidate_dirs = [
    edu_dir_arg,
    os.environ.get("EDU_DIR"),
    os.getcwd(),
    os.path.expanduser("~/smartLearning/worku-lms/edu"),
    os.path.expanduser("~/worku-lms/edu"),
    os.path.expanduser("~/edu"),
    "/home/azureuser/smartLearning/worku-lms/edu",
    "/home/azureuser/worku-lms/edu",
    "/var/www/smartLearning/worku-lms/edu",
    "/var/www/worku-lms/edu",
    os.path.abspath(os.path.join(COURSE_ROOT, "..", "worku-lms", "edu")),
    os.path.abspath(os.path.join(COURSE_ROOT, "..", "smartLearning", "worku-lms", "edu")),
    os.path.abspath(os.path.join(COURSE_ROOT, "..", "edu")),
    os.path.abspath(os.path.join(COURSE_ROOT, "..", "Downloads", "webdev", "Django_Projects", "e-learning", "edu")),
    r"C:\Users\hi\Downloads\webdev\Django_Projects\e-learning\edu",
]

EDU_PROJECT_DIR = None
for c in candidate_dirs:
    if c and (os.path.exists(os.path.join(c, "edu", "settings")) or os.path.exists(os.path.join(c, "manage.py"))):
        EDU_PROJECT_DIR = os.path.abspath(c)
        break

if not EDU_PROJECT_DIR:
    print("Error: Could not locate Django project root (containing 'edu/settings' or 'manage.py').")
    print("Please specify with --edu-dir <path> or set EDU_DIR environment variable.")
    sys.exit(1)

if EDU_PROJECT_DIR not in sys.path:
    sys.path.insert(0, EDU_PROJECT_DIR)

# 2. Determine Settings Module (Smart Production Default on Linux)
if settings_arg:
    settings_module = settings_arg
elif os.environ.get("DJANGO_SETTINGS_MODULE"):
    settings_module = os.environ.get("DJANGO_SETTINGS_MODULE")
elif not sys.platform.startswith("win"):
    # On Linux servers (Azure VM, Ubuntu, etc.), default to production settings
    settings_module = "edu.settings.prod"
else:
    settings_module = "edu.settings.local"

os.environ["DJANGO_SETTINGS_MODULE"] = settings_module

# 3. Determine Instructor Username
INSTRUCTOR_USERNAME = instructor_arg or os.environ.get("INSTRUCTOR_USERNAME", "gold")

import django
django.setup()

from django.db import transaction
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from courses.models import Subject, Course, Module, Content, Text, File

PLACEHOLDER = "REPLACE_ME"
TOKEN_RE = re.compile(r"\{\{\s*media:\s*([A-Za-z0-9_\-]+)\s*\}\}")


def load_json(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def verify_youtube_video(url):
    """
    Verifies that a YouTube video is currently LIVE, public, and active via oEmbed.
    Includes retry logic to handle transient network / DNS fluctuations.
    100% cross-platform: works on Windows, Linux, and macOS.
    Returns (True, title) or (False, error).
    """
    import time
    import urllib.parse
    import urllib.request
    encoded_url = urllib.parse.quote(url, safe="")
    endpoint = f"https://www.youtube.com/oembed?url={encoded_url}&format=json"

    for attempt in range(3):
        # 1. Primary: Python standard library urllib (fast, reliable, cross-platform)
        try:
            req = urllib.request.Request(
                endpoint,
                headers={"User-Agent": "Mozilla/5.0 (compatible; EduInjector/1.0)"}
            )
            with urllib.request.urlopen(req, timeout=12) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return True, data.get("title", "")
        except urllib.error.HTTPError as he:
            if he.code in (404, 401, 403):
                return False, f"HTTP {he.code} Video Unavailable"
        except Exception:
            pass

        # 2. Secondary: System curl fallback
        try:
            curl_bin = "curl.exe" if sys.platform.startswith("win") else "curl"
            cmd = [curl_bin, "-s"]
            if sys.platform.startswith("win"):
                cmd.append("--ssl-no-revoke")
            cmd.extend(["-A", "Mozilla/5.0", endpoint])
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=12)
            out = res.stdout.strip()
            if "Not Found" in out:
                return False, "404 Video Not Found / Unavailable"
            if out.startswith("{"):
                data = json.loads(out)
                return True, data.get("title", "")
        except Exception:
            pass

        if attempt < 2:
            time.sleep(1.0)
    return False, "Verification timeout or rate limit exceeded after 3 attempts"


def sync_course_assets(course_folder_name):
    """
    Auto-syncs image assets from notes/<Course>/assets to settings.MEDIA_ROOT/notes/<course_lower>/
    """
    course_dir = os.path.join(NOTES_DIR, course_folder_name)
    assets_dir = os.path.join(course_dir, "assets")
    if not os.path.isdir(assets_dir):
        return 0
    target_dir = os.path.join(settings.MEDIA_ROOT, "notes", course_folder_name.lower())
    os.makedirs(target_dir, exist_ok=True)
    copied = 0
    for fname in os.listdir(assets_dir):
        src = os.path.join(assets_dir, fname)
        dst = os.path.join(target_dir, fname)
        if os.path.isfile(src) and (not os.path.exists(dst) or os.path.getmtime(src) > os.path.getmtime(dst)):
            shutil.copy2(src, dst)
            copied += 1
    return copied


def resolve_pdf_path(manifest):
    explicit = manifest.get("pdf")
    if explicit:
        p = explicit if os.path.isabs(explicit) else os.path.join(COURSE_ROOT, explicit)
        return p if os.path.exists(p) else None
    return None


def stitch_media(md, media_map, lesson_name, pending_media):
    def repl(match):
        mid = match.group(1)
        spec = media_map.get(mid)
        if not spec:
            pending_media.append(f"{lesson_name}:{mid} (no entry in meta.json 'media')")
            return ""
        url = (spec.get("url") or "").strip()
        if not url or PLACEHOLDER in url:
            pending_media.append(f"{lesson_name}:{mid} ({spec.get('type','media')} url still {PLACEHOLDER})")
            return ""
        
        # Rigorous live verification for YouTube videos
        if spec.get("type") == "video":
            is_live, info = verify_youtube_video(url)
            if not is_live:
                pending_media.append(f"{lesson_name}:{mid} (DEAD VIDEO LINK: {url} -> {info})")
                return ""
            return url

        if spec.get("type") == "image":
            alt = spec.get("alt") or spec.get("note") or mid
            return f"![{alt}]({url})"
        return url

    stitched = TOKEN_RE.sub(repl, md)
    stitched = re.sub(r"\n{3,}", "\n\n", stitched)
    return stitched


def put_content(module, item, order):
    ct = ContentType.objects.get_for_model(type(item))
    content = Content.objects.filter(module=module, content_type=ct, object_id=item.pk).first()
    created = False
    if content is None:
        content = Content(module=module, content_type=ct, object_id=item.pk)
        created = True
    if content.order != order:
        content.order = order
    content.save()
    return created


def upsert_text(owner, title, md):
    md = md.replace("\x00", "")
    item, _ = Text.objects.get_or_create(owner=owner, title=title, defaults={"content": md})
    if item.content != md:
        item.content = md
        item.save(update_fields=["content"])
    return item


def upsert_pdf_file(owner, title, abs_path):
    rel = os.path.relpath(abs_path, COURSE_ROOT).replace("\\", "/")
    dest = os.path.join(settings.MEDIA_ROOT, rel)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    if not os.path.exists(dest) or os.path.getmtime(abs_path) > os.path.getmtime(dest):
        shutil.copy2(abs_path, dest)
    item, created = File.objects.get_or_create(owner=owner, title=title, defaults={"file": rel})
    if not created and item.file.name != rel:
        item.file.name = rel
        item.save(update_fields=["file"])
    return item


def inject_unit(course_folder, unit_folder, owner):
    course_dir = os.path.join(NOTES_DIR, course_folder)
    unit_dir = os.path.join(course_dir, unit_folder)
    course_json = os.path.join(course_dir, "course.json")
    manifest_json = os.path.join(unit_dir, "manifest.json")

    if not os.path.exists(course_json):
        return False, f"Missing course.json in {course_dir}"
    if not os.path.exists(manifest_json):
        return False, f"Missing manifest.json in {unit_dir}"

    course_meta = load_json(course_json)
    manifest = load_json(manifest_json)
    subject_title = course_meta["subject"]["title"]

    pending_media = []
    skipped = []
    created_blocks = 0
    order = 0

    with transaction.atomic():
        subject, _ = Subject.objects.get_or_create(
            title=subject_title,
            defaults={"slug": course_meta["subject"]["slug"]},
        )
        course, _ = Course.objects.get_or_create(
            owner=owner,
            subject=subject,
            slug=course_meta["course"]["slug"],
            defaults={
                "title": course_meta["course"]["title"],
                "overview": course_meta["course"].get("overview", ""),
            },
        )
        module, _ = Module.objects.get_or_create(
            course=course,
            title=manifest["moduleTitle"],
            defaults={"description": manifest.get("moduleDescription", "")},
        )

        # 1) Chapter PDF
        pdf_path = resolve_pdf_path(manifest)
        if pdf_path:
            pdf_item = upsert_pdf_file(owner, f"{manifest['moduleTitle']} — Chapter PDF", pdf_path)
            if put_content(module, pdf_item, order):
                created_blocks += 1
            order += 1
        else:
            skipped.append("chapter PDF (not found)")

        # 2) Lesson text blocks
        for lesson_name in manifest.get("lessons", []):
            meta_path = os.path.join(unit_dir, f"{lesson_name}.meta.json")
            if not os.path.exists(meta_path):
                skipped.append(f"missing {lesson_name}.meta.json")
                continue
            meta = load_json(meta_path)
            media_map = meta.get("media", {})
            lesson_file = os.path.join(unit_dir, meta.get("file", f"{lesson_name}.md"))
            if not os.path.exists(lesson_file):
                skipped.append(f"missing {lesson_file}")
                continue
            raw = open(lesson_file, encoding="utf-8").read()
            md = stitch_media(raw, media_map, lesson_name, pending_media)
            item = upsert_text(owner, meta.get("title", lesson_name), md)
            if put_content(module, item, order):
                created_blocks += 1
            order += 1

    return True, {
        "subject": subject.title,
        "course": course.title,
        "module": module.title,
        "module_id": module.id,
        "blocks": order,
        "created_blocks": created_blocks,
        "pending_media": pending_media,
        "skipped": skipped,
    }


def parse_cli_args(argv, available_courses):
    alias_map = {
        "oop": "ObjectOrientedProgramming",
        "java": "ObjectOrientedProgramming",
        "dsa": "DataStructuresAndAlgorithms",
        "coa": "ComputerOrganizationAndArchitecture",
        "ip": "InternetProgramming",
        "sam": "SystemAnalysisAndModelling",
    }
    for c in available_courses:
        alias_map[c.lower()] = c

    if not argv:
        return {c: None for c in sorted(available_courses)}

    plan = {}
    current_course = None

    for arg in argv:
        raw = arg.strip()
        if raw in ("-h", "--help"):
            print(__doc__)
            sys.exit(0)

        clean = raw.lstrip("-").lower()
        if clean in alias_map:
            current_course = alias_map[clean]
            if current_course not in plan:
                plan[current_course] = []
        elif current_course:
            if "-" in clean and not clean.startswith("-"):
                parts = clean.split("-")
                p1 = re.sub(r"[^\d]", "", parts[0])
                p2 = re.sub(r"[^\d]", "", parts[1])
                if p1.isdigit() and p2.isdigit():
                    start, end = int(p1), int(p2)
                    for n in range(min(start, end), max(start, end) + 1):
                        plan[current_course].append(f"unit{n}")
                    continue

            u_num = re.sub(r"[^\d]", "", clean)
            if u_num:
                plan[current_course].append(f"unit{u_num}")
            else:
                plan[current_course].append(clean)
        else:
            if raw.lower() in alias_map:
                current_course = alias_map[raw.lower()]
                if current_course not in plan:
                    plan[current_course] = []

    for s in plan:
        if not plan[s]:
            plan[s] = None
        else:
            plan[s] = sorted(list(set(plan[s])), key=lambda x: int(re.sub(r"[^\d]", "", x) or 0))

    return plan


def main():
    available_courses = [
        d for d in os.listdir(NOTES_DIR)
        if os.path.isdir(os.path.join(NOTES_DIR, d)) and not d.startswith(".") and d != "__pycache__"
    ]

    plan = parse_cli_args(sys.argv[1:], available_courses)

    if not plan:
        print("No matching courses found for the provided arguments.")
        print(f"Available courses: {', '.join(sorted(available_courses))}")
        return

    try:
        owner = User.objects.get(username=INSTRUCTOR_USERNAME)
    except User.DoesNotExist:
        owner = User.objects.filter(is_superuser=True).first()
        if not owner:
            print(f"Error: Instructor user '{INSTRUCTOR_USERNAME}' not found and no superuser exists.")
            return
        print(f"Notice: User '{INSTRUCTOR_USERNAME}' not found. Falling back to superuser '{owner.username}' (ID: {owner.id}).")

    print("=" * 70)
    print("       3RD-YEAR UNIVERSITY COURSE INJECTOR (EDUCAMIND)")
    print(f"Target courses  : {', '.join(plan.keys())}")
    print(f"Content Owner   : {owner.username} (ID: {owner.id})")
    print(f"Django Settings : {os.environ.get('DJANGO_SETTINGS_MODULE')}")
    print(f"Media Root      : {settings.MEDIA_ROOT}")
    print("=" * 70)

    total_units_processed = 0
    total_blocks_created = 0
    total_pending_media = 0

    for course_folder, units_to_run in plan.items():
        course_dir = os.path.join(NOTES_DIR, course_folder)
        if not os.path.isdir(course_dir):
            continue

        # Auto-sync assets for this course
        synced_assets = sync_course_assets(course_folder)

        # Find available unit folders
        available_units = [
            u for u in os.listdir(course_dir)
            if os.path.isdir(os.path.join(course_dir, u)) and u.startswith("unit")
        ]
        available_units = sorted(available_units, key=lambda x: int(re.sub(r"[^\d]", "", x) or 0))

        if units_to_run is None:
            target_units = available_units
        else:
            target_units = [u for u in units_to_run if u in available_units]

        if not target_units:
            print(f"\n[{course_folder}] No matching units found to inject.")
            continue

        print(f"\n>>> [{course_folder.upper()}] Injecting {len(target_units)} unit(s)...")
        if synced_assets > 0:
            print(f"  [MEDIA] Synchronized {synced_assets} asset image(s) to media/notes/{course_folder.lower()}/")

        for u in target_units:
            success, res = inject_unit(course_folder, u, owner)
            total_units_processed += 1
            if not success:
                print(f"  [ERROR] {course_folder}/{u}: {res}")
                continue

            created = res["created_blocks"]
            total_blocks_created += created
            pending = len(res["pending_media"])
            total_pending_media += pending

            status_str = f"{res['blocks']} blocks ({created} newly created)"
            if pending > 0:
                status_str += f", {pending} pending media"
            print(f"  [OK] {u}: {res['module']} [ID: {res['module_id']}] -> {status_str}")

            if res["pending_media"]:
                for pm in res["pending_media"]:
                    print(f"       ! pending: {pm}")

    print("\n" + "=" * 70)
    print(f"ALL DONE: Processed {total_units_processed} unit(s) across {len(plan)} course(s).")
    print(f"Total new Content blocks created: {total_blocks_created}")
    print(f"Total pending media items remaining: {total_pending_media}")
    print("=" * 70)


if __name__ == "__main__":
    main()
