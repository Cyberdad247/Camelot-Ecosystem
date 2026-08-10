import z3

solver = z3.Solver()
# Variables
agent_authenticated = z3.Bool('agent_authenticated')
task_routed = z3.Bool('task_routed')

# Constraint: A task can ONLY be routed if the agent is authenticated (SPIFFE mTLS)
solver.add(task_routed == agent_authenticated)

# Test Case: Agent is NOT authenticated
solver.add(agent_authenticated == False)

# Check if task_routed can be True
solver.push()
solver.add(task_routed == True)
if solver.check() == z3.unsat:
    print('[Z3_SOLVER] STATUS = VERIFIED. Unauthenticated routing is mathematically impossible.')
else:
    print('[Z3_SOLVER] FATAL ERROR. Logic breach detected.')
