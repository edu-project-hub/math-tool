from flask import Blueprint, request, render_template
from graphviz import Digraph
from math_utils import factorial, binom_coeff
from fractions import Fraction

tree_bp = Blueprint('tree', __name__, url_prefix='/tree')

@tree_bp.route("/", methods=["GET", "POST"])
def tree():
    if request.method == "POST":
        event_count = int(request.form.get("eventCount", "0"))
        identical = (request.form.get("identical") == "yes")
        without_replacement = (request.form.get("withoutReplacement") == "yes")
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
        
        if identical and without_replacement:
            # Without replacement: use the raw state counts from the first event.
            # Convert values to integers to ensure proper Fraction calculations.
            initial_raw_states = [(n, int(v)) for n, v in all_events[0]]
            dot, combos = build_probability_tree(initial_raw_states, without_replacement=True, event_count=event_count)
        else:
            # Standard calculation: compute probabilities for each event independently.
            events = []
            for raw_states in all_events:
                sum_vals = sum(v for (_, v) in raw_states)
                if sum_vals == 0:
                    prob_states = [(n, Fraction(1, len(raw_states))) for (n, v) in raw_states] if raw_states else []
                else:
                    prob_states = [
                        (n, Fraction(v).limit_denominator() / Fraction(sum_vals).limit_denominator())
                        for (n, v) in raw_states
                    ]
                events.append(prob_states)
            dot, combos = build_probability_tree(events, without_replacement=False)
        dot.format = "svg"
        svg_data = dot.pipe().decode("utf-8")
        return render_template("tree.html", svg_graph=svg_data, combinations=combos)
    else:
        return render_template("tree.html")

def build_probability_tree(data, without_replacement=False, event_count=None):
    if without_replacement:
        # data is the initial_raw_states: a list of (state_name, count) with integer counts.
        total = sum(v for (n, v) in data)
        dot = Digraph(comment="Wahrscheinlichkeitsbaum")
        dot.node("root", label="Start")
        # Each branch stores: (node_id, path_label, probability, current_counts, current_total)
        current_level = [("root", "", Fraction(1), {n: v for (n, v) in data}, total)]
        for i in range(event_count):
            next_level = []
            for (parent_node_id, path_label, parent_prob, counts, tot) in current_level:
                for state in counts:
                    if counts[state] > 0:
                        new_prob = parent_prob * Fraction(counts[state], tot)
                        new_counts = counts.copy()
                        new_counts[state] = new_counts[state] - 1
                        new_tot = tot - 1
                        edge_prob = Fraction(counts[state], tot)
                        edge_label = f"{state} (p={float(edge_prob):.6f} = {edge_prob})"
                        new_node_id = f"e{i}_{state}_{parent_node_id}"
                        new_node_label = f"{path_label}{state}\\nGesamt p={float(new_prob):.6f} = {new_prob}"
                        dot.node(new_node_id, label=new_node_label)
                        dot.edge(parent_node_id, new_node_id, label=edge_label)
                        next_level.append((new_node_id, path_label + state + ", ", new_prob, new_counts, new_tot))
            current_level = next_level
        combos = []
        for (node_id, path_label, prob, counts, tot) in current_level:
            states_str = path_label.strip().rstrip(",")
            combo_tuple = tuple(s.strip() for s in states_str.split(",")) if states_str else ()
            combos.append((combo_tuple, float(prob)))
        return dot, combos
    else:
        # data is a list of events; each event is a list of (state_name, probability)
        dot = Digraph(comment="Wahrscheinlichkeitsbaum")
        dot.node("root", label="Start")
        current_level = [("root", "", Fraction(1))]
        for event_index, states in enumerate(data):
            next_level = []
            for (parent_node_id, path_label, parent_prob) in current_level:
                for state_index, (state_name, state_prob) in enumerate(states):
                    new_node_id = f"e{event_index}_s{state_index}_{parent_node_id}"
                    new_prob = parent_prob * state_prob
                    edge_label = f"{state_name} (p={float(state_prob):.6f} = {state_prob})"
                    new_node_label = f"{path_label}{state_name}\\nGesamt p={float(new_prob):.6f} = {new_prob}"
                    dot.node(new_node_id, label=new_node_label)
                    dot.edge(parent_node_id, new_node_id, label=edge_label)
                    next_level.append((new_node_id, path_label + state_name + ", ", new_prob))
            current_level = next_level
        combos = []
        for (node_id, path_label, prob) in current_level:
            states_str = path_label.strip().rstrip(",")
            combo_tuple = tuple(s.strip() for s in states_str.split(",")) if states_str else ()
            combos.append((combo_tuple, float(prob)))
        return dot, combos
