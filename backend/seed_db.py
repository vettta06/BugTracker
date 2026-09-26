from app.database import session
from app.models import Bug, Project, User


def seed_db():
    db = session()
    try:
        if db.query(User).first() is not None:
            print("Database already seeded. Skipping.")
            return

        users = [
            User(name="Alice Smith", email="alice@devbug.com"),
            User(name="Bob Jones", email="bob@devbug.com"),
            User(name="Charlie Brown", email="charlie@devbug.com"),
        ]
        db.add_all(users)
        db.flush()

        projects = [
            Project(name="Frontend App", description="Main client application"),
            Project(name="Backend API", description="Core API services"),
        ]
        db.add_all(projects)
        db.flush()

        bugs = [
            Bug(
                title="Login button not working",
                description="Clicking login does nothing on mobile",
                status="open",
                priority="high",
                project_id=projects[0].id,
                assignee_id=users[0].id,
            ),
            Bug(
                title="Slow API response",
                description="Users endpoint takes > 2s",
                status="in_progress",
                priority="medium",
                project_id=projects[1].id,
                assignee_id=users[1].id,
            ),
        ]
        db.add_all(bugs)
        db.commit()
        print("Database seeded successfully.")

    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    seed_db()
