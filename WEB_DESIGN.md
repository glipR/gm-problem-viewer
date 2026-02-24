## Basics

The web design is intended to be:

1. Run locally
2. Minimally designed from defaults (use a no-nonsense library like mantine for components)

Some other things to note:

All potentially long running processes (generating test files, running solutions, etc) should happen asynchronously (the run endpoint should give you and ID that you can query the status of intermittently)

Some checks should live-update the current page (Problem Detail - Solutions) using this polling mechanism, and large processes (Run/Review) should give a notification when complete.

## Pages

### Kanban Board

This view shows problems that are still in development, and their progress. There are three lanes that problems can sit within:

1. Lane 1: Draft - For problems that are still just ideas - these likely have a very short statement, maybe a solution, but nothing else.
2. Lane 2: In progress - For problems in active development
3. Lane 3: Review - These problems are more or less complete, save for some review, but haven't been used in a contest yet

There is a 4th state - complete, for problems that have been used in a contest.

Problems in the kanban board appear as tiles. These tiles show the following information:

1. slug (grey and small)
2. Human readable title
3. The problem tags and difficulty (top right)
4. Along the bottom of the card, an array of icons representing the different facets of problems (statement, solution, validators, tests), which receives a different colour based on the status of these elements.
5. Along the bottom of the card shows a progress bar to represent how many of the deterministic checks from the "Review" process have passed.

This card should be draggable into the different lanes, and also clickable to bring up the problem detail. It should also have an action button in the top right to perform an export.

### Problem Detail

This page shows everything necessary for a problem. The aim here is not to make any content for the problem editable, but to surface it with a nice UI and provide some contextual actions.

The header has some basic problem information (Name, tags, status, mem/time limits), author, as well as the same icons that the the kanban board has.

the bottom border of the header is the same progress bar from the kanban board, and can be hovered to show what particular checks are failing.

There is also a collection of buttons along the right bottom part of the header, which do the following:

1. Run - does the following in order:
    a. Generate tests cases by running all test generators
    b. Run all input validators against all relevant test cases
    c. Run all solutions against all test cases
    d. Collate results
2. Review - Computes some deterministic metrics about the problem - does it have input validators, does it have a WA expected solution, if interactive does it have a grader
3. AI Review - Computes some AI-based metrics about the problem - do statement bounds line up with input validators, does each test set have its own input validator, should the problem have a custom output validator, are all boundary cases caught, etc. The AI output is non-deterministic, but each of the things to check is predefined.

Below this is a tabular section, with the following tabs:

#### Problem Detail - Statement

This is just a readonly rendering of the statement in markdown. There is a button at the top to review with claude and make some grammatical changes.

#### Problem Detail - Solutions

This shows all solutions, which are organised in a tree view by their folder structure. The nodes in the tree are details-summary blocks, which can be expanded to view test results from the most recent run. This shows ticks and cross for each test, separated by test set, with an overall verdict for each test set.

Additionally, there is a button at the top to run all solutions against all test cases. And also a button in each tree item to run just that solution.

Each solution block shows an icon to represent if it is consistent with it's own config (expecting TLE on set A, for example).

#### Problem Detail - Tests

This is a test viewer, and the only page where editing is expected (although just for test descriptions). Here you can view each individual test set (detail summary auto-expanded), containing their tests, and generators. Generators render at the top of the list.

There is a button to run a particular generator + all generators. Each test when clicked will show the input on the right side of the screen, and also has a auto-focused description text edit where you can add information.

When clicking on a test set, you can also edit the configuration there.

##### Adding test sets

At the bottom of the test sets list there is an "Add test set" button. This opens a modal with fields for the test set's config (name, description, points, marking_style). Submitting creates the directory and its config.yaml on disk.

##### Adding test cases manually

Each test set has an "Add test" button alongside its header. This opens a modal with a textarea for the raw input and an optional description field. Submitting writes a new `.in` file (and sidecar `.yaml` if a description was provided) into the set's directory. The file is named automatically (e.g. incrementing from the highest existing numeric name, or a user-supplied name if provided).
