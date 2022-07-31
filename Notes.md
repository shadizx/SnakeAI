# TODO
- Restructure code - Shadi [X]
- Add score - [ ]
- Add gameover screen - [ ]
- Add obstructions - [ ]
- Change speed of snake - [ ]

---------------------------------------------------
# Workflow Format
- Making a change? Here's how
- Make a new branch monitoring main branch
- ex: git checkout -b branch_name_here origin/main
- Make your changes and commit
- rebase from target branch
- ex: git pull --rebase
- merge main with what you have
- ex:   git checkout main
        git merge branch_name_here

---------------------------------------------------
# BUG report format
- Bug name
- Assignee:
- Reporter:
- Severity: (low, medium, high)
- Description:
- Date:
- Workflow: (scheduled, in-progress, complete)
- Comments:
---------------------------------------------------
# BUG [X]
- Code Restructuring
- Assignee:
    Shadi
- Reporter:
    Shadi and Roham
- Severity: high
- Description:
    Need to restructure code
- Date:
    July 29, 2022
- Workflow:
    Completed
- Comments:
    Changed the way random item was chosen, added grid list

---------------------------------------------------
# BUG [ ]
- Apple in Snake Bug
- Assignee:
    Shadi
- Reporter:
    Roham
- Severity: high
- Description:
    Apple kept reappearing in snake, changed the place() function for snake and food
- Date:
    July 30, 2022
- Workflow:
    Completed
- Comments:
    Rarely did random pick a block thats inside snake, so time efficiency wasn't too bad