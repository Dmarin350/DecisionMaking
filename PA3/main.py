from collections import defaultdict
import random

states = [
    "RU_8p", "TU_10p", "RU_10p", "RD_10p","RD_8a","RU_8a",
    "TU_10a", "RU_10a", "RD_10a", "TD_10a",
    "CLASS BEGINS"
]

actions = {
    "RU_8p": ["P", "R", "S"],
    "TU_10p": ["P", "R"],
    "RU_10p": ["R", "S", "P"],
    "RD_10p": ["R", "S", "P"], 
    "TU_10a": ["any"], "RU_10a": ["any"],
    "RD_10a": ["any"], "TD_10a": ["any"],
    "RD_8a": ["P", "R"],
    "RU_8a": ["P", "R", "S"],
    "CLASS BEGINS": []
}

P = defaultdict(list)

# RU_8p
P["RU_8p","P"] = [(1.0, "TU_10p", 2)]
P["RU_8p","R"] = [(1.0, "RU_10p", 0)]
P["RU_8p","S"] = [(1.0, "RD_10p", -1)]

# TU_10p
P["TU_10p","R"] = [(1.0,"RU_8a",0)]
P["TU_10p","P"] = [(1.0,"RU_10a",2)]

# RU_10p
P["RU_10p","R"] = [(1.0, "RU_8a", 0)]
P["RU_10p","S"] = [(1.0, "RD_8a", -1)]
P["RU_10p","P"] = [(0.5, "RU_8a", 2), (0.5, "RU_10a", 2)]

# RD_10p
P["RD_10p","R"] = [(1.0, "RD_8a", 0)]
P["RD_10p","P"] = [(0.5, "RD_8a", 2), (0.5, "RD_10a", 2)]

# RU_8a
P["RU_8a","P"] = [(1.0, "TU_10a", 2)]
P["RU_8a","R"] = [(1.0, "RU_10a", 0)]
P["RU_8a","S"] = [(1.0, "RD_10a", -1)]

# RD_8a
P["RD_8a","P"] = [(1.0, "TD_10a", 2)]
P["RD_8a","R"] = [(1.0, "RD_10a", 0)]

# TU_10a
P["TU_10a","any"] = [(1.0, "CLASS BEGINS", -1)]
# RU_10a
P["RU_10a","any"] = [(1.0, "CLASS BEGINS", 0)]
# RD_10a
P["RD_10a","any"] = [(1.0, "CLASS BEGINS", 4)]
# TD_10a
P["TD_10a","any"] = [(1.0, "CLASS BEGINS", 3)]


lambda_s = 0.99
theta = 0.001

# Initialize V(s)=0
V = {s: 0.0 for s in states}

iteration = 0
while True:
    delta = 0.0
    iteration += 1

    print(f"\n=== Iteration {iteration} ===")
    # Sweep over all states, that aren't back in CLASS BEGINS
    for s in [s for s in states if s != "CLASS BEGINS"]:
        v_old = V[s]

        # Compute Q(s,a) for each action
        q_values = {}
        for a in actions[s]:
            q = 0.0
            for (prob, s_next, reward) in P[(s, a)]:
                q += prob * (reward + lambda_s * V[s_next])
            q_values[a] = q

        # Best action & new value
        best_a, v_new = max(q_values.items(), key=lambda item: item[1])

        # Print debug info
        print(f"State {s}: V_old = {v_old:.4f}")
        for a, q in q_values.items():
            print(f"    Q({a}) = {q:.4f}")
        print(f"    -> choose {best_a}, V_new = {v_new:.4f}")

        # Update
        V[s] = v_new
        delta = max(delta, abs(v_new - v_old))

    # Convergence check
    if delta < theta:
        print(f"\nConverged (Δ={delta:.6f} < {theta})\n")
        break


# Get the final policy
policy = {}
for s in [s for s in states if s not in ("CLASS BEGINS",)]:
    # recompute Q(s,a)
    q_values = {a: sum(prob*(reward + lambda_s*V[s2]) 
                       for prob, s2, reward in P[(s, a)])
                for a in actions[s]}
    best_a = max(q_values, key=q_values.get)
    policy[s] = best_a


# Total Number of Iterations
print(f"Total iterations: {iteration}\n")

print("Final values V*(s):")
for s in states:
    if s != "CLASS BEGINS":
        print(f"  V({s}) = {V[s]:.4f}")
print(f"  V(CLASS BEGINS) = {V['CLASS BEGINS']:.4f}")

print("(States omitted from policy are terminal or have no actions)")
for s, a in policy.items():
    print(f"  π({s}) = {a}")
    
    

# Q-learning parameters
Q = defaultdict(float)
alpha = 0.1
epsilon = 0.2
episodes = 0

lambda_s = 0.99  # reuse from earlier

def is_terminal(state):
    return state == "CLASS BEGINS"

print("\n=== Starting Q-Learning ===")
max_delta = float("inf")

while max_delta > 0.001:
    episodes += 1
    s = "RU_8p"
    max_delta = 0.0

    while not is_terminal(s):
        # Get valid actions with defined transitions
        valid_actions = [a for a in actions[s] if (s, a) in P]
        if not valid_actions:
            print(f"No valid transitions from {s}, stopping episode.")
            break

        # Epsilon-greedy action selection
        if random.random() < epsilon:
            a = random.choice(valid_actions)
        else:
            q_vals = {a: Q[(s, a)] for a in valid_actions}
            a = max(q_vals, key=q_vals.get)

        # Sample transition from P
        transitions = P[(s, a)]
        prob, s_next, reward = random.choices(
            transitions, weights=[t[0] for t in transitions]
        )[0]

        # Q-learning update
        max_q_next = max((Q[(s_next, a2)] for a2 in actions[s_next] if (s_next, a2) in P), default=0.0)
        q_old = Q[(s, a)]
        q_new = q_old + alpha * (reward + lambda_s * max_q_next - q_old)
        Q[(s, a)] = q_new
        max_delta = max(max_delta, abs(q_new - q_old))

        # Logging
        print(f"Episode {episodes}, State {s}, Action {a}")
        print(f"    Q_old = {q_old:.4f}, Reward = {reward}, Q_next_max = {max_q_next:.4f}")
        print(f"    Q_new = {q_new:.4f}, ΔQ = {abs(q_new - q_old):.6f}")

        s = s_next

print(f"\nQ-Learning Converged after {episodes} episodes\n")

# Derive final policy
final_policy = {}
for s in [s for s in states if s != "CLASS BEGINS"]:
    valid_actions = [a for a in actions[s] if (s, a) in P]
    if valid_actions:
        best_a = max(valid_actions, key=lambda a: Q[(s, a)])
        final_policy[s] = best_a

# Print Q values and final policy
print("Final Q-values:")
for (s, a), q_val in Q.items():
    print(f"  Q({s},{a}) = {q_val:.4f}")

print("\nOptimal Policy from Q-learning:")
for s, a in final_policy.items():
    print(f"  π({s}) = {a}")
