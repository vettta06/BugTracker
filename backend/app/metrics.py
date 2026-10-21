from prometheus_client import Counter

BUGS_CREATED = Counter(
    "devbug_bugs_created", "Total number of created bugs", ["priority"]
)

BUGS_STATUS_CHANGED = Counter(
    "devbug_bugs_status_changed",
    "Total number of bug status changes",
    ["from_status", "to_status"],
)

BUGS_ASSIGNED = Counter(
    "devbug_bugs_assigned", "Total number of bugs assigned to users"
)

PROJECTS_CREATED = Counter("devbug_projects_created", "Total number f created projects")
