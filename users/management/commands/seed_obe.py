"""
OBE Dataset Seeder
==================
Generates a complete Outcome-Based Education dataset:
  - 5 Programs (BSCS, BSIT, BSSE, BSDS, BSCY)
  - 50 Courses (10 per program, some shared across programs)
  - 8–12 PLOs per program (weightage sum = 100)
  - 4–5 CLOs per course (weightage sum = 100)
  - CLO→PLO mappings (each course maps to 3–5 PLOs per program)

Usage:
    python manage.py seed_obe
    python manage.py seed_obe --flush   # clears existing OBE data first
"""

import random

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from courses.models.course import Course
from outcomes.models.clo import CourseLearningOutcome
from outcomes.models.mapping import PloCloMapping
from outcomes.models.plo import ProgramLearningOutcome
from programs.models.program import Program

User = get_user_model()

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def weights_summing_to(n, total=100):
    """
    Return a list of *n* positive integers that sum to exactly *total*.
    Requires n >= 1 and total >= n (each part is at least 1).
    """
    if n == 1:
        return [total]
    cuts = sorted(random.sample(range(1, total), n - 1))
    return [cuts[0]] + [cuts[i] - cuts[i - 1] for i in range(1, n - 1)] + [total - cuts[-1]]


# ---------------------------------------------------------------------------
# Static seed data
# ---------------------------------------------------------------------------

PROGRAMS = [
    ("Bachelor of Computer Science",    "BSCS"),
    ("Bachelor of Information Technology", "BSIT"),
    ("Bachelor of Software Engineering", "BSSE"),
    ("Bachelor of Data Science",        "BSDS"),
    ("Bachelor of Cyber Security",      "BSCY"),
]

# 10 unique courses per program.
# credit_hours max = 4 (model validator); FYP courses use 4.
COURSES_BY_PROGRAM = {
    "BSCS": [
        ("CS101", "Introduction to Programming",          3),
        ("CS102", "Object-Oriented Programming",          3),
        ("CS201", "Data Structures and Algorithms",       3),
        ("CS202", "Computer Organization and Architecture", 3),
        ("CS301", "Operating Systems",                    3),
        ("CS302", "Database Management Systems",          3),
        ("CS401", "Software Engineering",                 3),
        ("CS402", "Artificial Intelligence",              3),
        ("CS403", "Computer Networks",                    3),
        ("CS499", "Final Year Project (CS)",              4),
    ],
    "BSIT": [
        ("IT101", "Fundamentals of Information Technology", 3),
        ("IT102", "Web Technologies and Development",      3),
        ("IT201", "Database Administration",               3),
        ("IT202", "Network Administration and Management", 3),
        ("IT301", "System Analysis and Design",            3),
        ("IT302", "IT Project Management",                 3),
        ("IT401", "Cloud Computing",                       3),
        ("IT402", "Information Security Fundamentals",     3),
        ("IT403", "Enterprise Resource Planning",          3),
        ("IT499", "Final Year Project (IT)",               4),
    ],
    "BSSE": [
        ("SE101", "Programming Fundamentals",              3),
        ("SE102", "Software Requirements Engineering",     3),
        ("SE201", "Software Design and Architecture",      3),
        ("SE202", "Agile and Scrum Methodologies",         3),
        ("SE301", "Software Testing and Quality Assurance", 3),
        ("SE302", "DevOps and Continuous Integration",     3),
        ("SE401", "Software Project Management",           3),
        ("SE402", "Distributed Systems",                   3),
        ("SE403", "Human-Computer Interaction",            3),
        ("SE499", "Final Year Project (SE)",               4),
    ],
    "BSDS": [
        ("DS101", "Introduction to Data Science",          3),
        ("DS102", "Statistical Methods for Data Science",  3),
        ("DS201", "Machine Learning Fundamentals",         3),
        ("DS202", "Data Mining and Warehousing",           3),
        ("DS301", "Big Data Analytics",                    3),
        ("DS302", "Deep Learning and Neural Networks",     3),
        ("DS401", "Natural Language Processing",           3),
        ("DS402", "Data Visualization and Reporting",      3),
        ("DS403", "Applied ML in Production",              3),
        ("DS499", "Final Year Project (DS)",               4),
    ],
    "BSCY": [
        ("CY101", "Introduction to Cybersecurity",         3),
        ("CY102", "Cryptography and Network Security",     3),
        ("CY201", "Ethical Hacking and Penetration Testing", 3),
        ("CY202", "Digital Forensics",                     3),
        ("CY301", "Malware Analysis and Reverse Engineering", 3),
        ("CY302", "Security Operations and Monitoring",    3),
        ("CY401", "Incident Response and Management",      3),
        ("CY402", "Cloud Security and Compliance",         3),
        ("CY403", "Secure Software Development",           3),
        ("CY499", "Final Year Project (CY)",               4),
    ],
}

# Shared courses that belong to multiple programs
SHARED_COURSES = [
    ("GEN101", "Technical Communication Skills",   3),
    ("GEN102", "Professional Ethics and Society",  3),
    ("MATH101", "Calculus and Linear Algebra",     3),
    ("MATH102", "Discrete Mathematics",            3),
    ("STAT101", "Probability and Statistics",      3),
]

# Each shared course is assigned to a subset of programs
SHARED_ASSIGNMENTS = {
    "GEN101":  ["BSCS", "BSIT", "BSSE"],
    "GEN102":  ["BSDS", "BSCY", "BSSE"],
    "MATH101": ["BSCS", "BSDS", "BSSE"],
    "MATH102": ["BSCS", "BSCY"],
    "STAT101": ["BSDS", "BSIT", "BSCY"],
}

# ---------------------------------------------------------------------------
# PLO data: (number, heading, description) per program (8–12 PLOs each)
# ---------------------------------------------------------------------------

PLO_DATA = {
    "BSCS": [
        (1,  "Engineering Knowledge",
             "Apply knowledge of mathematics, algorithms, and computer science fundamentals to solve complex computing problems."),
        (2,  "Problem Analysis",
             "Identify, formulate, and analyze complex computing problems reaching substantiated conclusions using first principles."),
        (3,  "Design and Development",
             "Design software solutions, systems, and components that meet specified computing needs with appropriate consideration for constraints."),
        (4,  "Investigation",
             "Conduct investigations of complex computing problems using research-based knowledge and experimental methods."),
        (5,  "Modern Tool Usage",
             "Select and apply appropriate programming tools, IDEs, frameworks, and platforms to computing activities."),
        (6,  "Ethics and Professionalism",
             "Apply ethical principles and commit to professional responsibilities in computing and software practice."),
        (7,  "Teamwork",
             "Function effectively as an individual and as a member or leader in diverse software development teams."),
        (8,  "Communication",
             "Communicate effectively on complex computing activities with technical and non-technical audiences."),
        (9,  "Project Management",
             "Demonstrate knowledge of project management and delivery principles to manage computing projects."),
        (10, "Lifelong Learning",
             "Recognize the need for and engage in independent and life-long learning in computing and technology."),
    ],
    "BSIT": [
        (1,  "IT Fundamentals",
             "Apply core IT knowledge encompassing hardware, software, and infrastructure management."),
        (2,  "Systems Analysis",
             "Analyze, model, and design information systems to meet organizational and user requirements."),
        (3,  "Network Administration",
             "Configure, manage, and troubleshoot enterprise network infrastructure effectively."),
        (4,  "Database Management",
             "Design, implement, and manage relational and non-relational database systems for enterprise use."),
        (5,  "Cloud and Virtualization",
             "Deploy, manage, and optimize cloud-based services and virtualized infrastructure."),
        (6,  "Security Awareness",
             "Apply information security principles and practices to protect organizational data assets."),
        (7,  "IT Project Management",
             "Plan, execute, monitor, and close IT projects using established project management frameworks."),
        (8,  "Communication",
             "Communicate technical solutions, reports, and proposals effectively to diverse stakeholders."),
        (9,  "Professional Ethics",
             "Apply ethical standards, legal frameworks, and organizational policies in IT professional practice."),
        (10, "Emerging Technologies",
             "Evaluate and recommend emerging technologies to improve organizational efficiency and competitiveness."),
        (11, "Lifelong Learning",
             "Engage in continuous learning and professional development in the rapidly evolving IT landscape."),
    ],
    "BSSE": [
        (1,  "Software Engineering Foundations",
             "Apply software engineering principles, models, and standards to develop quality software systems."),
        (2,  "Requirements Engineering",
             "Elicit, analyze, specify, validate, and manage software requirements for complex systems."),
        (3,  "Software Architecture and Design",
             "Design scalable, maintainable, and reliable software architectures and detailed component designs."),
        (4,  "Implementation and Coding",
             "Implement software solutions using appropriate languages, design patterns, and coding standards."),
        (5,  "Testing and Quality Assurance",
             "Apply systematic testing methodologies and quality assurance techniques to ensure software reliability."),
        (6,  "Process and Agile Methods",
             "Apply agile, DevOps, and process improvement methodologies across the software development lifecycle."),
        (7,  "Team Collaboration",
             "Work collaboratively and effectively in multi-disciplinary software development environments."),
        (8,  "Technical Communication",
             "Produce clear technical documentation, design specifications, and reports for diverse audiences."),
        (9,  "Ethics and Professionalism",
             "Demonstrate professional responsibility, ethical conduct, and legal awareness in software practice."),
        (10, "Project Delivery",
             "Deliver software projects on schedule, within scope, and meeting defined quality standards."),
        (11, "Research and Innovation",
             "Apply research skills to identify novel and innovative solutions for complex software engineering challenges."),
        (12, "Lifelong Learning",
             "Adapt to new tools, languages, and paradigms through continuous professional development."),
    ],
    "BSDS": [
        (1,  "Statistical Foundations",
             "Apply statistical and mathematical foundations to analyze, model, and interpret data effectively."),
        (2,  "Machine Learning",
             "Design, implement, and evaluate machine learning models to solve real-world prediction and classification problems."),
        (3,  "Data Engineering",
             "Build and manage scalable data pipelines, warehouses, and big data infrastructure."),
        (4,  "Deep Learning",
             "Apply deep learning architectures and neural networks to solve complex pattern recognition problems."),
        (5,  "Data Visualization",
             "Create effective, interpretable visualizations and dashboards to communicate data-driven insights."),
        (6,  "Research Methods",
             "Apply scientific research methods and experimental design to empirical studies in data science."),
        (7,  "Domain Application",
             "Apply data science and analytics techniques to domain-specific problems in healthcare, finance, and NLP."),
        (8,  "Ethics and Privacy",
             "Address ethical, privacy, bias, and fairness concerns in data collection, processing, and model deployment."),
        (9,  "Communication",
             "Communicate data findings, model results, and analytical insights effectively to technical and business audiences."),
        (10, "Lifelong Learning",
             "Continuously update skills and knowledge in the rapidly evolving field of data science and AI."),
    ],
    "BSCY": [
        (1,  "Security Fundamentals",
             "Apply core cybersecurity principles including the CIA triad, threat modeling, and security frameworks."),
        (2,  "Cryptography",
             "Understand and implement cryptographic algorithms and protocols to secure data and communications."),
        (3,  "Network Security",
             "Analyze network vulnerabilities and design and implement appropriate security controls and architectures."),
        (4,  "Offensive Security",
             "Conduct authorized penetration testing, vulnerability assessments, and red team operations."),
        (5,  "Digital Forensics",
             "Apply forensic methodologies and tools to investigate, analyze, and report on cyber incidents."),
        (6,  "Incident Response",
             "Develop and execute structured incident response plans to contain, eradicate, and recover from attacks."),
        (7,  "Governance and Compliance",
             "Apply security governance frameworks, risk management, and regulatory compliance requirements."),
        (8,  "Ethics and Cyber Law",
             "Apply legal and ethical frameworks governing cybersecurity research, disclosure, and professional practice."),
        (9,  "Communication",
             "Prepare and present security advisories, audit reports, and technical documentation professionally."),
        (10, "Secure Development",
             "Apply secure coding practices and SSDLC principles to develop resilient and hardened software."),
        (11, "Lifelong Learning",
             "Stay current with the evolving threat landscape, defensive technologies, and offensive techniques."),
    ],
}

# ---------------------------------------------------------------------------
# CLO heading & description templates
# ---------------------------------------------------------------------------

CLO_HEADINGS = [
    "Knowledge and Understanding",
    "Analysis and Problem Solving",
    "Design and Implementation",
    "Evaluation and Testing",
    "Communication and Reporting",
]

CLO_DESC_TEMPLATES = [
    "Demonstrate understanding of core theoretical concepts in {topic} and apply them to practical scenarios.",
    "Analyze complex problems related to {topic}, identify root causes, and develop structured solutions.",
    "Design and implement practical solutions in {topic} using appropriate tools, frameworks, and methodologies.",
    "Evaluate existing systems and solutions in {topic} against defined criteria for quality, performance, and correctness.",
    "Communicate technical findings, designs, and results in {topic} clearly through written reports and presentations.",
]


# ---------------------------------------------------------------------------
# Main command
# ---------------------------------------------------------------------------

class Command(BaseCommand):
    help = "Seed the database with a complete OBE dataset (programs, courses, PLOs, CLOs, mappings)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--flush",
            action="store_true",
            help="Delete all existing OBE data before seeding",
        )
        parser.add_argument(
            "--seed",
            type=int,
            default=42,
            help="Random seed for reproducibility (default: 42)",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        random.seed(options["seed"])

        if options["flush"]:
            self._flush()

        faculty_user = self._ensure_faculty_user()

        programs    = self._seed_programs(faculty_user)
        courses     = self._seed_courses(programs)
        plos        = self._seed_plos(programs)
        clos        = self._seed_clos(courses)
        self._seed_mappings(programs, courses, plos, clos)

        self._print_summary(programs)

    # -----------------------------------------------------------------------
    # Flush
    # -----------------------------------------------------------------------

    def _flush(self):
        self.stdout.write("  Flushing existing OBE data...")
        PloCloMapping.objects.all().delete()
        CourseLearningOutcome.objects.all().delete()
        ProgramLearningOutcome.objects.all().delete()
        Course.objects.all().delete()
        Program.objects.all().delete()
        self.stdout.write(self.style.WARNING("  Existing OBE data cleared."))

    # -----------------------------------------------------------------------
    # Faculty user (required by Program.program_incharge)
    # -----------------------------------------------------------------------

    def _ensure_faculty_user(self):
        user = User.objects.filter(role="faculty").first()
        if user:
            return user
        user = User.objects.create_user(
            username="obe_faculty",
            email="obe_faculty@example.com",
            password="faculty123",
            role="faculty",
            first_name="OBE",
            last_name="Coordinator",
        )
        self.stdout.write("  Created faculty user: obe_faculty")
        return user

    # -----------------------------------------------------------------------
    # Programs
    # -----------------------------------------------------------------------

    def _seed_programs(self, faculty_user):
        self.stdout.write("Seeding programs...")
        programs = {}
        for title, abbr in PROGRAMS:
            prog, created = Program.objects.get_or_create(
                program_abbreviation=abbr,
                defaults={
                    "program_title": title,
                    "program_type": "UG",
                    "program_incharge": faculty_user,
                },
            )
            programs[abbr] = prog
            status = "created" if created else "exists"
            self.stdout.write(f"  [{status}] {abbr} – {title}")
        return programs

    # -----------------------------------------------------------------------
    # Courses
    # -----------------------------------------------------------------------

    def _seed_courses(self, programs):
        """
        Returns dict: course_id -> Course object.
        Also populates the ManyToMany program–course relation.
        """
        self.stdout.write("Seeding courses...")
        courses = {}

        # Program-specific courses
        for abbr, course_list in COURSES_BY_PROGRAM.items():
            program = programs[abbr]
            for course_id, name, credit_hours in course_list:
                course, created = Course.objects.get_or_create(
                    course_id=course_id,
                    name=name,
                    credit_hours=credit_hours,
                )
                course.programs.add(program)
                courses[course_id] = course
                if created:
                    self.stdout.write(f"  [created] {course_id} – {name}")

        # Shared courses
        for course_id, name, credit_hours in SHARED_COURSES:
            course, created = Course.objects.get_or_create(
                course_id=course_id,
                name=name,
                credit_hours=credit_hours,
            )
            for abbr in SHARED_ASSIGNMENTS.get(course_id, []):
                course.programs.add(programs[abbr])
            courses[course_id] = course
            if created:
                self.stdout.write(f"  [created] {course_id} – {name} (shared)")

        return courses

    # -----------------------------------------------------------------------
    # PLOs
    # -----------------------------------------------------------------------

    def _seed_plos(self, programs):
        """Returns dict: program_abbr -> list[ProgramLearningOutcome]"""
        self.stdout.write("Seeding PLOs...")
        plos = {}

        for abbr, program in programs.items():
            plo_list_data = PLO_DATA[abbr]
            n = len(plo_list_data)
            weightages = weights_summing_to(n)

            plo_objects = []
            for (number, heading, description), weightage in zip(plo_list_data, weightages):
                plo, created = ProgramLearningOutcome.objects.get_or_create(
                    program=program,
                    PLO=number,
                    defaults={
                        "heading": heading,
                        "description": description,
                        "weightage": float(weightage),
                    },
                )
                plo_objects.append(plo)

            plos[abbr] = plo_objects
            self.stdout.write(f"  {abbr}: {n} PLOs, weightage sum = {sum(weightages)}")

        return plos

    # -----------------------------------------------------------------------
    # CLOs
    # -----------------------------------------------------------------------

    def _seed_clos(self, courses):
        """
        Returns dict: course_id -> list[CourseLearningOutcome]

        CourseLearningOutcome.save() calls full_clean(), which validates that
        the running total of weightages for the course does not exceed 100.
        CLOs are therefore created in sequence, with the last one receiving
        the exact remainder to hit 100.
        """
        self.stdout.write("Seeding CLOs...")
        clos = {}

        for course_id, course in courses.items():
            # Skip if already seeded
            existing = list(course.course_outcomes.all().order_by("CLO"))
            if existing:
                clos[course_id] = existing
                continue

            n = random.randint(4, 5)
            weightages = weights_summing_to(n)
            topic = course.name

            clo_objects = []
            for i, weightage in enumerate(weightages, start=1):
                heading  = CLO_HEADINGS[i - 1]
                desc     = CLO_DESC_TEMPLATES[i - 1].format(topic=topic)
                # save() calls full_clean() internally – weightages are valid by construction
                clo = CourseLearningOutcome(
                    course=course,
                    CLO=i,
                    heading=heading,
                    description=desc,
                    weightage=float(weightage),
                )
                clo.save()
                clo_objects.append(clo)

            clos[course_id] = clo_objects

        total_clos = sum(len(v) for v in clos.values())
        self.stdout.write(f"  Total CLOs created: {total_clos}")
        return clos

    # -----------------------------------------------------------------------
    # CLO → PLO Mappings
    # -----------------------------------------------------------------------

    def _seed_mappings(self, programs, courses, plos, clos):
        """
        The model's clean() enforces: each CLO maps to at most ONE PLO globally
        (it checks filter(course, clo) without a program filter). Therefore
        each CLO must appear in exactly one PloCloMapping row.

        Strategy per course:
          1. Collect PLOs from ALL programs the course belongs to.
          2. Pick 3–5 of those PLOs.
          3. Assign each CLO round-robin to one selected PLO.
          4. For each (PLO, [CLOs]) group, assign weightages summing to 100.
             The PLO's program becomes the mapping's program field.

        For shared courses this distributes CLOs across the programs that
        share the course, satisfying the 3–5 PLO coverage requirement.
        """
        self.stdout.write("Seeding CLO→PLO mappings...")
        total_mappings = 0

        for course_id, course in courses.items():
            course_clos = clos.get(course_id, [])
            if not course_clos:
                continue

            # Skip if already seeded
            if PloCloMapping.objects.filter(course=course).exists():
                continue

            # Gather PLOs from every program this course belongs to
            course_programs = list(course.programs.all())
            all_available_plos = []
            for prog in course_programs:
                all_available_plos.extend(plos.get(prog.program_abbreviation, []))

            if not all_available_plos:
                continue

            # Pick 3–5 distinct PLOs
            num_plos = min(random.randint(3, 5), len(all_available_plos))
            selected_plos = random.sample(all_available_plos, num_plos)

            # Assign each CLO to exactly one PLO (round-robin)
            plo_to_clos = {plo.id: [] for plo in selected_plos}
            for idx, clo in enumerate(course_clos):
                plo_to_clos[selected_plos[idx % num_plos].id].append(clo)

            # Create mappings — the PLO's own program is used as mapping.program
            for plo in selected_plos:
                mapped_clos = plo_to_clos[plo.id]
                if not mapped_clos:
                    continue

                mapping_weights = weights_summing_to(len(mapped_clos), total=100)

                for clo, weight in zip(mapped_clos, mapping_weights):
                    mapping = PloCloMapping(
                        program=plo.program,   # derived from the PLO itself
                        course=course,
                        plo=plo,
                        clo=clo,
                        weightage=float(weight),
                    )
                    mapping.save()   # full_clean() runs internally
                    total_mappings += 1

        self.stdout.write(f"  Total mappings created: {total_mappings}")

    # -----------------------------------------------------------------------
    # Summary
    # -----------------------------------------------------------------------

    def _print_summary(self, programs):
        prog_count    = Program.objects.count()
        course_count  = Course.objects.count()
        pc_count      = sum(p.courses.count() for p in programs.values())
        plo_count     = ProgramLearningOutcome.objects.count()
        clo_count     = CourseLearningOutcome.objects.count()
        mapping_count = PloCloMapping.objects.count()

        self.stdout.write("\n" + "=" * 50)
        self.stdout.write(self.style.SUCCESS("OBE Dataset Seeding Complete"))
        self.stdout.write("=" * 50)
        self.stdout.write(f"  Programs              : {prog_count}")
        self.stdout.write(f"  Courses               : {course_count}")
        self.stdout.write(f"  Program–Course links  : {pc_count}")
        self.stdout.write(f"  PLOs                  : {plo_count}")
        self.stdout.write(f"  CLOs                  : {clo_count}")
        self.stdout.write(f"  CLO→PLO Mappings      : {mapping_count}")
        self.stdout.write("=" * 50)
