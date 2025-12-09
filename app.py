import gradio as gr
import random

# -----------------------------------------------------
# Helper: Generate athletes in lanes
# -----------------------------------------------------
def create_heat(target_runner, count):
    athlete_pool = [
        "Lyles", "Coleman", "Omanyala", "Blake",
        "De Grasse", "Jacobs", "Hughes", "Simbine",
        "Kerley", "Shahnoor"
    ]
    if target_runner not in athlete_pool:
        athlete_pool.append(target_runner)

    heat = random.sample(athlete_pool, count)
    if random.random() < 0.25 and target_runner in heat:
        heat.remove(target_runner)
    return heat

# -----------------------------------------------------
# Render heat with lane-specific emojis
# -----------------------------------------------------
def render_heat(heat, current_index, found_index):
    total = len(heat)
    if current_index == -1:
        progress_percent = 0
    elif current_index >= total:
        progress_percent = 100
    else:
        progress_percent = int((current_index / total) * 100)

    progress_html = f"""
    <div style="background:#CFD8DC; border-radius:10px; height:18px; width:100%; margin-bottom:15px;">
        <div style="
            background:#0D47A1;
            width:{progress_percent}%;
            height:100%;
            border-radius:10px;
            transition: width 0.3s;
        "></div>
    </div>
    <div style="text-align:right; font-size:12px; color:#37474F; margin-bottom:10px;">
        {progress_percent}% searched
    </div>
    """

    lane_html = ""
    for i, athlete in enumerate(heat):
        bg = "#F5F5F5"
        border = "2px solid #888"
        emoji = ""
        status = ""

        if i == current_index:
            bg = "#F4D371"          
            border = "3px solid #FFA000"
            emoji = "🏃"
            status = "Checking…"

        elif i < current_index:
            bg = "#ECEFF1"          
            border = "2px solid #B0BEC5"
            emoji = "✅"
            status = "Checked"

        if i == found_index:
            bg = "#8BC34A"          
            border = "3px solid #558B2F"
            emoji = "🎯"
            status = "FOUND!"

        lane_html += f"""
        <div style="
            padding:12px;
            margin-bottom:8px;
            background:{bg};
            border:{border};
            border-radius:8px;
            font-family: Arial, Times New Roman, sans-serif;
            display:flex;
            justify-content:space-between;
            font-size:16px;
        ">
            <span>{emoji} Lane {i+1}: <b>{athlete}</b></span>
            <span>{status}</span>
        </div>
        """

    wrapped = f"""
    <div style="
        background:#ECEFF1;
        padding:25px;
        border-radius:12px;
        width:500px;
        margin:auto;
        box-shadow: 0 6px 15px rgba(0,0,0,0.15);
    ">
        <h3 style="text-align:center; color:#0D47A1; margin-bottom:15px;">
            🏟️ Heat Lane Tracker
        </h3>
        {progress_html}
        {lane_html}
    </div>
    """
    return wrapped

# -----------------------------------------------------
# Linear search step logic
# -----------------------------------------------------
def step_search(heat, target, idx):
    if idx == -1:
        idx = 0
    if idx >= len(heat):
        return (
            f"🚫 <b>{target}</b> isn't in this heat!<br>All lanes are checked.",
            render_heat(heat, -1, -1),
            -2
        )
    if heat[idx].lower() == target.lower():
        return (
            f"🎯 <b>{target}</b> found in Lane {idx+1}!",
            render_heat(heat, idx, idx),
            -2
        )
    return (
        f"🔎 Checking Lane {idx+1}…",
        render_heat(heat, idx, -1),
        idx + 1
    )

# -----------------------------------------------------
# Story stage control
# -----------------------------------------------------
def next_stage(stage, target_input, heat):
    target = (target_input or "").strip()
    if stage == 1:
        if target == "":
            return (
                "⚠️ Please enter the sprinter you're trying to locate...",
                gr.update(),
                gr.update(visible=False),
                stage,
                heat
            )
        new_heat = create_heat(target, 8)
        return (
            f"🏁 Heat generated!<br><br>"
            f"Linear search will now look for <b>{target}</b> lane by lane. "
            "Remember: the list is unsorted, so each lane must be checked in order.",
            gr.update(visible=True),
            gr.update(value="Start Searching"),
            2,
            new_heat
        )
    if stage == 2:
        info = (
            "<div style='background:#CFD8DC; padding:12px; border-radius:8px; margin-top:10px;'>"
            "<h4 style='margin:0; color:#37474F;'>💡 Linear Search Info</h4>"
            "<ul style='margin-top:5px;'>"
            "<li>⏱ Time complexity: O(n) in the worst case.</li>"
            "</ul></div>"
        )
        return (
            f"🚦 Searching for <b>{target}</b>…{info}",
            gr.update(visible=True),
            gr.update(value="Next Lane ➡️"),
            3,
            heat
        )
    return "", gr.update(), gr.update(), stage, heat

# -----------------------------------------------------
# Reset app
# -----------------------------------------------------
def reset_app():
    return (
        "🏃‍♂️ Welcome Coach!<br>Type the runner's name to start the search.",
        gr.update(visible=True, value=""),
        gr.update(visible=True, value="Find Runner"),
        gr.update(value=""),
        1,
        [],
        -1
    )

# -----------------------------------------------------
# Build Gradio UI
# -----------------------------------------------------
with gr.Blocks() as demo:

    gr.Markdown(
        """
        <h1 style="text-align:center; color:#0D47A1;">
        🏟️ Linear Search Tracker
        </h1>
        <p style="text-align:center; font-size:16px;">
        Step through each lane to locate your athlete coach!
        </p>
        """
    )

    story = gr.HTML("🏃‍♂️ Welcome Coach!<br>Type the runner's name to start the search.")
    name_box = gr.Textbox(label="Athlete Name", placeholder="e.g., Lyles")
    heat_display = gr.HTML("")

    main_button = gr.Button("Find Runner :)")

    # States
    stage_state = gr.State(1)
    heat_state = gr.State([])
    search_idx = gr.State(-1)

    # Advance stage
    def handle_stage(stage, name, heat):
        return next_stage(stage, name, heat)

    main_button.click(
        fn=handle_stage,
        inputs=[stage_state, name_box, heat_state],
        outputs=[story, heat_display, main_button, stage_state, heat_state]
    )

    # Lane-by-lane search
    def handle_step(stage, heat, name, idx):
        if stage == 3:
            return step_search(heat, name, idx)
        return gr.update(), gr.update(), idx

    main_button.click(
        fn=handle_step,
        inputs=[stage_state, heat_state, name_box, search_idx],
        outputs=[story, heat_display, search_idx]
    )

demo.launch(share=True)
