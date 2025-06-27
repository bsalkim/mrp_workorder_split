{
    "name": "MRP Workorder Split",
    "version": "16.0.1.0.2",  # ⬅️ Versiyon bilgisi
    "summary": "Allows partial workorder completion and auto-creates new workorders for remaining quantity.",
    "description": """
        This module enables partial processing of MRP Work Orders.
        When a workorder is completed for less than its planned quantity,
        a new workorder is automatically generated for the remaining amount.
    """,
    "author": "Your Name or Company",
    "website": "https://github.com/bsalkim",
    "category": "Manufacturing",
    "depends": ["mrp"],
    "data": [],
    "installable": True,
    "application": False,
    "auto_install": False,
    "license": "LGPL-3",
    "post_init_hook": "test_hook"
}
