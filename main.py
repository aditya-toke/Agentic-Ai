from agent.observer import observe
from agent.reasoner import reason
from agent.decider import decide
from agent.actor import act
from agent.memory import remember

def agent_loop():
    tickets, logs, merchants = observe()
    reasoning = reason(tickets, logs, merchants)
    action = decide(reasoning)
    act(action, reasoning)
    remember(reasoning, action)

if __name__ == "__main__":
    agent_loop()
