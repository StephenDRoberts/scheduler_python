# Python Scheduler

![Diagram](documentation/scheduler.png) <!-- .element height="50%" width="50%" -->

## Installation

This project was made using the [Poetry](https://python-poetry.org/docs/basic-usage/) dependency management tool.
As such, the poetry environment comes built with the dependencies required to run.

Follow the instructions on [poetry's website](https://python-poetry.org/docs/) to download the tool. At the time of
writing this requires Python 3.7+.

## Running

From the root directory, run the following command to start the scheduler task.

```
 poetry run python main.py                                              
```

The scheduler currently takes between 5-10 minutes to complete. 

## Testing

The project uses [pytest](https://docs.pytest.org/en/7.2.x/) for the test framework.
To run all tests, type the following command in the terminal:

```
poetry run pytest                               
```

## Walkthrough

### Entry point

`main.py` is the entry point for the project. This file orchestrates the Extract/Transform/Load areas of the
application.

### Constants

Holds some configuration settings for task durations, capacity, etc as well as time helper constants.

### Parser

There is one parser method that takes in a filepath, reads the CSV if present and loads into
a [pandas](https://pandas.pydata.org/) dataframe.

### Formatters

Each filetype has its own formatter. Their job is to clean and format the data in a way that makes the processes later
on easier.
For instance, in [format_schedule](src/formatters/format_schedule.py), additional information is added for shift
start/end
times.
The schedule is extended to create employee (collectors) IDs for each employee working on a shift. Similarly, matches
have been extended to tasks where each task represents analysing on a specific team in a match.
The formatters are also responsible for relabeling columns in their respective dataframes.

### Joiners

Joiners are responsible for combining like-minded dataframes. For instance, a match is linked to a competition which in
turn has a corresponding priority as noted in the task instructions. Preferences have been hydrated with additional
information for competitions that don't have a preference squad. This is to aid processing in the scheduler task.

### Schedule

The role of the scheduler is to orchestrate the planning of tasks within each shift. It creates 2 dataframes to track
progress, one for processed tasks (both complete and incomplete) and another for partially completed tasks that need to
be prioritised in the next shift. The partial bucket is a temporary dataframe where entries are removed when they are
fully completed. The scheduler:

* picks up partials that need to be processed first
* filters for new tasks that can be picked up in this shift
* filters for employees in this shift

It then iterates over each task in a shift, calling the processor to assign a task to an employee and track the time
completed.

### Processor

The processor is responsible for assigning an employee to a task. It calls `task_planner` which provides times for when
the
task in question can be processed for each employee in the shift, given their other scheduling
commitments. From there it will assign the task to
the collector who completes the most, and then by the earliest. If there are collectors available for the task. If no
collectors are available (indicated with a `percentage_complete` of 0), then that task is put into the partial bucket.

Every task picked up is put into `processed_tasks` with a corresponding `percentage_complete` input. If it is complete,
it is removed from the `partially_processed_tasks` dataframe. If it is incomplete by the end of the shift, it's put
into `partially_processed_tasks`.

### Task_Planner

This is responsible for checking when the task under consideration can be picked up by an employee. It starts by
searching
the `processed_task` dataframe for any previous processing efforts for that task. From there it calculates the hours
remaining for completion given the employees speed for completion (1.0 if the collector is in the preference squad for
the competition, 0.8 otherwise).

It then searches the current processed tasks for any records for that employee. As employee ids are shift specific, any
records here mean the employee has a task scheduled during that shift. It then calculates possible start/end times given
their scheduling commitments and the shift end time. NB if a collector cannot complete the task in question before their
next scheduled task, then it will be planned to be picked up after the scheduled task as I've assumed they can
stop/start processing tasks unless it was the end of a shift.

The planner reports back with start/end times and percentage complete for the employee and task combination in question.

## Notes

* The concept of an 'employee' is only with regards to a single shift. No employees span different shifts, which
  wouldn't happen in reality (ie) we create a new employee ID for each shift.
* An employees id is `employee-{squad}-{date}-{shift}-{employee number}`

#### Assumptions

* A game can be processed by two collectors at the same time, one assessing the home team and another assessing the away
  team.
* A partially processed game needs to be completed in th next shift NB I believe this assumption to be wrong (see note
  below).
* Tasks can't be stopped/started unless it's the end of a shift. Because of this, collectors cannot process a task
  before another scheduled task unless it can be completed.
* Assumed max amount of tasks any employee can pick up is 4. In reality it is probably more like 3 if an employee picks
  up a partial task first, then completes a full task, and then finishes by partially completing a 3rd. This was put in
  to avoid any unnecessary calculation when it's thought no employee can't pick up the task.

#### Issues with the algorithm

* I made the false assumption that partially completed tasks needed to be picked up in the very next shift. After
  re-reading, this is incorrect. Instead, the algorithm should maybe group partials and new tasks together in each new
  shift and organise by processing deadline again.
* The algorithm could probably be simplified down to just use one `processed_tasks` dataframe to keep a record of what
  has been processed. Rather than keeping two separate dataframes for partials/processed, it should just use that one
  and calculate all the partial hours calculations and shift times from there.
* Tasks are ordered by processing deadline. However, I've not taken into account whether deferring the processing of a
  match to another shift would make it quicker.

#### Next steps

* Look into better algorithm construciton. Possibly using
  more [genetic algorithm](https://en.wikipedia.org/wiki/Genetic_algorithm_scheduling#:~:text=To%20apply%20a%20genetic%20algorithm,start%20time%20represents%20a%20gene.)
  .
* Allow for tasks to be start/stopped at any point.
* Use single task dataframe rather than keep acount of processed and partials separately. Would allow for more
  confidence rather than having the potential for one dataframe to be out of sync with another.
* It would be better to have a more robust capacity check rather than just looking at an arbitrary amount of tasks I
  think they might be able to handle in a shift. This would also
* In [format_matches_to_tasks](src/formatters/format_matches.py) I would have liked to have checked/applied language
  decoding programatically across any series that needed it. However, in the interest of time applying to
  the `competition`
  seemed sensible given this dataset.
