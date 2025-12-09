import gradio as gr
import random

# --- To start this function will be created the "heat" (list of runners in the race)
def create_heat(target_runner, count):
    runner_list = [
        "Lyles", "Coleman", "Omanyala", "Blake", #I wrote down random well-known athletes and my name down for fun
        "De Grasse", "Jacobs", "Hughes", "Simbine",
        "Mclaughlin", "Shahnoor"
    ] #this if-statement basically states the if the user types in a runner that is not already here, I will add them to the list
    runner_list.append(target_runner)
#This randomly picks a number of runners that is equal to the count to create a heatsheet
   #also, I wanted to make this app to work under worse-case and average-case scenarios so I created a small chance that the target is "not" in the heat
    heat = random.sample(runner_list, count)
    if random.random() < 0.25 and target_runner in heat:
        heat.remove(target_runner)
    return heat

# --- NOW I am building the HTML Layout that visually shows all the lanes, progress bar, and the app itself.

def html_heat(heat, c_index, f_index):
    total = len(heat)  #here we are calculating and creating the progress percentage of each search
    if c_index == -1:
        progress_percent = 0
    elif c_index >= total:
        progress_percent = 100
    else: #detects how into the list we have checked!
        prog_percent = int((c_index / total) * 100)

#actuallycreating the progress bar, background width, height, border-rad, etc.
    prog_html = f"""
    <div style="background:#CFD8DC; border-radius:10px; height:18px; width:100%; margin-bottom:15px;">
        <div style="
            background:#0D47A1;
            width:{prog_percent}%; 
            height:100%;
            border-radius:10px;
            transition: width 0.3s;
        "></div>
    </div>
    <div style="text-align:right; font-size:12px; color:#37474F; margin-bottom:10px;">
        {prog_percent}% searched
    </div>
    """

    lane_html = ""
#So here we are looping through each of the lanes and are showing whether its been checked or not
    for i, athlete in enumerate(heat):
        bg = "#F5F5F5"
        border = "2px solid #888"
        emoji = ""
        status = ""
#if this is the lane we are currently checking.... make it yellow
        if i == c_index:
            bg = "#F4D371"          
            border = "3px solid #FFA000"
            emoji = "🏃"
            status = "Checking…"
#elif its the lane below the current index, indicate that we have checked it already.
        elif i < c_index:
            bg = "#ECEFF1"          
            border = "2px solid #B0BEC5"
            emoji = ""
            status = "Checked"
#now, if its the lane we have found the target runner in, state found and make it green
        if i == f_index:
            bg = "#8BC34A"          
            border = "3px solid #558B2F"
            emoji = "🎯"
            status = "FOUND!"
#Here I am adding more visualization because I tried to make the lanes sort of like a track lane but then I realized CSS isnt compatible with gradio so I sucked it up with html, apologies.
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
#create a rectangle so the lanes fit inside of it
    rectangle = f"""
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
        {prog_html}
        {lane_html}
    </div>
    """
    return rectangle

#  --- HERE IS THE STEP BY STEP LINEAR SEARCH LOGIC

def step_search(heat, target, var):
    if var == -1:
        var = 0.    # if this is the first click, we start at index 0
    if var >= len(heat):  # If we've gone past the heat length, we didn’t find the runner :((
        return (
            f" <b>{target}</b> isn't in this heat, go find them coach!<br>All lanes are checked.",
            html_heat(heat, -1, -1),
            -2 #stop searching
        )
    if heat[var].lower() == target.lower():
        return ( #if we have found the runner at the index
            f"🎯 <b>{target}</b> found in Lane {var+1}!",
            html_heat(heat, var, var),
            -2
        ) #otherwise this continues to check the next lane
    return ( 
        f"🔎 Checking Lane... {var+1}…",
        html_heat(heat, var, -1),
        var + 1
    )


# --- This function controls the most important part of the app
# --- Step 1 - generate the heat
# --- Step 2 - display the instructions of the app
# --- Step 3 - search through each and all lanes


def next_step(stage, target_input, heat):
    target = (target_input or "").strip()
    if stage == 1: #ensure the user actually typed a name, EDGE-CASE
        if target == "":
            return (
                "⚠️ Please enter the sprinter you're trying to locate...",
                gr.update(),
                gr.update(visible=False),
                stage,
                heat
            ) #once we know the name is validated, create the heat
        new_heat = create_heat(target, 8)
        return (
            f" Heat generated!<br><br>"
            f"Linear search will now look for <b>{target}</b> lane by lane. "
            "Remember: the list is unsorted, so each lane must be checked in order.",
            gr.update(visible=True),
            gr.update(value="Start Searching"),
            2,
            new_heat
        ) #here we are actually providing information about linear search
    if stage == 2:
        info = (
            "<div style='background:#CFD8DC; padding:12px; border-radius:8px; margin-top:10px;'>"
            "<h4 style='margin:0; color:#37474F;'> Linear Search Info</h4>"
            "<ul style='margin-top:5px;'>"
            "<li>⏱ Time complexity: O(n) in the worst case.</li>"
            "</ul></div>"
        )
        return (
            f" Searching for <b>{target}</b>…{info}",
            gr.update(visible=True),
            gr.update(value="Next Lane."),
            3,
            heat
        )
    return "", gr.update(), gr.update(), stage, heat

#now we are resetting everything to the start 
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

# --- HERE we are building the Gradio interface
with gr.Blocks() as demo:

    gr.Markdown( # create TOP header
        """ 
        <h1 style="text-align:center; color:#0D47A1;">
        🏟️ Linear Search Tracker
        </h1>
        <p style="text-align:center; font-size:16px;">
        Step through each lane to locate your athlete coach!
        </p>
        """
    )
#diplay the boxes
    storyline = gr.HTML("🏃‍♂️ Welcome Coach!<br>Type the runner's name to start the search.")
    name_box = gr.Textbox(label="Athlete Name", placeholder="e.g., Lyles")
    heat_display = gr.HTML("")

    main_button = gr.Button("Find Runner :)")

      # internal states to track where we are

    stage_state = gr.State(1)
    heat_state = gr.State([])
    search_var = gr.State(-1)

  
    def handle_steps(stage, name, heat):
        return next_step(stage, name, heat)
#move through steps 1 2 and 3

    main_button.click(
        fn=handle_steps,
        inputs=[stage_state, name_box, heat_state],
        outputs=[storyline, heat_display, main_button, stage_state, heat_state]
    )
#ACTUALLY check the lanes during step 3 
    def lanes_search(stage, heat, name, idx):
        if stage == 3:
            return step_search(heat, name, idx)
        return gr.update(), gr.update(), idx

    main_button.click(
        fn=lanes_search,
        inputs=[stage_state, heat_state, name_box, search_var],
        outputs=[storyline, heat_display, search_var]
    )
#launch the app
demo.launch(share=True)
