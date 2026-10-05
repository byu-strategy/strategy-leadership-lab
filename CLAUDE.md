# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this
repository.

## Project Overview

Quarto book for **Strategy Leadership Lab**, **STRAT 490R Section 2**, in the BYU Marriott
School of Business. 1.5 credits, letter graded, offered fall and winter. Taught by Scott Murff,
Strategy Program Director.

Enrollment is limited to the roughly 30 students who lead the Strategy Program and its four
clubs (MCA, PMA, CSA, WSA). The course is the coordination mechanism in the Strategy Program
operating model: 30 minutes of leadership development followed by a 45 minute project
roundtable, once a week.

STRAT 490R is a shared course number. Strategy Prototyping (`byu-strategy/strategy-prototyping`)
uses it, and AI Foundry (`byu-strategy/ai-foundry`) is cross-listed under it as STRAT 490R /
MBA 693R. This course is Section 2 and is separate from both. That overlap is intentional, never
a typo to correct.

The site is student-facing. Structure follows `byu-strategy/product-management`.

## Build Commands

- **Preview during development**: `quarto preview`
- **Check installation**: `quarto --version`

**Never render locally.** The site auto-renders via GitHub Actions on push to main. See
`.github/workflows/publish.yml`. Output goes to `docs/`.

## Content Structure

```
index.qmd                 # Syllabus: structure, who is in the room, grading, credit vs pay
00-schedule.qmd           # Weekly session schedule
00-assessments.qmd        # The three course requirements
01-operating-model.qmd    # Program structure, clubs, selection process, employee vs volunteer
90-resources.qmd          # Readings and links
```

Source for `01-operating-model.qmd` is `_materials/Strategy_Operating_Model.pdf`.

## Still Unset

The grading scheme and category weights; the absence policy; the AI proficiency bar; the
leadership development topics for sessions 2 to 13; BYU policy boilerplate. These are marked
TBD in the files. Do not invent them, ask.

Settled: Fridays 12:30 to 1:45 PM in 1315 TNRB, 1.5 credits, 13 sessions Sep 4 to Dec 4, 2026.
Source is the Fall 2026 teaching schedule (STRAT 490R section 002) and the BYU academic
calendar. Nov 27 is a Thanksgiving holiday, the only Friday lost.

The operating model PDF says the Lab is Pass/Fail. That is out of date: the course is letter
graded. Do not restore Pass/Fail from the PDF.

## Where Files Go

- Course source, rubrics, teaching notes: this repo, committed
- Anything naming a student (rosters, grades, nominations, add codes): `_private`, never git
- Heavy files and third-party PDFs: `_materials`, never git

`_private` and `_materials` are symlinks into OneDrive "3. Teaching" and are gitignored.

## House Style

- No em dashes anywhere in this repository
- Plain, factual prose. Scott adds the flourishes
- No dramatic or coaching language. Examples Scott rejected: "Follow the fire," "own the
  front of the room," "Get twenty-six busy people to think out loud." Say what the student
  does, when it is due, and how it is graded, and stop
