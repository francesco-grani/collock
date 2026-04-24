Design a **first, simple UI concept** for a web app called **Collock**.

## App concept
Collock is a **job interview practice app**. The user enters the type of job they are applying for, and the system acts like a recruiter conducting a mock interview.

The recruiter should be able to:
- ask general interview questions
- ask technical questions
- ask personality / behavioral questions
- give short practical assignments, such as small coding exercises, to be completed in the same app interface

The user should be able to choose the **difficulty level** of the interview.

## Design direction
This is the **first iteration**, so keep the product **simple, focused, and realistic**. Avoid overdesigning or adding too many advanced features. Prioritize a clean MVP-like structure that feels immediately usable.

The app must be:
- **single-page**
- **simple but modern**
- visually appealing to a **Gen Z / Millennial audience**
- clean, minimal, slightly playful, but still credible for a career-oriented product

## Important product/design constraints
The UI must be designed so that it can realistically be built with **Python + Streamlit** only.

That means:
- no layouts or interactions that depend on complex frontend frameworks
- no designs that require highly custom drag-and-drop behavior
- no heavy animation-dependent concepts
- no multi-page architecture
- keep components aligned with what Streamlit can reasonably support: forms, text inputs, selectboxes, sliders, tabs, expanders, chat-like areas, code/text areas, buttons, status messages, sidebars, containers, columns, and simple progress or feedback elements

## Core UI areas to include
Please propose a simple single-page layout that includes at least:

1. **Setup / interview configuration area**
   - target job or role input
   - difficulty selection
   - optional interview type selection if useful

2. **Main interview area**
   - recruiter questions shown clearly
   - user answer input
   - support for both normal text answers and short technical exercises

3. **Session flow controls**
   - start interview
   - next question
   - submit answer
   - end/reset session

4. **Optional LLM settings panel**
   - advanced settings for parameters like temperature, top-p, and similar controls
   - this should feel secondary and optional, not the main focus

## Encourage smart but realistic additions
You may also propose a few **small extra UI elements or micro-features** that are naturally useful for interview practice, even if not explicitly listed above, as long as they are:
- inherently relevant to this app
- lightweight
- realistic for a first version
- achievable in Streamlit

Examples of the type of additions that are welcome:
- interview timer
- progress indicator
- answer tips/help hint
- interview category tag
- session summary box
- simple feedback area
- coding task instructions box
- confidence or stress check-in
- recruiter persona selector if lightweight

Do **not** turn this into a bloated product. Add only features that clearly improve the interview practice experience.

## What I want from you
Propose:
- a **simple single-page UI concept**
- the main sections/components
- a modern visual direction
- a component structure that is feasible in Streamlit
- a few smart optional UI items that enrich the experience without making it complex

Keep the concept grounded, elegant, and buildable.