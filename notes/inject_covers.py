#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Inject Course Cover Images & Set Difficulty to Advanced
For 3rd-Year University Software Engineering Courses.
Works locally on Windows and remotely in Docker containers (/code/edu).
"""

import os
import sys
import shutil

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
COURSE_ROOT = os.path.dirname(SCRIPT_DIR)
COVERS_DIR = os.path.join(COURSE_ROOT, "course_covers")

edu_dir_arg = None
settings_arg = None

for i, arg in enumerate(sys.argv[1:], start=1):
    if arg == "--edu-dir" and i < len(sys.argv) - 1:
        edu_dir_arg = sys.argv[i + 1]
    elif arg == "--settings" and i < len(sys.argv) - 1:
        settings_arg = sys.argv[i + 1]

candidate_dirs = [
    edu_dir_arg,
    os.environ.get("EDU_DIR"),
    os.getcwd(),
    os.path.join(os.getcwd(), "edu"),
    "/code/edu",
    "/code",
    "/app/edu",
    "/app",
    os.path.expanduser("~/smartLearning/worku-lms/edu"),
    os.path.expanduser("~/worku-lms/edu"),
    os.path.abspath(os.path.join(COURSE_ROOT, "..")),
    os.path.abspath(os.path.join(COURSE_ROOT, "..", "..")),
    r"C:\Users\hi\Downloads\webdev\Django_Projects\e-learning\edu",
]

EDU_PROJECT_DIR = None
for c in candidate_dirs:
    if c and (os.path.exists(os.path.join(c, "edu", "settings")) or os.path.exists(os.path.join(c, "manage.py"))):
        EDU_PROJECT_DIR = os.path.abspath(c)
        break

if not EDU_PROJECT_DIR:
    print("Error: Could not locate Django project root.")
    print("Please specify with --edu-dir <path>")
    sys.exit(1)

if EDU_PROJECT_DIR not in sys.path:
    sys.path.insert(0, EDU_PROJECT_DIR)

if settings_arg:
    settings_module = settings_arg
elif os.environ.get("DJANGO_SETTINGS_MODULE"):
    settings_module = os.environ.get("DJANGO_SETTINGS_MODULE")
elif not sys.platform.startswith("win"):
    settings_module = "edu.settings.prod"
else:
    settings_module = "edu.settings.local"

os.environ["DJANGO_SETTINGS_MODULE"] = settings_module

import django
django.setup()

from django.conf import settings
from courses.models import Course

COURSES_MAP = {
    "data-structures-and-algorithms": {
        "cover_file": "dsa_cover.jpg",
        "title": "Data Structures & Algorithms"
    },
    "object-oriented-programming-java": {
        "cover_file": "oop_cover.jpg",
        "title": "Object-Oriented Programming (Java)"
    },
    "internet-programming": {
        "cover_file": "ip_cover.jpg",
        "title": "Internet Programming"
    },
    "computer-organization-and-architecture": {
        "cover_file": "coa_cover.jpg",
        "title": "Computer Organization & Architecture"
    },
    "system-analysis-and-modelling": {
        "cover_file": "sam_cover.jpg",
        "title": "System Analysis and Modelling"
    },
}

def main():
    print("=" * 70)
    print("         COURSE COVER INJECTOR (EDUCAMIND 3RD-YEAR)")
    print(f"Django Settings : {settings_module}")
    print(f"Media Root      : {settings.MEDIA_ROOT}")
    print("=" * 70)

    rel_media_folder = os.path.join("courses", "images", "2026", "10", "03")
    target_disk_folder = os.path.join(settings.MEDIA_ROOT, rel_media_folder)
    os.makedirs(target_disk_folder, exist_ok=True)

    updated_count = 0

    for slug, meta in COURSES_MAP.items():
        src_path = os.path.join(COVERS_DIR, meta["cover_file"])
        if not os.path.exists(src_path):
            print(f"[WARN] Cover file not found for {slug}: {src_path}")
            continue

        dest_filename = f"{slug}_cover.jpg"
        dest_disk_path = os.path.join(target_disk_folder, dest_filename)
        shutil.copy2(src_path, dest_disk_path)

        db_image_rel_path = f"courses/images/2026/10/03/{dest_filename}"

        try:
            course = Course.objects.get(slug=slug)
            course.image = db_image_rel_path
            course.difficulty = "advanced"
            course.save(update_fields=["image", "difficulty"])
            print(f"[OK] Updated Course [{course.id}]: {course.title}")
            print(f"     -> Image: {db_image_rel_path}")
            print(f"     -> Difficulty: {course.difficulty.upper()}")
            updated_count += 1
        except Course.DoesNotExist:
            print(f"[ERROR] Course not found with slug: {slug}")

    print("\n" + "=" * 70)
    print(f"SUCCESS: Successfully updated {updated_count} / {len(COURSES_MAP)} courses with custom covers!")
    print("=" * 70)

if __name__ == "__main__":
    main()
