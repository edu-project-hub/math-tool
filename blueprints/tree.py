from flask import Blueprint, request, render_template
from graphviz import Digraph
from math_utils import factorial, binom_coeff

tree_bp = Blueprint('tree', __name__, url_prefix='/tree')

@tree_bp.route("/", methods=["GET", "POST"])
def tree():
    if request.method == "POST":
        event_count = int(request.form.get("eventCount", "0"))
        identical = (request.form.get("identical") == "yes")
        all_events = []
        for i in range(event_count):
            state_count = int(request.form.get(f"stateCount_{i}", "0"))
            raw_states = []
            for j in range(state_count):
                name = request.form.get(f"event_{i}_state_{j}_name", "").strip()
                val_str = request.form.get(f"event_{i}_state_{j}_value", "0").strip()
                try:
                    val = float(val_str)
                except ValueError:
                    val = 0.0
                raw_states.append((name, val))
            all_events.append(raw_states)
        if identical and len(all_events) > 0:
            first_event = all_events[0]
            all_events = [first_event for _ in range(event_count)]
        events = []
        for raw_states in all_events:
            sum_vals = sum(v for (_, v) in raw_states)
            if sum_vals == 0:
                prob_states = [(n, 1.0/len(raw_states)) for (n, v) in raw_states] if raw_states else []
            else:
                prob_states = [(n, v/sum_vals) for (n, v) in raw_states]
            events.append(prob_states)

        dot, combos = build_probability_tree(events)
        dot.format = "svg"
        svg_data = dot.pipe().decode("utf-8")
        return render_template("tree.html", svg_graph=svg_data, combinations=combos)
    else:
        return render_template("tree.html")

def build_probability_tree(events):
    dot = Digraph(comment="Wahrscheinlichkeitsbaum")
    dot.node("root", label="Start")
    current_level = [("root", "", 1.0)]
    for event_index, states in enumerate(events):
        next_level = []
        for (parent_node_id, path_label, parent_prob) in current_level:
            for state_index, (state_name, state_prob) in enumerate(states):
                new_node_id = f"e{event_index}_s{state_index}_{parent_node_id}"
                new_prob = parent_prob * state_prob
                edge_label = f"{state_name} (p={state_prob:.3f})"
                new_node_label = f"{path_label}{state_name}\\nGesamt p={new_prob:.4f}"
                dot.node(new_node_id, label=new_node_label)
                dot.edge(parent_node_id, new_node_id, label=edge_label)
                next_level.append((new_node_id, path_label + state_name + ", ", new_prob))
        current_level = next_level
    combinations = []
    for (node_id, path_label, prob) in current_level:
        states_str = path_label.strip().rstrip(",")
        combo_tuple = tuple(s.strip() for s in states_str.split(",")) if states_str else ()
        combinations.append((combo_tuple, prob))
    return dot, combinations
